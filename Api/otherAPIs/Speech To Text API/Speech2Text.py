def phrase2txt(resultl):
  main_content=''
  length=len(resultl['segments'])
  for i in range (0,length):
    main_content=main_content+str(resultl['segments'][i]['text'])
  # print(main_content)
  return main_content

def predict(path):
    modell = whisper.load_model("large")
    # print('**Start of the STT operation:\n')
    resultl = modell.transcribe(path)
    main_content = phrase2txt(resultl)
    return main_content
