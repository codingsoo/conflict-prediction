import pymysql

conn = pymysql.connect(host='127.0.0.1',
                            user='root',
                            password='99189918',
                            db='uci_chat_bot',
                            charset='utf8')
# get cursor
cursor = conn.cursor()

# create sql
sql = "select * " \
      "from working_table "

# execute sql
cursor.execute(sql)
conn.commit()

raw_list = cursor.fetchall()
raw_list = list(raw_list)


print(raw_list)

temp1 = [
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|class TestClass|def __init__', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|class TestClass'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|class TestClass|def print11', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|class TestClass'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test2.py|def test2_function', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|class TestClass'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|class TestClass|def print1', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|class TestClass'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test2.py|def test2_function', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|def gcd'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test2.py|def test2_function', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test1.py|def gcd_dep'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector|def __init__', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector|def __str__', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector|def __add__', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector|def temp', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector'],
    ['C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector|def temp1', 'C:\\Users\\jc\\Desktop\\chat_bot_server\\git_graph_draw\\py_test\\test3.py|class Vector']
]

temp = [
    ['py_test\\test1.py|class TestClass|def __init__',  'py_test\\test1.py|class TestClass'],
    ['py_test\\test1.py|class TestClass|def print11',   'py_test\\test1.py|class TestClass'],
    ['py_test\\test2.py|def test2_function',            'py_test\\test1.py|class TestClass'],
    ['py_test\\test1.py|class TestClass|def print1',    'py_test\\test1.py|class TestClass'],
    ['py_test\\test2.py|def test2_function', 'py_test\\test1.py|def gcd'],
    ['py_test\\test2.py|def test2_function', 'py_test\\test1.py|def gcd_dep'],
    ['py_test\\test3.py|class Vector|def __init__', 'py_test\\test3.py|class Vector'],
    ['py_test\\test3.py|class Vector|def __str__', 'py_test\\test3.py|class Vector'],
    ['py_test\\test3.py|class Vector|def __add__', 'py_test\\test3.py|class Vector'],
    ['py_test\\test3.py|class Vector|def temp', 'py_test\\test3.py|class Vector'],
    ['py_test\\test3.py|class Vector|def temp1', 'py_test\\test3.py|class Vector']
]

test = [
    # repository   file          logic                        user               필요없음
    ('a project', 'b file', 'class:AClass:function11', 'learnitdeep@gmail.com', 4, 16, datetime.datetime(2018, 8, 13, 23, 12, 18)),
    ('a project', 'b file', 'function:function114442', 'learnitdeep@gmail.com', 4, 16, datetime.datetime(2018, 8, 13, 23, 12, 18)),
    ('UCNLP/client.git', 'UCNLP/client/client.py', 'function:verifying_user', 'chan_j@naver.com', 151, 1, datetime.datetime(2018, 8, 14, 14, 43, 2))
]


#############################
