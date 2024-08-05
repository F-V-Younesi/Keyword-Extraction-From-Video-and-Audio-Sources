#functions:
#this function Investigate that the input file is audio or video or None of them:
def is_video(path):
  audio_suffixes = ("mp3", "wav","3gp",'8svx','aa','aac','aax','act','aiff','alac','amr','ape','au','awb','cda','dss','dvf','flac','gsm','iklax','ivs','m4a','m4b','m4p','mmf','movpkg','mpc','msv','nmf','ogg','oga','mogg','opus','rm','ra','raw','rf64','sln','tta','voc','vox','webm','wma','wv')
  video_suffixes =('webm','mkv','mp4','m4p','m4v','flv','vob','ogv','drc','gif','gifv','mng','avi','MTS','M2TS','TS','mov','qt','wmv','yuv','rmvb','viv','asf','amv','rm','ogg','sv','3pg','3g2','mxf','roq','nsv','f4v','f4p','f4a','f4b')

  if path.endswith(video_suffixes):
    print("**The input is a video file.")
    return True
  elif path.endswith(audio_suffixes):
    print("**The input is an audio file.")
    return False
  else:
    print("**This file has neither video nor audio format. Please enter another file.")

#Convertion of video to audio:
def vid2audio(path):
  #Load the Video
  video = moviepy.editor.VideoFileClip(path)

  #Extract the Audio
  audio = video.audio

  #Export the Audio
  audio.write_audiofile("data/Audio.mp3")

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
    out_path = Path('data/separated')
    in_path = Path('data/tmp_in')

    if in_path.exists():
        shutil.rmtree(in_path)
    in_path.mkdir()

    if out_path.exists():
        shutil.rmtree(out_path)
    out_path.mkdir()

    # name='Audio.mp3'
    shutil.copy('data/Audio.mp3','data/tmp_in')
    separate(in_path, out_path)


def remove_music2():
  os.system('spleeter separate -o data/output/ data/Audio.mp3')
  
def phrase2txt(resultl):
  main_content=''
  length=len(resultl['segments'])
  for i in range (0,length):
    main_content=main_content+str(resultl['segments'][i]['text'])
  print(main_content)
  return main_content

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

def predict(path,caption):
    video=is_video(path)
    if video is True:
      vid2audio(path)
      path="data/Audio.mp3"
    elif video is False:
      os.rename(path,'data/Audio.mp3')
    if os.path.exists('data/Audio.mp3'):
      print('**Start of the operation to separate music from the audio file:\n')
    
      remove_music2()

      modell = whisper.load_model("large")
      audio_path='data/output/Audio/vocals.wav'
      if os.path.exists(audio_path):
        print('**Start of the STT operation:\n')
        resultl = modell.transcribe(audio_path)
        os.system('rm -rf data/output')
      main_content=phrase2txt(resultl)

      checker=SpellCheck()
      corrected_text=checker.spell_corrector(main_content)
      print('**This is the main content of Input video/Audio:\n',corrected_text)

      tags, without_tag = pure_caption(caption)
      goal_text = without_tag + corrected_text
      valid_pos_tags = {'NOUN', 'NUM','NOUN,EZ','ADJ','NUM,EZ'}
      extractor = TopicRank(valid_pos_tags=valid_pos_tags)
      extractor.load_text(input=goal_text, word_normalization_method=None)
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
      output_massage='!! Your input file is not Audio or Video. Please submit a video/audio file. !!'
      return output_massage
#caption = "دوستانی که میگن شاه خودش رفت به اون جمله فرار کرد هم توجه داشته باشند "
#predict('/home/younesi/data/audio.mp3',caption)
