# nlp

## Punctuator
### Requirements

- Python 2.7
- punctuator2 [https://github.com/ottokart/punctuator2]
- punkt [https://www.nltk.org/_modules/nltk/tokenize/punkt.html]

### Usage

1. Pretrained models can be downloaded [here](https://drive.google.com/drive/folders/0B7BsN5f2F1fZQnFsbzJ3TWxxMms?usp=sharing)
   (model/download here)
2. python punctuator.py
3. TEXT : Enter the text that you want to puntuate.

### Results

sentense.json

## POS tagging, Dependency tagging
### Requirements

- Python 2.7
- stanford-parser-full-2017-06-09/stanford-parser.jar
- stanford-parser-full-2017-06-09/stanford-parser-3.8.0-models.jar

### Usage

1. Stanford-parser can be downloaded [here](https://nlp.stanford.edu/software/lex-parser.shtml)
2. python tagging.py
3. Input : chat_text.text
4. Output : [[verb, object, subject, original sentence],[verb, object, subject, original sentence]...]
