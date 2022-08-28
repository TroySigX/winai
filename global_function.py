import Levenshtein
import json
import requests
import speech_recognition as sr
#from difflib import SequenceMatcher

direction = json.loads(open('Resources/training/all tasks/direction.json').read())
training_batch_size = 200
training_epochs = 500
training_ignore_letters = ['?', ',', '!', '.', '"', ':', ';', '{', '}', '[', ']', '(', ')']

voiceRecognizer = sr.Recognizer()
voiceRecognizer.energy_threshold = 3500

def sr_dynamic_energy_on():
    voiceRecognizer.dynamic_energy_threshold = True

def sr_dynamic_energy_off():
    voiceRecognizer.dynamic_energy_threshold = False

def remove_accents(input_str):
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s.lower()

def refine_sentence(sentence):
    words = sentence.split()
    return remove_accents(' '.join(words))

#search level decreases, strictness increases
def data_exist(terms, command, search_level = 1):
    if search_level == 0:
        for term in terms:
            if term == command:
                return True
        return False

    command_word = command.split()
    #check if there is term in terms such that term is a segment in command_word
    if search_level == 1:
        for term in terms:
            if term == '':
                return True
            term_word = term.split()
            for i in range(len(term_word) - 1, len(command_word)):
                ok = True
                for j in range(len(term_word)):
                    if term_word[j] != command_word[i - len(term_word) + 1 + j]:
                        ok = False
                        break
                if ok:
                    return True
        return False

    #check if there is term in terms such that term is a subsequence in command_word (not neccessarily continuous)
    if search_level == 2:
        for term in terms:
            if term == '':
                return True
            term_word = term.split()
            pos = 0
            for x in command_word:
                if x == term_word[pos]:
                    pos += 1
                    if pos == len(term_word):
                        return True
        return False

    #check if there is term in terms such that term is in command
    if search_level == 3:
        for term in terms:
            if term in command:
                return True
        return False

    #check prefix of command_word (0 -> len(term_word) - 1), term_word[i] is a prefix of command_word[i]
    if search_level == 4:
        for term in terms:
            term_word = term.split()
            if len(term_word) != len(command_word):
                continue
            ok = True
            for i in range(len(term_word)):
                if len(term_word[i]) > len(command_word[i]):
                    ok = False
                    break
                if command_word[i][:len(term_word[i])] != term_word[i]:
                    ok = False
                    break
            if ok:
                return True
        return False

    #similar to search level 4, doesn't need to be prefix of command_word, but have to be continuous (segment)
    if search_level == 5:
        for term in terms:
            if term == '':
                return True
            term_word = term.split()
            for i in range(len(term_word) - 1, len(command_word)):
                ok = True
                for j in range(len(term_word)):
                    if len(term_word[j]) > len(command_word[i - len(term_word) + 1 + j]):
                        ok = False
                        break

                    if term_word[j] != command_word[i - len(term_word) + 1 + j][:len(term_word[j])]:
                        ok = False
                        break
                if ok:
                    return True
        return False

    #similar to search level 5, but doesn't need to be continuous (subsequence)
    if search_level == 6:
        for term in terms:
            if term == '':
                return True
            term_word = term.split()
            pos = 0
            for x in command_word:
                if len(x) >= len(term_word[pos]):
                    if x[:len(term_word[pos])] == term_word[pos]:
                        pos += 1
                        if pos == len(term_word):
                            return True
        return False


def Convert_To_Int(n):
    num = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9
    }

    if n in num:
        return num[n]

    try:
        return int(n)
    except:
        return 0

def rindex(li, x):
    for i in reversed(range(len(li))):
        if li[i] == x:
            return i

def string_similarity(a, b):
    #return SequenceMatcher(None, a, b).ratio()
    return Levenshtein.ratio(a, b)

def Internet():
    try:
        requests.get('https://www.google.com/', timeout=1.5)
        return True
    except:
        return False

choosing_avatar = False

def Choosing_Avatar():
    return choosing_avatar

def Choosing_Avatar_Set_True():
    global choosing_avatar
    choosing_avatar = True

def Choosing_Avatar_Set_False():
    global choosing_avatar
    choosing_avatar = False

adjust_volume = True

def Adjust_Volume_On():
    global adjust_volume
    adjust_volume = True

def Adjust_Volume_Off():
    global adjust_volume
    adjust_volume = False

def Adjust_Volume_Allowed():
    global adjust_volume
    return adjust_volume

