def remove_music2(path):
  os.system('spleeter separate -o output/ '+path)

def predict(path):
      remove_music2(path)
      filename=path.replace('static/','')
      overlay_music=AudioSegment.from_wav('output/'+filename+'/accompaniment.wav')
      vocal=AudioSegment.from_wav('output/'+filename+'/vocals.wav')
      useful_content=music_mode(overlay_music,'output/'+filename+'/accompaniment.wav',vocal)
      return useful_content