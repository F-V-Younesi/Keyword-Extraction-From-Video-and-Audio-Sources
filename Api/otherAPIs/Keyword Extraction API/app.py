from pathlib import Path
from flask import Flask, render_template, request
def dummy_npwarn_decorator_factory():
  def npwarn_decorator(x):
    return x
  return npwarn_decorator
np._no_nep50_warning = getattr(np, '_no_nep50_warning', dummy_npwarn_decorator_factory)
from perke.unsupervised.graph_based import TopicRank
from KeywordExtraction import *


app = Flask(__name__)

# routes
@app.route("/", methods=['GET', 'POST'])
def main():
	return render_template("index.html")


@app.route("/submit", methods = ['GET', 'POST'])
def get_output():
	if request.method == 'POST':
		text = request.form['textarea']
		p = predict(text)

	return render_template("index.html", prediction = p, file_path = file_path)


if __name__ =='__main__':
	# app.debug = True
	app.run(debug = True)
