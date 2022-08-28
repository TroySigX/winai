import datetime
import webbrowser
import requests
from bs4 import BeautifulSoup
import urllib.request
import os
from geopy.geocoders import Nominatim
from geopy.distance import great_circle

import AITasks
from global_function import data_exist, direction, Convert_To_Int, Internet
import json
import random
import subprocess
import wolframalpha
import pickle
from lyricsgenius import Genius


##########REMEMBER TO INCLUDE HEADERS############

headers = {
	'user-agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}

covid_scrape_last_time = datetime.datetime.now()
def Covid19(country):
	current_time = datetime.datetime.now()
	global covid_scrape_last_time
	if not os.path.exists('Resources/web scraping/covid/result.json') or (current_time - covid_scrape_last_time).total_seconds() / 3600 > 1:
		if os.path.exists('Resources/web scraping/covid/result.json'):
			os.remove('Resources/web scraping/covid/result.json')
		if Internet() == False:
			return None
		si = subprocess.STARTUPINFO()
		si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		subprocess.run('Resources/web scraping/covid/covidSpider.exe', startupinfo=si)

	data = json.loads(open('Resources/web scraping/covid/result.json').read())
	res = None
	for info in data:
		if data_exist([country], info['region'].lower(), 0):
			res = [
				'Total cases: ' + info['total_case'],
				'New cases: ' + info['new_case'],
				'Active cases: ' + info['active_case'],
				'Total deaths: ' + info['total_death'],
				'New deaths: ' + info['new_death'],
				'Total recovers: ' + info['total_recover'],
				'New recovers: ' + info['new_recover']
			]

	covid_scrape_last_time = current_time

	return res

class Codeforces:
	def __init__(self):
		self.owner_username = 'thantrongtri3'

	def Get_User_Ranking(self):
		html_text = requests.get(f'https://codeforces.com/profile/{self.owner_username}').content
		soup = BeautifulSoup(html_text, 'lxml')
		user_box = soup.find('div', class_='userbox')
		rating = int(user_box.find('li').find('span').text)
		level = user_box.find('div', class_='user-rank').text.strip()
		return {
			'level' : level,
			'rating' : rating
		}

	def Available_Contests(self):
		rating = self.Get_User_Ranking()['rating']
		html_text = requests.get('https://codeforces.com/contests/').content
		soup = BeautifulSoup(html_text, 'lxml')
		table = soup.find('table').find_all('tr')
		if soup.find('div', class_='contests-table') is None:
			li = table[1].find_all('td')
			if 'Before start' in li[4].text:
				return [1, len(table) - 1]
			return [2, len(table) - 1]
		res = 0
		for i in range(1, len(table)):
			li = table[i].find_all('td')
			status = li[-1].find('a', class_='red-link') is not None
			if status:
				contest_name = li[0].text.strip().lower()
				contest_length = li[3].text.strip()
				if len(contest_length) > 5:
					continue
				if contest_length > '03:00':
					continue
				omissions = ["kotlin", "q#", "unrate"]
				if data_exist(omissions, contest_name):
					continue
				if 'div. 1' in contest_name and 'div. 2' not in contest_name:
					if rating >= 1900:
						res += 1
				else:
					res += 1
		return [0, res]

	def Check_Active_User(self, user_name):
		html_text = requests.get(f'https://codeforces.com/profile/{user_name}').content
		soup = BeautifulSoup(html_text, 'lxml')

		user_box = soup.find('div', class_='userbox')

		if user_box is None:
			return None

		status = user_box.find_all('li')[3].find('span').text

		if status == 'online now':
			return True

		return False

codeforces_info = Codeforces()

def Weather(location):
	geolocator = Nominatim(user_agent='smartbot')
	loc_code = geolocator.geocode(location)
	if loc_code is None:
		return [None, None]
	url = 'https://weather.com/en-IN/weather/today/l/' + str(loc_code.latitude) + ',' + str(loc_code.longitude)
	result = requests.get(url, headers=headers)
	src = result.content
	soup = BeautifulSoup(src, 'lxml')

	spans = soup.find_all('span')
	tempValue = ''
	currCondition = ''

	for span in spans:
		try:
			if span['data-testid'] == "TemperatureValue":
				tempValue = span.text[:-1]
				break
		except:
			pass

	divs = soup.find_all('div', {'data-testid' : 'wxPhrase'})
	for div in divs:
		currCondition = div.text
		break
	return [tempValue, currCondition]

def maps(text):
	text = text.replace('maps', '')
	text = text.replace('map', '')
	text = text.replace('google', '')
	webbrowser.open('https://www.google.com/maps/place/'+text)

def giveDirections(startingPoint, destinationPoint):

	geolocator = Nominatim(user_agent='smartbot')
	if data_exist(['current', 'here'], startingPoint):
		res = requests.get("https://ipinfo.io/")
		data = res.json()
		startinglocation = geolocator.reverse(data['loc'])
	else:
		startinglocation = geolocator.geocode(startingPoint)

	destinationlocation = geolocator.geocode(destinationPoint)
	startingPoint = startinglocation.address.replace(' ', '+')
	destinationPoint = destinationlocation.address.replace(' ', '+')

	webbrowser.open('https://www.google.co.in/maps/dir/'+startingPoint+'/'+destinationPoint+'/')

	startinglocationCoordinate = (startinglocation.latitude, startinglocation.longitude)
	destinationCoordinate = (destinationlocation.latitude, destinationlocation.longitude)
	total_distance = great_circle(startinglocationCoordinate, destinationCoordinate).km #.mile
	return str(round(total_distance, 2)) + 'KM'

def Billboard_Songs():
	if not os.path.exists('Resources/web scraping/billboard/result.json'):
		si = subprocess.STARTUPINFO()
		si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		subprocess.run('Resources/web scraping/billboard/billboardSpider.exe', startupinfo=si)

	with open('Resources/web scraping/billboard/result.json', 'r') as file:
		songs = json.loads(file.read())

	return songs

def youtube(query):
	if data_exist(direction['random music sign'], query, 6):
		top = 100
		if data_exist(['top'], query):
			command_word = query.split()
			pos = command_word.index('top')
			if pos != len(command_word) - 1:
				num = Convert_To_Int(command_word[pos + 1])
				if num != 0:
					top = min(top, num)
		songs = Billboard_Songs()
		song = songs[random.randint(0, top - 1)]
		query =  song['name'] + ' ' + song['artist']
	else:
		redundancy = ['play', 'search for', 'look for', 'find a video of', 'find a video about']
		for x in redundancy:
			if x in query:
				query = query[query.find(x) + len(x) + 1:]
		youtube_sign = ['on youtube', 'youtube']
		for x in youtube_sign:
			if x in query:
				query = query[: query.find(x)]

	query = query.strip()

	from youtube_search import YoutubeSearch
	results = YoutubeSearch(query, max_results=1).to_dict()
	webbrowser.open('https://www.youtube.com/watch?v=' + results[0]['id'])


def downloadImage(query, n = 4):
	redundancy = ['show me', 'give me', 'get me', 'show', 'give', 'get']
	for x in redundancy:
		if x in query:
			query = query[query.find(x) + len(x) + 1:]
	redundancy = ['images', 'image', 'photos', 'photo', 'pictures', 'picture']
	redundancy.sort(key=lambda x : len(x), reverse=True)
	words = query.split()
	check = False
	for x in redundancy:
		if words[-1] == x:
			query = ' '.join(words[:-1])
			check = True
			break
	if check == False:
		for x in redundancy:
			tmp = x + ' of'
			if tmp in query:
				query = query[query.find(tmp) + len(tmp) + 1:]
				break
			if x in query:
				query = query[query.find(x) + len(x) + 1:]
				break

	query = query.replace('%', '%25')
	query = query.replace('+', '%2B')
	query = query.replace(' ', '%20')
	query = query.replace("'", '%27')
	URL = f'https://www.google.com/search?q={query}&tbm=isch'
	result = requests.get(URL)
	src = result.content

	soup = BeautifulSoup(src, 'lxml')
	imgTags = soup.find_all(class_='yWs4tf')

	if not os.path.exists('Resources/web scraping/imgDownloads'):
		os.mkdir('Resources/web scraping/imgDownloads')

	count=0
	for i in imgTags:
		if count==n: break
		try:
			urllib.request.urlretrieve(i['src'], f'Resources/web scraping/imgDownloads/{str(count)}.jpg')
			count += 1
		except Exception as e:
			pass

def Wikipedia_Link(query):
	query = query.replace(' Vs. ', ' vs. ')
	query = query.replace('%', '%25')
	query = query.replace('+', '%2B')
	query = query.replace(' ', '+')
	query = query.replace("'", '%27')

	query = 'https://en.wikipedia.org/w/index.php?search=' + query + '&title=Special:Search&profile=advanced&fulltext=1&ns0=1'
	html_text = requests.get(query, headers=headers).content
	soup = BeautifulSoup(html_text, 'lxml')

	if soup.find('p', class_='mw-search-createlink') is not None:
		return None

	try:
		result = soup.find('li', class_='mw-search-result')
		result_link = result.find('a', href=True)
		return 'https://en.wikipedia.org/' + result_link['href']
	except:
		return None

def Wikipedia(query):
	URL = Wikipedia_Link(query)
	if URL is None:
		return None

	html_text = requests.get(URL, headers=headers).content
	soup = BeautifulSoup(html_text, 'lxml')

	try:
		body = soup.find('div', class_='mw-body-content mw-content-ltr')
		paragraphs = body.find_all('p')

		for paragraph in paragraphs:
			if paragraph.find('b') is not None:
				res = paragraph.text

				title = paragraph.find('b').text

				redundancy = []

				pronunciation = paragraph.find_all('span', class_='rt-commentedText nowrap')
				for x in pronunciation:
					redundancy.append(x.text)

				reference = paragraph.find_all('sup', class_='reference')
				for x in reference:
					redundancy.append(x.text)

				for x in redundancy:
					res = res.replace(x, '')

				res = AITasks.Get_First_Sentence(res)
				return res

		return None
	except:
		return None

def Wolframalpha(query):
	try:
		with open('Resources/API key/wolfram alpha.pck', 'rb') as file:
			app_id = pickle.load(file)
		client = wolframalpha.Client(app_id)
		res = client.query(query)
		answer = next(res.results).text

		return answer
	except:
		return None

def Song_Lyrics(song_name):
	with open('Resources/API key/genius.pck', 'rb') as file:
		token = pickle.load(file)

	genius = Genius(token)
	song = genius.search_song(song_name)
	if song is None:
		return None
	return song.lyrics

def Get_Antonyms(word):
	for c in word:
		if c < 'a' or 'z' < c:
			if c != '-' and c != ' ':
				return None
	word = word.replace(' ', '%20')
	html_text = requests.get('https://www.thesaurus.com/browse/' + word, headers=headers).content
	soup = BeautifulSoup(html_text, 'lxml')

	try:
		antonym_box = soup.find('div', {'id' : 'antonyms'})
		antonym_list = antonym_box.find_all('li')
		random.shuffle(antonym_list)

		return [word.text.strip() for word in antonym_list[:min(len(antonym_list), 5)]]
	except:
		return None