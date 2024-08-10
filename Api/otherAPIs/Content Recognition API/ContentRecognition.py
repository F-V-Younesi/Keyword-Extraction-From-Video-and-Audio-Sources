
#functions:
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
    #print('"\n **This Video/Audio basically contains Music and does not contain any useful contents."')
    useful_content="**This Video/Audio basically contains Music and does not contain any useful contents."
    return useful_content
  else:
    #print('"\n **This Video/Audio contains useful contents."')
    useful_content=" **This Video/Audio contains useful contents."
    return useful_content

def music_mode(overlay_music,overlay_music_path,vocal):
  vocal_loudness=vocal.dBFS
  loudness=overlay_music.dBFS
  if loudness<-40:
    #print('\n **This Video/Audio does not contain Music contents.')
    useful_content='**This Video/Audio does not contain Music contents.'
    return useful_content

  elif loudness<-30:
    #print('\n **This Video/Audio contain background music on main contents that can influence on accuracy of results.')
    useful_content='**This Video/Audio contain background music on main contents that can influence on accuracy of results.'
    return useful_content

  elif loudness>-18:
    if vocal_loudness<-30:
#        print("\n **This Video/Audio contains Only Music and does not contain any useful contents.")
        useful_content="**This Video/Audio contains Only Music and does not contain any useful contents."
        return useful_content
    else:
        #print("\n **This Video/Audio contains Music & singer's voice and does not contain any useful contents.")
        useful_content="**This Video/Audio contains Music & singer's voice and does not contain any useful contents."
        return useful_content

  else:
    y, sr = librosa.load(overlay_music_path)
    total_numbers=len(y)
    zeros=find_silense(y,total_numbers)
    content_finder(zeros,total_numbers)

def remove_music2(path):
  os.system('spleeter separate -o output/ '+path)

def predict(path):
      remove_music2(path)
      filename=path.replace('static/','')
      overlay_music=AudioSegment.from_wav('output/'+filename+'/accompaniment.wav')
      vocal=AudioSegment.from_wav('output/'+filename+'/vocals.wav')
      useful_content=music_mode(overlay_music,'output/'+filename+'/accompaniment.wav',vocal)
      return useful_content

#caption = ""
#predict('/home/younesi/data/audio.mp3',caption)
