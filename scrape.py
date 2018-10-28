from bs4 import BeautifulSoup
import requests
import csv

domain = "https://forum.gamestm.co.uk/"
general_gaming = "https://forum.gamestm.co.uk/viewforum.php?f=3"
high_scores = "https://forum.gamestm.co.uk/viewforum.php?f=4"
off_topic = "https://forum.gamestm.co.uk/viewforum.php?f=7"
news = "https://forum.gamestm.co.uk/viewforum.php?f=10"

sections = [high_scores]

def get_forum_section(section_url):

	page_content = scrape_html(section_url)
	pagination = page_content.find("div", class_="pagination")
	pagelinks = pagination.find_all("a")
	page_numbers = []
	threads_per_page = 50
	thread_urls = []
	for i in range(0, pagelinks.__len__()):
		page_number = pagelinks[i].get_text()
		try:
			page_number = int(page_number)
			if page_number:
				page_numbers.append(page_number)
		except ValueError:
			pass

	section_length = max(page_numbers)
	for i in range(0, section_length):
		get_threads_in_section_page(section_url, i, thread_urls, threads_per_page)

	return thread_urls

def get_threads_in_section_page(section_url, section_page, thread_urls, threads_per_page):
	querystring = ""
	if (section_page > 0):
		querystring = ("&start=" + str(section_page * threads_per_page))
	else:
		querystring = ""

	url = section_url + querystring
	page_content = scrape_html(section_url)
	threads = page_content.find_all("a", class_="topictitle")
	for i in range(0, threads.__len__()):
		thread = threads[i]
		thread_url = thread.attrs['href']
		thread_url = domain + thread_url[1:]
		thread_urls.append(thread_url)
		print "Scraping this: " + thread_url


def get_thread(url):
	print "getting this thread: " + url
	page_content = scrape_html(url)
	if page_content == None:
		return None

	pagination = page_content.find("div", class_="pagination")
	pagelinks = pagination.find_all("a")
	thread_title = page_content.find("h2", class_="topic-title")
	thread_title = thread_title.get_text()
	page_numbers = []

	if pagelinks:
		for i in range(0, pagelinks.__len__()):
			page_number = pagelinks[i].get_text()
			try:
				page_number = int(page_number)
				if page_number:
					page_numbers.append(page_number)
			except ValueError:
				pass

	thread_length = 1

	if page_numbers:
		thread_length = max(page_numbers)
	
	posts_per_page = 15
	thread = []
	for i in range(0, thread_length):
		if (i > 0):
			querystring = ("&start=" + str(i * posts_per_page))
		else:
			querystring = ("&start=0")
		thread_page_url = url + querystring
		print "getting posts from " + thread_page_url
		get_thread_page(thread, thread_page_url, thread_title)

	return thread

def get_thread_page(thread, url, thread_title):

	##returns a page, written as a series of csv rows

	page_content = scrape_html(url)
	if (page_content == None):
		return

	thread_page = []
	posts = page_content.find_all("div", class_="post")
	posts_length = posts.__len__()
	for i in range(0, posts_length):
		post = posts[i]
		thread_title
		try:
			thread_title = thread_title.encode("utf-8", "replace")
		except:
			##malformed thread title
			thread_title = "Malformed title: " + url
		row = [thread_title]

		postprofile = post.find("dl", class_="postprofile")
		author = postprofile.select(".username,.username-coloured")
		author = author[0] or "Unknown Author"

		author = author.get_text()
		author = author.strip()
		author = author.encode('utf-8','replace')

		row.append(author)

		postbody = post.find("div", class_="postbody")
		postcontent = postbody.find("div", class_="content")
		postcontent = postcontent.get_text()
		postcontent = postcontent.strip()
		
		timestamp = postbody.find("p", class_="author")#.find("span", class_="responsive-hide")

		timestamp.find("span", class_="responsive-hide").extract()
		timestamp = timestamp.get_text()
		timestamp = timestamp.encode('utf-8','replace')
		timestamp = timestamp.replace("Post", "").strip()

		row.append(timestamp)
		postcontent = postcontent.encode('utf-8','replace')
		row.append(postcontent)
		thread.append(row)
		

def scrape_html(url):

	try:
		page_response = requests.get(url, timeout=5)
		page_content = BeautifulSoup(page_response.content, "html.parser")
	except:
		return None
	return page_content


headers = ["Thread", "Author", "Timestamp", "Post"]
with open("gtm.csv", "wb") as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(headers)

	for section in sections:
		threads = get_forum_section(section)
		for i in range(0, threads.__len__()):
			thread = get_thread(threads[i])
			if thread:
				writer.writerows(thread)