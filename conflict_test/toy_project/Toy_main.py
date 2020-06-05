import toy_project.ClassA
import toy_project.ClassAofA

# if __name__ == '__main__':
#     CA = toy_project.ClassA.ClassA(1)
#     CAofA = toy_project.ClassAofA.ClassAofA(1)
#     # CBofA = CA.ClassBofA()
#
#     # sum = CA.getSumOfMemberValue() + CAofA.getSumOfMemberValue() + CBofA.getSumOfMemberValue()
#     sum = CA.getSumOfMemberValue() + CAofA.getSumOfMemberValue()
#
#     print("Sum of all member values : {}".format(sum))

def run():
    CA = toy_project.ClassA.ClassA(1)
    CAofA = toy_project.ClassAofA.ClassAofA(1)
    # CBofA = CA.ClassBofA()

    CAofA.printClassName()
    # sum = CA.getSumOfMemberValue() + CAofA.getSumOfMemberValue() + CBofA.getSumOfMemberValue()
    sum = CA.getSumOfMemberValue() + CAofA.getSumOfMemberValue()

    print("Sum of all member values : {}".format(sum))


def run2():
    run()
