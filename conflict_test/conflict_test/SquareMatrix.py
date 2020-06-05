class SquareMatrix:
    def __init__(self, n):
        self.__n = n
        self.__data = [[0 for col in range(self.__n)] for row in range(self.__n)]

    def __matmul__(self, other):
        if self.__n == other.__n:
            ret = SquareMatrix(self.__n)
            for i in range(self.__n):
                for j in range(self.__n):
                    for k in range(self.__n):
                        ret.__data[i][k] += self.__data[i][j] * other.__data[j][k]
            return ret
        else:
            print("Error :: {} != {}".format(self.__n, other.__n))
            exit()

    def __mul__(self, other):
        if self.__n == other.__n:
            ret = SquareMatrix(self.__n)
            for i in range(self.__n):
                for j in range(self.__n):
                    ret.__data[i][j] = self.__data[i][j] * other.__data[i][j]
            return ret
        else:
            print("Error :: {} != {}".format(self.__n, other.__n))
            exit()

    def get_lower(self):
        ret = SquareMatrix(self.__n)
        for i in range(self.__n):
            for j in range(i):
                ret.__data[i][j] = self.__data[i][j]
        return ret

    def get_upper(self):
        ret = SquareMatrix(self.__n)
        for i in range(self.__n):
            for j in range(i + 1, self.__n):
                ret.__data[i][j] = self.__data[i][j]
        return ret

    def __str__(self):
        ret = ''
        for i in range(self.__n):
            for j in range(self.__n):
                ret += str(self.__data[i][j]) + ' '
            ret += '\n'
        return ret

    def set_value(self, row, col, value):
        if 0 <= row < self.__n and 0 <= col < self.__n:
            self.__data[row][col] = value
        else:
            print("Error :: Out of Range")
            exit()

    def temp_func(self):
        print("This is temp func")
        str = "Sun"
        if str == "Sun":
            print("He is Sun.")
        else:
            print("He is not Sun.")



class SquareMatrix2:
    def __init__(self, n):
        self.__n = n
        self.__data = [[0 for col in range(self.__n)] for row in range(self.__n)]

    def __matmul__(self, other):
        if self.__n == other.__n:
            ret = SquareMatrix(self.__n)
            for i in range(self.__n):
                for j in range(self.__n):
                    for k in range(self.__n):
                        ret.__data[i][k] += self.__data[i][j] * other.__data[j][k]
            return ret
        else:
            print("Error :: {} != {}".format(self.__n, other.__n))
            exit()

    def __mul__(self, other):
        if self.__n == other.__n:
            ret = SquareMatrix(self.__n)
            for i in range(self.__n):
                for j in range(self.__n):
                    ret.__data[i][j] = self.__data[i][j] * other.__data[i][j]
            return ret
        else:
            print("Error :: {} != {}".format(self.__n, other.__n))
            exit()

    def get_lower(self):
        ret = SquareMatrix(self.__n)
        for i in range(self.__n):
            for j in range(i):
                ret.__data[i][j] = self.__data[i][j]
        return ret

    def get_upper(self):
        ret = SquareMatrix(self.__n)
        for i in range(self.__n):
            for j in range(i + 1, self.__n):
                ret.__data[i][j] = self.__data[i][j]
        return ret

    def __str__(self):
        ret = ''
        for i in range(self.__n):
            for j in range(self.__n):
                ret += str(self.__data[i][j]) + ' '
            ret += '\n'
        return ret

    def set_value(self, row, col, value):
        if 0 <= row < self.__n and 0 <= col < self.__n:
            self.__data[row][col] = value
        else:
            print("Error :: Out of Range")
            exit()

    def temp_func(self):
        print("This is temp func")
        str = "Sun"
        if str == "Sun":
            print("He is Sun.")
        else:
            print("He is not Sun.")


def get_lower(self):
    ret = SquareMatrix(self.__n)
    for i in range(self.__n):
        for j in range(i):
            ret.__data[i][j] = self.__data[i][j]
    return ret

def get_upper(self):
    ret = SquareMatrix(self.__n)
    for i in range(self.__n):
        for j in range(i + 1, self.__n):
            ret.__data[i][j] = self.__data[i][j]
    return ret