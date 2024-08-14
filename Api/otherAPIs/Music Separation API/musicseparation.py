def remove_music2(path):
  os.system('spleeter separate -o output/ '+path)
  return "Convertion Done!"

def is_audio(path):
  audio_suffixes = ("mp3", "wav","3gp",'8svx','aa','aac','aax','act','aiff','alac','amr','ape','au','awb','cda','dss','dvf','flac','gsm','iklax','ivs','m4a','m4b','m4p','mmf','movpkg','mpc','msv','nmf','ogg','oga','mogg','opus','rm','ra','raw','rf64','sln','tta','voc','vox','webm','wma','wv')
  #video_suffixes =('webm','mkv','mp4','m4p','m4v','flv','vob','ogv','drc','gif','gifv','mng','avi','MTS','M2TS','TS','mov','qt','wmv','yuv','rmvb','viv','asf','amv','rm','ogg','sv','3pg','3g2','mxf','roq','nsv','f4v','f4p','f4a','f4b')

  if path.endswith(audio_suffixes):
    #print("**The input is a audio file.")
    return True

  else:
    msg="**This file has not a audio format. Please enter appropriate file."
    return msg
    
def predict(path):
      audio=is_audio(path)
      if audio==True:
        os.rename(path,'static/Audio.mp3')
        output=remove_music2('static/Audio.mp3')
        return output
      else:
        return audio
