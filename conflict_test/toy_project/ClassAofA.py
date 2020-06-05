import toy_project.ClassA as ClassA

class ClassAofA:
    memberValueAofA_A = 30
    memberValueAofA_B = 40

    def __init__(self, n):
        self.testVal = n
        self.strAofA = "AofA"

    def printClassName(self):
        CA = ClassA.ClassA(3)
        CB = CA.ClassBofA()
        CA.printClassName()
        CB.printClassName()
        print("ClassName : {}".format(self.strAofA))

    def getSumOfMemberValue(self):
        self.sum = self.memberValueAofA_A + self.memberValueAofA_B

        return self.sum