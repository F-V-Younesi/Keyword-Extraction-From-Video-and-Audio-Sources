# -*- coding: utf-8 -*-
"""Copy of Media2keyword-time/accur.ipynb

Automatically generated by Colab.

# **بسم الله الرحمن الرحیم**

#Format Recognition | Converting Video to Audio | Removing Music

##Format Recognition | Converting Video to Audio
"""

# Importing Libraries:
import moviepy.editor
import statistics
import os

"""###Upload Your video/Audio file here:"""

from google.colab import files
uploaded = files.upload()
path = next(iter(uploaded))

# This section of code, Investigate that the input file is audio or video or None of them.
audio_suffixes = ("mp3", "wav","3gp",'8svx','aa','aac','aax','act','aiff','alac','amr','ape','au','awb','cda','dss','dvf','flac','gsm','iklax','ivs','m4a','m4b','m4p','mmf','movpkg','mpc','msv','nmf','ogg','oga','mogg','opus','rm','ra','raw','rf64','sln','tta','voc','vox','webm','wma','wv')
video_suffixes =('webm','mkv','mp4','m4p','m4v','flv','vob','ogv','drc','gif','gifv','mng','avi','MTS','M2TS','TS','mov','qt','wmv','yuv','rmvb','viv','asf','amv','rm','ogg','sv','3pg','3g2','mxf','roq','nsv','f4v','f4p','f4a','f4b')
def is_video(path):
  if path.endswith(video_suffixes):
    print("The input is a video file.")
    return True
  elif path.endswith(audio_suffixes):
    print("The input is an audio file.")
    return False
  else:
    print("This file has neither video nor audio format. Please enter another file.")

#Convertion of video to audio:
def vid2audio(path):
  #Load the Video
  video = moviepy.editor.VideoFileClip(path)

  #Extract the Audio
  audio = video.audio

  #Export the Audio
  audio.write_audiofile("Audio.mp3")

# path='موزیک.mp4'
video=is_video(path)
if video is True:
  vid2audio(path)
  path="Audio.mp3"
elif video is False:
  os.rename(path,'Audio.mp3')

path="/content/موزیک سرعت.mp4"
vid2audio(path)

"""##Recognize & remove music:"""

import io,os
from pathlib import Path
import select
from shutil import rmtree
import subprocess as sp
import sys
from typing import Dict, Tuple, Optional, IO
!pip install pydub
from pydub import AudioSegment, silence
import librosa , numpy as np

def find_files(in_path):
    out = []
    for file in Path(in_path).iterdir():
        if file.suffix.lower().lstrip(".") in extensions:
            out.append(file)
    return out

def copy_process_streams(process: sp.Popen):
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
        p_stdout.fileno(): (p_stdout, sys.stdout),
        p_stderr.fileno(): (p_stderr, sys.stderr),
    }
    fds = list(stream_by_fd.keys())

    while fds:
        # `select` syscall will wait until one of the file descriptors has content.
        ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            buf = raw_buf.decode()
            std.write(buf)
            std.flush()

def separate(inp=None, outp=None):
    inp = inp or in_path
    outp = outp or out_path
    cmd = ["python3", "-m", "demucs.separate", "-o", str(outp), "-n", model]
    if mp3:
        cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]
    if float32:
        cmd += ["--float32"]
    if int24:
        cmd += ["--int24"]
    if two_stems is not None:
        cmd += [f"--two-stems={two_stems}"]
    files = [str(f) for f in find_files(inp)]
    if not files:
        print(f"No valid audio files in {in_path}")
        return
    print("**Going to separate Music and Vocals from the files:\n")
    # print('\n'.join(files))
    # print("With command: ", " ".join(cmd))
    p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
    copy_process_streams(p)
    p.wait()
    if p.returncode != 0:
        print("Command failed, something went wrong.")


def remove_music():
    out_path = Path('separated')
    in_path = Path('tmp_in')

    if in_path.exists():
        rmtree(in_path)
    in_path.mkdir()

    if out_path.exists():
        rmtree(out_path)
    out_path.mkdir()

    # uploaded = files.upload()
    name='Audio.mp3'
    !cp '/content/Audio.mp3' '/content/tmp_in'
    # for name, content in uploaded.items():
    #     (in_path / name).write_bytes(content)
    separate(in_path, out_path)


