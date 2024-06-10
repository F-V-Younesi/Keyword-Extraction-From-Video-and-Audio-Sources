
# -*- coding: utf-8 -*-
"""Media2keyword.ipynb


###The first mode of input: Upload Your video/Audio file here:
"""

# from google.colab import files
# uploaded = files.upload()
# path = next(iter(uploaded))

"""### Or place a .csv file that contains a column for video|audio path and a column for caption text:"""

# csv_path='data.csv'
# csv=pd.read_csv(csv_path)
# path=csv['video_path'][0]
# caption=csv['caption'][0]

from google.colab import drive
drive.mount('/content/drive')

"""#Get Input | Format Recognition | Converting Video to Audio | Removing Music:

## Get Input | Format Recognition | Converting Video to Audio
"""

# Importing Libraries:
import moviepy.editor
import os
import pandas as pd

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
    print("This file has neither video nor audio format. Please enter a file with correct format.")

#Convertion of video to audio:
def vid2audio(path):
  #Load the Video
  video = moviepy.editor.VideoFileClip(path)

  #Extract the Audio
  audio = video.audio

  #Export the Audio
  audio.write_audiofile("Audio.mp3")

path='/content/414669282_856731373122399_1711351064169457727_n.mp4'
video=is_video(path)
if video is True:
  vid2audio(path)
  path="Audio.mp3"
elif video is False:
  os.rename(path,'Audio.mp3')

"""##Recognize & remove music:"""

!pip install pydub
from pydub import AudioSegment, silence
import io
from pathlib import Path
import select
from shutil import rmtree
import subprocess as sp
import sys
from typing import Dict, Tuple, Optional, IO

# This function checks that if a audio file exists for music separation or not. if exists, saves the file path:
def find_files(in_path):
    out = []
    for file in Path(in_path).iterdir():
        if file.suffix.lower().lstrip(".") in extensions:
            out.append(file)
    return out

# This function is used for printing subprocesses:
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

# This function seperate music from audio file. the outputs are vocal file and three music files:
def separate(inp=None, outp=None):
    inp = inp or in_path
    outp = outp or out_path
    cmd = ["python3", "-m", "demucs.separate", "-o", str(outp), "-n", model]
    if mp3:
        cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]

    files = [str(f) for f in find_files(inp)]
    if not files:
        print(f"No valid audio files in {in_path}")
        return
    print("**Going to separate Music and Vocals from the files:\n")
    p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
    copy_process_streams(p)
    p.wait()
    if p.returncode != 0:
        print("Command failed, something went wrong.")

# This function calls "seperate" function and saves vocal file and three music files:
def remove_music():
    out_path = Path('separated')
    in_path = Path('tmp_in')

    if in_path.exists():
        rmtree(in_path)
    in_path.mkdir()

    if out_path.exists():
        rmtree(out_path)
    out_path.mkdir()

    # name='Audio.mp3'
    !cp '/content/Audio.mp3' '/content/tmp_in'
    separate(in_path, out_path)

# This function finds length of music in audio file:
def music_length(overlay_music):
    silence1 = silence.detect_silence(overlay_music, min_silence_len=3000, silence_thresh=-40)
    silencelist = [((start/1000),(stop/1000)) for start,stop in silence1] #convert to sec
    c=0
    for i in range(0,len(silencelist)):
      c=c+silencelist[i][1]-silencelist[i][0]
    T=len(overlay_music)
    music_len=(T-c)/(T)
    return music_len

# This function finds audio content usability mode:
def music_mode(overlay_music,vocal):
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
    if music_length(overlay_music)<0.95:
      print('\n **This Video/Audio contain background music on main contents that can influence on accuracy of results.')
      useful_content=True
      return useful_content
    else:
      print("\n **This Video/Audio contains Music & singer's voice and does not contain any useful content for key extraction.")
      useful_content=False
      return useful_content

