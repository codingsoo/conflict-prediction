Conflict Detect Chatbot
=======================

Purpose
-------------------
The conflict detect chatbot is for early detection of potential conflicts which include direct conflicts and indirect conflicts.

In parallel works which are performed in personal workspaces, conflicts between developers may occur. There are two kinds of conflicts. One is a direct conflict and the other one is an indirect conflict. Direct conflicts may occur when multiple developers work on the same artifact. On the other hand, indirect conflicts may occur when changes of codes made by multiple developers are parallel and incompatible across artifacts. All these conflicts have the potential of being severe and serious.

This chatbot works for detecting the potential conflicts and lets developers know about them to not develop these conflicts.

System Architecture
---------------------
![system_structure](/img/system_structure.png)  

There are two parts in our system - Client and Server.
## Client
  * Slackbot
  * Git listener : It monitors repositories of developers every other minutes.

## Server

We have four parts in Server - Analysis of user's working status, Sentence boundary detection, Catch needs, and Give answers.

* Sentence boundary detection : The system tokenizes each sentence to analyze it. Most of sentence boundary detection projects are about articles, so we put "Chatting word translation" to convert chatting words to normal words and also put "[Punctuator](https://github.com/ottokart/punctuator2)" to add missing punctuations. We use [Punkt](https://www.nltk.org/_modules/nltk/tokenize/punkt.html) algorithm to detect the sentence boundary.

* Catch needs :The chatbot basically uses [Stanford parser](https://nlp.stanford.edu/software/lex-parser.html) and [nltk](https://www.nltk.org) to interpret sentences from a developer.
If the chatbot doesn’t understand the needs of a developer, it goes to RNN(Recurrent Neural Network) reaction. While it proceeds to the rule-based answer when it gets the needs of a developer.  
We find user's needs for four cases following :
  1. Making a question : SQ tag
  2. Imperative : start with verb or let
  3. Suggestion : put ‘you’ in front of the modal
  4. Desire expression : make desire verb list and check with synonym


* Give answers : The chatbot responds to a developer with RNN reaction or rule-based answer. RNN reaction is a human-like response, however, rule-based answer presents the exact answer for the claims of a developer.

* Analysis of user's working status : It gets which files developers are working on, and where the files are located at. Then, it compares and analyzes a working status of developers based on the information. After all, it is linked to rule-based answer component if conflict is detected.
