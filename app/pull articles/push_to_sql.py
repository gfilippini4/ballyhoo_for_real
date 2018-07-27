import mysql.connector as connector
from functions import *
import operator
from PyDictionary import PyDictionary
from getpass import getpass

def parse_article(article,username,password):
    hooks = []
    try:
        hooks = get_hooks(article['content'])
    except Exception as e:
        logger(str(e))
    insert_article(article,hooks, username, password)

def insert_article(article,hooks,username,password):
    try:
        client = connector.connect(user=username,password=password,host='127.0.0.1',database='Articles')
        cursor = client.cursor()
        sql_insert = """
            INSERT INTO articles (id, date_scraped, title, url, word_count, author, content) values (%s,%s,%s,%s,%s,%s,%s)
            """

        id,date_scraped,title,url,word_count,author,content = None,None,None,None,None,None,None
        keys = article.keys()
        if 'id' in keys:
            id = article['id']
        if 'date_scraped' in keys:
            date_scraped = article['date_scraped']
        if 'title' in keys:
            title = article['title']
        if 'url' in keys:
            url = article['url']
        if 'word_count' in keys:
            word_count = article['word_count']
        if 'author' in keys:
            author = article['author']
        if 'content' in keys:
            content = article['content']
        data = (id,date_scraped,title,url,word_count,author,content)
        cursor.execute(sql_insert,data)
        client.commit()
        try:
            sql_insert = """
                INSERT INTO hooks (id, hook, frequency) values (%s,%s,%s)
                """
            for hook in hooks.keys():
                data = (article['id'], hook, hooks[hook])
                cursor.execute(sql_insert,data)
                client.commit()

        except:
            logger("Counldn't add hooks.")
        client.close()
    except Exception as e:
        password = ''
        logger(str(e))

def get_hooks(content):
    dic = PyDictionary()
    arr = content.split()
    dict = {}
    for item in arr:
        if item in dict.keys():
            dict[item] += 1
        else:
            dict[item] = 1
    dict_sorted = sorted(dict.items(), key=operator.itemgetter(1))
    hooks = {}
    x = 0
    count = 0
    while count < 10 and len(dict_sorted) - (x + 1) > 0:
        word = dict_sorted[len(dict_sorted) - (x + 1)][0]
        num = dict_sorted[len(dict_sorted) - (x + 1)][1]
        try:
            if dic.meaning(word):
                hooks[word] = num
                count += 1
        except:
            pass
        x += 1
    return hooks
