import conflict_test.ClassA as ClassA2

class ClassAofA:
    memberValueAofA_A = 30
    memberValueAofA_B = 40

    def __init__(self, n):
        self.testVal = n
        self.strAofA = "AofA"

    def printClassName(self):
        with ClassA2.Test():
            ClassA2.test(5)
            CA = ClassA2.ClassA()
            CA.printClassName()
            print("ClassName : {}".format(self.strAofA))

    def getSumOfMemberValue(self):
        self.sum = self.memberValueAofA_A + self.memberValueAofA_B

        return self.sum