import requests
from googletrans import Translator, LANGUAGES
import pickle
import webScraping

with open('Resources/API key/oxford.pck', 'rb') as file:
    api_key = pickle.load(file)
    app_id = api_key['app id']
    app_key = api_key['app key']
url_base = 'https://od-api.oxforddictionaries.com/api/v2/'
language_code = 'en-us'

def lemmatize(word):
    endpoint = 'lemmas'
    url = url_base + endpoint + '/' + language_code + '/' + word
    res = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
    if format(res.status_code) != '404':
        return res.json()['results'][0]['lexicalEntries'][0]['inflectionOf'][0]['id']
    else:
        return ''

def Definition(word):
    word = lemmatize(word)
    if word != '':
        endpoint = 'entries'
        url = url_base + endpoint + '/' + language_code + '/' + word
        res = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
        try:
            return res.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]
        except:
            return None
    else:
        return None

def Synonyms(word):
    word = lemmatize(word)
    if word != '':
        endpoint = 'entries'
        url = url_base + endpoint + '/' + language_code + '/' + word
        res = requests.get(url, headers={"app_id": app_id, "app_key": app_key})
        try:
            list_of_synonyms = res.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['synonyms']
            result_list = []
            for i in range(min(5, len(list_of_synonyms))):
                result_list.append(list_of_synonyms[i]['text'])
            return result_list
        except:
            return None
    else:
        return None

def Antonyms(word):
    if word.find(' ') != -1:
        return None

    word = lemmatize(word)

    return webScraping.Get_Antonyms(word)

def lang_translate(text,language):
    if language in LANGUAGES.values():
        translator = Translator()
        result = translator.translate(text, src='en', dest=language)
        return result
    else:
        return None