*The GUI is inspired by: https://github.com/roshan9419/PersonalAssistantChatbot

### Features of Smart Bot: 
  + Do basic conversations (greetings, jokes,...)
  + Play Youtube videos
  + Play music
  + Trending songs
  + Song lyrics
  + Covid tracking
  + Look up in dictionary (Meaning, Synonym, Antonym)
  + Tell date and time
  + Set timer
  + Tell weather
  + Do translation
  + Open websites
  + Check Internet status
  + Get OS info (CPU, RAM, Battery)
  + Maths (calculations, calculus, conversion,...)
  + Show user info (ip address, isp, location)
  + OS control (change volume, type key, shutdown, cleanup, open and close programs, screen capture)
  + Web search (Wikipedia, Wolframalpha, ...)

### Minor background features:
  + Automatically adjust volume

### Modules Requirements and Installation: 
  + pip install beautifulsoup4
  + pip install comtypes
  + pip install geopy
  + pip install googletrans==3.1.0a0
  + pip install Levenshtein
  + pip install lxml
  + pip install lyricsgenius
  + pip install nltk
  + pip install numpy
  + pip install Pillow
  + pip install psutil
  + pip install py-cpuinfo
  + pip install pyaudio
  + pip install pycaw
  + pip install pygame
  + pip install pyjokes
  + pip install pynput
  + pip install python-vlc
  + pip install pythonping
  + pip install pyttsx3
  + pip install pytz
  + pip install requests
  + pip install scrapy
  + pip install SpeechRecognition
  + pip install tensorflow
  + pip install timezonefinder
  + pip install tinytag
  + pip install watchdog
  + pip install winshell
  + pip install wmi
  + pip install wolframalpha
  + pip install youtube_search

### Reminder:
  Replace **URL** in **recognize_google** (init file in speechrecognition) with this code:

  url = "http://www.google.com/speech-api/v2/recognize?{}".format(urlencode({
            "client": "chromium",
            "lang": language,
            "key": key,
            "pFilter": 0
        }))

### Hidden Imports:
  + pynput.keyboard._win32
  + pynput.mouse._win32 
  + pyttsx3.drivers.sapi5

### Pyinstaller Command:
  pyinstaller -w --icon=Icon.ico --hidden-import "pynput.keyboard._win32" --hidden-import "pynput.mouse._win32" --hidden-import "pyttsx3.drivers.sapi5" smartbot.py
