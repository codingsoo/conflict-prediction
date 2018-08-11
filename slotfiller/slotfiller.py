import json

def slot_filler(verb, obj):
    with open("response.json", 'r') as f:
        response_dict = json.load(f)

    user_request = [verb, obj]

    if user_request[0] in response_dict.keys():
        if user_request[1] in response_dict[user_request[0]].keys():
            user_response = response_dict[user_request[0]][user_request[1]]

    return user_response