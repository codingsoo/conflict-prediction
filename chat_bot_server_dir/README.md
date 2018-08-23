# Natural Language Processing

## Requirement

- [nltk](https://www.nltk.org/)(punkt, wordnet)
- [stanfordCoreNLP](https://stanfordnlp.github.io/CoreNLP/) and [python wrapper](https://github.com/Lynten/stanford-corenlp)
- [spacy](https://spacy.io/)
- [slacker](https://github.com/os/slacker)

## Preprocess of sentence

To improve the quality of Natural Language Processing, we simplify the sentence. For example, we omit "please" and "I think" from the sentence, because they are not necessary in understanding the sentence. We also replace "have to" and "don't have to" with "should" and "should not". When we detect if the sentence is suggestion or not, we use "MD" part of speech tag. The two words, "have to" and "dont't have to", have same meaning with "should" and "should not", however, they are not regarded as "MD" part of speech tag.

## Classification of the sentence

We have five categories to classify the input sentence; question, command, suggestion, desire and conversation. We classify the input sentence by using following rules.

- Question: a sentence with "SBARQ" or "SQ" parse component.
- Command: a sentence starting with "VB" part of speech tag
- Suggestion: a sentence with "MD" part of speech tag
- Desire: a sentence with a certain verb which contains a meaning of desire
- Conversation: a sentence which doesn't correspond to above

## Classification of the intention

We use [spacy vector similarity algorithm](https://spacy.io/usage/vectors-similarity) for classifying intention. This algorithm is affected by sentence structure, but we devide the sentence structure(Classification of the sentence) before use it, so we could enhance the accuracy.

## Extraction of attention words(Slot filling)

Based on the classification of the intention, we extract information from the user to provide the output which the user is looking for. After the extraction, we fill our slot, and we call another function to respond to the user.

- Scenarios for slot filling

  -  Scenario 1 (All slots are filled)  
User : Can you ignore hello.py?

      | Sentence | Can | you | ignore  | hello.py  |
      |:----------:|:---:|:------:|:--------:|:--------:|
      | Slot     | O | O    | Slot1 | Slot2  |

  - Scenario 2 (There is no Slot2)  
User : Can you ignore this file?

      | Sentence | Can | you | ignore  | this | file |
      |:----------:|:---:|:------:|:-------:|:---------:|:---------:|
      | Slot     | O | O    | Slot1 | O       | O |

      If any slot is not filled, Sayme(bot) fill slot from our recent history data.


## Sequence diagram(NLP)

![nlp_sequence_diagram](https://github.com/UCNLP/conflict-detector/blob/py3_server/images/nlp_sequence_diagram.jpg)
