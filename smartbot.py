#########################
# GLOBAL VARIABLES USED #
#########################
import random
import threading
import pyttsx3
from tkinter import ttk, messagebox
from tkinter import colorchooser
import tensorflow
import pickle
import pyjokes
import webbrowser
from pythonping import ping
from geopy.geocoders import Nominatim
from tkinter import *
import os
from PIL import Image, ImageTk
from pynput.keyboard import Listener, HotKey
import multiprocessing
from pynput.keyboard import KeyCode
import time
import ctypes
import vlc
import subprocess
import pygame
import re

import webScraping
import mediaSearch
import dictionary
import music
import OSHandler
from global_function import *
import DateTime
import AITasks

direct_answer = []

inquiry = ''
inprogress_answer = ''
inprogress = False
voicemedium_thread_killed = False

with open('Resources/userData/standard volume level.txt') as file:
	standard_volume = int(file.read())

botChatTextBg = "#007cc7"
botChatText = "white"
userChatTextBg = "#4da8da"

chatBgColor = '#12232e'
background = '#203647'
textColor = 'white'
AITaskStatusLblBG = '#203647'
KCS_IMG = 1 #0 for light, 1 for dark
voice_id = 0 #0 for male, 1 for female
ass_voiceRate = 200 #normal voice rate
user_avatar = 7
displayed_userIcon = []
displayed_userText = []
displayed_botIcon = []
displayed_botText = []
displayed_img = set()  #images won't disappear when call show image function again

def Exit():
	OSHandler.Delete_Trash_Files()
	OSHandler.Update_Program_List()
	os._exit(0)

def Initialize():
	get_program_list_thread = threading.Thread(target=OSHandler.Get_Program_List, daemon=True)
	get_song_list_thread = threading.Thread(target=music.Get_Song_List, daemon=True)
	get_program_list_thread.start()
	get_song_list_thread.start()
	OSHandler.Delete_Trash_Files()
	if training_required:
		try:
			AITasks.Bot_Training()
		except:
			Exit()

	AITasks.Initialize()
	list_of_intents = direction['intents']
	for i in list_of_intents:
		direct_answer.append(i['tag'])
		if i['tag'] == 'ability':
			break

	get_program_list_thread.join()
	get_song_list_thread.join()

def Play_Music():
	command = inquiry

	if data_exist(direction['random music sign'], command, 6):
		song_name = 'music'
	else:
		song_name = command
		for word in ['playing', 'play', 'listen to']:
			if data_exist([word], song_name):
				song_name = song_name[song_name.find(word) + len(word) + 1:].strip()

	threading.Thread(target=speak, args=(f'Playing {song_name}...',), daemon=True).start()
	music.Play_Music(root, song_name)

def Stop_Music():
	music.Stop_Music()
	speak('Music stopped')

def Pause_Music():
	status = music.Pause_Music()

	if status:
		speak('Music paused')
	else:
		speak('There is currently no music playing')

def Next_Song():
	status = music.Next_Song()

	if status:
		speak('Playing next song...')
	else:
		speak('There is currently no music playing')

def Prev_Song():
	status = music.Prev_Song()

	if status:
		speak('Playing previous song...')
	else:
		speak('There is currently no music playing')

def lemmatize_word(query):
	list_of_word = AITasks.clean_up_sentence(query)
	return ' '.join(list_of_word)

def Get_Definition():
	word = ''
	with open('Resources/redundancy/definition redundancy.pck', 'rb') as file:
		definition_redundancy = pickle.load(file)
		definition_redundancy.sort(key=lambda x: len(x[0]), reverse=True)
		definition_redundancy.sort(key=lambda x: len(x[0].split()), reverse=True)
		definition_redundancy.sort(key=lambda x : x[2], reverse=True)
	for redundancy in definition_redundancy:
		if data_exist([redundancy[0]], inquiry, 2):
			question_word = redundancy[0].split()
			command_word = inquiry.split()
			for x in redundancy[1]:
				if x == -1:
					pos = command_word.index(question_word[0])
					word = ' '.join(command_word[:pos])
				elif x == len(question_word) - 1:
					pos = command_word.index(question_word[x])
					word = ' '.join(command_word[pos + 1:])
				else:
					pos = command_word.index(question_word[x])
					pos1 = rindex(command_word, question_word[x + 1])
					word = ' '.join(command_word[pos + 1: pos1])
				if word:
					break
			if word:
				break

	if word == '':
		word = Further_Question('What word do you want to get definition for?')
		if word == None:
			return

	word = word.replace("'s", '')
	word = word.replace("'", '')
	word = word.replace('?', '')
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	speak('Looking up in dictionary...')
	status = dictionary.Definition(word)
	if status is not None:
		if word_count(status) <= 10:
			speak(word + ' means ' + status)
		else:
			speak("Here's the result...")
			attachTOframe(word + ' means ' + status, True)
	else:
		speak('This word is not in dictionary')

def Tell_Joke():
	speak("here's a joke")
	speak(pyjokes.get_joke())

def Tell_Time():
	if data_exist(['in'], inquiry):
		if chatMode == 1:
			if not Internet():
				speak('i\'m having trouble connecting to the Internet')
				return
		command_word = inquiry.split()
		pos = command_word.index('in')
		location = ' '.join(command_word[pos + 1:])
		location = location.replace('currently', '')
		location = location.replace('right now', '')
		location = location.replace('now', '')
		location = refine_sentence(location)
		if data_exist(['current location', 'current place', 'here'], location):
			location = 'here'
	else:
		location = 'here'

	time = DateTime.Tell_Time(location)
	if time is None:
		speak("Sorry, I don't know where that is")

	speak(f"It's {time}" + (f" in {Capitalize_Sentence(location)}" if location != 'here' else ""))

def Tell_Day():
	command = inquiry
	date_declare = []
	list_of_intents = direction['intents']
	for i in list_of_intents:
		if i['tag'] == 'day and date':
			date_declare = i['response']
			break

	tell_day = 'date' not in command
	res = DateTime.Tell_Day(tell_day)

	speak(random.choice(date_declare) + ' ' + res[0] + res[1])

def Get_Random_Number():
	command_word = inquiry.split()
	start = -1000000000
	stop = 1000000000
	if data_exist(['non positive'], inquiry):
		stop = 0
	elif 'positive' in command_word:
		start = 1
	elif data_exist(['non negative'], inquiry):
		start = 0
	elif 'negative' in command_word:
		stop = -1
	if 'from' in command_word:
		pos = command_word.index('from')
		if pos + 1 != len(command_word):
			try:
				start = max(start, int(command_word[pos + 1]))
			except:
				pass
	if 'to' in command_word:
		pos = command_word.index('to')
		if pos + 1 != len(command_word):
			try:
				stop = min(stop, int(command_word[pos + 1]))
			except:
				pass


	if start > stop:
		start, stop = stop, start

	answers = ['The number I chose is', 'I choose the number', 'My choice is', 'I choose']
	speak(random.choice(answers) + ' ' + str(random.randint(start, stop)))

def Tell_Weather():
	location = ''
	global inquiry
	command_word = inquiry.split()
	if command_word[-1] == 'weather':
		if len(command_word) > 1:
			if not data_exist(['me', 'the', 'show', 'give', 'get', 'tell'], command_word[-2]):
				location = ' '.join(command_word[:-1])

	if location == '':
		if 'in' in command_word:
			pos = command_word.index('in')
			location = ' '.join(command_word[pos + 1:])
			if data_exist(['current', 'here'], location):
				location = ''

	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	if location == '':
		url = 'http://ipinfo.io/json'
		res = requests.get(url).json()
		location = res['city']

	location = location.replace("'s", '')
	data = webScraping.Weather(location)
	if data[0] is None:
		inquiry = 'weather ' + location
		Search_On_Web()
		return
	speak('', False)
	today = DateTime.Tell_Day(True)[0]
	location = Capitalize_Sentence(location)
	showSingleImage('weather', [data[0], data[1], today, location])
	speak('Currently in ' + location + ", it's " + data[0] + ' degree, and seems to be ' + data[1], False, False)

def Capitalize_Sentence(sentence):
	sentence = sentence.capitalize()
	for i in range(1, len(sentence)):
		if sentence[i - 1] == ' ':
			sentence = sentence[:i] + sentence[i:].capitalize()
	return sentence

def Open_Websites():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return

	query = inquiry
	with open('Resources/command/rename website.pck', 'rb') as file:
		rename_website = pickle.load(file)
		for website in rename_website:
			if website in query:
				query = query.replace(website, rename_website[website])

	with open('Resources/command/open website.pck', 'rb') as file:
		web_pages = pickle.load(file)
	web_pages.sort(key=lambda x: len(x['name']), reverse=True)
	for site in web_pages:
		if site['name'] in query:
			threading.Thread(target=speak, args=(f"opening {Capitalize_Sentence(site['name'])}...",), daemon=True).start()
			webbrowser.get().open(site['url'])
			return

	Open_Programs()

def Media_Search():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	media_name = []
	with open('Resources/command/media search.pck', 'rb') as file:
		media_search_items = pickle.load(file)
	for x in media_search_items:
		media_name.append(x['tag'])
	type = ''
	global inquiry
	command_words = inquiry.split()
	if 'search' in command_words:
		pos = command_words.index('search')
		if pos != 0:
			if command_words[pos - 1] in media_name:
				type = command_words[pos - 1]

	if type == '':
		for x in media_name:
			if data_exist(['search on ' + x], inquiry, 2):
				type = x
				break

	if type == '':
		for x in media_name:
			if data_exist(['search ' + x], inquiry):
				type = x
				break

	if type == '':
		if command_words[-1] in media_name:
			type = command_words[-1]

	if type != '':
		url = mediaSearch.Get_Url(type, inquiry, media_search_items)
		threading.Thread(target=speak, args=('This is what I found on ' + Capitalize_Sentence(type),), daemon=True).start()
		webbrowser.get().open(url)
	else:
		Search_On_Web()

def Youtube():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	threading.Thread(target=speak, args=("here's the video...",), daemon=True).start()
	webScraping.youtube(inquiry)

