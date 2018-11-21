# Natural Language Processing

## Requirement

- [Dialogflow](https://dialogflow-python-client-v2.readthedocs.io/en/latest/)
- [slacker](https://github.com/os/slacker)

## Classification of the intention

We use [Dialogflow](https://dialogflow.com/) for classifying intention. Dialogflow is machine learning based NLP platform. We trained some sentences for each intent so Dialogflow classify which intent user input is based on their training data.

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

    
## Sequence diagram(NLP)

![nlp_sequence_diagram](https://github.com/UCNLP/conflict-prediction/blob/py3_server/images/nlp_sequence_diagram.png)
