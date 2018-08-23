# Conflict Detect Chatbot - Sayme

## Purpose of Project

We aim to improve developer's collaboration environment. We develop a chatbot which can detect python code conflicts automatically in real time and send the conflict information to people who are in conflict through slack.

## Installation

## Demo Vedio

## Bot's functional features

1.	Detect direct conflict : Sayme can detect direct conflict and three types of severity.
2.	Detect indirect conflict : Sayme can detect indirect conflict.
3.	Ignore file : It functions like gitignore. A user can customize his/her ignore files.
4.	Lock file : A user can lock his/her files. If other users try to modify the locked file, Sayme gives them a warning.
5.	Check code history : A user can ask who wrote certain code lines.
6.	Ignore alarm : A user can ignore direct alarm and indirect alarm.
7.	Check conflict possibility : Before a user starts to work, the user can check whether editing certain file generates conflict or not.
8.	Check working status : A user can ask about other user's working status
9.	Give channel message : A user can let chatbot give a message to channel.
10.	Give user message : A user can let chatbot give a message to other users.
11.	Give recommendation : A user can ask chatbot to recommend how to deal with the conflict.
12.	Recognize user : Chatbot knows when last time a user connected is, so bot can greet the user with time information. ex) It's been a week~!
13.	Greet user : Chatbot can greet users.
14.	Complimentary close : Chatbot can say good bye.

## Bot's non functional features

1. Chatbot immediately detects the conflict and after first warning, twice rewarning per 30 min.
2. If user keeps ignoring conflict message, chatbot give message to the channel.
3. Every time a conflict is solved or solving, the chatbot sends a message immediately.
4. The authentication is needed only one time.
5. If user keeps ignoring conflict message, chatbot give message to the channel.
6. Chatbot should detect user data every 5 minutes. Crawling repository should be done every 4 hours.
7. Chatbot should respond to user within 5 seceonds.

## Algorithm

- NLP : You can see the algorithm in [chat_bot_server_dir folder](https://github.com/UCNLP/conflict-detector/tree/py3_server/chat_bot_server_dir)
- Conflict detection : You can see the algorithm in [server_dir folder](https://github.com/UCNLP/conflict-detector/tree/py3_server/server_dir)

## Future Work

- Research about the ways of chatbot that human likes(What behaviors should chatbot have?).
- Adopt voice recognition technology : Chatbot can recognize the voice input from a user, and chatbot can respond to the voice input with its own voice.
