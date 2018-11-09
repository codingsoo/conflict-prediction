def get_cost(user_input, no_typo_error):
    x_length = len(user_input)+1
    y_length = len(no_typo_error)+1

    arr = [[0 for i in range(y_length)] for j in range(x_length)]

    for i in range(x_length-1):
        arr[i+1][0] = i+1

    for j in range(y_length-1):
        arr[0][j+1] = j+1

    for j in range(y_length-1):
        for i in range(x_length-1):
            if user_input[i] == no_typo_error[j] :
                arr[i+1][j+1] = arr[i][j]
            else :
                arr[i+1][j+1] = min(arr[i][j]+1, min(arr[i+1][j]+1,arr[i][j+1]+1))


    return arr[x_length-1][y_length-1]
