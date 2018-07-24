########################################################################################################################
# 1. git clone => receive repository
# 2. each files => create class, def dependency => make graph => make dictionary
# 3. all files => create dependency => make graph => make dictionary\

#### function dependency
# def1 includes def2 => def1 -> def2

# 1. parameter modify
# 2. function name modify
# 3. logic modify

#### class dependency
# In file1
# class A : def1()
#
# In file2
# A.def1()
#
# => If User modified class A : def1() of file1,
# => then it effects A.def1() line of file2.
# [file1, class A, def1] -> [file2, A.def1()]
########################################################################################################################

# {