class Further_Record_Thread(threading.Thread):
	def __init__(self, question):
		threading.Thread.__init__(self)
		self.daemon = True
		self.question = question

	def run(self):
		global inprogress_answer
		asked = False
		while True:
			if not asked:
				said = record(self.question, True)
			else:
				said = record('', True)
			asked = True
			if said is not None and chatMode == 0:
				inprogress_answer = refine_sentence(said)
				break

	def get_id(self):
		if hasattr(self, '_thread_id'):
			return self._thread_id
		for id, thread in threading._active.items():
			if thread is self:
				return id

	def raise_exception(self):
		thread_id = self.get_id()
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
		if res > 1:
			ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)


def Further_Question(question):
	global inprogress_answer
	inprogress_answer = None
	record_thread = Further_Record_Thread(question)
	record_thread.start()
	while inprogress_answer is None:
		time.sleep(0.05)
	record_thread.raise_exception()

	return inprogress_answer

def Translate():
	sentence = ''
	language = ''
	with open('Resources/redundancy/translation redundancy.pck', 'rb') as file:
		translation_redundancy = pickle.load(file)
		translation_redundancy.sort(key=lambda x: len(x[0]), reverse=True)
		translation_redundancy.sort(key=lambda x: len(x[0].split()), reverse=True)
	for redundancy in translation_redundancy:
		if data_exist([redundancy[0]], inquiry, 2):
			question_word = redundancy[0].split()
			command_word = inquiry.split()
			for x in redundancy[1]:
				if x == len(question_word) - 1:
					pos = command_word.index(question_word[x])
					sentence = ' '.join(command_word[pos + 1:])
				else:
					pos = command_word.index(question_word[x])
					pos1 = rindex(command_word, question_word[x + 1])
					sentence = ' '.join(command_word[pos + 1: pos1])
					language = ' '.join(command_word[pos1 + 1:])
				if sentence or language:
					break
			if sentence or language:
				break

	if sentence == '':
		sentence = Further_Question('What do you want to translate?')
		if sentence == None:
			return
	if language == '':
		language = Further_Question('Which language to translate?')
		if language == None:
			return

	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	result = dictionary.lang_translate(sentence, language)
	if result is None:
		speak("This language doesn't exists.")
	else:
		if word_count(sentence) <= 10:
			speak(f'In {Capitalize_Sentence(language)}, "{sentence.capitalize()}" is:')
			attachTOframe(result.text, True)
			if result.pronunciation is not None:
				speak(str(result.pronunciation), False, False)
		else:
			speak(f'In {Capitalize_Sentence(language)}, it is:')
			attachTOframe(result.text, True)

def Get_Direction():
	From = ''
	To = ''
	with open('Resources/redundancy/direction redundancy.pck', 'rb') as file:
		direction_redundancy = pickle.load(file)
		direction_redundancy.sort(key=lambda x: len(x[0]), reverse=True)
		direction_redundancy.sort(key=lambda x: len(x[0].split()), reverse=True)
	for redundancy in direction_redundancy:
		if data_exist([redundancy[0]], inquiry, 2):
			question_word = redundancy[0].split()
			command_word = inquiry.split()
			for x in redundancy[1]:
				if x == len(question_word) - 1:
					pos = command_word.index(question_word[x])
					From = ' '.join(command_word[pos + 1:])
				else:
					pos = command_word.index(question_word[x])
					pos1 = rindex(command_word, question_word[x + 1])
					From = ' '.join(command_word[pos + 1: pos1])
					To = ' '.join(command_word[pos1 + 1:])
				if From or To:
					break
			if From or To:
				break

	if From == '':
		From = Further_Question('What is your starting location?')
		if From == None:
			return
	if To == '':
		To = Further_Question('Where do you want to go?')
		if To == None:
			return

	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	try:
		speak('Getting directions...')
		distance = webScraping.giveDirections(From, To)
		speak('You have to cover a distance of ' + distance)
	except:
		speak('I think location is not proper, Try Again!')

def Check_Email():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	if data_exist(['protonmail'], inquiry):
		url = 'https://mail.protonmail.com/u/0/inbox'
		threading.Thread(target=speak, args=('you can check your Protonmail here',), daemon=True).start()
		webbrowser.get().open(url)
	else:
		url = 'https://mail.google.com/mail/u/0/#inbox'
		threading.Thread(target=speak, args=('you can check your email here',), daemon=True).start()
		webbrowser.get().open(url)

def Battery():
	speak(OSHandler.batteryInfo())

def System_Info():
	if data_exist(['cpu', 'processor', 'frequency', 'speed'], inquiry, 5):
		type = 2
	elif data_exist(['ram', 'memory'], inquiry):
		type = 1
	else:
		type = 0

	res = '\n'.join(OSHandler.systemInfo(type))
	speak(f'Here is your {"CPU" if type == 2 else "Memory" if type == 1 else "System"} Information...')
	attachTOframe(res, True)

def System_Usage():
	if data_exist(['cpu'], inquiry):
		speak('your CPU usage is: ' + OSHandler.systemUsage(0) + '%')
	elif data_exist(['ram', 'memory'], inquiry):
		if data_exist(['you', 'this program', 'this procedure', 'this app'], inquiry, 3):
			res = OSHandler.systemUsage(1, True)
			speak(f'I take up {res[0]} MB ({res[1]}%) of RAM')
		else:
			res = OSHandler.systemUsage(1)
			speak('your Memory usage is: ' + str(res[0]) + ' GB (' + str(res[1]) + '%)')
	else:
		speak('Here is your System usage...')
		attachTOframe('\n'.join(OSHandler.systemUsage(2)), True)

img = []
def Show_Image():
	if os.path.exists('Resources/web scraping/imgDownloads'):
		folder = 'Resources/web scraping/imgDownloads'
		for file in os.listdir(folder):
			file_path = os.path.join(folder, file)
			try:
				os.remove(file_path)
			except:
				pass

	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return

	download_thread = threading.Thread(target=webScraping.downloadImage, args=(inquiry,), daemon=True)
	download_thread.start()
	speak('Getting photos...')
	download_thread.join()

	if not os.path.exists('Resources/web scraping/imgDownloads/0.jpg'):
		speak('Sorry, there is no data available')
	else:
		def get_bit(x, pos):
			return (x >> pos) & 1

		global img, displayed_img
		img = []
		speak('Here are the images...')
		w, h = 150, 110
		global img0, img1, img2, img3

		# Showing Images
		imageContainer = Frame(chat_frame, bg='#EAEAEA')
		imageContainer.pack(anchor='w')
		for i in range(4):
			if os.path.exists(f'Resources/web scraping/imgDownloads/{i}.jpg'):
				img.append(ImageTk.PhotoImage(Image.open(f'Resources/web scraping/imgDownloads/{i}.jpg').resize((w, h), Image.ANTIALIAS)))
			else:
				break

		for i in range(len(img)):
			displayed_img.add(img[i])
			Label(imageContainer, image=img[i], bg='#EAEAEA').grid(row=get_bit(i, 1), column=get_bit(i, 0))

		update_chat_frame()

def Wolframalpha():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return

	answer = webScraping.Wolframalpha(inquiry)

	if answer is None:
		Search_On_Web()
		return

	if len(answer) <= 10:
		speak('The answer is ' + answer)
	else:
		speak('Here\'s the result')
		attachTOframe(answer, True)

def Math_Calculation():
	global inquiry
	inquiry = inquiry.replace('on wolframalpha', '')
	inquiry = inquiry.replace('wolframalpha', '')
	Web_Based_Redundancy_Filter()

	cpp = ctypes.CDLL(os.path.join(os.getcwd(), 'Resources/cpp algorithm/calculator.dll'))
	cpp.Calculate.restype = ctypes.c_wchar_p

	command = inquiry
	command = ctypes.c_char_p(command.encode('utf-8'))

	result = str(cpp.Calculate(command))
	if result:
		speak('The answer is ' + result)
	else:
		Wolframalpha()

def word_count(sentence):
	words = sentence.split()
	return len(words)

def Web_Based_Redundancy_Filter():
	global inquiry
	command = ''
	with open('Resources/redundancy/web search redundancy filter.pck', 'rb') as file:
		web_based_redundancy = pickle.load(file)
		web_based_redundancy.sort(key=lambda x: len(x[0].split()), reverse=True)
		web_based_redundancy.sort(key=lambda x: x[2], reverse=True)
	for redundancy in web_based_redundancy:
		if data_exist([redundancy[0]], inquiry, 2):
			question_word = redundancy[0].split()
			command_word = inquiry.split()
			for x in redundancy[1]:
				if x == len(question_word) - 1:
					pos = command_word.index(question_word[x])
					command = ' '.join(command_word[pos + 1:])
				else:
					pos = command_word.index(question_word[x])
					pos1 = rindex(command_word, question_word[x + 1])
					command = ' '.join(command_word[pos + 1: pos1])
				if command:
					break
			if command:
				if data_exist(['info', 'information'], redundancy[0]):
					if len(command) > 1 and command[-2:] == "'s":
						command = command[:-2]
					elif command[-1] == "'":
						command = command[:-1]

				if command:
					break

	#status = True if found matching form of inquiry in "web search redundancy filter.pck" file
	status = False
	if command:
		inquiry = command
		status = True

	# eliminate "?"
	pos = len(inquiry)
	while pos > 1 and inquiry[pos - 1] == '?':
		pos -= 1
	inquiry = inquiry[:pos]
	return status

def Task_Confirm(sentence):
	return AITasks.task_confirmation.Is_Approve(sentence)

def Wikipedia():
	Web_Based_Redundancy_Filter()

	img_thread = threading.Thread(target=webScraping.downloadImage, args=(inquiry, 1,), daemon=True)
	img_thread.start()
	wiki_result = webScraping.Wikipedia(Capitalize_Sentence(inquiry))
	img_thread.join()

	if wiki_result is not None:
		if word_count(wiki_result) <= 10:
			speak('', False)
			showSingleImage('wiki')
			speak(wiki_result, True, False)
		else:
			speak("Here's the result...")
			showSingleImage('wiki')
			attachTOframe(wiki_result, True)
		return

	Search_On_Web()

