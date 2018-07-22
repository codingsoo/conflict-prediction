import os

file_dir = []

def search_directory(url):
    for (file_path, dir, files) in os.walk(url):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.py':
                # print("%s/%s" % (file_path, filename))
                file_dir.append(os.path.join(file_path,filename))


if __name__ == '__main__':
    search_directory("C:\Users\learn\PycharmProjects\conflict-detector\UCI_chatbot_Server")
    print file_dir
