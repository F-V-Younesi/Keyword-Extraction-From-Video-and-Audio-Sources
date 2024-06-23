#functions:
#this function Investigate that the input file is audio or video or None of them:
def is_video(path):
  audio_suffixes = ("mp3", "wav","3gp",'8svx','aa','aac','aax','act','aiff','alac','amr','ape','au','awb','cda','dss','dvf','flac','gsm','iklax','ivs','m4a','m4b','m4p','mmf','movpkg','mpc','msv','nmf','ogg','oga','mogg','opus','rm','ra','raw','rf64','sln','tta','voc','vox','webm','wma','wv')
  video_suffixes =('webm','mkv','mp4','m4p','m4v','flv','vob','ogv','drc','gif','gifv','mng','avi','MTS','M2TS','TS','mov','qt','wmv','yuv','rmvb','viv','asf','amv','rm','ogg','sv','3pg','3g2','mxf','roq','nsv','f4v','f4p','f4a','f4b')

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
  audio.write_audiofile("static/Audio.mp3")

#music Separation functions:
def find_files(in_path):
    extensions = ["mp3", "wav", "ogg", "flac"]  # those file types supported in this model.
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
    cmd = ["python3", "-m", "demucs.separate", "-o", str(outp), "-n", "htdemucs"]
    # if mp3:
    cmd += ["--mp3", f"--mp3-bitrate={320}"]
    # if float32:
    #     cmd += ["--float32"]
    # if int24:
    #     cmd += ["--int24"]
    # if two_stems is not None:
    #     cmd += [f"--two-stems={two_stems}"]
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


def remove_music():
    out_path = Path('static/separated')
    in_path = Path('static/tmp_in')

    if in_path.exists():
        shutil.rmtree(in_path)
    in_path.mkdir()

    if out_path.exists():
        shutil.rmtree(out_path)
    out_path.mkdir()

    # name='Audio.mp3'
    shutil.copy('static/Audio.mp3','static/tmp_in')
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

def phrase2txt(resultl):
  main_content=''
  length=len(resultl['segments'])
  for i in range (0,length):
    main_content=main_content+str(resultl['segments'][i]['text'])
  print(main_content)
  return main_content

def predict(path):
    video=is_video(path)
    if video is True:
      vid2audio(path)
      path="static/Audio.mp3"
    elif video is False:
      os.rename(path,'static/Audio.mp3')
    if os.path.exists('static/Audio.mp3'):
      print('**Start of the operation to check the presence of music in the audio file:\n')
      # !python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs
      model = "htdemucs"
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
      # !zip -r separated.zip separated

      music1=AudioSegment.from_mp3('static/separated/htdemucs/Audio/bass.mp3')
      music2=AudioSegment.from_mp3('static/separated/htdemucs/Audio/drums.mp3')
      music3=AudioSegment.from_mp3('static/separated/htdemucs/Audio/other.mp3')
      vocal=AudioSegment.from_mp3('static/separated/htdemucs/Audio/vocals.mp3')
      overlay_music = music1.overlay(music2, position=0).overlay(music3, position=0)
      overlay_music.export('music.mp3',format='mp3')
      useful_content=music_mode(overlay_music,'music.mp3',vocal)

      modell = whisper.load_model("large")
      audio_path='static/separated/htdemucs/Audio/vocals.mp3'
      if os.path.exists(audio_path):
        print('**Start of the STT operation:\n')
        resultl = modell.transcribe(audio_path)
      main_content=phrase2txt(resultl)

      checker=SpellCheck()
      corrected_text=checker.spell_corrector(main_content)
      print('This is the main content of Input video/Audio:\n',corrected_text)

      valid_pos_tags = {'NOUN', 'NUM','NOUN,EZ','ADJ','NUM,EZ'}
      extractor = TopicRank(valid_pos_tags=valid_pos_tags)
      extractor.load_text(input=corrected_text, word_normalization_method=None)
      extractor.select_candidates()
      extractor.weight_candidates(threshold=0.5, metric='jaccard', linkage_method='average')
      keyphrases = extractor.get_n_best(n=20)
      score=[20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]
      keywords=[]
      for i,(keyphrase,weight) in enumerate(keyphrases):
        keywords.append(keyphrase)
      dict_score = {score[i]:keywords[i] for i in range(len(keywords))}
      sorted_dict = dict(sorted(dict_score.items()))
      for i in range(0,10):
          print(f'{i+1}. \t{sorted_dict[20-i]}')
      return sorted_dict
    else:
      output_massage='Your input file is not Audio or Video. Please submit a video/audio file.'
      return output_massage