def Search_On_Web(filter_redundancy = True, search_engine = 'google'):
	if filter_redundancy:
		Web_Based_Redundancy_Filter()

	command = inquiry

	command = command.replace('%', '%25')
	command = command.replace('+', '%2B')
	command = command.replace(' ', '+')
	command = command.replace("'", '%27')

	if search_engine == 'google':
		url = 'https://www.google.com/search?q=' + command
	elif search_engine == 'duckduckgo':
		url = 'https://duckduckgo.com/?q=' + command
	else:
		url = 'https://search.brave.com/search?q=' + command

	threading.Thread(target=speak, args=('this is what I found on the Internet',), daemon=True).start()
	webbrowser.get().open(url)

def Web_Based_Search():
	if data_exist(['on brave'], inquiry, 6):
		search_engine = 'brave'
	elif data_exist(['on duckduckgo'], inquiry, 6):
		search_engine = 'duckduckgo'
	else:
		search_engine = 'google'

	search_on_web = data_exist(['on web', 'on internet', 'on google', 'on brave', 'on duckduckgo'], inquiry, 6)
	redundancy_filter_status = Web_Based_Redundancy_Filter()
	if chatMode == 0:
		if not redundancy_filter_status:
			confirm = Further_Question('Do you want me to search on web?')

			if not Task_Confirm(confirm):
				answers = ['ok', 'okay', 'got it']
				speak(random.choice(answers))
				return

	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return

	if search_on_web:
		Search_On_Web(False, search_engine)
	else:
		Wikipedia()

def Get_Ip_Address():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	url = 'http://ipinfo.io/json'
	info = requests.get(url).json()
	speak('Your ip address is: ' + info['ip'])

def Find_Location():
	if data_exist(['for'], inquiry):
		command = inquiry[inquiry.find('for') + 4:]
	elif data_exist(['where is'], inquiry, 2):
		command_word = inquiry.split()
		pos = command_word.index('where')
		pos1 = command_word.index('is')
		if pos + 1 != pos1:
			command = ' '.join(command_word[pos + 1 : pos1])
		else:
			command = inquiry[inquiry.find('is') + 3:]
	elif data_exist(['of'], inquiry):
		command = inquiry[inquiry.find('of') + 3:]
	else:
		command = ''

	if command == '':
		questions = ['what is your destination?', 'what place are you looking for?', 'which place do you wanna go?']
		command = Further_Question(random.choice(questions))
		if command == None:
			return

	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	threading.Thread(target=speak, args=('I have found the location on google map',), daemon=True).start()
	url = 'https://www.google.com/maps/search/' + command
	webbrowser.get().open(url)

def Get_ISP():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	url = 'http://ipinfo.io/json'
	info = requests.get(url).json()
	speak('Your ISP is: ' + info['org'][info['org'].find(' ') + 1:])

def Get_Synonyms():
	word = ''
	with open('Resources/redundancy/synonym redundancy.pck', 'rb') as file:
		synonym_redundancy = pickle.load(file)
		synonym_redundancy.sort(key=lambda x: len(x[0]), reverse=True)
		synonym_redundancy.sort(key=lambda x: len(x[0].split()), reverse=True)
		synonym_redundancy.sort(key=lambda x : x[2], reverse=True)
	for redundancy in synonym_redundancy:
		if data_exist([redundancy[0]], inquiry, 2):
			question_word = redundancy[0].split()
			command_word = inquiry.split()
			for x in redundancy[1]:
				if x == -1:
					pos = command_word.index(question_word[0])
					word = ' '.join(command_word[:pos])
				elif x == len(question_word) - 1:
					pos = command_word.index(question_word[x])
					word = ' '.join(command_word[pos + 1:])
				else:
					pos = command_word.index(question_word[x])
					pos1 = rindex(command_word, question_word[x + 1])
					word = ' '.join(command_word[pos + 1: pos1])
				if word:
					break
			if word:
				break

	if word == '':
		word = Further_Question('What word do you wanna get synonyms?')
		if word == None:
			return

	word = word.replace("'s", '')
	word = word.replace("'", '')
	word = word.replace('?', '')
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	speak('Looking up in dictionary...')
	res = dictionary.Synonyms(word)
	if res != None:
		answer = ', '.join(res)
		answer = 'Synonyms of ' + word + ' includes: ' + answer
		speak(answer)
	else:
		speak('This word does not have any synonym')

def Get_Current_Location():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	url = 'http://ipinfo.io/json'
	location = requests.get(url).json()
	speak('Based on your ip address, you are currently in ' + location['city'] + ', ' + location['country'])

def Get_Antonyms():
	word = ''
	with open('Resources/redundancy/antonym redundancy.pck', 'rb') as file:
		antonym_redundancy = pickle.load(file)
		antonym_redundancy.sort(key=lambda x: len(x[0]), reverse=True)
		antonym_redundancy.sort(key=lambda x: len(x[0].split()), reverse=True)
		antonym_redundancy.sort(key=lambda x : x[2], reverse=True)
	for redundancy in antonym_redundancy:
		if data_exist([redundancy[0]], inquiry, 2):
			question_word = redundancy[0].split()
			command_word = inquiry.split()
			for x in redundancy[1]:
				if x == -1:
					pos = command_word.index(question_word[0])
					word = ' '.join(command_word[:pos])
				elif x == len(question_word) - 1:
					pos = command_word.index(question_word[x])
					word = ' '.join(command_word[pos + 1:])
				else:
					pos = command_word.index(question_word[x])
					pos1 = rindex(command_word, question_word[x + 1])
					word = ' '.join(command_word[pos + 1: pos1])
				if word:
					break
			if word:
				break

	if word == '':
		word = Further_Question('What word do you wanna get antonyms?')
		if word == None:
			return

	word = word.replace("'s", '')
	word = word.replace("'", '')
	word = word.replace('?', '')
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return
	speak('Looking up in dictionary...')
	res = dictionary.Antonyms(word)
	if res != None:
		answer = ', '.join(res)
		answer = 'Antonyms of ' + word + ' includes: ' + answer
		speak(answer)
	else:
		speak('this word does not have any antonym')

def Codeforces():
	if chatMode == 1:
		if not Internet():
			speak('i\'m having trouble connecting to the Internet')
			return

	if data_exist(['rating', 'ranking'], inquiry, 5):
		speak('Checking...')
		res = webScraping.codeforces_info.Get_User_Ranking()
		vowels = ['A', 'E', 'I', 'O', 'U']
		article = 'a'
		if res['level'] in vowels:
			article = 'an'

		speak(f'You are currently {article} {res["level"]}, with {res["rating"]} rating.')
	elif data_exist(['online', 'active'], inquiry, 5):
		username = ''

		with open('Resources/redundancy/codeforces active status redundancy.pck', 'rb') as file:
			active_status_redundancy = pickle.load(file)
			active_status_redundancy.sort(key=lambda x : len(x[0]), reverse=True)

		for redundancy in active_status_redundancy:
			if data_exist([redundancy[0]], inquiry, 2):
				question_word = redundancy[0].split()
				command_word = inquiry.split()
				for x in redundancy[1]:
					if x == len(question_word) - 1:
						pos = command_word.index(question_word[x])
						username = ' '.join(command_word[pos + 1:])
					else:
						pos = command_word.index(question_word[x])
						pos1 = rindex(command_word, question_word[x + 1])
						username = ' '.join(command_word[pos + 1: pos1])
					if username:
						break
				if username:
					break

		if username == '' or data_exist(['anyone', 'anybody', 'everyone', 'everybody', 'someone', 'somebody'], username):
			username = Further_Question('Which user exactly?')
			if username is None:
				return

		if len(username) > 8 and username[:9] == 'my friend':
			friend_name = username[10:]
			with open('Resources/command/codeforces friend username.pck', 'rb') as file:
				codeforces_friend_username = pickle.load(file)
			if friend_name in codeforces_friend_username:
				username = codeforces_friend_username[friend_name]

		speak('Checking...')
		res = webScraping.codeforces_info.Check_Active_User(username)

		if res is None:
			speak('Sorry, there is no such user')
		else:
			if res:
				answers = ['yes', 'yup', 'yep', 'yeah', 'certainly', 'sure', 'absolutely', 'definitely']
			else:
				answers = ['no', 'nope', 'not likely', "i don't think so"]
			speak(random.choice(answers))
	else:
		speak('Checking...')
		res = webScraping.codeforces_info.Available_Contests()
		if res[0] == 2:
			if res[1] > 1:
				answer = 'There are'
			else:
				answer = 'There is'
			answer += f' currently {res[1]} running contest'
			if res[1] > 1:
				answer += 's'
			answer += '.'
		elif res[0] == 1:
			if res[1] > 1:
				answer = 'There are'
			else:
				answer = 'There is'
			answer += f' {res[1]} upcoming contest'
			if res[1] > 1:
				answer += 's'
			answer += '.'
		else:
			num = res[1]
			if num == 0:
				answer = 'There is no available contest right now.'
			elif num == 1:
				answer = 'There is 1 contest you might wanna register.'
			else:
				answer = f'There are {num} contests you might wanna register.'

		threading.Thread(target=speak, args=(answer,), daemon=True).start()
		if res[1] != 0:
			webbrowser.get().open('https://codeforces.com/contests/')

def Ping():
	res = str(ping('google.com', verbose=False))
	res = ''.join(res.split('\r'))
	speak('Here\'s the result')
	attachTOframe(res, True)