def music_length(overlay_music):
# myaudio = AudioSegment.from_mp3("/content/merged.mp3")
    silence1 = silence.detect_silence(overlay_music, min_silence_len=3000, silence_thresh=-40)
    silencelist = [((start/1000),(stop/1000)) for start,stop in silence1] #convert to sec
    c=0
    for i in range(0,len(silencelist)):
      c=c+silencelist[i][1]-silencelist[i][0]
    T=len(overlay_music)
    music_len=(T-c)/(T)
    return music_len
#   elif loudness>-18:
#     if vocal_loudness<-30:
#         print("\n **This Video/Audio contains Only Music and does not contain any useful contents.")
#     else:
#         print("\n **This Video/Audio contains Music & singer's voice and does not contain any useful contents.")
#     # if loudness>-20:
#     #       print('\n **This Video/Audio contains Music and voice of a singer and does not contain useful content for key extraction.')
#     # else:
#     #       print('\n **This Video/Audio contains only background Music.')

def find_silense(y,total_numbers):
  zero_nums=0
  start=int(0.1*total_numbers)
  ending=int(0.9*total_numbers)
  for i in range(start,ending):
    if -0.002<y[i]<0.002:
      # y[i]=0
      zero_nums=zero_nums+1
  return zero_nums

def content_finder(zeros,total_numbers):
  percent_zeros=zeros/total_numbers
  if percent_zeros<0.2:
    print('"\n **This Video/Audio basically contains Music and does not contain any useful contents."')
  else:
    print('"\n **This Video/Audio contains useful contents."')

def music_mode(overlay_music,overlay_music_path,vocal):
  vocal_loudness=vocal.dBFS
  loudness=overlay_music.dBFS
  if loudness<-40:
    print('\n **This Video/Audio does not contain Music contents.')
    useful_content=True
    return useful_content

  elif loudness<-30:
    print('\n **This Video/Audio contain background music on main contents that can influence on accuracy of results.')
    useful_content=True
    return useful_content

  elif loudness>-18:
    if vocal_loudness<-30:
        print("\n **This Video/Audio contains Only Music and does not contain any useful contents.")
        useful_content=False
        return useful_content
    else:
        print("\n **This Video/Audio contains Music & singer's voice and does not contain any useful contents.")
        useful_content=False
        return useful_content

  else:
    y, sr = librosa.load(overlay_music_path)
    total_numbers=len(y)
    zeros=find_silense(y,total_numbers)
    content_finder(zeros,total_numbers)
    # print(zeros,total_numbers)

!pip install praat-parselmouth
import parselmouth
import seaborn as sns

snd = parselmouth.Sound("/content/Audio.mp3")

def draw_pitch(pitch):
    # Extract selected pitch contour, and
    # replace unvoiced samples by NaN to not plot
    pitch_values = pitch.selected_array['frequency']
    pitch_values[pitch_values==0] = np.nan
    plt.plot(pitch.xs(), pitch_values, 'o', markersize=5, color='w')
    plt.plot(pitch.xs(), pitch_values, 'o', markersize=2)
    plt.grid(False)
    plt.ylim(0, pitch.ceiling)
    plt.ylabel("fundamental frequency [Hz]")
def draw_spectrogram(spectrogram, dynamic_range=70):
    X, Y = spectrogram.x_grid(), spectrogram.y_grid()
    sg_db = 10 * np.log10(spectrogram.values)
    plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
    plt.ylim([spectrogram.ymin, spectrogram.ymax])
    plt.xlabel("time [s]")
    plt.ylabel("frequency [Hz]")

pitch = snd.to_pitch()
# If desired, pre-emphasize the sound fragment before calculating the spectrogram
pre_emphasized_snd = snd.copy()
pre_emphasized_snd.pre_emphasize()
spectrogram = pre_emphasized_snd.to_spectrogram(window_length=0.03, maximum_frequency=8000)
# plt.figure()
# draw_spectrogram(spectrogram)
# plt.twinx()
# draw_pitch(pitch)
# plt.xlim([snd.xmin, snd.xmax])
# plt.show()

