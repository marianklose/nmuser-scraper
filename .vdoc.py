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
#
#
#
#
#
#
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
import time
from bs4 import BeautifulSoup
from pprint import pprint
#
#
#
#
#
# define pats and api tokens safely via gitignored file 
from secrets import gh_api_token
from secrets import ai_api_token
#
#
#
#
#
# Define repository and category IDs
repository_id = 'R_kgDOKYhvWw'
category_id = 'DIC_kwDOKYhvW84CZobi'

# Define most recent message ID
# recent_id = 8686
recent_id = 8677

# Define number of messages we want to retrieve (for testing)
n_msg = 5
#
#
#
#
#
# define fetching function based on msg number
def fetch_details(msg_number):
    # Initialize an empty dictionary to hold the details
    details = {}

    # Add the message number to the dictionary
    details['id'] = msg_number
    
    # Generate the full URL of the detailed page
    url = f"https://www.mail-archive.com/nmusers@globomaxnm.com/msg{msg_number}.html"
    
    # Fetch the HTML content from the URL
    response = requests.get(url)
    page_content = response.text
    
    # Initialize a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(page_content, 'html.parser')

    # Additional fields for thread details
    thread_section = soup.select_one('div.tSliceList ul.icons')
    
    # Check if the list is empty
    details['is_thread'] = len(thread_section.find_all('li', recursive=False)) == 0 if thread_section else True
                                   
    # Extract message IDs within the thread
    details['thread_message_ids'] = []
    if not details['is_standalone']:
        thread_msgs = thread_section.select('a[href^="msg"]')
        details['thread_message_ids'] = [msg['href'].replace('msg', '').replace('.html', '') for msg in thread_msgs]

    # append id to thread_message_ids
    details['thread_message_ids'].append(msg_number)

    # sort message ids in upscending order
    details['thread_message_ids'] = sorted(details['thread_message_ids'], key=int)
    
    # Extract the date
    date_tag = soup.select_one('span.date a')
    if date_tag:
        details['date'] = date_tag.text.strip()

    # Extract the subject
    subject_tag = soup.select_one('span.subject span[itemprop="name"]')
    if subject_tag:
        details['subject'] = subject_tag.text.strip()

    # Extract the author
    author_tag = soup.select_one('span.sender span[itemprop="name"]')
    if author_tag:
        details['author'] = author_tag.text.strip()
    
    # Extract the message text
    message_tag = soup.select_one('div.msgBody')
    if message_tag:
        details['message'] = message_tag.text.strip()
        
    return details

# define function to create discussion in GitHub repo
def create_discussion(api_token, repository_id, category_id, date, author, title, body, silent):
    # define url
    url = 'https://api.github.com/graphql'

    # define additional information (pre)
    add_inf_pre = f'**Date:** {date}\n**Author:** {author}\n\n'

    # defione additional information (post)
    add_inf_post = f'\n\n---\n\n*Please note: this discussion was automatically created via web scraping of the nmusers mail archive. If you have any questions, please contact the original author of this message. If you are the original author and want your message deleted, you can contact the maintainer at any time.*'

    # replace '"' with '\"' in body
    body = body.replace('"', '\\"')

    # add additional information to body
    body = add_inf_pre + body + add_inf_post

    # define query
    query = f'mutation{{createDiscussion(input: {{repositoryId: "{repository_id}", categoryId: "{category_id}", body: "{body}", title: "{title}"}}) {{discussion {{id}}}}}}'

    # define json
    json = { 'query' : query}

    # define headers
    headers = {'Authorization': 'token %s' % api_token}

    # post request and return json
    r = requests.post(url=url, json=json, headers=headers)

    # print response text if not silent
    if silent == False:
        print(r.text + "\n")
#
#
#
#
#
#
#
# Define vector of message IDs
msg_ids = list(range(recent_id, recent_id - n_msg, -1))

# Convert numerics to strings and paste 0 in front
msg_ids = ["0" + str(x) for x in msg_ids]

# show
msg_ids

# Initialize an empty dictionary to hold the msg information
msg = {}

# Loop through each msg item and extract the details
for msg in msg_ids:
    # Initialize an empty dictionary to hold individual msg info
    single_msg = {}

    # Fetch the details
    single_msg = fetch_details(msg)

    # get rid of messages
    single_msg.pop('message', None)

    # pretty print single message
    pprint(single_msg, indent=4)


#
#
#
#
#
#
#
#
# # Create discussion
# create_discussion(
#     api_token=gh_api_token,
#     title=single_msg['subject'],
#     body=single_msg['message'],
#     date=single_msg['date'],
#     author=single_msg['author'],
#     repository_id = repository_id,
#     category_id = category_id,
#     silent=False
# )

#
#
#
