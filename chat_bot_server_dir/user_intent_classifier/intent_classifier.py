from stanfordcorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP('http://localhost', port=9000)

def is_command(pos_tag_list):
    for pos_tag in pos_tag_list:
        if pos_tag[1] == "RB" or pos_tag[1] == "MD":
            continue
        elif pos_tag[1] == "VB":
            return True
        else:
            return False

def is_desire(pos_tag_list):
    desire_list = ["want", "hope", "wish", "desire"]
    for pos_tag in pos_tag_list:
        print(pos_tag[0],pos_tag[1])
        if pos_tag[1] == "PRP" or pos_tag[1] == "NNP" or pos_tag[1] == "RB":
            pass
        elif pos_tag[0] in desire_list :
            return True
        else:
            return False

def is_suggestion(pos_tag_list):
    suggestion_noun_list = ["Sayme", "sayme", "You", "you"]
    for pos_tag in pos_tag_list:
        if pos_tag[0] in suggestion_noun_list:
            continue
        elif pos_tag[1] == "MD" :
            return True
        else:
            return False

def is_question(parse_list):
    if "SBARQ" in parse_list or "SQ" in parse_list:
        return True

    return False

def require_something_sentence(sentence):
    sentence = sentence.replace("please ", '')
    sentence = sentence.replace("Please ", '')
    pos_tag_list = nlp.pos_tag(sentence)
    parse_list = nlp.parse(sentence)

    if(is_command(pos_tag_list) or is_desire(pos_tag_list) or is_question(parse_list) or is_suggestion(pos_tag_list)):
        return True
    return False