def Open_Programs():
	def execute_program(program_path):
		if not OSHandler.Program_Already_Opened(program_path):
			try:
				subprocess.run(program_path)
			except Exception as e:
				messagebox.showerror('Error', e)

	program_name = inquiry
	with open('Resources/redundancy/open program.pck', 'rb') as file:
		open_program_redundancy = pickle.load(file)
		open_program_redundancy.sort(key=lambda x : len(x[0]), reverse=True)
	with open('Resources/command/system files.pck', 'rb') as file:
		system_files = pickle.load(file)

	command_word = program_name.split()
	for redundancy in open_program_redundancy:
		if data_exist([redundancy[0]], program_name, 2):
			redundancy_word = redundancy[0].split()
			pos = command_word.index(redundancy_word[0])
			if len(redundancy_word) == 1:
				if redundancy[1] == -1:
					name = ' '.join(command_word[:pos])
				else:
					name = ' '.join(command_word[pos + 1:])
			else:
				pos1 = rindex(command_word, redundancy_word[1])
				name = ' '.join(command_word[pos + 1 : pos1])
			if name:
				program_name = name
				break

	for file in system_files:
		if data_exist(file['name'], program_name, 0):
			threading.Thread(target=speak, args=(f'Opening {Capitalize_Sentence(program_name)}...',), daemon=True).start()
			si = subprocess.STARTUPINFO()
			si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			subprocess.run(file['cmd'], startupinfo=si)
			return

	program_obj = OSHandler.Program_Obj(program_name)
	program_name = Capitalize_Sentence(program_name)
	error_answers = ['Sorry, I\'m not able to help with this one.', f'Sorry, I couldn\'t find {program_name} for you',
					 f'Sorry, {program_name} might not be on your computer']
	if program_obj is None:
		speak(random.choice(error_answers))
		return

	program_path = program_obj[0]
	if program_obj[1]:
		program_path += ' ' + program_obj[1]

	threading.Thread(target=speak, args=(f'Opening {Capitalize_Sentence(program_name)}...',), daemon=True).start()
	threading.Thread(target=execute_program, args=(program_path,), daemon=True).start()

def Close_Program():
	program_name = inquiry
	with open('Resources/redundancy/close program.pck', 'rb') as file:
		close_program_redundancy = pickle.load(file)
		close_program_redundancy.sort(key=lambda x: len(x), reverse=True)

	command_word = program_name.split()
	for redundancy in close_program_redundancy:
		if data_exist([redundancy], program_name, 2):
			redundancy_word = redundancy.split()
			pos = command_word.index(redundancy_word[0])
			if len(redundancy_word) == 1:
				name = ' '.join(command_word[pos + 1:])
			else:
				pos1 = rindex(command_word, redundancy_word[1])
				name = ' '.join(command_word[pos + 1: pos1])
			if name:
				program_name = name
				break

	if data_exist(['explorer', 'control panel'], program_name):
		speak("Sorry, I can't do that")
	else:
		OSHandler.Close_Program(program_name)
		speak(Capitalize_Sentence(program_name) + ' closed')

def Exit_Program():
	command = {}
	for intent in direction['intents']:
		if intent['tag'] == 'exit':
			command = intent
			break
	speak(random.choice(command['response']))
	Exit()

def Shutdown():
	command = {}
	for intent in direction['intents']:
		if intent['tag'] == 'shutdown':
			command = intent
			break
	speak(random.choice(command['response']))
	si = subprocess.STARTUPINFO()
	si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	subprocess.run('shutdown /s', startupinfo=si)
	Exit()

def Check_Ability():
	action = inquiry
	command_word = inquiry.split()
	redundancy = ['can you', 'are you able to', 'are you capable of']
	for x in redundancy:
		if data_exist([x], inquiry):
			x_word = x.split()
			pos = command_word.index(x_word[-1])
			action = ' '.join(command_word[pos + 1:])

	command = {}
	for intent in direction['intents']:
		if intent['tag'] == 'check ability':
			command = intent
			break

	action = lemmatize_word(action)
	if data_exist(command['response']['able']['actions'], action, 2):
		speak(random.choice(command['response']['able']['response']))
	else:
		speak(random.choice(command['response']['unable']['response']))

def Unikey_Switch():
	OSHandler.Unikey_Switch()
	speak('Language switched')

def File_Update():
	def set_bit(x, pos):
		return x | (1 << pos)

	speak('Updating...')
	if data_exist(['program', 'music', 'song'], inquiry):
		type = 0
		if 'program' in inquiry:
			type = set_bit(type, 0)
		if data_exist(['music', 'song'], inquiry):
			type = set_bit(type, 1)
	else:
		type = 3

	OSHandler.Path_Update(type)

	speak('File path updated')

def Switch_Record_Mode():
	if 'voice' in inquiry:
		target = 0
	elif data_exist(['chat', 'type'], inquiry):
		target = 1
	else:
		target = 2

	if target != chatMode:
		changeChatMode()
		if target == 2:
			speak('Record mode switched')
		elif target == 0:
			speak('voice mode activated')
		else:
			speak('chat mode activated')
	else:
		if target == 0:
			speak('you are already in voice mode')
		else:
			speak('you are already in chat mode')

def Volume():
	status = OSHandler.Volume(inquiry)
	if 'set standard' in status:
		num = re.findall(r'[0-9]+', status)[0]
		with open('Resources/userData/standard volume level.txt', 'w') as file:
			file.write(num)
		global standard_volume
		standard_volume = int(num)
	speak(status)

def Type_Key():
	command_word = inquiry.split()
	if not data_exist(['enter', 'type', 'press'], inquiry):
		pos = -1
		command_type = 'press'
	else:
		type_pos = len(command_word)
		enter_pos = len(command_word)
		press_pos = len(command_word)
		if 'type' in command_word:
			type_pos = command_word.index('type')
		if 'enter' in command_word:
			enter_pos = command_word.index('enter')
		if 'press' in command_word:
			press_pos = command_word.index('press')

		pos = min(type_pos, enter_pos, press_pos)
		command_type = command_word[pos]

	times_pos = []
	twice_pos = []
	# type multiple times
	if 'times' in command_word[pos + 1:]:
		times_pos.append(command_word.index('times'))
		times_pos.append(rindex(command_word, 'times'))
	else:
		times_pos.append(-1)
		times_pos.append(-1)
	if 'twice' in command_word[pos + 1:]:
		twice_pos.append(command_word.index('twice'))
		twice_pos.append(rindex(command_word, 'twice'))
	else:
		twice_pos.append(-1)
		twice_pos.append(-1)

	word = ''
	type_num = 1

	# check if user really command type multiple times
	if max(times_pos[1], twice_pos[1]) == len(command_word) - 1:
		if times_pos[1] == len(command_word) - 1:
			cnt = Convert_To_Int(command_word[-2])
			if cnt != 0:
				type_num = cnt
				if len(command_word) > 3 and command_word[-3] == 'for':
					cnt_begin = len(command_word) - 3
				else:
					cnt_begin = len(command_word) - 2
				if pos + 1 == cnt_begin:
					word = ' '.join(command_word[pos + 1:])
					type_num = 1
				else:
					word = ' '.join(command_word[pos + 1: cnt_begin])
		else:
			type_num = 2
			if pos + 1 != len(command_word) - 1:
				word = ' '.join(command_word[pos + 1: -1])
			else:
				type_num = 1
				word = ' '.join(command_word[pos + 1])

	if word == '':
		if pos + 1 == twice_pos[0]:
			type_num = 2
			word = ' '.join(command_word[twice_pos[0] + 1:])
		else:
			if times_pos[0] > 0:
				cnt = Convert_To_Int(command_word[times_pos[0] - 1])
				if cnt != 0:
					if times_pos[0] > 1 and command_word[times_pos[0] - 2] == 'for':
						cnt_begin = times_pos[0] - 2
					else:
						cnt_begin = times_pos[0] - 1
					if pos + 1 == cnt_begin:
						type_num = cnt
						word = ' '.join(command_word[times_pos[0] + 1:])

	if command_type == 'press':
		with open('Resources/command/special keys.pck', 'rb') as file:
			special_keys = pickle.load(file)
		special_keys.sort(key=lambda x : len(x[0]), reverse=True)

		cur = 0
		if word == '':
			word = inquiry
		command_word = word.split()
		command_word_len = len(command_word)
		command = []
		while cur < command_word_len:
			for x in special_keys:
				cnt = len(x[0].split())
				if cur + cnt > command_word_len:
					continue
				if data_exist(command_word[cur: cur + cnt], x[0]):
					command.extend(x[1])
					cur += cnt - 1
					break
			else:
				if len(command_word[cur]) == 1:
					command.append(KeyCode(char=command_word[cur]))
			cur += 1

		if chatMode == 1:
			time.sleep(1.5)
		OSHandler.Press(command, type_num)
	else:
		if len(command_word) == 1 and command_word[0] != 'enter':
			word = Further_Question('What do you want me to type?')
			if word is None:
				return
		else:
			if word == '':
				word = ' '.join(command_word[pos + 1:])

		if chatMode == 1:
			time.sleep(1.5)
		OSHandler.Type(word, type_num, command_type == 'enter')

	speak("That's done.")

def Screen_Capture():
	res = OSHandler.Screen_Capture()
	speak(f'photo saved to this path')
	attachTOframe(res, True)

def Recycle_Bin():
	bot_speaking = threading.Thread(target=speak, args=('Emptying recycle bin...',), daemon=True)
	bot_speaking.start()
	OSHandler.Empty_Recycle_Bin()
	bot_speaking.join()
	speak('Recycle bin emptied')

def Open_Folder():
	res = OSHandler.Open_Folder(inquiry)
	if res is None:
		Open_Programs()
		return

	threading.Thread(target=speak, args=(f'Opening {res[0]} folder...',), daemon=True).start()
	os.startfile(res[1])

def Covid19():
	region = 'world'
	bot_speaking = threading.Thread(target=speak, args=('Checking...',), daemon=True)
	bot_speaking.start()
	if data_exist(['in'], inquiry):
		command_word = inquiry.split()
		pos = command_word.index('in')
		location = ' '.join(command_word[pos + 1:])
		geolocator = Nominatim(user_agent='smartbot')
		location = geolocator.geocode(location)
		if location is not None:
			location = str(geolocator.reverse(f'{location.latitude},{location.longitude}', language='en'))
			location = location[location.rfind(',') + 2:]
			region = location.lower()

	if region == 'united states':
		region = 'usa'
	if region == 'united kingdom':
		region = 'uk'

	res = webScraping.Covid19(region)

	if region == 'usa':
		region = 'the US'
	elif region == 'uk':
		region = 'the UK'
	elif region == 'world':
		region = 'the globe'
	else:
		region = Capitalize_Sentence(region)

	bot_speaking.join()

	if res is None:
		speak('Sorry, there is no data available.')
	else:
		speak('Here is the Covid-19 Information in ' + region + '...')
		attachTOframe('\n'.join(res), True)

