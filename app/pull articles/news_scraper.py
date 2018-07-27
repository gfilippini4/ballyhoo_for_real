# This script takes major news outlets and is able to scape the article URL
# as well as all the content corresponding to the article. Using multiple threads,
# we can gain a large volume of articles while maintaining a certain level of
# efficiency. The script is set up to update every 60 seconds but can be wound up
# or down depending on hardware resources available. Finally, after gathering all
# the data pertaining to an article, the script will save the information to a
# directory named after the source it was pulled from to help us give credit where
# it is due.

# AUTHOR: GARRETT FILIPPINI
# DATE: 7/16/18


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os.path
import threading
import datetime
import getpass
import time
import json
from getpass import getpass
import push_to_sql as ps
from functions import *


# thread called which then launches the corresponding init function which pulls the
# articles from the sources respective website.
class new_source_thread(threading.Thread):
	def __init__(self, threadName, threadID, func):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.threadID = threadID
		self.func = func

	def run(self):
		logger('Launching ' + self.threadName + ' ' + str(self.threadID))
		self.func()
		logger('Closing ' + self.threadName + ' ' + str(self.threadID))
		check(1)

# Simple check method to see if the number of threads launched have completed. If
# so, we release the lock, and allow the next batch of threads to launch there after.
def check(num):
	global checker
	global lock
	checker += num
	if checker == 3:
		logger('UPDATE COMPLETE')
		checker = 0
		lock.release()
	print(str(checker))

# This is the main loop where we call the initialize our threads, and launch them.
def update_sources():
	global lock
	count = 0
	while True:
		lock.acquire()
		thread_onion = new_source_thread('Onion', count, initTheOnion)
		thread_cnn = new_source_thread('cnn', count, initCNN)
		thread_fox = new_source_thread('fox', count, initFOX)

		thread_onion.start()
		thread_cnn.start()
		thread_fox.start()
		lock.acquire()
		time.sleep(60)
		lock.release()
		count += 1

# init function for The Onion news source.
def initTheOnion():
	driver = webdriver.Chrome()
	driver.set_page_load_timeout(20)
	generic(driver, 'The Onion', 'https://theonion.com', ['onion'])

# init function for CNN news source.
def initCNN():
	driver = webdriver.Chrome()
	driver.set_page_load_timeout(20)
	generic(driver, 'cnn', 'https://cnn.com', ['cnn', '?'])

# init function for Fox News source.
def initFOX():
	driver = webdriver.Chrome()
	driver.set_page_load_timeout(20)
	generic(driver, 'fox', 'https://foxnews.com', ['fox', '.html'])

# This function is where we do most of the work. We begin by defining the path that
# the scraped articles will be stored. From there, we store the URL's into a dictionary
# to avoid inefficiencies by hitting the same URL twice. We then are able to pull
# the necessary data from each URL and then write it to a local file to be stored in
# its respective directory.
def generic(driver, src, main_link, key_words):
	global password
	global username
	article_info = {}
	# Path where the article will be stored.
	save_path = '/Users/garrettfilippini/Desktop/ballyhoo/app/pull articles/' + src
	try:
		driver.get(main_link)
	except:
		print("Load Page Stopped")
	time.sleep(10)
	# Grabs every link in the homepage of the news source.
	links = driver.find_elements_by_css_selector('a')
	arr = {}
	# This for loop clenses the URL's, only taking those that are believed to have
	# relevant data.
	for link in links:
		try:
			url = link.get_attribute('href')
			if len(key_words) == 1:
				if 'onion' in url and url[len(url) - 1].isdigit():
					arr[str(url)] = 1
			else:
				if key_words[0] in url and key_words[1] in url:
					arr[str(url)] = 1
		except:
			logger('href doesnt exist')

	# At this point we iterate through all of the keys in the dictionary which are
	# URL's and begin the process of scraping the actual data.
	count = 0
	for url in arr.keys():
		try:
			driver.get(url)
		except:
			pass
		# First we try and get a title for the article by using the following checking
		# method.
		data = driver.find_elements_by_css_selector('body')
		title = data[0].find_elements_by_css_selector('header')

		for item in title:
			try:
				t = item.find_elements_by_css_selector('h1')
				title = t[0].text
				article_info['title'] = title
				break
			except:
				try:
					t = item.find_elements_by_css_selector('h2')
					title = t[0].text
					article_info['title'] = title
					break
				except:
					pass
		if 'selenium' in str(title):
			title = 'test' + str(count)
			article_info['title'] = title
		if '/' in str(title):
			title = title.replace('/', ' ')
			article_info['title'] = title
		logger(str(title))

		# Here we grab every paragraph in the html file and append each paragraph to
		# a local string variable.
		article = data[0].find_elements_by_css_selector('p')
		str_article = ''
		j = 0
		while j < len(article):
			str_article += article[j].text + '\n\n'
			j += 1
		article_info['id'] = str(count) + src[0]
		article_info['content'] = str_article
		article_info['url'] = str(url)
		try:
			article_info['word_count'] = str(len(str_article.split(' ')))
		except:
			article_info['word_count'] = '0'
		article_info['date_scraped'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
		ps.parse_article(article_info,username,password)
		json_encoded = json.dumps(article_info)
		# Now that we have the title, URL, and the content of the article, we can create
		# filename, and save the data to the file. The file is then placed in its
		# respective directory to be further parsed (for hooks) and stored into the database.
		# If all goes well at this point, we notify that the process for a single article
		# been successfully completed, and then the process begins again.

		# complete_name = os.path.join(save_path, str(title) + '.txt')
		# f = open(complete_name, 'w')
		# f.write(json_encoded)
		# f.close()
		logger('SUCCESSFULLY WRITTEN')
		count += 1
	# At the end of execution, we close the browser window by closing our driver. (Instance of Chrome)
	driver.close()



# Local variables that help the threads run concurrently.
lock = threading.Lock()
checker = 0
username = input('Username: ')
password = getpass()
