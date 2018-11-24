# Definition of conflict


## Definition of direct conflict

Direct conflict is a conflict that occurs when two users (programmers) modify the same file in a project file stored in the destination hub. The types of direct conflicts are following: modifying the same function, modifying the same function in the same class, modifying the same class, and modifying code lines in the same file. We define modifying the same function as the riskiest situation such as modifying the same function in the same class. Next, we define modifying the same class as the second riskiest situation and modifying code lines in the same file as the least risky situation.

## Definition of indirect conflict

Indirect Conflict is a conflict that occurs when two users (programmers) modify a function or a class with dependencies among files of a project stored in the hub. "A function or a class with dependencies" refers to the relationship between two functions or classes when importing one function or class module from another function or class. We draw a graph of the relationship between a function and a class, and use an algorithm that computes the length between nodes. The short length means a high risk while the long length means a low risk.

## Structure of conflict detector

### Platform architecture

![conflict_server_structure](https://github.com/UCNLP/conflict-prediction/blob/py3_server/images/conflict_server_structure.png)

### Class diagram

![conflict_server_class_diagram](https://github.com/UCNLP/conflict-prediction/blob/py3_server/images/conflict_server_class_diagram.png)

### Sequence diagram

![conflict_server_sequence_diagram](https://github.com/UCNLP/conflict-prediction/blob/py3_server/images/conflict_server_sequence_diagram.jpg)

## How to detect conflict

### Get user's working status

Our server fisrt write function-line mapping dataset from git repository, and rewrite it per every 4 hours. Then client file use github diff function and function-line mapping dataset to detect where users are working on, and how many lines users are modifying.

### Draw project's indirect graph

1.	We parse Python files into the following form using ['ast'] among Python libraries (https://docs.python.org/3/library/ast.html).

	1.	'type': There are 'Function', 'Class', and 'Call' and each represents function, class, and callee respectively.
	2.	'name' : It stores the name of corresponding type.
	3.	'start' and 'end' : They mean the beginning and end of the corresponding logic (function and class) for a function and class.
	4.	'members' : It stores 'Function', 'Class' and 'Call' types which are in functions and classes.\`\`\`

2.	We obtain the relationship between each logic from the parsing results and store it in the form of edge list.

3.	We measure the distance between logics using [Floyd-Warshall](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)

#### Result Of Parsing

```javascript
conflict_test/counting_triangle.py : [
    {
        "type": "Function",
        "name": "run",
        "start": 5,
        "end": 34,
        "members": [
            {
                "type": "Call",
                "id": "dict"
            },
            {
                "type": "Call",
                "id": "sqrt"
            },
            {
                "type": "Call",
                "id": "byeongal_math.SquareMatrix.SquareMatrix"
            },
            {
                "type": "Call",
                "id": "byeongal_math.SquareMatrix.SquareMatrix.set_value"
            },
            {
                "type": "Call",
                "id": "byeongal_math.SquareMatrix.SquareMatrix.set_value"
            },
            {
                "type": "Call",
                "id": "byeongal_math.SquareMatrix.SquareMatrix.get_lower"
            },
            {
                "type": "Call",
                "id": "byeongal_math.SquareMatrix.SquareMatrix.get_upper"
            },
            {
                "type": "Call",
                "id": "print"
            }
        ]
    },
    {
        "type": "Call",
        "id": "run"
    }
]
```

### Detect direct conflict

1.	We delete the direct conflict list from the database when an alarm count is over 2 and the amount of time is over 24 hours.
2.	We check if there is another user whose working status overlaps with a current user using the project name and job information of the current user

	1.	The user information where project name and working file overlap exists (direct conflict)

		1.	We check if there is direct conflict information in the direct conflict table using the current direct conflict information.

			1.	Direct Conflict information is in the table.

				1.	We bring the riskiest direct conflict information among the direct conflict information that occurred between the current user and other users.
				2.	We compare the current direct conflict information and the direct conflict information in the database, and give the user an alert according to the risk.
				3.	We update the current direct conflict information to the database.

			2.	Direct conflict information is not in the table(First Direct Conflict)

				1.	We bring the riskiest direct conflict information among the direct conflict information that occurred between the current user and other users.
				2.	We inform the direct conflict information to the user.
				3.	We insert the current direct conflict information into the database.

	2.	The user information where project name and working file overlap doesn't exist (non-direct conflict)

		1.	We check if there is current user's information in the conflict table.
		2.	There is current user's information in the conflict table.
			1.	We let users know that the direct conflict has been resolved.
		3.	We delete all direct conflict information related to the user in the current direct conflict table.

### Detect indirect conflict

2.	1.	We delete the indirect conflict list from the database when an alarm count is over 2 and the amount of time is over 24 hours.

2.	We check if there is another user whose project name is same with the one of the current user from the working table in the database.

3.	We look up the logic dependency table in the database using the current user's project name, and another user's working history whose project name and working history are same with the current user's.

	1.	The current user's working history and another user's working history are connected by the dependency table in the database (indirect conflict).

		1.	We go over the indirect conflict table in the database using the current indirect conflict information.

		2.	Indirect conflict information already exists.

			1.	If an alarm count of current indirect conflict information is 1 and the amount of time is more than 30 minutes, we let the user know about the indirect conflict information.
			2.	We update the current indirect conflict information to the database.

		3.	Indirect information does not exist. (First indirect conflict)

			1.	We let the user know about the indirect conflict information.
			2.	We update the current indirect conflict information to the database.

	2.	The current user's working history and another user's working history are not connected by the dependency table in the database (non-indirect conflict).

		1.	We make it sure if the indirect table contains the information about the current user.
		2.	Direct table has the information about the current user.
			1.	We let the users know that the indirect conflict has been resolved.
		3.	We delete the data of current user from the indirect table.