def Billboard_List():
	songs = webScraping.Billboard_Songs()

	top = 100
	if data_exist(['top'], inquiry):
		command_word = inquiry.split()
		pos = command_word.index('top')
		if pos != len(command_word) - 1:
			num = Convert_To_Int(command_word[pos + 1])
			if num != 0:
				top = min(top, num)

	result = ''
	for i, song in enumerate(songs):
		result += f"{i + 1}. {song['name']} - {song['artist']}"
		if i + 1 != top:
			result += '\n\n'
		else:
			break

	if result == '':
		speak("Sorry, there's no data available.")
		os.remove('Resources/web scraping/billboard/result.json')
	else:
		speak("Here's your song list")
		attachTOframe(result, True)

def Song_Lyrics():
	song_name = ''
	with open('Resources/redundancy/song lyrics redundancy.pck', 'rb') as file:
		song_lyrics_redundancy = pickle.load(file)
		song_lyrics_redundancy.sort(key=lambda x : len(x[0]), reverse=True)

	for redundancy in song_lyrics_redundancy:
		if data_exist([redundancy[0]], inquiry, 2):
			question_word = redundancy[0].split()
			command_word = inquiry.split()
			for x in redundancy[1]:
				if x == -1:
					pos = command_word.index(question_word[0])
					song_name = ' '.join(command_word[:pos])
				elif x == len(question_word) - 1:
					pos = command_word.index(question_word[x])
					song_name = ' '.join(command_word[pos + 1:])
				else:
					pos = command_word.index(question_word[x])
					pos1 = rindex(command_word, question_word[x + 1])
					song_name = ' '.join(command_word[pos + 1: pos1])
				if song_name:
					break
			if song_name:
				break

	if len(song_name) > 2 and song_name[-2:] == "'s":
		song_name = song_name[:-2]
	if len(song_name) > 1 and song_name[-1] == "'":
		song_name = song_name[:-1]

	lyrics = webScraping.Song_Lyrics(song_name)
	if lyrics is None:
		speak("Sorry, there's no lyrics available")
	else:
		speak("Here's the lyrics")
		attachTOframe(lyrics, True)

def Stop_Timer():
	DateTime.Stop_Timer()

	answers = ["it's cancelled", "it's stopped"]
	speak(random.choice(answers))

#return -1 : can not determine duration, return -2 : duration exceed limit (23 hour 59 minute 59 second)
def Set_Timer():
	def get_duration(query):
		query = lemmatize_word(query)
		command_word = query.split()

		hour_pos = -1
		minute_pos = -1
		second_pos = -1

		if 'hour' in command_word:
			hour_pos = command_word.index('hour')
		if data_exist(['min', 'minute'], query):
			if 'minute' in command_word:
				minute_pos = command_word.index('minute')
			if 'min' in command_word:
				if minute_pos != -1:
					minute_pos = min(minute_pos, command_word.index('min'))
				else:
					minute_pos = command_word.index('min')
		if data_exist(['sec', 'second'], query):
			if 'second' in command_word:
				second_pos = command_word.index('second')
			if 'sec' in command_word:
				if second_pos != -1:
					second_pos = min(second_pos, command_word.index('sec'))
				else:
					second_pos = command_word.index('sec')

		if max(hour_pos, minute_pos, second_pos) > 0:
			request_seconds = 0
			if hour_pos > 0:
				if data_exist(['a', 'an'], command_word[hour_pos - 1]):
					request_seconds = 3600
				else:
					request_seconds = 3600 * Convert_To_Int(command_word[hour_pos - 1])

			if minute_pos > 0:
				if data_exist(['a', 'an'], command_word[minute_pos - 1]):
					request_seconds += 60
				else:
					request_seconds += 60 * Convert_To_Int(command_word[minute_pos - 1])

			if second_pos > 0:
				if data_exist(['a', 'an'], command_word[second_pos - 1]):
					request_seconds += 1
				else:
					request_seconds += Convert_To_Int(command_word[second_pos - 1])


			if request_seconds >= 3600 * 24:
				return -2

			return request_seconds

		return -1

	command = inquiry
	while True:
		duration = get_duration(command)

		if duration == -2:
			speak('Sorry, I can only set timer for less than 24 hours')
			return

		if duration != -1:
			break

		command = Further_Question('For how long?')

	status = DateTime.Set_Timer(root, duration)
	if status == -1:
		speak('Timer started')
	else:
		running_hour = status // 3600
		running_minute = (status % 3600) // 60
		running_second = status % 60
		running_time = ''

		if running_hour != 0:
			running_time = str(running_hour) + ' hour' + ('s' if running_hour > 1 else '')
		if running_minute != 0:
			if running_time:
				running_time += ' ' + ('and ' if running_second != 0 else '')
			running_time += str(running_minute) + ' minute' + ('s' if running_minute > 1 else '')
		if running_second != 0:
			if running_time:
				running_time += ' and '
			running_time += str(running_second) + ' second' + ('s' if running_second > 1 else '')

		if not Task_Confirm(Further_Question(f"There's already a {running_time} timer running. Replace it?")):
			answers = ['okay', 'ok', 'got it']
			speak(random.choice(answers))
			return

		DateTime.Set_Timer(root, duration, True)
		speak('Timer started')

def Give_Assistance():
	questions = ['What can I do for you?', 'What do you want me to do?', 'Ask me anything', 'Feel free to ask', "I'm listening", 'What do you need me to help with?']
	query = Further_Question(random.choice(questions))
	get_response(query)

def openSettings():
	threading.Thread(target=speak, args=('Opening Settings...',), daemon=True).start()
	raise_frame(root2)

#user command recorded
def changeProfileIMG():
	threading.Thread(target=speak, args=('Here are the avatars to choose',), daemon=True).start()
	SelectAvatar()

#user command recorded
def switchTheme():
	global themeValue
	if data_exist(['dark'], inquiry):
		themeValue.set(0)
		type = 'dark'
	elif data_exist(['light'], inquiry):
		themeValue.set(1)
		type = 'light'
	else:
		themeValue.set(themeValue.get() ^ 1)
		type = ''
	changeTheme()
	if type:
		speak(f'Switched to {type} theme')
	else:
		speak('Theme switched')

def changeChatColor():
	threading.Thread(target=speak, args=('Here are the colors to choose',), daemon=True).start()
	getChatColor()

procedures = {
	'play music' : Play_Music,
	'stop music' : Stop_Music,
	'meaning' : Get_Definition,
	'joke' : Tell_Joke,
	'time' : Tell_Time,
	'day and date' : Tell_Day,
	'weather' : Tell_Weather,
	'website' : Open_Websites,
	'youtube' : Youtube,
	'translate' : Translate,
	'email' : Check_Email,
	'system info' : System_Info,
	'battery' : Battery,
	'show image' : Show_Image,
	'direction' : Get_Direction,
	'math calculation' : Math_Calculation,
	'web based search' : Web_Based_Search,
	'file update' : File_Update,
	'ip address' : Get_Ip_Address,
	'find location' : Find_Location,
	'current location' : Get_Current_Location,
	'isp' : Get_ISP,
	'synonym' : Get_Synonyms,
	'antonym' : Get_Antonyms,
	'random number' : Get_Random_Number,
	'media search' : Media_Search,
	'codeforces' : Codeforces,
	'internet' : Ping,
	'open programs' : Open_Programs,
	'exit' : Exit_Program,
	'check ability' : Check_Ability,
	'unikey' : Unikey_Switch,
	'switch record mode' : Switch_Record_Mode,
	'type key' : Type_Key,
	'shutdown' : Shutdown,
	'volume' : Volume,
	'screen capture' : Screen_Capture,
	'system usage' : System_Usage,
	'recycle bin' : Recycle_Bin,
	'open folder' : Open_Folder,
	'covid' : Covid19,
	'billboard' : Billboard_List,
	'ask for favor' : Give_Assistance,
	'close program' : Close_Program,
	'pause music' : Pause_Music,
	'next song' : Next_Song,
	'prev song' : Prev_Song,
	'settings' : openSettings,
	'switch theme' : switchTheme,
	'avatar' : changeProfileIMG,
	'chat color' : changeChatColor,
	'song lyrics' : Song_Lyrics,
	'set timer' : Set_Timer,
	'stop timer' : Stop_Timer
}

def get_response(command):
	AITaskStatusLbl['text'] = 'Processing...'
	global inquiry, inprogress, voiceMedium_thread, voicemedium_thread_killed
	inprogress = True
	inquiry = refine_sentence(command)
	try:
		tag = AITasks.predict_class(inquiry)
		if tag is not None:
			if tag in direct_answer:
				list_of_intents = direction['intents']
				for i in list_of_intents:
					if i['tag'] == tag:
						speak(random.choice(i['response']))
						break
			else:
				procedures[tag]()
		else:
			Web_Based_Search()
	except Exception as e:
		messagebox.showerror('Error', e)

	inprogress = False

	if chatMode == 0:
		if voicemedium_thread_killed:
			voicemedium_thread_killed = False
			voiceMedium_thread = voiceMedium()
			voiceMedium_thread.start()
	else:
		if not voicemedium_thread_killed:
			voicemedium_thread_killed = True
			voiceMedium_thread.raise_exception()


########################################## BOOT UP WINDOW ###########################################
def ChangeSettings(write=False):
	global background, textColor, chatBgColor, voice_id, ass_voiceRate, AITaskStatusLblBG, KCS_IMG, botChatTextBg, botChatText, userChatTextBg, user_avatar
	setting = {'background': background,
				'textColor': textColor,
				'chatBgColor': chatBgColor,
				'AITaskStatusLblBG': AITaskStatusLblBG,
				'KCS_IMG': KCS_IMG,
				'botChatText': botChatText,
				'botChatTextBg': botChatTextBg,
				'userChatTextBg': userChatTextBg,
				'voice_id': voice_id,
				'ass_voiceRate': ass_voiceRate,
			   	'user_avatar' : user_avatar
			}
	if write:
		with open('Resources/userData/settings.pck', 'wb') as file:
			pickle.dump(setting, file)
		return
	try:
		with open('Resources/userData/settings.pck', 'rb') as file:
			loadSettings = pickle.load(file)
			background = loadSettings['background']
			textColor = loadSettings['textColor']
			chatBgColor = loadSettings['chatBgColor']
			AITaskStatusLblBG = loadSettings['AITaskStatusLblBG']
			KCS_IMG = loadSettings['KCS_IMG']
			botChatText = loadSettings['botChatText']
			botChatTextBg = loadSettings['botChatTextBg']
			userChatTextBg = loadSettings['userChatTextBg']
			voice_id = loadSettings['voice_id']
			ass_voiceRate = loadSettings['ass_voiceRate']
			user_avatar = loadSettings['user_avatar']
	except:
		Exit()

