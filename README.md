Conflict Detector
=================

Definition of conflict
----------------------

### Definition of direct conflict

다이렉트 컨플릭트란 두명의 사용자(프로그래머)가 깃허브에 저장된 프로젝트의 파일 중에서 같은 파일을 수정할 때 발생하는 컨플릭트를 말한다. 다이렉트 컨플릭트의 종류는 같은 함수를 수정하는 경우, 같은 클래스의 같은 함수를 수정하는 경우, 같은 클래스를 수정하는 경우, 같은 파일 안에서 수정하는 경우 총 3가지로 구성된다. 우리는 같은 함수를 수정하는 경우와 같은 클래스의 같은 함수를 수정하는 경우를 위험도가 가장 높은 상황으로 정의했다. 그다음으로 같은 클래스를 수정하는 경우를 두번째로 위험도가 높은 상황으로 정의했다. 마지막으로 같은 파일에서만 수정하는 경우에는 가장 낮은 위험도로 정의했다.<br>

Direct conflict is a conflict that occurs when two users (programmers) modify the same file in a project file stored in the destination hub. The types of direct conflicts are following: modify the same function, modify the same function in the same class, modify the same class, and modify code lines in the same file. We define modifying the same function as the riskiest situation such as modifying the same function in the same class. Next, we define modifying the same class as the second riskiest situation and modifying code lines in the same file as the least risky situation.<br>

<br>

### Definition of indirect conflict

인다이렉트 컨플릭트란 두명의 사용자(프로그래머)가 깃허브에 저장된 프로젝트의 파일 중에서 디펜던시를 갖는 함수나 클래스를 서로 수정할 때 발생하는 컨플릭트를 말한다. 디펜던시를 갖는 함수나 클래스란 한 함수나 클래스에서 다른 함수나 클래스의 모듈을 import 할 때 두 개의 함수나 클래스 사이에서 생기는 관계를 말한다. 우리는 함수와 클래스간의 관계를 그래프로 그리고, 노드 간의 길이를 계산하는 알고리즘을 이용해서 길이가 높아지면 위험도가 낮아지고 길이가 낮아지면 위험도가 높아지는 것으로 정의했다.<br>

Indirect Conflict is a conflict that occurs when two users (programmers) modify a function or a class with dependencies among files of a project stored in the hub. "A function or a class with dependencies" refers to the relationship between two functions or classes when importing one function or class module from another function or class. We draw a graph of the relationship between a function and a class, and use an algorithm that computes the length between nodes. The length gets shorter when the risk decreases while it gets longer when the risk increases.

<br>

Structure of conflict detector
------------------------------

### Platform architecture

<div align="center">
<img src="images/uci_st.png" width="100%" height="100%">
</div>

<br>

### Class diagram

<div align="center">
<img src="images/uml_diagram.JPG" width="100%" height="100%">
</div>

<br>

### Sequence diagram

<div align="center">
<img src="images/uci_seq1.JPG" width="100%" height="100%">
</div>

<br>

How to detect conflict
----------------------

### Analyze the information of git-diff

우리가 git bash에서 보는 git-diff 정보는 아래와 같다. <br> 우리는 git diff 정보의 첫 줄로부터 사용자가 어떤 파일을 수정했는지 확인할 수 있다. <br> 또한 우리는 git diff 정보의 6번째 줄로부터 과거 파일의 수정된 부분과 현재 파일의 수정된 부분을 확인할 수 있다. <br> 마지막으로 우리는 git diff 정보의 9~10번째 줄로부터 어떤 라인이 빠지고(-기호) 어떤 라인이 추가(+기호) 되어졌는지 확인할 수 있다. <br> The information of git diff we see from git bash is shown below. <br> From the first line of the git diff information, we can see which files a user modified. <br> We can also see the modified part of the past file and the modified part of the current file from the sixth line of the git diff information. <br> Finally, we can see which line is missing (- sign) and which line is appended (+ sign) from line 9 to line 10 of the git diff information.

```
diff --git a/server_dir/direct_work_database.py b/server_dir/direct_work_database.py
index 07686b7..ff16809 100644

--- a/server_dir/direct_work_database.py
+++ b/server_dir/direct_work_database.py

@@ -3,7 +3,7 @@ import datetime as d
from server_dir.slack_message_sender import *
from server_dir.conflict_flag_enum import Conflict_flag
-class work_database:
+class direct_work_database:
```

<br>

### Process the information of git-diff

