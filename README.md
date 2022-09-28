*The GUI was inspired by: https://github.com/roshan9419/PersonalAssistantChatbot

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

### Reminder:
  Replace **URL** in **recognize_google** (init file in speechrecognition) with this code:

  url = "http://www.google.com/speech-api/v2/recognize?{}".format(urlencode({
            "client": "chromium",
            "lang": language,
            "key": key,
            "pFilter": 0
        }))

### Pyinstaller Command:
  pyinstaller -w --icon=Icon.ico --hidden-import "pynput.keyboard._win32" --hidden-import "pynput.mouse._win32" --hidden-import "pyttsx3.drivers.sapi5" smartbot.py
