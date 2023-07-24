import time
import datetime
import os
import threading
import sys
import configparser
import subprocess
import queue
import requests
import streamlink
from PySide6 import QtCore, QtWidgets

import Utils
import tkinter as tk

if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

mainDir = sys.path[0]
Config = configparser.ConfigParser()
setting = {}
# processingQueue = queue.Queue()
recording = []
postprocessing = []
runProg = True
hilos = []
recording_history = []


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def readConfig():
    global setting

    Config.read(mainDir + '/config.conf')
    setting = {
        'save_directory': Config.get('paths', 'save_directory'),
        'wishlist': Config.get('paths', 'wishlist'),
        'interval': int(Config.get('settings', 'checkInterval')),
        'postProcessingCommand': Config.get('settings', 'postProcessingCommand'),
        }
    try:
        setting['postProcessingThreads'] = int(Config.get('settings', 'postProcessingThreads'))
    except ValueError:
        if setting['postProcessingCommand'] and not setting['postProcessingThreads']:
            setting['postProcessingThreads'] = 1

    if not os.path.exists(f'{setting["save_directory"]}'):
        os.makedirs(f'{setting["save_directory"]}')

# def postProcess():
#     while runProg is True:
#         while processingQueue.empty():
#             time.sleep(1)
#         parameters = processingQueue.get()
#         print("PostProcess")
#         model = parameters['model']
#         path = parameters['path']
#         filename = os.path.split(path)[-1]
#         directory = os.path.dirname(path)
#         file = os.path.splitext(filename)[0]
#         subprocess.call(setting['postProcessingCommand'].split() + [path, filename, directory, model,  file, 'cam4'])

class Modelo(threading.Thread):
    def __init__(self, modelo):
        super().__init__()
        self.modelo = modelo
        self._stopevent = threading.Event()
        self.file = None
        self.online = None
        self.lock = threading.Lock()
        self.start_time = None
        self.stop_time = None
        self.repair_thread = None

    def run(self):
        global recording, hilos, recording_history
        isOnline = self.isOnline()
        if isOnline == False:
            self.online = False
        else:
            self.online = True
            self.file = os.path.join(setting['save_directory'], self.modelo, f'{datetime.datetime.fromtimestamp(time.time()).strftime("%Y.%m.%d_%H.%M.%S")}_{self.modelo}.mp4')
            try:
                if self.start_time is None:
                    self.start_time = time.time()
                session = streamlink.Streamlink()
                streams = session.streams(f'hlsvariant://{isOnline}')
                stream = streams['best']
                fd = stream.open()
                if not isModelInListofObjects(self.modelo, recording):
                    os.makedirs(os.path.join(setting['save_directory'], self.modelo), exist_ok=True)
                    with open(self.file, 'wb') as f:
                        self.lock.acquire()
                        recording.append(self)
                        recording_history.append({"model": self.modelo, "filename": self.file, "status": "Recording"})
                        print(self.modelo + " added to recording history")
                        for index, hilo in enumerate(hilos):
                            if hilo.modelo == self.modelo:
                                del hilos[index]
                                break
                        self.lock.release()
                        while not (self._stopevent.isSet() or os.fstat(f.fileno()).st_nlink == 0):
                            try:
                                data = fd.read(1024)
                                f.write(data)
                                # Utils.add_duration_to_mp4(self.file, time.time() - self.start_time)
                                # print("WRITE DURATION: "+self.modelo + time.time() - self.start_time)
                            except:
                                fd.close()
                                break
                    # if setting['postProcessingCommand']:
                    #     processingQueue.put({'model': self.modelo, 'path': self.file})
            except Exception as e:
                with open('log.log', 'a+') as f:
                    f.write(f'\n{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} EXCEPTION: {e}\n')
                self.stop()
            finally:
                self.exceptionHandler()

    def exceptionHandler(self):
        self.stop()
        self.online = False
        self.lock.acquire()
        for index, hilo in enumerate(recording):
            if hilo.modelo == self.modelo:
                del recording[index]
                matching_item = next((item for item in recording_history if item["model"] == self.modelo), None)
                matching_item["status"] = "Stopped Recording"
                print("RECORDING HISTORY: " + '\n'.join([f"{recording_history[i]}" for i in range(len(recording_history))]))
                break
        self.lock.release()
        try:
            file = os.path.join(os.getcwd(), self.file)
            if os.path.isfile(file):
                if os.path.getsize(file) <= 1024:
                    os.remove(file)

        except Exception as e:
            with open('log.log', 'a+') as f:
                f.write(f'\n{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} EXCEPTION: {e}\n')
    def isOnline(self):
        try:
            resp = requests.get(f'https://stripchat.com/api/front/v2/models/username/{self.modelo}/cam').json()
            hls_url = ''
            if 'cam' in resp.keys():
                if {'isCamAvailable', 'streamName', 'viewServers'} <= resp['cam'].keys():
                    if 'flashphoner-hls' in resp['cam']['viewServers'].keys():
                        hls_url = f'https://b-{resp["cam"]["viewServers"]["flashphoner-hls"]}.doppiocdn.com/hls/{resp["cam"]["streamName"]}/{resp["cam"]["streamName"]}.m3u8'
                        print(hls_url)
            if len(hls_url):
                return hls_url
            else:
                return False
        except:
            return False

    def stop(self):
        global recording, hilos
        self._stopevent.set()
        if isModelInListofObjects(self.modelo, recording):
            print("STOP MODEL: " + self.modelo + "self.file: " + self.file)
            if not (self.file in postprocessing):
                postprocessing.append(self.file)
                print(postprocessing)
            #self.repair_thread = self.repair_mp4_file_thread()


class CleaningThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.interval = 0
        self.lock = threading.Lock()

    def run(self):
        global hilos, recording, runProg
        while runProg is True:
            self.lock.acquire()
            new_hilos = []
            for hilo in hilos:
                if hilo.is_alive() or hilo.online:
                    new_hilos.append(hilo)
            # Get the new elements (i.e. elements in new_array but not in old_array)
            new_model = list(set(new_hilos) - set(hilos))

            # Get the removed elements (i.e. elements in old_array but not in new_array)
            removed_model = list(set(hilos) - set(new_hilos))

            # Print the new and removed elements
            print(f"New elements: {new_model[i]}" for i in range(len(new_model)))
            print(f"Removed elements: {removed_model[i]}" for i in range(len(removed_model)))
            hilos = new_hilos
            self.lock.release()
            for i in range(10, 0, -1):
                self.interval = i
                time.sleep(1)




class AddModelsThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.wanted = []
        self.lock = threading.Lock()
        self.repeatedModels = []
        self.counterModel = 0

    def run(self):
        global hilos, recording
        lines = open(setting['wishlist'], 'r').read().splitlines()
        self.wanted = (x for x in lines if x)
        self.lock.acquire()
        aux = []
        for model in self.wanted:
            model = model.lower()
            if model in aux:
                self.repeatedModels.append(model)
            else:
                aux.append(model)
                self.counterModel = self.counterModel + 1
                if not isModelInListofObjects(model, hilos) and not isModelInListofObjects(model, recording):
                    thread = Modelo(model)
                    thread.start()
                    # print("APPEND MODEL: " + model)
                    hilos.append(thread)
        for hilo in recording:
            if hilo.modelo not in aux:
                hilo.stop()
        self.lock.release()

def isModelInListofObjects(obj, lista):
    result = False
    for i in lista:
        if i.modelo == obj:
            result = True
            break
    return result

def stopRecording():
    global runProg
    runProg = False
    for hilo in recording:
        hilo.stop()