우리는 사용자로부터 git diff 정보를 받게 되면 .py를 찾아서 사용자가 수정한 파일명을 받아온다. 우리는 수정한 파일명을 받고 git diff 정보 중에서 @@ 가 있는 라인을 찾고, 사용자가 수정한 라인을 찾는다. @@ 태그 안에 있는 숫자 쌍의 정보는 사용자가 수정한 라인의 위로 3줄 밑으로 3줄 정보이다. 우리는 git diff의 라인 수정 정보를 보고 사용자가 어떤 라인을 수정했는지 알 수 있다. 그리고 우리는 라인 정보의 +기호와 -기호를 세서 어떤 라인이 변화했는지 알 수 있다. 우리는 위의 과정을 통해서 git diff 정보를 서버로 넘겨준다. <br> When we receive the information of git diff from a user, we look for .py and get the file name that the user modified. After getting the modified filename, we look for the line with @@ in the git diff information and find the line that the user modified. The @@ includes a pair of number. The one refers to the information about three upper code lines from the modified code line and the other refers to the information about three lower code lines from it. We can recognize which lines a user modified by checking the line modification information. In addition, we can figure out which lines changed by counting the + and - signs of the line information. We pass the git diff information to the server through these process.

<br>

Algorithms of detect conflict
-----------------------------

### Preprocessing of Project

