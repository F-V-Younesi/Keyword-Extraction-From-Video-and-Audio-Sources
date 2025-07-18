
# Project tree

 * [templates](./templates)
   * [index.html](./templates/index.html)
 * [SpellCorrection.py](./SpellCorrection.py)
 * [requirements](./requirements)

As shown above, the directory with files and folders with same names must be created.

**First: install necessary packages:**
```
!pip install -r requirements.txt
# or in conda: conda install --yes --file requirements.txt

```

**Second: make following directory in local path of "parsivar package" then download and copy onegram.pckl & mybigram_lm.pckl models in this directoy. this stage must be done "after installing Packages":** <br>
download onegram.pckl from:<br>
https://drive.google.com/file/d/1-BWmc5-kH637ZpgI-DPonwpwKKk1Q8Rj/view?usp=sharing<br>
download mybigram_lm.pckl from:<br>
https://drive.google.com/file/d/1uCh2S2wqUbTke5TH7cv9V3xLILlLsGW0/view?usp=sharing<br>

```
#Making "spell" folder in "parsivar/resource" path:
!mkdir '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell' #change this with your parsivar installed path
!cp 'onegram.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
!cp 'mybigram_lm.pckl' '/usr/local/lib/python3.10/dist-packages/parsivar/resource/spell'
```
**Third: Run app.py :**
```
from pathlib import Path
from parsivar import SpellCheck
from flask import Flask, render_template, request
from SpellCorrection import *

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

```
