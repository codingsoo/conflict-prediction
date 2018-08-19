import spacy

# https://spacy.io/usage/vectors-similarity

nlp = spacy.load('C:\\Users\\learn\\PycharmProjects\\conflict-detector2\\venv\\Lib\\site-packages\\en_core_web_lg\\en_core_web_lg-2.0.0')
doc1 = nlp("Where is the conflict?")
doc2 = nlp("hi")
doc3 = nlp("give me the conflict location")
doc5 = nlp("Where is the conflict?")
doc6 = nlp("tell me the conflict location")
doc7 = nlp("Where is the conflict?")
doc8 = nlp("tell me the conflict location")
doc9 = nlp("ignore that file")
doc10 = nlp("can you tell me user2's working status?")
print(doc1.similarity(doc2))
print(doc1.similarity(doc3))
print(doc5.similarity(doc6))
print(doc7.similarity(doc8))
print(doc8.similarity(doc9))
print(doc8.similarity(doc10))


# for token in tokens:
#     print(token.text, token.has_vector, token.vector_norm, token.is_oov)