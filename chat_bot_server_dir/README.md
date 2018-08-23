Natural Language Processing
---------------------------

### Requirement

-	nltk
-	stanfordCoreNLP
-	spacy

### Preprocessing of the sentence

To improve the quality of Natural Language Processing, we simplify the sentence. We omit "please" and "I think" from the sentence, because they are not necessary in understanding the sentence. We also replace "have to" and "don't have to" with "should" and "should not". When we detect if the sentence is suggestion or not, we use "MD" part of speech tag. The two words, "have to" and "dont't have to", have same meaning with "should" and "should not", however, they are not regarded as "MD" part of speech tag.

### Classification of the sentence

We have five categories to classify the input sentence; question, command, suggestion, desire and conversation. We classify the input sentence by using following rules.

-	question: a sentence with "SBARQ" or "SQ" parse component.
-	command: a sentence starting with "VB" part of speech tag
-	suggestion: a sentence with "MD" part of speech tag
-	desire: a sentence with a certain verb which contains a meaning of desire
-	conversation: a sentence which doesn't correspond to above

### Classification of the intention

There are nine functions that chatbot can provide to users. We have four lists of categories (question, command, suggestion, and desire) and each consists of nine sentences which represent the function. We understand the category of the input sentence after classifying the sentence. Therefore, in this phrase, we go over the nine sentences of the certain category and compare the similarity with the input sentence.

### Extraction of attention words

Based on the classification of the intention, we extract information from the user to provide the output which the user is looking for. After the extraction, we call another function to respond to the user.

### Sequence diagram(NLP)

<div align="center">
<img src="images/uci_seq2.JPG" width="100%" height="100%">
</div>
