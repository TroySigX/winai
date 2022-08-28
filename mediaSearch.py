from global_function import data_exist, rindex
import pickle

def Filter_Redundancy(type, query, replace_space, replace_percentage, replace_apostrophe, replace_plus):
    with open('Resources/redundancy/media search redundancy filter.pck', 'rb') as file:
        media_search_redundancy = pickle.load(file)
    for i in range(len(media_search_redundancy)):
        media_search_redundancy[i][0] = media_search_redundancy[i][0].replace('__social_media_name__', type)
    media_search_redundancy.sort(key=lambda x : len(x[0]), reverse=True)

    command = ''
    for redundancy in media_search_redundancy:
        if data_exist([redundancy[0]], query, 2):
            question_word = redundancy[0].split()
            command_word = query.split()
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
                query = command
                break

    if replace_percentage:
        query = query.replace('%', '%25')
    if replace_apostrophe:
        query = query.replace("'", '%27')
    if replace_plus:
        query = query.replace('+', '%2B')
    query = query.replace(' ', replace_space)
    return query

def Get_Url(type, query, media):
    url = ''
    replace_space = ''
    replace_percentage = False
    replace_apostrophe = False
    replace_plus = False
    for x in media:
        if type == x['tag']:
            url = x['url']
            replace_space = x['replace space']
            replace_percentage = ['replace %']
            replace_apostrophe = x["replace '"]
            replace_plus = x['replace plus']
            break
    url += Filter_Redundancy(type, query, replace_space, replace_percentage, replace_apostrophe, replace_plus)
    return url

