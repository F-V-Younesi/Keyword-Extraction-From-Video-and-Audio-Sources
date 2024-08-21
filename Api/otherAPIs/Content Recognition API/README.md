
# Project tree

 * [static](./static)
 * [templates](./templates)
   * [index.html](./templates/index.html)
 * [AudioKeys.py](./AudioKeys.py)
 * [requirements](./requirements)

As shown above, the directory with files and folders with same names must be created.

**First: install necessary packages:**
```
!pip install -r requirements.txt
# or in conda: conda install --yes --file requirements.txt
!python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs

#only in conda environment it is necessary to run:
!conda install conda-forge::ffmpeg
```

**Second: and then run app:**
```
import io,os, re
from pathlib import Path
from pydub import AudioSegment, silence
import librosa #, numpy as np
import numpy as np
from flask import Flask, render_template, request
# replace "AudioKeys" name in below line with api code version name, such as "AudioKeys_5M"
from ContentRecognition import *

app = Flask(__name__)

# routes
@app.route("/", methods=['GET', 'POST'])
def main():
	return render_template("index.html")


@app.route("/submit", methods = ['GET', 'POST'])
def get_output():
	if request.method == 'POST':
		file = request.files['myfile']
		#text = request.form['textarea']
		file_path = "static/" + file.filename	
		file.save(file_path)
		p = predict(file_path)
	return render_template("index.html", prediction = p, file_path = file_path)


if __name__ =='__main__':
	# app.debug = True
	app.run(debug = True)

```