# class ChatRecorder(QtCore.QObject):
#     messageSignal = QtCore.Signal(str)
#
#     def __init__(self):
#         super().__init__()
#         self.stop_event = threading.Event()
#         self.recordingList = []
#     def startRecording(recordingList):
#         global runProg, recording_history
#         readConfig()
#         runProg = True
#         cleaningThread = CleaningThread()
#         cleaningThread.start()
#
#         while runProg is True:
#             readConfig()
#             addModelsThread = AddModelsThread()
#             addModelsThread.start()
#             i = 1
#             for i in range(setting['interval'], 0, -1):
#                 cls()
#                 if (runProg is True):
#                     recordingList[0].clear()
#                     recordingList[1].clear()
#                     if len(addModelsThread.repeatedModels): print(
#                         'The following models are more than once in wanted: [\'' + ', '.join(
#                             modelo for modelo in addModelsThread.repeatedModels) + '\']')
#                     print(
#                         f'{len(hilos):02d} alive Threads (1 Thread per non-recording model), cleaning dead/not-online Threads in {cleaningThread.interval:02d} seconds, {addModelsThread.counterModel:02d} models in wanted')
#                     print(f'Online Threads (models): {len(recording):02d}')
#                     print('The following models are being recorded:')
#                     for hiloModelo in recording:
#                         print(f'  Model: {hiloModelo.modelo}  -->  File: {os.path.basename(hiloModelo.file)}')
#                         recordingList[0].append(hiloModelo)
#                     for history in recording_history:
#                         recordingList[1].append(history)
#                     print("inside recordng list", recordingList[0])
#                     print("inside recordng history", recordingList[1])
#                     print(f'Next check in {i:02d} seconds')
#
#                     time.sleep(1)
#                 else:
#
#                     recordingList[0].clear()
#                     recordingList[1].clear()
#             addModelsThread.join()
#
#             del addModelsThread, i
#             print("START POSTPROCESSING: " + '\n'.join([f"{postprocessing[i]}" for i in range(len(postprocessing))]))
#
#         for file in postprocessing:
#             print("START REPAIR THREAD")
#
#             def target():
#                 Utils.repair_mp4_file_ffmpeg(file)
#
#             # output_file = Utils.repair_mp4_file_ffmpeg(file)
#             thread = threading.Thread(target=target)
#             thread.daemon = True
#             thread.start()
#         postprocessing.clear()
#
#         # Create a new thread and start it
#         # thread = threading.Thread(target=target)
#         # thread.daemon = True
#         # thread.start()
#         cleaningThread.join()
#         # processingQueue.join()
#         exit()
#
#     def stopRecording(self):
#         self.stop_event.set()

def startRecording(recordingList):
    global runProg, recording_history
    readConfig()
    runProg = True
    cleaningThread = CleaningThread()
    cleaningThread.start()

    while runProg is True:
        readConfig()
        addModelsThread = AddModelsThread()
        addModelsThread.start()
        i = 1
        for i in range(setting['interval'], 0, -1):
            cls()
            if (runProg is True):
                recordingList[0].clear()
                recordingList[1].clear()
                if len(addModelsThread.repeatedModels): print('The following models are more than once in wanted: [\'' + ', '.join(modelo for modelo in addModelsThread.repeatedModels) + '\']')
                print(f'{len(hilos):02d} alive Threads (1 Thread per non-recording model), cleaning dead/not-online Threads in {cleaningThread.interval:02d} seconds, {addModelsThread.counterModel:02d} models in wanted')
                print(f'Online Threads (models): {len(recording):02d}')
                print('The following models are being recorded:')
                for hiloModelo in recording:
                    print(f'  Model: {hiloModelo.modelo}  -->  File: {os.path.basename(hiloModelo.file)}')
                    recordingList[0].append(hiloModelo)
                for history in recording_history:
                    recordingList[1].append(history)
                print("inside recordng list", recordingList[0])
                print("inside recordng history", recordingList[1])
                print(f'Next check in {i:02d} seconds')

                time.sleep(1)
            else:

                recordingList[0].clear()
                recordingList[1].clear()
        addModelsThread.join()

        del addModelsThread, i
        print("START POSTPROCESSING: " + '\n'.join([f"{postprocessing[i]}" for i in range(len(postprocessing))]))

    for file in postprocessing:
        print("START REPAIR THREAD")

        def target():
            Utils.repair_mp4_file_ffmpeg(file)
        # output_file = Utils.repair_mp4_file_ffmpeg(file)
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
    postprocessing.clear()

        # Create a new thread and start it
        # thread = threading.Thread(target=target)
        # thread.daemon = True
        # thread.start()
    cleaningThread.join()
    # processingQueue.join()
    exit()

