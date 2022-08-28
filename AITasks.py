import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from numpy import array
import pickle
import os
from global_function import training_ignore_letters, training_epochs, training_batch_size

def Training_Required():
    res = os.path.exists('Resources/training/all tasks/model.h5')
    res &= os.path.exists('Resources/training/all tasks/classes.pck')
    res &= os.path.exists('Resources/training/all tasks/words.pck')
    return not res

def clean_up_sentence(sentence):
    for letter in training_ignore_letters:
        sentence = sentence.replace(letter, '')
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    bag = []
    sentence_words = clean_up_sentence(sentence)

    word_count = {}
    for word in sentence_words:
        try:
            word_count[word] += 1
        except:
            word_count[word] = 1

    for word in words:
        try:
            bag.append(word_count[word])
        except:
            bag.append(0)
    return array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    result = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    result.sort(key=lambda x : x[1], reverse=True)
    if result:
        return classes[result[0][0]]

    return None

def Bot_Training():
    import training
    training.run_code('Resources/training/all tasks', training_epochs, training_batch_size, 512, 256)

global lemmatizer, words, classes, model

def Initialize():
    global lemmatizer, words, classes, model
    lemmatizer = WordNetLemmatizer()

    words = pickle.load(open('Resources/training/all tasks/words.pck', 'rb'))
    classes = pickle.load(open('Resources/training/all tasks/classes.pck', 'rb'))
    model = load_model('Resources/training/all tasks/model.h5')

    predict_class('hello')

def Get_First_Sentence(paragraph):
    return nltk.sent_tokenize(paragraph)[0].strip()

class Task_Confirmation:
    def __init__(self):
        if not (os.path.exists('Resources/training/task confirmation/model.h5') and os.path.exists('Resources/training/task confirmation/classes.pck') and os.path.exists('Resources/training/task confirmation/words.pck')):
            import training
            training.run_code('Resources/training/task confirmation', 50, 5, 128, 64)

        self.words = pickle.load(open('Resources/training/task confirmation/words.pck', 'rb'))
        self.classes = pickle.load(open('Resources/training/task confirmation/classes.pck', 'rb'))
        self.model = load_model('Resources/training/task confirmation/model.h5')

    def bag_of_words(self, sentence):
        bag = []
        sentence_words = clean_up_sentence(sentence)

        word_count = {}
        for word in sentence_words:
            try:
                word_count[word] += 1
            except:
                word_count[word] = 1

        for word in self.words:
            try:
                bag.append(word_count[word])
            except:
                bag.append(0)
        return array(bag)

    def Is_Approve(self, sentence):
        bow = self.bag_of_words(sentence)
        res = self.model.predict(array([bow]))[0]
        ERROR_THRESHOLD = 0.25
        result = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        result.sort(key=lambda x: x[1], reverse=True)
        if result:
            return self.classes[result[0][0]] == 'approve'
        else:
            return False

task_confirmation = Task_Confirmation()