y, sr = librosa.load('/content/Audio.mp3')
# y, sr = librosa.load('/content/music.mp3')
len(y)
# total_numbers=len(y)
# zeros=find_silense(y,total_numbers)
# content_finder(zeros,total_numbers)

#speeding up or down audio:
root = r'/content/Audio.mp3'
speed = 1.2

sound = AudioSegment.from_file(root)
so = sound.speedup(speed)
so.export(root[:-4] + '1.2.mp3', format = 'mp3')

!python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs

if os.path.exists('Audio.mp3'):
  print('**Start of the operation to check the presence of music in the audio file:\n')
  # !python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs


  model = "htdemucs"
  extensions = ["mp3", "wav", "ogg", "flac"]  # those file types supported in this model.
  two_stems = None   # only separate one stems from the rest, for instance
  # two_stems = "vocals"

  # Options for the output audio:
  mp3 = True
  mp3_rate = 320

  float32 = False  # output as float 32 wavs, unsused if 'mp3' is True.
  int24 = False    # output as int24 wavs, unused if 'mp3' is True.

  in_path = '/content/demucs'
  out_path = '/content/demucs_separated/'

  remove_music()
  !zip -r separated.zip separated

  # overlay_music.export("merged.mp3", format="mp3")

music1=AudioSegment.from_mp3('/content/separated/htdemucs/Audio/bass.mp3')
music2=AudioSegment.from_mp3('/content/separated/htdemucs/Audio/drums.mp3')
music3=AudioSegment.from_mp3('/content/separated/htdemucs/Audio/other.mp3')
vocal=AudioSegment.from_mp3('/content/separated/htdemucs/Audio/vocals.mp3')
overlay_music = music1.overlay(music2, position=0).overlay(music3, position=0)
overlay_music.export('music.mp3',format='mp3')
useful_content=music_mode(overlay_music,'music.mp3',vocal)

"""##Tests:"""

y, sr = librosa.load('Audio.mp3')
fig, ax = plt.subplots(nrows=3, sharex=True)
librosa.display.waveshow(y, sr=sr, ax=ax[0])
ax[0].set(title='agha')
ax[0].label_outer()

y, sr = librosa.load('/content/separated/htdemucs/Audio/vocals.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[1])
ax[1].set(title='vocals agha')
ax[1].label_outer()

y, sr = librosa.load('/content/soroush_music.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[2])
ax[2].set(title='music agha')
ax[2].legend()

y, sr = librosa.load('/content/drive/MyDrive/agha.mp3')
fig, ax = plt.subplots(nrows=3, sharex=True)
librosa.display.waveshow(y, sr=sr, ax=ax[0])
ax[0].set(title='agha')
ax[0].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/agha_vocals.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[1])
ax[1].set(title='vocals agha')
ax[1].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/agha_music.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[2])
ax[2].set(title='music agha')
ax[2].legend()

#soroush_hazer
y, sr = librosa.load('/content/Audio.mp3')
statistics.mode(y),statistics.mean(y),statistics.median(y)

#agha
y, sr = librosa.load('/content/agha.mp3')
statistics.mode(y),statistics.mean(y),statistics.median(y)

#challenge1
y, sr = librosa.load('/content/challenge1.mp3')
statistics.mode(y),statistics.mean(y),statistics.median(y)

#challenge2
y, sr = librosa.load('/content/challe2.mp3')
statistics.mode(y),statistics.mean(y),statistics.median(y)

#ebrahim
y, sr = librosa.load('/content/ebrahimzade.mp3')
statistics.mode(y),statistics.mean(y),statistics.median(y)

y, sr = librosa.load('/content/drive/MyDrive/nois30.wav')
fig, ax = plt.subplots(nrows=3, sharex=True)
librosa.display.waveshow(y, sr=sr, ax=ax[0])
ax[0].set(title='whole_noise30')
ax[0].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/nois30_vocals.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[1])
ax[1].set(title='vocals noise30')
ax[1].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/nois30_music.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[2])
ax[2].set(title='music nois30')
ax[2].legend()

