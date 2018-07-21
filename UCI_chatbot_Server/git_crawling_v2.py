import requests
from bs4 import BeautifulSoup
import urllib2

base_url = "http://github.com"
github_url = 'https://github.com/UCNLP/conflict-detector'
code_file_links = []

#Get html document from url
def __init__bs(url):
    request = urllib2.Request(url)
    html = urllib2.urlopen(request).read()
    bs = BeautifulSoup(html, 'html.parser')

    return bs

#Get Directory link list
def getFileLink(url):

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
            getFileLink(next_url)

    return code_file_links

# get
def request_article(url):
    print url
    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.select('tr > td')

    return html

if __name__ == '__main__':
    getFileLink(github_url);
    print request_article(github_url+code_file_links[0])

