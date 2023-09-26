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
from bs4 import BeautifulSoup
#
#
#
#
#
# define token safely via gitignored file 
from secrets import api_token
#
#
#
#
#
# define global parameters
repository_id = 'R_kgDOKYhvWw'
category_id = 'DIC_kwDOKYhvW84CZobi'
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
    url = f"https://www.mail-archive.com/nmusers@globomaxnm.com/msg{msg_number}.html"
    
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
    message_tag = soup.select_one('div.msgBody')
    if message_tag:
        details['message'] = message_tag.text.strip()
        
    return details

# define function to create discussion in GitHub repo
def create_discussion(api_token, repository_id, category_id, title, body, silent):
    # define url
    url = 'https://api.github.com/graphql'

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
        print(r.text)
#
#
#
#
#
#
#
# Define number of messages we want to retrieve (for testing)
n_msg = 3

# Define most recent message ID
recent_id = 8686

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
    
    # print msg
    print(single_msg)
#
#
#
#
#
#
# create discussion
create_discussion(
    api_token=api_token,
    title="Parameter based",
    body="Parameter based",
    repository_id = repository_id,
    category_id = category_id,
    silent=False
)
#
#
#
