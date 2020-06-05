class Test:

    def __init__(self):
        self.testVal = -1
        print(self.testVal)

    def __enter__(self):
        self.testVal = 1
        print(self.testVal)

    def __exit__(self):
        self.testVal = 0
        print(self.testVal)

def test(n):
    testVal = n
    print(testVal)

class ClassA:
    memberValueA_A = 10
    memverValueA_B = 20

    def __init__(self, n):
        self.testVal = n
        self.strA = "A"

    def printClassName(self):
        print("ClassName : {}".format(self.strA))

    def getSumOfMemberValue(self):
        self.sum = self.memberValueA_A + self.memverValueA_B
        return self.sum