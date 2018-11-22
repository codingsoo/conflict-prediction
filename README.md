# Conflict Prediction Chatbot - Sayme

## Purpose of Project

We aim to improve developer's collaboration environment. We develop a chatbot which can detect and predict python code conflicts automatically in real time and send the conflict information to people who are in conflict through slack.

## Usage

#### Using conflict_test project

   1. Clone [conflict_test](https://github.com/UCNLP/conflict_test.git) repository
    
        ```$ git clone https://github.com/UCNLP/conflict_test.git``` 
           
   2. Set IP and PORT in *conflict_test/client_setting.ini*
        ```
           [CONNECTION]
            IP = 35.196.166.28
            PORT = 5009
            
           [GRAPH_CONNECTION]
            IP = 35.196.166.28
            PORT = 5010
        ```
    
   3. Run *client.py*
    
        ```$ python3 ./client.py```

#### Using your own project

   1. Download [client.py](https://github.com/UCNLP/conflict_test/blob/master/client.py) and [client_setting.ini](https://github.com/UCNLP/conflict_test/blob/master/client_settings.ini) in your own project
    
        ```$ git clone https://github.com/UCNLP/conflict_test.git``` 
           
   2. Set IP and PORT in *conflict_test/client_setting.ini*
   
        ```
           [CONNECTION]
            IP = 35.196.166.28
            PORT = 5009
            
           [GRAPH_CONNECTION]
            IP = 35.196.166.28
            PORT = 5010
        ```
    
   3. Run *client.py*
    
        ```$ python3 ./client.py```

## Demo Video
https://www.youtube.com/embed/FO2RW24wHFQ<br>

## Bot's Main Features

1.	Detect direct conflict : Chatbot can detect a direct conflict and three types of severity.
2.	Detect indirect conflict : Chatbot can detect a indirect conflict.
3.  Predict direct conflict : Chatbot can predict the probability of a direct conflict in the project.

## Bot's Functional Features

1.	Ignore file : It functions like gitignore. A user can customize his/her ignore files.
2.	Lock file : A user can lock his/her files. If other users try to modify the locked file, Sayme gives them a warning.
3.	Check code history : A user can ask who wrote certain code lines.
4.	Ignore alarm : A user can ignore direct alarm and indirect alarm.
5.	Check conflict possibility : Before a user starts to work, the user can check whether editing certain file generates a conflict or not.
6.	Check working status : A user can ask about other user's working status.(Working Project, Logic, Line, Amount)
7.	Give user message : A user can let chatbot give a message to other users.
8.	Give recommendation : A user can ask chatbot to recommend how to deal with the conflict in certain file.
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
6. Chatbot predicts the probability of a direct conflict with each of other users when a user starts editing a new file.
7. Chatbot shows a git diff code of other user involved, when a code conflict occurs. 
8. Chatbot catches the file name typo created by a user and recommends the most accurate file to the user.

## Algorithm

- NLP : You can see the algorithm in [chat_bot_server_dir folder](https://github.com/UCNLP/conflict-prediction/tree/py3_server/chat_bot_server_dir)
- Conflict detection : You can see the algorithm in [server_dir folder](https://github.com/UCNLP/conflict-prediction/tree/py3_server/server_dir)
- Conflict prediction : You can see the algorithm in [server_dir_folder](https://github.com/UCNLP/conflict-prediction/tree/py3_server/server_dir)

## Future Work

- Research about the ways of chatbot that human likes(What behaviors should chatbot have?).
- Adopt voice recognition technology : Chatbot can recognize the voice input from a user, and chatbot can respond to the voice input with its own voice.
