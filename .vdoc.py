# type: ignore
# flake8: noqa
#
#
#
#
#
#
#
#
# load packages
import requests
from bs4 import BeautifulSoup
#
#
#
#
#
# define fetching function based on msg number
def fetch_details(msg_number):
    # Initialize an empty dictionary to hold the details
    details = {}
    
    # Generate the full URL of the detailed page
    url = "https://www.mail-archive.com/nmusers@globomaxnm.com/msg{msg_number}.html"
    
    # Fetch the HTML content from the URL
    response = requests.get(url)
    page_content = response.text
    
    # Initialize a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Extract the date
    date_tag = soup.select_one('span.date a')
    if date_tag:
        details['date'] = date_tag.text.strip()
    
    # Extract the message text
    message_tag = soup.select_one('div.msgBody pre')
    if message_tag:
        details['message'] = message_tag.text.strip()
        
    return details
#
#
#
#
#
# Fetch the landing page
landing_url = 'https://www.mail-archive.com/nmusers@globomaxnm.com/'
response = requests.get(landing_url)
landing_page_content = response.text

# Initialize a BeautifulSoup object and specify the parser
soup = BeautifulSoup(landing_page_content, 'html.parser')

# Initialize an empty dictionary to hold the threads' information
threads = []

# show first element
soup.select('li')[0]
#
#
#
#
# Loop through each thread item and extract the details
for thread in soup.select('li'):
    # Initialize an empty dictionary to hold individual thread info
    thread_info = {}
    
    # Extract the thread title
    title_tag = thread.select_one('span.subject a')
    if title_tag:
        thread_info['title'] = title_tag.text.strip()
        
        # Extract the thread number from the 'name' attribute
        if 'name' in title_tag.attrs:
            thread_info['number'] = title_tag['name']
    
    # Extract the sender information
    sender_tag = thread.select_one('span.sender')
    if sender_tag:
        thread_info['sender'] = sender_tag.text.strip()
    
    # Append the dictionary to the list only if it contains some data
    if thread_info:
        threads.append(thread_info)

# Print the list of thread dictionaries
print(threads)
#
#
#
#
fetch_details(msg_number="08686")
#
#
#