1.	Python 라이브러리중 [`ast`](https://docs.python.org/3/library/ast.html)를 이용해서 파이썬 파일을 다음과 같은 형태로 파싱 한다.
	1.	`type` : `Function`, `Class` 그리고 `Call` 타입으로 분류 되며 각각은 함수, 클래스 그리고 피호출자를 의미 한다.
	2.	`name` : 해당 타입의 이름을 저장한다.
	3.	`start`, `end` : 함수와 클래스의 경우 해당 로직(함수와 클래스)의 시작과 끝을 의미 한다.
	4.	`members` : 함수와 클래스안에 있는 `Function`, `Class` 그리고 `Call` 타입을 저장 한다.
2.	파싱한 결과로 부터 각 로직간의 관계를 구해서 edge list 형태로 저장한다.
3.	edge list를 [Floyd-Warshall](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)를 이용해 각 로직간의 거리를 측정 한다.

	### dd

4.	Use ['ast'] of Python libraries (https://docs.python.org/3/library/ast.html) to parse Python files in the following form:

	1.	Type: 'Function', 'Class', and 'Call' types are categorized, each representing a function, class, and investee.
	2.	'name' : Store the name of the type.
	3.	'start' and 'end' : means the beginning and end of the corresponding logic (function and class) for a function and class.
	4.	'members' : Store 'Function', 'Class' and 'Call' types in functions and classes.

5.	Obtain the relationship between each logic from the parsing result and store it in the form of an edge list.

6.	Use the edge list [Floyd-Warshall](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm) to measure the distance between each logic.

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

### Algorithm of detect direct conflict

1.	알람 카운트가 2 이상이고 24시간 이상인 다이렉트 컨플릭트 리스트를 데이터베이스에서 삭제한다.
2.	프로젝트 이름과 현재 유저의 작업 정보를 이용해서 워킹 정보가 겹치는 다른 유저가 있는지 확인한다.

	1.	프로젝트 이름과 작업 파일이 겹치는 유저 정보가 있음 (다이렉트 컨플릭트)

		1.	현재 다이렉트 컨플릭트 정보를 이용해서 다이렉트 컨플릭트 테이블에 기존의 다이렉트 컨플릭트 정보가 있는지 확인한다.

			1.	기존의 다이렉트 컨플릭트 정보가 있음 (Already Direct Conflict)

				1.	현재 유저와 다른 유저랑 발생한 다이렉트 컨플릭트 정보 중에서 가장 위험도가 높은 다이렉트 컨플릭트 정보를 가져온다.
				2.	현재 다이렉트 컨플릭트 정보와 데이터베이스에 있는 다이렉트 컨플릭트 정보를 비교해서 위험도에 따른 알람을 사용자에게 해준다.
				3.	현재 다이렉트 컨플릭트 정보를 데이터베이스에 업데이트한다.

			2.	기존의 다이렉트 컨플릭트 정보가 없음 (First Direct Conflict)

				1.	현재 유저와 다른 유저랑 발생한 다이렉트 컨플릭트 정보 중에서 가장 위험도가 높은 다이렉트 컨플릭트 정보를 가져온다.
				2.	사용자에게 다이렉트 컨플릭트 정보를 알려준다.
				3.	현재 다이렉트 컨플릭트 정보를 데이터베이스에 삽입한다.

	2.	프로젝트 이름과 작업 파일이 겹치는 유저 정보가 없음 (non- direct conflict)

		1.	컨플릭트 테이블에서 현재 유저의 정보가 있는지 확인한다.
		2.	컨플릭트 테이블에서 현재 유저의 정보가 있음
			1.	해당 사용자들에게 다이렉트 컨플릭트가 해결되었다고 알려준다.
		3.	현재 다이렉트 컨플릭트 테이블에서 사용자와 관련된 모든 다이렉트 컨플릭트 정보를 삭제한다.

<br>

1.	Delete the direct conflict list with an alarm count of 2 or more and 24 hours or more from database.
2.	Use the project name and job information of the current user to check if there is another user whose working information overlaps.

	1.	Project name and work file have overlapping user information (direct conflict)

		1.	Confirm that there is direct conflict information in the direct conflict table using the current direct conflict information.

			1.	Already Direct Conflict exists.

				1.	Bring direct conflict information with the highest risk among the direct conflict information that occurred with the current user and other users.
				2.	It compares the current direct conflict information with the direct conflict information in the database, and gives the user an alarm according to the risk.
				3.	Update the current direct conflict information to the database.

			2.	There is no existing direct conflict information (First Direct Conflict)

				1.	Bring direct conflict information with the highest risk among the direct conflict information that occurred with the current user and other users.
				2.	Inform the user of the direct conflict information.
				3.	Insert the current direct conflict information into the database.

	2.	The project name and work file do not have overlapping user information (non direct conflict)

		1.	Make sure that there is information about the current user in the conflict table.
		2.	Conflict table has current user's information
			1.	Tell the users that the Direct Conflict has been resolved.
		3.	Delete all direct conflict information associated with the user in the current direct conflict table.

<br>

### Algorithm of detect indirect conflict
1. 알람 카운트가 2 이상이고 24시간 이상인 인다이렉트 컨플릭트 리스트를 데이터베이스에서 삭제한다.
2. 데이터베이스의 작업 테이블에서 현재 유저의 프로젝트 이름과 같은 다른 유저가 있는지 확인한다.
3. 현재 유저의 프로젝트 이름, 현재 유저의 작업 내역과 프로젝트 이름이 같은 다른 유저의 작업 내역을 이용해서 데이터베이스의 logic dependency 테이블에 검색을 한다.
    1. 현재 유저의 작업 내역과 다른 유저의 작업이 데이터베이스의 logic dependency 테이블에 의해서 연결이 됨 (indirect conflict)
        1. 현재 인다이렉트 컨플릭트 정보를 이용해서 데이터베이스의 인다이렉트 컨플릭트 테이블을 조사한다.
            1. 이미 인다이렉트 컨플릭트 정보가 존재함.
                1. 현재 인다이렉트 컨플릭트 정보의 알람 카운트가 1이고 30분 이상일 때, 사용자에게 인다이렉트 컨플릭트 정보를 알려준다.
                2. 현재 인다이렉트 컨플릭트 정보를 데이터베이스에 업데이트한다.
                
            2. 인다이렉트 정보가 존재하지 않음. (First indirect conflict)
                1. 사용자에게 인다이렉트 컨플릭트 정보를 알려준다.
                2. 현재 인다이렉트 컨플릭트 정보를 데이터베이스에 업데이트한다.
                
    2. 현재 유저의 작업 내역과 다른 유저의 작업이 데이터베이스의 logic dependency 테이블에 의해서 연결이 안 됨 (non-indirect conflict)
        1. 인다이렉트 테이블에 현재 유저 정보가 있는지 확인한다.
        2. 인다이렉트 테이블에 현재 유저 정보가 있음
            1. 사용자들에게 인다이렉트 컨플릭트가 해결됬다는 것을 알려준다.
        3. 인다이렉트 테이블에서 현재 유저 정보의 데이터를 삭제한다.
        
1. Delete the direct conflict list with an alarm count of 2 or more and 24 hours or more from the database.
2. Verify that there is another user in the work table of the database, such as the current user's project name.
3. Search the database's logic dependency table using the current user's project name, current user's job history and project name, and other user's job history.
    1. The current user's work and other user's jobs are indirectly conflicted by the database's dependency table.
        1. Investigate the in-direct conflict table of the database using the current direct conflict information.
            1. In-direct conflict information already exists.
                1. When the alarm count of current direct conflict information is 1 and is more than 30 minutes, it informs the user of in-direct conflict information.
                2. Update the current direct conflict information to the database.

            2. In direct information does not exist. (First indirect conflict)
                1. Inform the user of the in-direct conflict information.
                2. Update the current direct conflict information to the database.
                
    2. The current user's job history and other user's jobs are not linked by the database's dependency table (non-indirect conflict)
        1. Make sure that the direct table contains the current user information.
        2. Direct table has current user information
            1. Tell the users that the Direct Conflict has been resolved.
        3. Delete the current user information data from the direct table.