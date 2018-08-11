nlp
===

Punctuator
----------

### Requirements

-	Python 2.7
-	punctuator2 [https://github.com/ottokart/punctuator2\]
-	punkt [https://www.nltk.org/_modules/nltk/tokenize/punkt.html\]

### Usage

1.	Pretrained models can be downloaded [here](https://drive.google.com/drive/folders/0B7BsN5f2F1fZQnFsbzJ3TWxxMms?usp=sharing) (model/download here)
2.	python punctuator.py
3.	TEXT : Enter the text that you want to puntuate.

### Results

sentense.json

POS tagging, Dependency tagging
-------------------------------

### Requirements

-	Python 2.7
-	stanford-parser-full-2017-06-09/stanford-parser.jar
-	stanford-parser-full-2017-06-09/stanford-parser-3.8.0-models.jar

### Usage

1.	Stanford-parser can be downloaded [here](https://nlp.stanford.edu/software/lex-parser.shtml)
2.	python tagging.py
3.	Input : chat_text.text
4.	Output : \[[verb, object, subject, original sentence],[verb, object, subject, original sentence]...]

Lemmatization, Synonym Finder and SlotFiller
--------------------------------------------

### Requirement

-	nltk [https://www.nltk.org/install.html\]

### Usage

1.	Lemmatization needs sentences which include the extracted important words through punctuator, POS tagging, and dependencies.
2.	def lemm_word() finds lemmatized form of words and makes a list.
3.	def lemm_word() dumps the result to "fin_lemm.json"
4.	def wsd_synm() gets sentences from "fin_lemm.json" and find sysnonyms.
5.	Based on "response.json" which contains the list of responses, def wsd_synm() creates new dictionary and keys are important words and values are responses.
6.	def slotfiller(verb, object) compares the input of verb and object and compares them with keys in "response.json"
7.	def slotfiller(verb, object) returns the response
