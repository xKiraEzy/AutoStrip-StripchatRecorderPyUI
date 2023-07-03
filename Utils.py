import os
import time
from datetime import datetime
import subprocess

def format_model_to_UI(models):
    result = []
    for model in models:
        elapsed_time = time.time() - model.start_time
        minutes, seconds = divmod(elapsed_time, 60)
        start_datetime = datetime.fromtimestamp(model.start_time).strftime('%H:%M:%S')
        result.append(f"{model.modelo} | Start From: {start_datetime} ({int(minutes)}m {int(seconds)}s)")
    return '\n'.join([f"{result[i]}" for i in range(len(result))])

def format_recording_history_to_UI(recording_history):
    # Get the model, filename, and isRecording values from the dictionary
    model = recording_history["model"]
    filename = recording_history["filename"]
    status = recording_history["status"]
    # Format the dictionary values into the desired format
    formatted_string = f"model: {model} | status: {status}\nFile: {filename}"
    # Join the formatted strings with a newline separator
    return formatted_string

def add_duration_to_mp4(path, duration):
    cmd = f'ffmpeg -i "{path}" -c copy -metadata duration={duration} "{path}_new.mp4"'
    subprocess.run(cmd, shell=True)

def repair_mp4_file(input_file):
    output_file = os.path.splitext(input_file)[0] + "_fix.mp4"
    vlc_process = subprocess.Popen(["vlc", "-I", "rc", input_file, "--sout", "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100}:standard{access=file,mux=mp4,dst=" + output_file + "}", "vlc://quit"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Return the output file name
    vlc_process.wait()

    # Replace the input file with the output file
    # os.replace(output_file, input_file)
    return output_file

def repair_mp4_file_ffmpeg(input_file):
    # Call ffmpeg to repair the input file
    output_file = os.path.splitext(input_file)[0] + "_fix.mp4"
    cmd = f'ffmpeg -y -i "{input_file}" -c copy "{output_file}"'
    ffmpeg_process = subprocess.run(cmd, shell=True)

    # ffmpeg_process.wait()
    os.replace(output_file, input_file)

    return input_file
    # Replace the input file with the output file
