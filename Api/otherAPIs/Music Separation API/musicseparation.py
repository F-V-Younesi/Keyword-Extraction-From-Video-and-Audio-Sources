def remove_music2(path):
  os.system('spleeter separate -o output/ '+path)
  return "Convertion Done!"
def predict(path):
      output=remove_music2(path)
      return output