y, sr = librosa.load('/content/drive/MyDrive/challe2.mp3')
fig, ax = plt.subplots(nrows=3, sharex=True)
librosa.display.waveshow(y, sr=sr, ax=ax[0])
ax[0].set(title='whole_challe2')
ax[0].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/challe2_vocals.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[1])
ax[1].set(title='vocals challe2')
ax[1].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/challe2_music.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[2])
# librosa.display.waveshow(y_perc, sr=sr, color='r', alpha=0.5, ax=ax[2], label='Percussive')
ax[2].set(title='music challe2')
ax[2].legend()

y, sr = librosa.load('/content/drive/MyDrive/challenge1.mp3')
fig, ax = plt.subplots(nrows=3, sharex=True)
librosa.display.waveshow(y, sr=sr, ax=ax[0])
ax[0].set(title='whole_challenge1')
ax[0].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/challenge1_vocals.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[1])
ax[1].set(title='vocals challenge1')
ax[1].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/challenge1_music.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[2])
# librosa.display.waveshow(y_perc, sr=sr, color='r', alpha=0.5, ax=ax[2], label='Percussive')
ax[2].set(title='music challenge1')
ax[2].legend()

y, sr = librosa.load('/content/drive/MyDrive/ebrahimzade.mp3')
fig, ax = plt.subplots(nrows=3, sharex=True)
librosa.display.waveshow(y, sr=sr, ax=ax[0])
ax[0].set(title='ebrahimzade')
ax[0].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/ebrahimzade_vocals.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[1])
ax[1].set(title='vocals ebrahimzade')
ax[1].label_outer()

y, sr = librosa.load('/content/drive/MyDrive/ebrahimzade_music.mp3')
librosa.display.waveshow(y, sr=sr, ax=ax[2])
# librosa.display.waveshow(y_perc, sr=sr, color='r', alpha=0.5, ax=ax[2], label='Percussive')
ax[2].set(title='music ebrahimzade')
ax[2].legend()

