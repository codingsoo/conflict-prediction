# coding: utf-8

from __future__ import division
from nltk.tokenize import word_tokenize
import nltk.tokenize.punkt
# from nltk.tokenize import sent_tokenize

import models

import theano
import sys
import re
import json
import theano.tensor as T
import numpy as np

# set model path (model file)
MODEL_FILE = "model/Demo-Europarl-EN.pcl"
END = "</S>"
UNK = "<UNK>"
SPACE = "_SPACE"
EOS_TOKENS = {".PERIOD", "?QUESTIONMARK", "!EXCLAMATIONMARK"}
MAX_SEQUENCE_LEN = 50

numbers = re.compile(r'\d')
is_number = lambda x: len(numbers.sub('', x)) / len(x) < 0.6

def to_array(arr, dtype=np.int32):
	return np.array([arr], dtype=dtype).T

def convert_punctuation_to_readable(punct_token):
    	if punct_token == SPACE:
        	return ' '
   	elif punct_token.startswith('-'):
        	return ' ' + punct_token[0] + ' '
    	else:
        	return punct_token[0] + ' '

def punctuate(predict, word_vocabulary, punctuation_vocabulary, reverse_punctuation_vocabulary, reverse_word_vocabulary, words, show_unk):
    	paragraph = ""

    	if len(words) == 0:
        	sys.exit("Input text from stdin missing.")

    	if words[-1] != END:
        	words += [END]

    	i = 0

    	while True:

        	subsequence = words[i:i+MAX_SEQUENCE_LEN]

        	if len(subsequence) == 0:
        		break

        	converted_subsequence = [word_vocabulary.get(
                	"<NUM>" if is_number(w) else w.lower(),
                	word_vocabulary[UNK])
           		for w in subsequence]

		if show_unk:
           		subsequence = [reverse_word_vocabulary[w] for w in converted_subsequence]

		y = predict(to_array(converted_subsequence))

    		paragraph += subsequence[0].title()

    		last_eos_idx = 0
     		punctuations = []
     		for y_t in y:
           		p_i = np.argmax(y_t.flatten())
           		punctuation = reverse_punctuation_vocabulary[p_i]

           		punctuations.append(punctuation)

           		if punctuation in EOS_TOKENS:
           			last_eos_idx = len(punctuations)

     		if subsequence[-1] == END:
           		step = len(subsequence) - 1
     		elif last_eos_idx != 0:
           		step = last_eos_idx
     		else:
           		step = len(subsequence) - 1

     		for j in range(step):
           		current_punctuation = punctuations[j]
           		paragraph += convert_punctuation_to_readable(current_punctuation)
           		if j < step - 1:
                		if current_punctuation in EOS_TOKENS:
                			paragraph += subsequence[j + 1].title()
                		else:
                			paragraph += subsequence[j + 1]

     		if subsequence[-1] == END:
           		break

     		i += step

     	return paragraph


if __name__ == "__main__":
	paragraph = ""
	sentence_list = []
	show_unk = False

 	x = T.imatrix('x')

    	print "Loading model parameters..."
   	net, _ = models.load(MODEL_FILE, 1, x)

   	print "Building model..."
    	predict = theano.function(inputs=[x], outputs=net.y)
    	word_vocabulary = net.x_vocabulary
    	punctuation_vocabulary = net.y_vocabulary
    	reverse_word_vocabulary = {v:k for k,v in net.x_vocabulary.items()}
    	reverse_punctuation_vocabulary = {v:k for k,v in net.y_vocabulary.items()}

    	human_readable_punctuation_vocabulary = [p[0] for p in punctuation_vocabulary if p != SPACE]
    	tokenizer = word_tokenize
    	untokenizer = lambda text: text.replace(" '", "'").replace(" n't", "n't").replace("can not", "cannot")

    	text = raw_input("\nTEXT: ").decode('utf-8')

    	words = [w for w in untokenizer(' '.join(tokenizer(text))).split()
    		if w not in punctuation_vocabulary and w not in human_readable_punctuation_vocabulary]
    
    	paragraph = punctuate(predict, word_vocabulary, punctuation_vocabulary, reverse_punctuation_vocabulary, reverse_word_vocabulary, words, show_unk)

    	tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
    	for sentence in tokenizer.tokenize(paragraph):
    		sentence_list.append(sentence)

	with open('sentences.json' , 'w') as f:
		f.write(json.dumps(sentence_list, indent=4))    	

    	# for sentence in sent_tokenize(paragraph):
     #    	sentence_list.append(sentence)

    	# with open('sentences.json' , 'w') as f:
     #    	f.write(json.dumps(sentence_list, indent=4))