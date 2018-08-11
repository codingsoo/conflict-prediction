# coding=utf-8
# for def lemm_word()
import nltk
# to write and read the sentences
import json

# for def wsd_synm()
from nltk.wsd import lesk

# for def lemm_word()
nltk.download('wordnet')

# lemmatize words
def lemm_word():
    lemmatizer = nltk.WordNetLemmatizer()
    # get the sentences from temp.json
    with open("temp.json", 'r') as f:
        sntcs = json.load(f)
        # the set of sentences before finding synonyms
        bef_wsd = []
        # for each sentence, find lemmatized form and make a list [verb in the sentence, infinitive verb, objective, sentence]
        for sntc in sntcs:
            org_verb_sntc = []
            org_verb = lemmatizer.lemmatize(sntc[0], pos="v")
            org_verb_sntc.append(sntc[0])
            org_verb_sntc.append(org_verb)
            org_verb_sntc.append(sntc[1])
            org_verb_sntc.append(sntc[2])
            bef_wsd.append(org_verb_sntc)
    # json list [verb in the sentence, infinitive verb, object, sentence]
    with open("fin_lemm.json", 'w') as f:
        json.dump(bef_wsd, f, ensure_ascii=False)

def wsd_synm():
    with open("fin_lemm.json", 'r') as f:
        sntcs = json.load(f)
    with open("response.json", 'r') as r:
        respons = json.load(r)


    af_wsd = []

    #verb_dict
    verb_dict = dict()
    for sntc in sntcs:
        # Each sentence has a synonym word [[original verb, objective, sentecne],[synonym verb, original verb, sentence]...]
        word_syn_set = []

         # Initialize each verb dict
        verb_dict[sntc[1]] = dict()
        # Create { verb : { obj : chat_response, obj : chat_response } ... }
        verb_dict[sntc[1]][sntc[2]] = respons[sntc[1]][sntc[2]]

        #If verb contains "not" then when finding synonym, only original verb without "not" should be found.
        if (sntc[0].split("_")[0] != "not"):
            # a list of synonym verbs
            syn_set = lesk(sntc[2].split(), sntc[0], 'v').lemma_names()
            # get rid of lesk form
            sntc[0] = lesk(sntc[2].split(), sntc[0], 'v').lemmas()[0].name()
        else:
            # a list of synonym verbs
            syn_set = lesk(sntc[2].split(), sntc[0].split("_")[1], 'v').lemma_names()
            # get rid of lesk form
            sntc[0] = lesk(sntc[2].split(), sntc[0].split("_")[1], 'v').lemmas()[0].name()



        # make a list in this form [synonym verb, original verb, sentence] for each synonym verb
        for syn in syn_set:
            #if synonym length is 2 except the word "not" then ignore it. )
            if (len(syn.split("_")) == 3 or (syn.split("_")[0] != "not" and len(syn.split("_")) == 2)):
                continue
            else :
                if str(sntc[1]) != str(syn):
                    #If verb contains "not" then synonyms also should contains "not"
                    if (sntc[1].split("_")[0] == "not"):
                        syn = "not_" + syn
                    verb_dict[syn] = dict()
                    verb_dict[syn][sntc[2]] = respons[sntc[1]][sntc[2]]
                    syn_verb = [str(syn), str(sntc[2]), str(sntc[3])]
                    word_syn_set.append(syn_verb)
                else:
                    continue
        del sntc[0]
        word_syn_set.insert(0, sntc)
        af_wsd.append(word_syn_set)

    with open("synonym.json", "w") as f:
        f.write(json.dumps(af_wsd))
    with open("responds2.json", "w") as temp_file:
        temp_file.write(json.dumps(verb_dict))
