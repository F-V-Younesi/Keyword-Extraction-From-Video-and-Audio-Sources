from pathlib import Path
from flask import Flask, render_template, request
import os
from musicseparation import *


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