signal, sr = librosa.load('/content/drive/MyDrive/challenge1_vocals.mp3',duration=60)
f0, voiced_flag, voiced_probs = librosa.pyin(signal, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

# Computing pitch using the PEPLOs algorithm
f0, voiced_flag, voiced_probs = librosa.pyin(signal, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

#pitch contour plot:
plt.figure(figsize=(12, 4))
librosa.display.waveshow(signal, sr=sr, alpha=0.5)
plt.plot(librosa.frames_to_time(range(len(f0))), f0, color='r')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Pitch Contour')
plt.show()

# y, sr2 = librosa.load('/content/drive/MyDrive/ebrahimzade_vocals.mp3',duration=60)
# f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

# Plot pitch contour
plt.figure(figsize=(12, 4))
librosa.display.waveshow(signal, sr=sr, alpha=0.5)
plt.plot(librosa.frames_to_time(range(len(f0))), f0, color='r')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Pitch Contour')
plt.show()

uni,count=np.unique(f0, return_counts=True)

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/agha.mp3',duration=60)

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/agha_vocals.mp3',duration=60)

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/agha_music.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/ebrahimzade.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/ebrahimzade_music.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/ebrahimzade_vocals.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/challe2.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/challe2_music.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/challe2_vocals.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/nois30.wav')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/nois30_music.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

# Load the recorded file
signal, sr = librosa.load('/content/drive/MyDrive/challenge1_vocals.mp3')

# Compute the mel-spectrogram
mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr)

# Plot the mel-spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), sr=sr, hop_length=512, y_axis="mel", x_axis="time")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel-spectrogram")
plt.tight_layout()
plt.show()

"""#STT(Speech To Text):

##Whisper:
"""

!whisper "Audio.mp3" --model small --language Persian

def list2str(main_content):
  main_content_str=''
  for i in range (0,len(main_content)):
    main_content_str=main_content_str+'،'+main_content[i]
  return main_content_str

def find_end_segments(segments,segmentsl):
  listend=[]
  listendl=[]
  for segment in segments:
    listend.append(segment['end'])

  for segment in segmentsl:
    listendl.append(segment['end'])
  return listend,listendl

def common_endings(list1,list2):
  listcommon1=[]
  listcommon2=[]
  if len(list1)<len(list2):
    slist=list1
    dlist=list2
  else:
    slist=list2
    dlist=list1

  for i in range(0, len(slist)):
    d=[]
    for j in range(0,len(dlist)):
        d.append(abs(slist[i]-dlist[j]))
    if min(d)<5:
      listcommon2.append(dlist[d.index(min(d))])
      listcommon1.append(slist[i])

  if slist==list1:
    return listcommon1,listcommon2
  else:
    return listcommon2,listcommon1

def best_prediction(segments,segmentsl,listcommon1,listcommon2):
  listtxt=[]
  previous_id=-1
  previous_id2=-1

  for j in range(0,len(listcommon1)):
    id=0
    while segments[id]['end']!=listcommon1[j]:
      id=id+1
    id2=0
    while segmentsl[id2]['end']!=listcommon2[j]:
      id2=id2+1

    txt1=''
    txt2=''
    for i in range(previous_id+1,id+1):
      txt1=txt1+segments[i]['text']
    for i in range(previous_id2+1,id2+1):
      # startTime = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'
      # endTime = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'
      txt2=txt2+segmentsl[i]['text']
    if len(txt1)>len(txt2):
      listtxt.append(txt1)
    else:
      listtxt.append(txt2)
    previous_id=id
    previous_id2=id2

  return listtxt

def Integrated_stt(result,resultl):
  segments = result['segments']
  segmentsl=resultl['segments']
  listend,listendl = find_end_segments(segments,segmentsl)

  listcommon1,listcommon2 = common_endings(listend,listendl)

  main_content = best_prediction(segments,segmentsl,listcommon1,listcommon2)
  return main_content

!pip install git+https://github.com/openai/whisper.git
import whisper

modell = whisper.load_model("large")

# This function detect language that is spoken in audio file:
def detect_lang(vocal_path):
  model = whisper.load_model("base")

  # load audio and trim it to fit 30 seconds
  audio = whisper.load_audio(vocal_path)
  audio = whisper.pad_or_trim(audio)

  # make log-Mel spectrogram and move to the same device as the model
  mel = whisper.log_mel_spectrogram(audio).to(model.device)

  # detect the spoken language
  _, probs = model.detect_language(mel)
  lang=max(probs, key=probs.get)
  print(f"Detected language: {lang}")
  return lang

audio_path='/content/separated/htdemucs/Audio/vocals.mp3'

if os.path.exists(audio_path):
  print('**Start of the STT operation:\n')
  resultl = modell.transcribe(audio_path)

def phrase2txt(resultl):
  main_content=''
  length=len(resultl['segments'])
  for i in range (0,length):
    main_content=main_content+str(resultl['segments'][i]['text'])
  print(main_content)
  return main_content
main_content=phrase2txt(resultl)

!pip install parsivar
from parsivar import SpellCheck
!mkdir '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
!cp '/content/drive/MyDrive/colab_env/lib/python3.10/site-packages/parsivar/resource/spell/onegram.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
!cp '/content/drive/MyDrive/colab_env/lib/python3.10/site-packages/parsivar/resource/spell/mybigram_lm.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
checker=SpellCheck()

corrected_text=checker.spell_corrector(main_content)
print('This is the main content of Input video/Audio:\n',corrected_text)

!pip install jiwer

reference="محمد رضا شنیدن و گوش کردن به رادیو برلین را ترک می کند و نقشه را می کند و کنار می گذارد سفیر انگلیس میگوید می شود که او را به سلطنت انتخاب کرد مرداد 1332 هجری شمسی بود توانستن کودتای 28 مرداد را به وجود بیارن سرلشگر زاهدی بعد از آنی که حکومت مصدق را سرنگون کردن محمد رضا را که از ایران فرار کرده بود به ایران برگردانند محمد رضا پهلوی در سالهای دهه چهل و دهه پنجاه شدیدترین فشارها را بر این ملت"

#spleeter
import jiwer
hypothesis ="محمد رزا شنیدن و گوش کردن به رادیو برلین را ترک می کند و نقشه را می کند و کنار می گذارد سفیر انگلیس می گوید می شود که"
werror = jiwer.wer(reference, hypothesis)
cerror = jiwer.cer(reference, hypothesis)
werror,cerror

#demucs
hypothesis ="درود دوستان خب ما همیشه شنیده بودیم که بچه که میاد روزیش هم با خودش میاده ولی فکر کنم در واقع اصل این قضیه برای آلمانیا بوده چون اینجا توی آلمان هر بچهی که به دنیا میاد دولت به ازای هر بچه مایانه مبلغ 250 یورو به حساب پدر یا مادر واریز می کنه که معادل 14 ملیون تومن ما می شه فرقی نمی کنه چند تا بچه هر بچه 250 یورو تا سن 25 سالگی مایانه دریافت می کنه البته تا پرسال 220 یورو بوده که از امسال 2024 از سایش پیدا کرده و خانواده هایی که درامد کم تریم دارن 292 یورو مایانه دریافت می کنن و این که خب این پول رو خانواده ها می آن یه سریاشون تا یه سنی بر بچه هزینه می کنن بچه که میره مدرسه به عنوان پول تو جیبی بخشیش رو به بچه ها می دن دالبیش همینه که خب به همین خاطر خانواده ها اینجا توقع دارن که بچه هاشون قبل 25 سالگی زندگی مستقل خودشون رو داشته باشن زندگی خودشون رو تشکیل بدن درامد خودشون تا بتونن خودشون هزینه های خودشون رو پرداخت بکنن و بچه ها من وقتی براشون تریشون کنم که توی ایران مثلا خانواده های ما همه هزینه های ما رو کاملا خودشون پرداخت میکنن اینا براشون خیلی عجیبه این مسئله حالا نظر شما"#main_content
werror = jiwer.wer(reference, hypothesis)
cerror = jiwer.cer(reference, hypothesis)
werror,cerror

"""##Query"""

file_path = '/content/drive/MyDrive/Election Query.txt'

with open(file_path, 'r') as file:
	file_content = ''
	line = file.readline()

	while line:
		file_content += line
		line = file.readline()
file_content=file_content.lower()
file_content=file_content[7:]
without_=file_content.replace("_", " ").replace('"','').replace("(",'').replace(')','').replace("'","")
print(without_)

with open('/content/drive/MyDrive/1-keywordExtraction/modified_query3.txt','w') as file:
  file.write(without_)

import re
with open('/content/drive/MyDrive/1-keywordExtraction/modified_query3.txt', 'r') as file:
  query = ''
  line = file.readline()

  while line:
    query += line
    line = file.readline()

def query_in_string(string):
    # query ='"نماینده مجلس" or "کاندیدا" or "کاندید" or "کاندید مجلس" or "نامزد مجلس" or "اینبار فرق میکند" or "برای ایران" or "انتخابات کوری چشم دشمن" or " رای " or "رای نمیدهم" or "رای من سرنگونی" or "من رای میدهم" or "سیرک انتخابات" or "بایکوت انتخابات" or "دعوت مردم" or "نوبت انتخاب" or "انتخاب مردم" or "انتخابات" or "تائید صلاحیت" or "تائید صلاحیت" or "انتخاباتی" or "ردصلاحیت" or "رد صلاحیت" or "رای بی رای" or "رای بی رای" or "نه به انتخابات نمایشی" or "نه به انتخابات" or "نه به انتخابات نمایشی" or "نه به انتخابات فرمایشی" or "رای میدهم" or "رای میدهم" or "رای نمیدهم" or "رای نمیدهم" or "تبلیغات انتخاباتی" or "انتخابات فرمایشی" or "انتخابات نمایشی" or "رای مردم" or "انتخابات آزاد" or "انتخابات جعلی" or "انتخابات واقعی" or "رای مردم قدرت مردم" or "مردم سالاری" or "احراز صلاحیت" or "احراز صلاحیت" or "تحریم انتخابات" or "تحریم انتخابات قلابی" or "تحریم انتخابات فرمایشی" or "رای می دهم" or "رای می دهم" or "رای نمی دهم" or "رای نمی دهم" or "رای می دهیم" or "رای میدهیم" or "رای میدهیم" or "رای می دهیم" or "رای نمی دهیم" or "رای نمی دهیم" or "رای نمیدهیم" or "رای نمیدهیم" or "رای نمی دهیم" or "رای می دهیم" or "رای می دهم" or "رای نمی دهم" or "نباید رای داد" or "مهندسی انتخابات" or "نه به رای دادن" or "انتخابات خبرگان رهبری" or "انتخابات مجلس" or "انتخابات مجلس شورای اسلامی" or "انتخابات مجلس خبرگان" or "انتخابات مجلس خبرگان رهبری" or "صندوق رای" or "فریب انتخابات" or "فریب انتخاباتی" or "انتخابات آخوندی" or "مشارکت انتخاباتی" or "شمارش آرا" or "انتخابات " or ("نتایج" and "انتخابات") or ("نتیجه" and "انتخابات") or ("نتایج" and "انتخابات ") or ("نتیجه" and "انتخابات ") or ("مجلس" and "نامزد") or ("مجلس" and "کاندید") or ("رهبری" and "خبرگان")'
    # query ='نماینده مجلس or کاندیدا or کاندید or کاندید مجلس or نامزد مجلس or اینبار فرق میکند or برای ایران or انتخابات کوری چشم دشمن or  رای  or رای نمیدهم or رای من سرنگونی or من رای میدهم or سیرک انتخابات or بایکوت انتخابات or دعوت مردم or نوبت انتخاب or انتخاب مردم or انتخابات or تائید صلاحیت or تائید صلاحیت or انتخاباتی or ردصلاحیت or رد صلاحیت or رای بی رای or رای بی رای or نه به انتخابات نمایشی or نه به انتخابات or نه به انتخابات نمایشی or نه به انتخابات فرمایشی or رای میدهم or رای میدهم or رای نمیدهم or رای نمیدهم or تبلیغات انتخاباتی or انتخابات فرمایشی or انتخابات نمایشی or رای مردم or انتخابات آزاد or انتخابات جعلی or انتخابات واقعی or رای مردم قدرت مردم or مردم سالاری or احراز صلاحیت or احراز صلاحیت or تحریم انتخابات or تحریم انتخابات قلابی or تحریم انتخابات فرمایشی or رای می دهم or رای می دهم or رای نمی دهم or رای نمی دهم or رای می دهیم or رای میدهیم or رای میدهیم or رای می دهیم or رای نمی دهیم or رای نمی دهیم or رای نمیدهیم or رای نمیدهیم or رای نمی دهیم or رای می دهیم or رای می دهم or رای نمی دهم or نباید رای داد or مهندسی انتخابات or نه به رای دادن or انتخابات خبرگان رهبری or انتخابات مجلس or انتخابات مجلس شورای اسلامی or انتخابات مجلس خبرگان or انتخابات مجلس خبرگان رهبری or صندوق رای or فریب انتخابات or فریب انتخاباتی or انتخابات آخوندی or مشارکت انتخاباتی or شمارش آرا or انتخابات  or (نتایج and انتخابات) or (نتیجه and انتخابات) or (نتایج and انتخابات ) or (نتیجه and انتخابات ) or (مجلس and نامزد) or (مجلس and کاندید) or (رهبری and خبرگان)'
    for term in query.split('or'):
        lst = map(str.strip, term.split('and'))
        if all(re.search(r"\b%s\b" % re.escape(word), string) for word in lst):
           print(term)
           print("The Query was found in STT result. This video/audio is about elections")
           return True
    print("The Query was not found in STT result.")
    return False

# query='رای or رهبری and خبرگان'
query_in_string(corrected_text)

"""#Keyword Extraction:

##PERKE KEYWORD EXTRACTOR:
"""

pip install perke

!python -m perke download

import re

# This function modifies caption text and prepare it for key extraction:
def pure_caption(caption):
  #removing Imojis:
  emoji_pattern = re.compile("["
          u"\U0001F600-\U0001F64F"  # emoticons
          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
          u"\U0001F680-\U0001F6FF"  # transport & map symbols
          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags=re.UNICODE)
  without_emoji=emoji_pattern.sub(r'',caption)

  #Removing IDs:
  without_id = re.sub('@[^\s]+','',without_emoji)

  #Finding Hashtags in caption of post:
  tags=[]
  for tag in without_id.split():
    if tag.startswith("#"):
      tags.append(tag.strip("#").replace("_", " "))

  #Removing # sign and _:
  without_tag=without_id.replace('#','').replace("_", " ")

  return tags, without_tag

caption='برای یک صوت حدود 5دقیقه ای با حجم 4.3مگ، یک دقیقه طول می کشد. 22ثانیه ای با حجم 350کیلوبایت،11ثانیه یک دقیقه و 10 ثانیه، یک مگ، 20ثانیه 1:20ثانیه، 1.3مگ،26ثانیه 1:9ثانیه، 1مگ، 22ثانیه'

import numpy as np
def dummy_npwarn_decorator_factory():
  def npwarn_decorator(x):
    return x
  return npwarn_decorator
np._no_nep50_warning = getattr(np, '_no_nep50_warning', dummy_npwarn_decorator_factory)
from perke.unsupervised.graph_based import TopicRank

caption="دوستانی که میگن خودش رفت به اون جمله فرار کرد هم توجه داشته باشند "
tags, without_tag=pure_caption(caption)

# Merging modified caption text and STT result if existed:
if useful_content:
   goal_text=without_tag+corrected_text
else:
   goal_text=without_tag

# Goal Grammars:
valid_pos_tags = {'NOUN', 'NUM','NOUN,EZ','ADJ','NUM,EZ'}

# Create a TopicRank extractor:
extractor = TopicRank(valid_pos_tags=valid_pos_tags)

# Finding candidates:
extractor.load_text(input=goal_text, word_normalization_method=None)
extractor.select_candidates()
extractor.weight_candidates(threshold=0.5, metric='jaccard', linkage_method='average')

# Finding Keyword with Topic Rank Method:
keyphrases = extractor.get_n_best(n=20)
score=[20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]
keywords=[]
for i,(keyphrase,weight) in enumerate(keyphrases):
  keywords.append(keyphrase)

# Finding similarity between output keywords and hashtags in caption and Double score them:

# similarity=list(set(keywords).intersection(tags))
# for i in range(0,len(similarity)):
#   index=keywords.index(similarity[i])
#   score[index]=score[index]*2

dict_score = {score[i]:keywords[i] for i in range(len(keywords))}
sorted_dict = dict(sorted(dict_score.items()))
for i in range(0,10):
    print(f'{i+1}. \t{sorted_dict[20-i]}')

#POSITION RANK: 1-WORD OUTPUT
# extractor.select_candidates(grammar=grammers)
# extractor.weight_candidates(window_size=20)

#singlerank:
# extractor.select_candidates()
# extractor.weight_candidates(window=100)

# TextRank:
# extractor.weight_candidates(window_size=5, top_t_percent=0.9)
# NOIS50:window_size=10, top_t_percent=0.9
#news: window_size=5, top_t_percent=0.9

# # 4. Get the 10 highest weighted candidates as keyphrases.
# keyphrases = extractorm.get_n_best(n=10)
# for i, (weight, keyphrase) in enumerate(keyphrases):
#     print(f'{i+1}.\t{keyphrase}, \t{weight}')

"""##Keyword Extraction Evaluation:"""

listdata=[]
with open('/content/drive/MyDrive/keywordExtraction/KeywordExtractionDataset.txt','r') as file:
  line=file.readline()

  while line:
  # query += line
    listdata.append(line)
    line =  file.readline()

# Goal Grammars:
valid_pos_tags = {'NOUN', 'NUM','NOUN,EZ','ADJ','NUM,EZ'}
recall_sum=0
precision_sum=0

for i in range(200,350):
  print(i)
  text=eval(listdata[i])['body']
  keys=eval(listdata[i])['keywords']
  # Create a TopicRank extractor:
  extractor = TopicRank(valid_pos_tags=valid_pos_tags)
  # Finding candidates:
  extractor.load_text(input=text, word_normalization_method=None)
  extractor.select_candidates()
  extractor.weight_candidates(threshold=0.5, metric='jaccard', linkage_method='average')

  # Finding Keyword with Topic Rank Method:
  keyphrases = extractor.get_n_best(n=10)
  keywords=[]
  for i,(keyphrase,weight) in enumerate(keyphrases):
    keywords.append(keyphrase)
  TP=len(list(set(keys).intersection(keywords)))
  TP_FN=len(keys)
  recall=TP/TP_FN
  precision=TP/len(keywords)
  recall_sum=recall_sum+recall
  precision_sum=precision_sum+ precision

whole_recall=recall_sum/150
whole_precision=precision_sum/150
F1_score=2*whole_recall*whole_precision/(whole_recall+whole_precision)