if os.path.exists('Resources/userData/settings.pck')==False:
	ChangeSettings(True)

def changeTheme():
	global background, textColor, AITaskStatusLblBG, KCS_IMG, botChatText, botChatTextBg, userChatTextBg, chatBgColor, displayed_botIcon, displayed_userIcon, displayed_userText, displayed_botText
	if themeValue.get()==0:
		background, textColor, AITaskStatusLblBG, KCS_IMG = "#203647", "white", "#203647",1
		cbl['image'] = cblDarkImg
		kbBtn['image'] = kbphDark
		settingBtn['image'] = sphDark
		AITaskStatusLbl['bg'] = AITaskStatusLblBG
		botChatText, botChatTextBg, userChatTextBg = "white", "#007cc7", "#4da8da"
		chatBgColor = "#12232e"
		colorbar['bg'] = chatBgColor
	else:
		background, textColor, AITaskStatusLblBG, KCS_IMG = "#F6FAFB", "#303E54", "#14A769", 0
		cbl['image'] = cblLightImg
		kbBtn['image'] = kbphLight
		settingBtn['image'] = sphLight
		AITaskStatusLbl['bg'] = AITaskStatusLblBG
		botChatText, botChatTextBg, userChatTextBg = "#494949", "#EAEAEA", "#23AE79"
		chatBgColor = "#F6FAFB"
		colorbar['bg'] = '#E8EBEF'

	for i in range(len(displayed_userIcon)):
		displayed_userIcon[i]['bg'] = chatBgColor
	for i in range(len(displayed_userText)):
		displayed_userText[i].config(bg=userChatTextBg)
	for i in range(len(displayed_botIcon)):
		displayed_botIcon[i]['bg'] = chatBgColor
	for i in range(len(displayed_botText)):
		displayed_botText[i].config(bg=botChatTextBg, fg=botChatText)
	root['bg'] = root2['bg'] = background
	settingsFrame['bg'] = background
	settingsLbl['fg'], userPhoto['fg'], userName['fg'], assLbl['fg'], voiceRateLbl['fg'], volumeLbl['fg'], themeLbl['fg'], chooseChatLbl['fg'] = textColor, textColor, textColor, textColor, textColor, textColor, textColor, textColor
	settingsLbl['bg'], userPhoto['bg'], userName['bg'], assLbl['bg'], voiceRateLbl['bg'], volumeLbl['bg'], themeLbl['bg'], chooseChatLbl['bg'] = background, background, background, background, background, background, background, background
	s.configure('Wild.TRadiobutton', background=background, foreground=textColor)
	volumeBar['bg'], volumeBar['fg'], volumeBar['highlightbackground'] = background, textColor, background
	chat_frame['bg'], root1['bg'], chat_canvas['bg'], chat_main_frame['bg'] =  chatBgColor, chatBgColor, chatBgColor, chatBgColor
	userPhoto['activebackground'] = background
	ChangeSettings(True)

'''def changeVoice(e):
	global voice_id
	voice_id=0
	if assVoiceOption.get()=='Female': voice_id=1
	engine.setProperty('voice', voices[voice_id].id)
	ChangeSettings(True)'''

def changeVolume(e):
	Adjust_Volume_Off()
	ass_volume = volumeVar.get() / 100
	engine.setProperty('volume', ass_volume)
	pygame.mixer.music.set_volume(0.8 * ass_volume)

def adjustVolume():
	if Adjust_Volume_Allowed():
		current_volume = int(re.findall(r'[0-9]+', OSHandler.Volume('current volume'))[0])  # master volume
		current_level = volumeVar.get()  # smart bot volume
		target_level = round(standard_volume / current_volume * 100)
		target_level = min(target_level, 100)
		if current_level != target_level:
			global vlc_target_volume
			vlc_target_volume = min(100, round(target_level * 1.6))
			volumeVar.set(target_level)
			engine.setProperty('volume', target_level / 100)
			pygame.mixer.music.set_volume(target_level / 100 * 0.8)
	root.after(100, adjustVolume)

def changeVoiceRate(e):
	global ass_voiceRate
	temp = voiceOption.get()
	if temp=='Very Low': ass_voiceRate = 100
	elif temp=='Low': ass_voiceRate = 150
	elif temp=='Fast': ass_voiceRate = 250
	elif temp=='Very Fast': ass_voiceRate = 300
	else: ass_voiceRate = 200
	engine.setProperty('rate', ass_voiceRate)
	ChangeSettings(True)

ChangeSettings()

############################################ SET UP VOICE ###########################################
try:
	engine = pyttsx3.init()
	voices = engine.getProperty('voices')
	engine.setProperty('voice', voices[voice_id].id) #male
except:
	Exit()


####################################### SET UP TEXT TO SPEECH #######################################
def speak(text, display=True, showIcon=True):
	time.sleep(0.2)
	if text:
		text = text[0].upper() + text[1:]
	AITaskStatusLbl['text'] = 'Speaking...'
	if showIcon:
		displayLabel(True)
		update_chat_frame()
	if display:
		attachTOframe(text, True)
	try:
		engine.say(text)
		engine.runAndWait()
	except:
		pass

	if not inprogress:
		AITaskStatusLbl['text'] = 'Listening...'
	else:
		AITaskStatusLbl['text'] = 'Processing...'

####################################### SET UP SPEECH TO TEXT #######################################
recognition_waittime = 3
record_result = None
class Record_Thread(threading.Thread):
	def __init__(self, recognizer, audio):
		threading.Thread.__init__(self)
		self.daemon = True
		self.recognizer = recognizer
		self.audio = audio

	def run(self):
		global record_result
		try:
			#record_result remains None when encounter waittimeout error
			said = self.recognizer.recognize_google(self.audio)
			said = said[0].upper() + said[1:]
			record_result = said
		except Exception as e:
			record_result = type(e)


	def get_id(self):
		if hasattr(self, '_thread_id'):
			return self._thread_id
		for id, thread in threading._active.items():
			if thread is self:
				return id

	def raise_exception(self):
		thread_id = self.get_id()
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
		if res > 1:
			ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)

vlc_target_volume = 100

def record(ask = '', from_further_question = False):
	global record_result
	record_result = None
	with sr.Microphone() as source:
		AITaskStatusLbl['text'] = 'Listening...'
		recording_sound = False
		if ask:
			speak(ask)
			AITaskStatusLbl['text'] = 'Listening...'
			if chatMode == 0:
				media_player = vlc.MediaPlayer()
				media_player.set_media(vlc.Media('Resources/audio/listening.mp3'))
				media_player.audio_set_volume(vlc_target_volume)
				media_player.play()
				recording_sound = True
		voiceRecognizer.adjust_for_ambient_noise(source)
		audio = voiceRecognizer.listen(source)
		if chatMode == 0:
			if ask:
				if recording_sound:
					media_player = vlc.MediaPlayer()
					media_player.set_media(vlc.Media('Resources/audio/processing.mp3'))
					media_player.audio_set_volume(vlc_target_volume)
					media_player.play()
				AITaskStatusLbl['text'] = 'Processing...'
				result_thread = Record_Thread(voiceRecognizer, audio)
				start_time = time.time()
				result_thread.start()
				while time.time() - start_time < recognition_waittime and record_result is None:
					time.sleep(0.05)

				result_thread.raise_exception()

				if record_result is sr.RequestError:
					speak('i\'m having trouble connecting to the Internet')
					return None

				if record_result in [sr.UnknownValueError, sr.WaitTimeoutError, None]:
					error_response = ['i can\'t hear that', 'i didn\'t catch it']
					return refine_sentence(record(random.choice(error_response), from_further_question))

				if not (from_further_question ^ inprogress):
					displayLabel()
					update_chat_frame()
					attachTOframe(record_result)
				return record_result
			else:
				AITaskStatusLbl['text'] = 'Processing...'
				result_thread = Record_Thread(voiceRecognizer, audio)
				start_time = time.time()
				result_thread.start()
				while time.time() - start_time < recognition_waittime and record_result is None:
					time.sleep(0.05)

				result_thread.raise_exception()

				if inprogress:
					if record_result is sr.RequestError:
						speak('i\'m having trouble connecting to the Internet')
						return None
					elif record_result in [sr.WaitTimeoutError, sr.UnknownValueError, None]:
						error_response = ['i can\'t hear that', 'i didn\'t catch it']
						return refine_sentence(record(random.choice(error_response), from_further_question))
					else:
						if not (from_further_question ^ inprogress):
							displayLabel()
							update_chat_frame()
							attachTOframe(record_result)
						return record_result
				else:
					if record_result is sr.RequestError:
						speak('i\'m having trouble connecting to the Internet')
						return None
					elif record_result is sr.WaitTimeoutError:
						speak('something went wrong, try again!')
						return None
					elif record_result in [sr.UnknownValueError, None]:
						return None
					else:
						if not (from_further_question ^ inprogress):
							displayLabel()
							update_chat_frame()
							attachTOframe(record_result)
						return record_result
		else:
			return None

class voiceMedium(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True

	def run(self):
		while True:
			query = record()
			if query:
				get_response(query)


	def get_id(self):
		if hasattr(self, '_thread_id'):
			return self._thread_id
		for id, thread in threading._active.items():
			if thread is self:
				return id

	def raise_exception(self):
		thread_id = self.get_id()
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
		if res > 1:
			ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)

def keyboardInput(e):
	user_input = UserField.get()
	global inprogress
	if user_input:
		user_input = user_input[0].upper() + user_input[1:]
		if not inprogress:
			displayLabel()
			update_chat_frame()
			attachTOframe(user_input)
			threading.Thread(target=get_response, args=(user_input,), daemon=True).start()
		else:
			global inprogress_answer
			displayLabel()
			update_chat_frame()
			attachTOframe(user_input)
			inprogress_answer = refine_sentence(user_input)
		UserField.delete(0, END)

