import os

def search_directory(url):
    for (path, dir, files) in os.walk(url):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.py':
                print("%s/%s" % (path, filename))


if __name__ == '__main__':
    print search_directory("C:\Users\learn\PycharmProjects\conflict-detector\UCI_chatbot_Server\conflict-detector")