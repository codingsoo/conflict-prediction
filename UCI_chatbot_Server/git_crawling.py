import re
import random
import os
from bs4 import BeautifulSoup
import urllib2
import json
from collections import OrderedDict

code_file_links = []
base_url = "http://github.com"
url = "https://github.com/UCNLP/conflict-detector"

#Get html document from url
def __init__bs(url):
    request = urllib2.Request(url)
    html = urllib2.urlopen(request).read()
    bs = BeautifulSoup(html, 'html.parser')

    return bs

#Get Class name and Function name
def getClassFunctionInfo(url):
    def_name_list =[]
    class_name_list=[]

    bs = __init__bs(url)

    code = bs.find("div",{"itemprop":"text"})
    code = code.find_all("td")

    for line in code:
        temp_line = line.find_all("span",{"class":"pl-k"})
        for tag_finder in temp_line:
            tag_finder = tag_finder.text
            if tag_finder == 'def':
                name = line.find_all("span",{"class":"pl-en"})
                for function_name in name:
                    def_name_list.append(function_name.text)
            elif tag_finder == 'class':
                name = line.find_all("span",{"class":"pl-en"})
                for class_name in name:
                    class_name_list.append(class_name.text)
    print(def_name_list)
    print(class_name_list)

    return def_name_list, class_name_list

#Get Directory link list
def getLink(url):

    bs = __init__bs(url)

    dir_list = bs.find_all('td',{'class':'content'})
    dir_list = dir_list[1:]

    for i in dir_list:
        init_url = i.find('a').get('href')
        split_url = init_url.split('/')
        dir_url = split_url[3:]
        if dir_url[0]=='blob' and dir_url[len(dir_url)-1][-2:]=="py":
            path = "/"
            for k in dir_url:
                path = path + k + "/"
            code_file_links.append(path)
        else :
            next_url = base_url +init_url
            getLink(next_url)

    return code_file_links

#Write files' info in json file
def FilesInfo(url):

    getLink(url)
    # print(code_file_links)
    json_data = OrderedDict()

    for i in code_file_links:
        code_url = url + i
        getClassFunctionInfo(code_url)


'''
    main function
'''
if __name__ == '__main__':
    FilesInfo(url)