############ ATTACHING BOT/USER LABEL ON CHAT SCREEN ##########
def displayLabel(bot=False):
	global displayed_botIcon, displayed_userIcon
	if bot:
		displayed_botIcon.append(Label(chat_frame, image=botIcon, bg=chatBgColor))
		displayed_botIcon[-1].pack(anchor='w', pady=0)
	else:
		displayed_userIcon.append(Label(chat_frame, image=userIcon, bg=chatBgColor))
		displayed_userIcon[-1].pack(anchor='e', pady=0)


############ ATTACHING BOT/USER CHAT ON CHAT SCREEN ###########
def attachTOframe(text,bot=False):
	global displayed_botText, displayed_userText
	if bot:
		botchat = Label(chat_frame,text=text, bg=botChatTextBg, fg=botChatText, justify=LEFT, wraplength=250, font=('Montserrat',12, 'bold'))
		displayed_botText.append(botchat)
		displayed_botText[-1].pack(anchor='w',ipadx=5,ipady=5,pady=5)
	else:
		userchat = Label(chat_frame, text=text, bg=userChatTextBg, fg='white', justify=RIGHT, wraplength=250, font=('Montserrat',12, 'bold'))
		displayed_userText.append(userchat)
		displayed_userText[-1].pack(anchor='e',ipadx=2,ipady=2,pady=5)
	update_chat_frame()

### SWITCHING BETWEEN FRAMES ###
def raise_frame(frame):
	if frame is root1:
		scrollbar_position = chat_scrollbar.get()
		if scrollbar_position != (0.0, 0.0, 0.0, 0.0):
			chat_scrollbar.set(scrollbar_position[0], scrollbar_position[1])
	else:
		chat_canvas.unbind_all('<MouseWheel>')
		chat_canvas.unbind_all('<Down>')
		chat_canvas.unbind_all('<Up>')
	frame.tkraise()

################# SHOWING DOWNLOADED IMAGES ###############
img0, img1, img2, img3 = None, None, None, None
def showSingleImage(type, data=None):
	global img0, img1, img2, img3, displayed_img
	try:
		img0 = ImageTk.PhotoImage(Image.open('Resources/web scraping/imgDownloads/0.jpg').resize((90,110), Image.ANTIALIAS))
	except:
		pass
	#img1 = ImageTk.PhotoImage(Image.open('Resources/images/heads.jpg').resize((220,200), Image.ANTIALIAS))
	#img2 = ImageTk.PhotoImage(Image.open('Resources/images/tails.jpg').resize((220,200), Image.ANTIALIAS))
	img1 = ImageTk.PhotoImage(Image.open('Resources/images/WeatherImage.png'))

	if type == 'weather':
		weather = Frame(chat_frame)
		weather.pack(anchor='w')
		displayed_img.add(img1)
		Label(weather, image=img1, bg=chatBgColor).pack()
		Label(weather, text=data[0], font=('Arial Bold', 45), fg='white', bg='#3F48CC').place(x=65, y=45)
		Label(weather, text=data[1], font=('Montserrat', 15), fg='white', bg='#3F48CC').place(x=100 - int(len(data[1])/2)*9, y=110)
		Label(weather, text=data[2], font=('Montserrat', 10), fg='white', bg='#3F48CC').place(x=100 - int(len(data[2])/2*7.5), y=140)
		Label(weather, text=data[3], font=('Arial Bold', 12), fg='white', bg='#3F48CC').place(x=100 - int(len(data[3])/2 + len(data[3])%2)*8, y=160)
		update_chat_frame()
	else:
		displayed_img.add(img0)
		Label(chat_frame, image=img0, bg='#EAEAEA').pack(anchor='w', pady=5)
		update_chat_frame()


######################## CHANGING CHAT BACKGROUND COLOR #########################
def getChatColor():
	global chatBgColor, displayed_botIcon, displayed_userIcon
	myColor = colorchooser.askcolor()
	if myColor[1] is None: return
	chatBgColor = myColor[1]
	colorbar['bg'] = chatBgColor
	chat_frame['bg'] = chatBgColor
	root1['bg'] = chatBgColor
	chat_canvas['bg'] = chatBgColor
	chat_main_frame['bg'] = chatBgColor
	for i in range(len(displayed_botIcon)):
		displayed_botIcon[i]['bg'] = chatBgColor
	for i in range(len(displayed_userIcon)):
		displayed_userIcon[i]['bg'] = chatBgColor
	ChangeSettings(True)

chatMode = 0
def changeChatMode():
	global chatMode, inprogress, voicemedium_thread_killed, voiceMedium_thread
	if chatMode == 0:
		if not inprogress:
			voiceMedium_thread.raise_exception()
			voicemedium_thread_killed = True
		chatMode = 1
		VoiceModeFrame.pack_forget()
		TextModeFrame.pack(fill=BOTH)
		UserField.focus()
	else:
		if inprogress is False and voicemedium_thread_killed is True:
			voicemedium_thread_killed = False
			voiceMedium_thread = voiceMedium()
			voiceMedium_thread.start()
		chatMode = 0
		TextModeFrame.pack_forget()
		VoiceModeFrame.pack(fill=BOTH)
		root.focus()

def on_activate():
	changeChatMode()

def for_canonical(f):
	return lambda k: f(key_listener.canonical(k))

hotkey = HotKey(
		HotKey.parse('<alt>+a'),
		on_activate)

key_listener = Listener(
			on_press=for_canonical(hotkey.press),
			on_release=for_canonical(hotkey.release))

############################################## GUI #############################################

def onhover(e):
	userPhoto['image'] = chngPh
def onleave(e):
	userPhoto['image'] = userProfileImg

def UpdateIMAGE():
	import ChooseAvatarPIC
	global user_avatar, userProfileImg, userIcon, displayed_userIcon
	si = subprocess.STARTUPINFO()
	si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	ChooseAvatarPIC.run_code(root)
	userPhoto['state'] = DISABLED
	userPhoto.unbind('<Enter>')
	userPhoto.unbind('<Leave>')

	Choosing_Avatar_Set_True()
	while Choosing_Avatar():
		time.sleep(0.1)

	root.focus_set()
	userPhoto['state'] = NORMAL
	userPhoto.bind('<Enter>', onhover)
	userPhoto.bind('<Leave>', onleave)

	with open('Resources/userData/settings.pck', 'rb') as file:
		loadSettings = pickle.load(file)
		user_avatar = loadSettings['user_avatar']
		userProfileImg = ImageTk.PhotoImage(Image.open(f'Resources/images/avatars/a{user_avatar}.png').resize((120, 120)))

		userPhoto['image'] = userProfileImg
		userIcon = PhotoImage(file=f'Resources/images/avatars/ChatIcons/a{user_avatar}.png')

		for i in range(len(displayed_userIcon)):
			displayed_userIcon[i].config(image=userIcon)

def SelectAvatar():
	threading.Thread(target=UpdateIMAGE, daemon=True).start()


#####################################  MAIN GUI ####################################################

#### SPLASH/LOADING SCREEN ####
def progressbar():
	s = ttk.Style()
	s.theme_use('clam')
	s.configure("white.Horizontal.TProgressbar", foreground='white', background='white')
	progress_bar = ttk.Progressbar(splash_root, style="white.Horizontal.TProgressbar", orient="horizontal",
								   mode="determinate", length=303)
	progress_bar.pack()
	splash_root.update()
	progress_bar['value'] = 0
	splash_root.update()

	AiTask_Initialize_Increment = 0.04
	if training_required:
		num = 0
		for x in direction['intents']:
			num += len(x['patterns'])
		seconds_per_step = 6 / 1000
		required_second = seconds_per_step * ((num - 1) / training_batch_size + 1) * training_epochs
		increment = round(100 / (required_second * 20), 3) - AiTask_Initialize_Increment
	else:
		increment = 1.3 - AiTask_Initialize_Increment
	while progress_bar['value'] < 100:
		progress_bar['value'] += increment
		splash_root.update()
		time.sleep(0.05)

def destroySplash():
	splash_root.destroy()

class AutoScrollbar(Scrollbar):
	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			chat_canvas.unbind_all('<MouseWheel>')
			chat_canvas.unbind_all('<Down>')
			chat_canvas.unbind_all('<Up>')
		else:
			chat_canvas.bind_all('<MouseWheel>', on_mousewheel)
			chat_canvas.bind_all('<Down>', scrolldown)
			chat_canvas.bind_all('<Up>', scrollup)
		Scrollbar.set(self, lo, hi)

