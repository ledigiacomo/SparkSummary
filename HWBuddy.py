#! python
from flask import Flask, render_template
from flask import request, redirect, url_for
from flask.ext.uploads import UploadSet, configure_uploads, AUDIO
from sumy.parsers.plaintext import PlaintextParser #We're choosing a plaintext parser here, other parsers available for HTML etc.
from sumy.nlp.tokenizers import Tokenizer 
from sumy.summarizers.lex_rank import LexRankSummarizer #We're choosing Lexrank, other algorithms are also built in
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import speech_recognition as sr
import time
import sys
import os
from os import listdir
from os.path import isfile, join
import urllib

app = Flask(__name__)

lecs = UploadSet('lecs', AUDIO)

app.config['UPLOADED_LECS_DEST'] = 'static/lectures'
configure_uploads(app, lecs)


@app.route('/')
def hello_world():
	return 'Hello, World'

@app.route('/mostRecent', methods=['GET'])
def mostRecent():
	mypath = "./static/lectures/"
	#print os.getcwd()

	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) ]
	#print onlyfiles
	themax = 0
	maxname = ""
	filenames = []
	for n,i in enumerate(onlyfiles):
		onlyfiles[n] = os.path.splitext(join(mypath, onlyfiles[n]))[0]
		filepath = onlyfiles[n].split("/")
		filename = filepath[len(filepath)-1]
		#print filename
		try:
			filenames.append(int(filename))
		except ValueError:
			x = 3

	fileName = mypath + "/" + str(max(filenames)) + ".txt"
	print fileName
	file = open(fileName, "r")

	return file.read()
	#return render_template('upload.html')
	#return "whatttt"

@app.route('/allFiles', methods=['GET'])
def allFiles():
	path = "./static/lectures/"
	filesList = [f for f in listdir(path) if isfile(join(path, f)) ]
	files = ""
	for n,i in enumerate(filesList):
		tmpfile = filesList[n] + ";"	
		files += tmpfile
	return files


@app.route('/upload', methods=['GET', 'POST'])
def upload():
	print(request.files)
	if request.method == 'POST' and 'lecs' in request.files:
		AUDIO_FILE = request.files['lecs']
		r = sr.Recognizer()
		strg = " "
		with sr.AudioFile(AUDIO_FILE) as source:
		    audio = r.record(source)

		IBM_USERNAME = "58bc5040-b54e-45da-97b1-691b6bd9b669" # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
		IBM_PASSWORD = "AToZiNGpBK8T" # IBM Speech to Text passwords are mixed-case alphanumeric strings
		try:
		    strg += r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD)
		except sr.UnknownValueError:
		    print("IBM Speech to Text could not understand audio")
		except sr.RequestError as e:
		    print("Could not request results from IBM Speech to Text service; {0}".format(e))

		print(strg)
		strg = strg.replace(" \n", ". ")
		sys.stdout.flush()
		timestr = time.strftime("%Y%m%d%H%M%S")
		tempFile = "user1_"+timestr+".txt"

		with open(tempFile, "w") as text_file:
			text_file.write("{0}".format(strg))

		text_file.close()

		parser = PlaintextParser.from_file(tempFile, Tokenizer("english"))
		summarizer = LexRankSummarizer()

		summary = summarizer(parser.document, 1) #Summarize the document with par2 sentences
		summs = " "
		tempFile2 = "./static/lectures/"+timestr+".txt"
		for sentence in summary:
			summs+=str(sentence)+"\n"

		with open(tempFile2, "w") as text_file2:
			text_file2.write("{0}".format(summs))

		text_file2.close()

		os.remove(tempFile)

		# return "returned"
	return render_template('upload.html')

if __name__ == '__main__':
	app.run(debug=True)