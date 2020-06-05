# Conflict Detection Chatbot - Sayme

## Purpose of Project

We aim to improve developer's collaboration environment. We develop a chatbot which can detect python code conflicts automatically in real time and send the conflict information to people who are in conflict through slack.

## Usage

#### Using conflict_test project

   1. Clone [conflict_test](https://github.com/codingsoo/conflict_test.git) repository
        ```
        $ git clone this repo
        ```
   2. Set IP and PORT in *conflict_test/client_setting.ini*
        ```
           [CONNECTION]
            IP = 35.185.32.125
            PORT = 5009
            
           [GRAPH_CONNECTION]
            IP = 35.185.32.125
            PORT = 5010
        ```
   3. Run *client.py*
        ```
        $ python3 ./client.py
        ```
#### Using your own project

   1. Download [client.py](https://github.com/codingsoo/conflict_test/blob/master/client.py) and [client_setting.ini](https://github.com/codingsoo/conflict_test/blob/master/client_settings.ini) in your own project
        ```
        $ git clone this repo
        ``` 
   2. Set IP and PORT in *conflict_test/client_setting.ini*
        ```
           [CONNECTION]
            IP = 35.185.32.125
            PORT = 5009
            
           [GRAPH_CONNECTION]
            IP = 35.185.32.125
            PORT = 5010
        ```
   3. Run *client.py*
        ```
        $ python3 ./client.py
        ```

## Demo Video
https://www.youtube.com/embed/FO2RW24wHFQ<br>

## Bot's Main Features

1.	Detect direct conflict : Chatbot can detect a direct conflict and three types of severity.
2.	Detect indirect conflict : Chatbot can detect a indirect conflict.

## Bot's Functional Features

1.	Ignore file : It functions like gitignore. A user can customize his/her ignore files.
2.	Lock file : A user can lock his/her files. If other users try to modify the locked file, Sayme gives them a warning.
3.	Check code history : A user can ask who wrote certain code lines.
4.	Ignore alarm : A user can ignore direct alarm and indirect alarm.
5.	Check conflict possibility : Before a user starts to work, the user can check whether editing certain file generates a conflict or not.
6.	Check working status : A user can ask about other user's working status.(Working Project, Logic, Line, Amount)
7.	Give user message : A user can let chatbot give a message to other users.
8.	Give recommendation : A user can ask chatbot to recommend how to deal with the conflict.
9.  Check ignored file : A user can ask chatbot about which files are being ignored by certain user or ignored in the project.
10. Check who lock file : A user can ask chatbot about who lock certain file.
11. Check severity : A user can ask chatbot about how severe conflict is in certain file. 
12. Recognize user : Chatbot knows when last time a user connected is, so bot can greet the user with time information. ex) It's been a week~!
13.	Greet user : Chatbot can greet users.
14.	Complimentary close : Chatbot can say good bye.

## Bot's Non Functional Features

1. Chatbot immediately detects the conflict and warns users who engage in the conflict. If the conflict is not resolved even after 30 minutes, it warns again.
2. Every time a conflict is resolved, chatbot sends a conflict resolved message one time.
3. The authentication is needed only one time.
4. Chatbot should detect user data every 5 minutes. Crawling repository should be done every 4 hours. 
5. Chatbot should respond to user within 3 minutes.

## Algorithm

- NLP : You can see the algorithm in [chat_bot_server_dir folder](https://github.com/codingsoo/conflict-prediction/edit/py3_server/legacy/tree/py3_server/chat_bot_server_dir)
- Conflict detection : You can see the algorithm in [server_dir folder](https://github.com/codingsoo/conflict-prediction/edit/py3_server/legacy/tree/py3_server/server_dir)

## Future Work

- Research about the ways of chatbot that human likes(What behaviors should chatbot have?).
- Adopt voice recognition technology : Chatbot can recognize the voice input from a user, and chatbot can respond to the voice input with its own voice.
- Prediction the probability of conflicts that can occur.