if os.path.exists('Audio.mp3'):
  print('**Start of the operation to check the presence of music in the audio file:\n')
  !python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs


  model = "htdemucs"
  extensions = ["mp3", "wav", "ogg", "flac"]  # those file types supported in this model.
  two_stems = None   # only separate one stems from the rest, for instance

  # Options for the output audio:
  mp3 = True
  mp3_rate = 320
  in_path = '/content/demucs'
  out_path = '/content/demucs_separated/'

  remove_music()
  !zip -r separated.zip separated

  music1=AudioSegment.from_mp3('/content/separated/htdemucs/Audio/bass.mp3')
  music2=AudioSegment.from_mp3('/content/separated/htdemucs/Audio/drums.mp3')
  music3=AudioSegment.from_mp3('/content/separated/htdemucs/Audio/other.mp3')
  vocal=AudioSegment.from_mp3('/content/separated/htdemucs/Audio/vocals.mp3')

  overlay_music = music1.overlay(music2, position=0).overlay(music3, position=0)
  useful_content=music_mode(overlay_music,vocal)

"""#STT(Speech To Text):

##Merged Whisper(Large and Medium models):
"""

# This function convert STT result as "List" of phrases to "String":
def list2str(main_content):
  main_content_str=''
  for i in range (0,len(main_content)):
    main_content_str=main_content_str+'،'+main_content[i]
  return main_content_str

# This function finds end of time periods of every segments:
def find_end_segments(segments,segmentsl):
  listend=[]
  listendl=[]
  for segment in segments:
    listend.append(segment['end'])

  for segment in segmentsl:
    listendl.append(segment['end'])
  return listend,listendl

# This function Finds common endings in time periods of segments.
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

#This function finds best prediction between common time periods for medium and large model:
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
      txt2=txt2+segmentsl[i]['text']
    if len(txt1)>len(txt2):
      listtxt.append(txt1)
    else:
      listtxt.append(txt2)
    previous_id=id
    previous_id2=id2

  return listtxt

# This function Integrates best prediction for all time sections:
def Integrated_stt(result,resultl):
  segments = result['segments']
  segmentsl=resultl['segments']
  listend,listendl = find_end_segments(segments,segmentsl)

  listcommon1,listcommon2 = common_endings(listend,listendl)

  main_content = best_prediction(segments,segmentsl,listcommon1,listcommon2)
  return main_content

!pip install git+https://github.com/openai/whisper.git
import whisper

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

vocal_path='/content/separated/htdemucs/Audio/vocals.mp3'
if os.path.exists(vocal_path):
  if useful_content:
    language=detect_lang(vocal_path)
    if language=='fa':
      print('**Start of the STT operation:\n')

      model = whisper.load_model("medium")
      result = model.transcribe(vocal_path)
      modell = whisper.load_model("large")
      resultl = modell.transcribe(vocal_path)
      main_content=Integrated_stt(result,resultl)

      !pip install parsivar
      from parsivar import SpellCheck
      !mkdir '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
      !cp '/content/drive/MyDrive/colab_env/lib/python3.10/site-packages/parsivar/resource/spell/onegram.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
      !cp '/content/drive/MyDrive/colab_env/lib/python3.10/site-packages/parsivar/resource/spell/mybigram_lm.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
      checker=SpellCheck()
      corrected_text=checker.spell_corrector(list2str(main_content))
      print('This is the main content of Input video/Audio:\n',corrected_text)

"""#Keyword Extraction:

##PERKE KEYWORD EXTRACTOR:
"""

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

caption='محل سخنرانی #محمدرضا_شاه_پهلوی در دارالزهد #حرم مطهر #امام #رضا علیه السلام دقیقا مقابل اون درب آخر فیلم خیلی گشتم تا پیداش کردم برام جالب بود این فیلم فقط ثبت محل وقوع یک رخداد تاریخی ایران است و قصد هیچ طرفداری سیاسی ندارم . هر کسی رفت حرم التماس دعا. . . . #ایران #تهران #مشهد #حرم #توریسم #شاه #محمد_رضا_پهلوی #پهلوی #معیشت #انقلاب #خبر #تتلو #حرم #مشهد_مقدس #خبرفوری'

!pip install perke
!python -m perke download
import numpy as np
def dummy_npwarn_decorator_factory():
  def npwarn_decorator(x):
    return x
  return npwarn_decorator
np._no_nep50_warning = getattr(np, '_no_nep50_warning', dummy_npwarn_decorator_factory)
from perke.unsupervised.graph_based import TopicRank

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
similarity=list(set(keywords).intersection(tags))
for i in range(0,len(similarity)):
  index=keywords.index(similarity[i])
  score[index]=score[index]*2

dict_score = {score[i]:keywords[i] for i in range(len(keywords))}
sorted_dict = dict(sorted(dict_score.items()))
for i in range(0,10):
    print(f'{i+1}. \t{sorted_dict[20-i]}')
