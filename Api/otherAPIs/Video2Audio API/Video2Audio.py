#functions:
#this function Investigate that the input file is video or Not:
def is_video(path):
  #audio_suffixes = ("mp3", "wav","3gp",'8svx','aa','aac','aax','act','aiff','alac','amr','ape','au','awb','cda','dss','dvf','flac','gsm','iklax','ivs','m4a','m4b','m4p','mmf','movpkg','mpc','msv','nmf','ogg','oga','mogg','opus','rm','ra','raw','rf64','sln','tta','voc','vox','webm','wma','wv')
  video_suffixes =('webm','mkv','mp4','m4p','m4v','flv','vob','ogv','drc','gif','gifv','mng','avi','MTS','M2TS','TS','mov','qt','wmv','yuv','rmvb','viv','asf','amv','rm','ogg','sv','3pg','3g2','mxf','roq','nsv','f4v','f4p','f4a','f4b')

  if path.endswith(video_suffixes):
    #print("**The input is a video file.")
    return True

  else:
    msg="**This file has not a video format. Please enter appropriate file."
    return msg

#Convertion of video to audio:
def vid2audio(path):
  #Load the Video
  video = moviepy.editor.VideoFileClip(path)

  #Extract the Audio
  audio = video.audio

  #Export the Audio
  audio.write_audiofile("Audio.mp3")

def predict(path):
    format=is_video(path)
    if format is True:
      vid2audio(path)
    else:
      return format
