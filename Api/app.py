#@@@@ first install bellow packages: @@@@
# !pip install -r requirements.txt  | conda install --yes --file requirements.txt
# !pip install git+https://github.com/openai/whisper.git
# !python -m perke download
# !python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs

# @@@@ make following directory in local then download and copy onegram.pckl & mybigram_lm.pckl files in this directoy: @@@@
# @@@@ this stage must be done after importing libraries.@@@@
# !mkdir '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
# !cp 'onegram.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
# !cp 'mybigram_lm.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'

# Importing Libraries:
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

#@@@@ change below module name to version code name:@@@@
from AudioKeys import *


app = Flask(__name__)

# routes
@app.route("/", methods=['GET', 'POST'])
def main():
	return render_template("index.html")


@app.route("/submit", methods = ['GET', 'POST'])
def get_output():
	if request.method == 'POST':
		file = request.files['myfile']
		text = request.form['text']
		file_path = "static/" + file.filename	
		file.save(file_path)
		p = predict(file_path,text)
	return render_template("index.html", prediction = p, file_path = file_path)


if __name__ =='__main__':
	# app.debug = True
	app.run(debug = True)
