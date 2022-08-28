import random
import pickle
from numpy import array
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
from global_function import training_ignore_letters
import os
import json

def run_code(source_path, training_epochs, training_batch_size, layer1_units, layer2_units):
    lemmatizer = WordNetLemmatizer()

    direction = json.loads(open(os.path.join(source_path, 'direction.json')).read())
    words = []
    classes = []
    documents = []

    for intent in direction['intents']:
        for pattern in intent['patterns']:
            for letter in training_ignore_letters:
                pattern = pattern.replace(letter, '')
            word_list = word_tokenize(pattern.lower())
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = [lemmatizer.lemmatize(word.lower()) for word in words]
    words = sorted(set(words))

    classes = sorted(set(classes))

    pickle.dump(words, open(os.path.join(source_path, 'words.pck'), 'wb'))
    pickle.dump(classes, open(os.path.join(source_path, 'classes.pck'), 'wb'))

    training = []
    output_empty = [0] * len(classes)

    for document in documents:
        bag = []
        word_patterns = document[0]
        word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
        word_count = {}
        for word in word_patterns:
            try:
                word_count[word] += 1
            except:
                word_count[word] = 1

        for word in words:
            try:
                bag.append(word_count[word])
            except:
                bag.append(0)

        output_row = list(output_empty)
        output_row[classes.index(document[1])] = 1
        training.append([bag, output_row])

    random.shuffle(training)
    training = array(training, dtype=object)

    train_x = list(training[:, 0])
    train_y = list(training[:, 1])

    model = Sequential()
    model.add(Dense(layer1_units, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(layer2_units, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(train_y[0]), activation='softmax'))

    sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    hist = model.fit(array(train_x), array(train_y), epochs=training_epochs, batch_size=training_batch_size, verbose=1)
    model.save(os.path.join(source_path, 'model.h5'), hist)
