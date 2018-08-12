# Punctuator2

## introduce

- A bidirectional recurrent neural network model with attention mechanism for restoring missing inter-word punctuation in unsegmented text.
- Home repository : https://github.com/ottokart/punctuator2
- Trained model : [INTERSPEECH-T-BRNN.pcl](https://drive.google.com/drive/folders/0B7BsN5f2F1fZQnFsbzJ3TWxxMms?usp=sharing)

The model can be trained in two stages (second stage is optional):

1. First stage is trained on punctuation annotated text. Here the model learns to restore puncutation based on textual features only.
2. Optional second stage can be trained on punctuation and pause annotated text. In this stage the model learns to combine pause durations with textual features and adapts to the target domain. If pauses are omitted then only adaptation is performed. Second stage with pause durations can be used for example for restoring punctuation in automatic speech recognition system output.

## Contribution to our system

Chatting usually ommit pucntuation, so we use this auto-punctuation open source project.