def on_mousewheel(event):
	chat_canvas.yview_scroll(-1*event.delta//120, "units")

def scrolldown(event):
	chat_canvas.yview_scroll(1, "units")

def scrollup(event):
	chat_canvas.yview_scroll(-1, "units")

def update_chat_frame():
	chat_frame.update_idletasks()
	chat_canvas.config(scrollregion=chat_canvas.bbox('all'))
	chat_canvas.yview_moveto(1.0)

if __name__ == '__main__':
	multiprocessing.freeze_support()
	gpus = tensorflow.config.list_physical_devices('GPU')
	for gpu in gpus:
		try:
			tensorflow.config.experimental.set_memory_growth(gpu, True)
		except:
			pass
	training_required = AITasks.Training_Required()
	initialize_thread = threading.Thread(target=Initialize, daemon=True)
	initialize_thread.start()
	splash_root = Tk()
	splash_root.config(bg='#3895d3')
	splash_root.overrideredirect(True)
	splash_label = Label(splash_root, text='Processing...', font=('montserrat', 15), bg='#3895d3', fg='white')
	splash_label.pack(pady=40)

	w_width, w_height = 400, 200
	s_width, s_height = splash_root.winfo_screenwidth(), splash_root.winfo_screenheight()
	x, y = (s_width / 2) - (w_width / 2), (s_height / 2) - (w_height / 2)
	splash_root.geometry('%dx%d+%d+%d' % (w_width, w_height, x, y - 30))

	progressbar()
	initialize_thread.join()
	splash_root.after(10, destroySplash)
	splash_root.mainloop()

	key_listener.start()
	root = Tk()
	root.title('T.O.M')
	root.protocol('WM_DELETE_WINDOW', Exit)

	w_width, w_height = 400, 650
	s_width, s_height = root.winfo_screenwidth(), root.winfo_screenheight()
	x, y = (s_width / 2) - (w_width / 2), (s_height / 2) - (w_height / 2)
	root.geometry('%dx%d+%d+%d' % (w_width, w_height, x, y - 30))  # center location of the screen
	root.resizable(width=False, height=False)
	root.config(bg=background)
	root.pack_propagate(False)
	root.iconbitmap('Resources/images/assistant2.ico')

	root1 = Frame(root, bg=chatBgColor)
	root2 = Frame(root, bg=background)
	root3 = Frame(root, bg=background)

	for f in (root1, root2, root3):
		f.grid(row=0, column=0, sticky='news')	
	
	################################
	########  CHAT SCREEN  #########
	################################

	#Chat Frame
	chat_main_frame = Frame(root1, width=400, height=551, bg=chatBgColor, bd=0)
	chat_main_frame.pack()
	chat_main_frame.pack_propagate(False)

	chat_canvas = Canvas(chat_main_frame, width=380, height=551, highlightthickness=0, bd=0, bg=chatBgColor)
	chat_canvas.pack(side=LEFT, fill=BOTH, expand=1)
	chat_canvas.pack_propagate(False)

	chat_scrollbar = AutoScrollbar(chat_main_frame)
	chat_scrollbar.config(command=chat_canvas.yview, width=10)
	chat_scrollbar.pack(fill=Y, side=RIGHT)

	chat_canvas.config(yscrollcommand=chat_scrollbar.set)

	chat_frame = Frame(chat_canvas, bg=chatBgColor)
	chat_canvas.create_window((10, 0), window=chat_frame, anchor='nw', width=375)

	bottomFrame1 = Frame(root1, bg='#dfdfdf', height=100)
	bottomFrame1.pack(fill=X, side=BOTTOM)
	VoiceModeFrame = Frame(bottomFrame1, bg='#dfdfdf')
	VoiceModeFrame.pack(fill=BOTH)
	TextModeFrame = Frame(bottomFrame1, bg='#dfdfdf')
	TextModeFrame.pack(fill=BOTH)

	# VoiceModeFrame.pack_forget()
	TextModeFrame.pack_forget()

	cblLightImg = PhotoImage(file='Resources/images/centralButton.png')
	cblDarkImg = PhotoImage(file='Resources/images/centralButton1.png')
	if KCS_IMG==1: cblimage=cblDarkImg
	else: cblimage=cblLightImg
	cbl = Label(VoiceModeFrame, fg='white', image=cblimage, bg='#dfdfdf')
	cbl.pack(pady=17)
	AITaskStatusLbl = Label(VoiceModeFrame, text='    Offline', fg='white', bg=AITaskStatusLblBG, font=('montserrat', 16))
	AITaskStatusLbl.place(x=140,y=32)
	
	#Settings Button
	sphLight = PhotoImage(file = "Resources/images/setting.png")
	sphLight = sphLight.subsample(2,2)
	sphDark = PhotoImage(file = "Resources/images/setting1.png")
	sphDark = sphDark.subsample(2,2)
	if KCS_IMG==1: sphimage=sphDark
	else: sphimage=sphLight
	settingBtn = Button(VoiceModeFrame,image=sphimage,height=30,width=30, bg='#dfdfdf',borderwidth=0,activebackground="#dfdfdf",command=lambda: raise_frame(root2))
	settingBtn.place(relx=1.0, y=30,x=-20, anchor="ne")	
	
	#Keyboard Button
	kbphLight = PhotoImage(file = "Resources/images/keyboard.png")
	kbphLight = kbphLight.subsample(2,2)
	kbphDark = PhotoImage(file = "Resources/images/keyboard1.png")
	kbphDark = kbphDark.subsample(2,2)
	if KCS_IMG==1: kbphimage=kbphDark
	else: kbphimage=kbphLight
	kbBtn = Button(VoiceModeFrame,image=kbphimage,height=30,width=30, bg='#dfdfdf',borderwidth=0,activebackground="#dfdfdf", command=changeChatMode)
	kbBtn.place(x=25, y=30)

	#Mic
	micImg = PhotoImage(file = "Resources/images/mic.png")
	micImg = micImg.subsample(2,2)
	micBtn = Button(TextModeFrame,image=micImg,height=30,width=30, bg='#dfdfdf',borderwidth=0,activebackground="#dfdfdf", command=changeChatMode)
	micBtn.place(relx=1.0, y=30,x=-20, anchor="ne")	
	
	#Text Field
	TextFieldImg = PhotoImage(file='Resources/images/textField.png')
	UserFieldLBL = Label(TextModeFrame, fg='white', image=TextFieldImg, bg='#dfdfdf')
	UserFieldLBL.pack(pady=17, side=LEFT, padx=10)
	UserField = Entry(TextModeFrame, fg='white', bg='#203647', font=('Montserrat', 16), bd=6, width=22, relief=FLAT)
	UserField.place(x=20, y=30)
	UserField.bind('<Return>', keyboardInput)
	
	#User and Bot Icon
	userIcon = PhotoImage(file="Resources/images/avatars/ChatIcons/a"+str(user_avatar)+".png")
	botIcon = PhotoImage(file="Resources/images/assistant2.png")
	botIcon = botIcon.subsample(2,2)
	

	###########################
	########  SETTINGS  #######
	###########################

	settingsLbl = Label(root2, text='Settings', font=('Arial Bold', 15), bg=background, fg=textColor)
	settingsLbl.pack(pady=10)
	separator = ttk.Separator(root2, orient='horizontal')
	separator.pack(fill=X)
	#User Photo
	userProfileImg = Image.open("Resources/images/avatars/a"+str(user_avatar)+".png")
	userProfileImg = ImageTk.PhotoImage(userProfileImg.resize((120, 120)))
	userPhoto = Button(root2, image=userProfileImg, bg=background, bd=0, relief=FLAT, activebackground=background, command=SelectAvatar)
	userPhoto.pack(pady=(20, 5))

	#Change Photo
	chngPh = ImageTk.PhotoImage(Image.open("Resources/images/avatars/changephoto2.png").resize((120, 120)))
	
	userPhoto.bind('<Enter>', onhover)
	userPhoto.bind('<Leave>', onleave)

	#Username
	userName = Label(root2, text='Tri', font=('Arial Bold', 15), fg=textColor, bg=background)
	userName.pack()

	#Settings Frame
	settingsFrame = Frame(root2, width=300, height=300, bg=background)
	settingsFrame.pack(pady=20)

	assLbl = Label(settingsFrame, text='Assistant Voice', font=('Arial', 13), fg=textColor, bg=background)
	assLbl.place(x=0, y=20)
	n = StringVar()
	assVoiceOption = ttk.Combobox(settingsFrame, values=('Male'), font=('Arial', 13), width=13, textvariable=n)
	assVoiceOption.current(voice_id)
	assVoiceOption.place(x=150, y=20)
	#assVoiceOption.bind('<<ComboboxSelected>>', changeVoice)

	voiceRateLbl = Label(settingsFrame, text='Voice Rate', font=('Arial', 13), fg=textColor, bg=background)
	voiceRateLbl.place(x=0, y=60)
	n2 = StringVar()
	voiceOption = ttk.Combobox(settingsFrame, font=('Arial', 13), width=13, textvariable=n2)
	voiceOption['values'] = ('Very Low', 'Low', 'Normal', 'Fast', 'Very Fast')
	voiceOption.current(ass_voiceRate//50-2) #100 150 200 250 300
	voiceOption.place(x=150, y=60)
	voiceOption.bind('<<ComboboxSelected>>', changeVoiceRate)
	
	volumeLbl = Label(settingsFrame, text='Volume', font=('Arial', 13), fg=textColor, bg=background)
	volumeLbl.place(x=0, y=105)
	volumeVar = IntVar()
	volumeVar.set(100)
	volumeBar = Scale(settingsFrame, bg=background, fg=textColor, sliderlength=30, length=135, width=16, highlightbackground=background, orient='horizontal', from_=0, to=100, variable=volumeVar, command=changeVolume)
	volumeBar.place(x=150, y=85)


	themeLbl = Label(settingsFrame, text='Theme', font=('Arial', 13), fg=textColor, bg=background)
	themeLbl.place(x=0,y=143)
	themeValue = IntVar()
	s = ttk.Style()
	s.configure('Wild.TRadiobutton', font=('Arial Bold', 10), background=background, foreground=textColor, focuscolor=s.configure(".")["background"])
	darkBtn = ttk.Radiobutton(settingsFrame, text='Dark', value=0, variable=themeValue, style='Wild.TRadiobutton', command=changeTheme, takefocus=False)
	darkBtn.place(x=150,y=145)
	lightBtn = ttk.Radiobutton(settingsFrame, text='Light', value=1, variable=themeValue, style='Wild.TRadiobutton', command=changeTheme, takefocus=False)
	lightBtn.place(x=230,y=145)
	themeValue.set(0)
	if KCS_IMG==0: themeValue.set(1)

	chooseChatLbl = Label(settingsFrame, text='Chat Background', font=('Arial', 13), fg=textColor, bg=background)
	chooseChatLbl.place(x=0,y=180)
	cimg = PhotoImage(file = "Resources/images/colorchooser.png")
	cimg = cimg.subsample(3,3)
	colorbar = Label(settingsFrame, bd=3, width=18, height=1, bg=chatBgColor)
	colorbar.place(x=150, y=180)
	if KCS_IMG==0: colorbar['bg'] = '#E8EBEF'
	Button(settingsFrame, image=cimg, relief=FLAT, command=getChatColor).place(x=261, y=180)

	backBtn_text = ''
	for i in range(29):
		backBtn_text += ' '
	backBtn_text += 'Back'
	for i in range(29):
		backBtn_text += ' '
	backBtn = Button(settingsFrame, text=backBtn_text, bd=0, font=('Arial 12'), fg='white', bg='#14A769', relief=FLAT, command=lambda:raise_frame(root1))
	backBtn.place(x=5, y=250)

	voiceMedium_thread = voiceMedium()
	voiceMedium_thread.start()

	raise_frame(root1)
	root.after(100, adjustVolume)
	root.mainloop()
	key_listener.join()
