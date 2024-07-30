**First: install necessary packages:**
```
!pip install -r requirements.txt
!pip install git+https://github.com/openai/whisper.git
!python -m perke download
!python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs
```

**Second: Importing Libraries:**
```
import moviepy.editor
import io,os
from pathlib import Path
import select
import subprocess as sp
import sys
from typing import Dict, Tuple, Optional, IO
from pydub import AudioSegment, silence
import librosa #, numpy as np
from parsivar import SpellCheck
import whisper
import numpy as np
import shutil
def dummy_npwarn_decorator_factory():
  def npwarn_decorator(x):
    return x
  return npwarn_decorator
np._no_nep50_warning = getattr(np, '_no_nep50_warning', dummy_npwarn_decorator_factory)
from perke.unsupervised.graph_based import TopicRank
from flask import Flask, render_template, request
from AudioKeys import *
```

**Third: make following directory in local path of "parsivar package" then download and copy onegram.pckl & mybigram_lm.pckl models in this directoy. this stage must be done "after importing libraries":**
```
#Making "spell" folder in "parsivar/resource" path:
!mkdir '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell' #change this with your parsivar installed path
!cp 'onegram.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
!cp 'mybigram_lm.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
```
and then run app:
```
app = Flask(__name__)

# routes
@app.route("/", methods=['GET', 'POST'])
def main():
	return render_template("index.html")


@app.route("/submit", methods = ['GET', 'POST'])
def get_output():
	if request.method == 'POST':
		file = request.files['myfile']
		file_path = "static/" + file.filename	
		file.save(file_path)
		p = predict(file_path)
	return render_template("index.html", prediction = p, file_path = file_path)


if __name__ =='__main__':
	# app.debug = True
	app.run(debug = True)
```

$ ./tree-md .
# Project tree

.
 * [tree-md](./tree-md)
 * [static](./static)
   * [file21.ext](./dir2/file21.ext)
 * [templates](./templates)
   * [index.html](./templates/index.html)
 * [AudioKeys.py](./AudioKeys.py)
 * [README.md](./README.md)
 * [requirements](./requirements)



├── dir1
│   ├── file11.ext
│   └── file12.ext
├── dir2
│   ├── file21.ext
│   ├── file22.ext
│   └── file23.ext
├── dir3
├── file_in_root.ext
└── README.md

2 directories, 5 files
