#@@@@ first install bellow packages: @@@@
# !pip install -r requirements.txt  | conda install --yes --file requirements.txt
# !python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs


# Importing Libraries:
import io,os
from pathlib import Path
from pydub import AudioSegment, silence
import librosa #, numpy as np
import numpy as np
from flask import Flask, render_template, request

#@@@@ change below module name to version code name:@@@@
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
