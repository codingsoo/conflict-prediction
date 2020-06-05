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

    class ClassBofA:
        memberValueBofA_A = 50
        memberValueBofA_B = 60

        def __init__(self):
            self.strBofA = "BofA"

        def printClassName(self):
            ClassA.printClassName()
            print("ClassName : {}".format(self.strBofA))

        def getSumOfMemberValue(self):
            self.sum = self.memberValueBofA_A + self.memberValueBofA_B

            return self.sum