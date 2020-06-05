import conflict_test.SquareMatrix

def run():
    graph = [
        [1, 2],
        [1, 5],
        [2, 3],
        [2, 4],
        [2, 5],
        [3, 4],
        [3, 7],
        [4, 5]
    ]

    A = conflict_test.SquareMatrix.SquareMatrix( 8 )
    for u, v in graph :
        A.set_value(u, v, 1)
        A.set_value(v, u, 1)
    L = A.get_lower()
    U = A.get_upper()
    G = A.get_lower()
    B = L @ U
    C = A * B
    print(C)

def run2():
    graph = [
        [1, 2],
        [1, 5],
        [2, 3],
        [2, 4],
        [2, 5],
        [3, 4],
        [3, 7],
        [4, 5], 8
    ]

    A = conflict_test.SquareMatrix.SquareMatrix(8)
    for u, v in graph:
        A.set_value(u, v, 1)
        A.set_value(v, u, 1)
    L = A.get_lower()
    U = A.get_upper()
    G = A.get_lower()
    B = L @ U
    C = A * B
    print(C)

run()
