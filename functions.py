
# load packages
import openai
import requests
import json
from bs4 import BeautifulSoup
from pprint import pprint

######################################################################################
############################### fetch_details ########################################
######################################################################################

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
    details['is_standalone'] = len(thread_section.find_all('li', recursive=False)) == 0 if thread_section else True
                                   
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


######################################################################################
############################### create_discussion ####################################
######################################################################################

# define function to create discussion in GitHub repo
def create_discussion(api_token, repository_id, category_id, date, author, title, body):
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

    # define json paylod
    json_payload  = { 'query' : query}

    # define headers
    headers = {'Authorization': 'token %s' % api_token}

    # post request and return json
    r = requests.post(url=url, json=json_payload, headers=headers)

    # return response text and store as dict
    return json.loads(r.text)


#######################################################################################
############################ add_comment_to_discussion ################################
#######################################################################################

# Function to add a comment to an existing discussion in GitHub
def add_comment_to_discussion(api_token, discussion_id, body, date, author, silent):
    # Define GraphQL URL
    url = 'https://api.github.com/graphql'

    # define additional information (pre)
    add_inf_pre = f'**Date:** {date}\n**Author:** {author}\n\n'

    # defione additional information (post)
    add_inf_post = f'\n\n---\n\n*Please note: this discussion was automatically created via web scraping of the nmusers mail archive. If you have any questions, please contact the original author of this message. If you are the original author and want your message deleted, you can contact the maintainer at any time.*'
    
    # Replace '"' with '\"' in body
    body = body.replace('"', '\\"')

    # add additional information to body
    body = add_inf_pre + body + add_inf_post
    
    # Define GraphQL query for adding a comment
    query = f'''mutation{{
        addDiscussionComment(input: {{ body: "{body}", discussionId: "{discussion_id}"}}) {{
            comment {{
                id
            }}
        }}
    }}'''
    
    # Define JSON payload
    json_payload  = {'query': query}
    
    # Define headers
    headers = {'Authorization': f'token {api_token}'}
    
    # Make POST request
    r = requests.post(url=url, json=json_payload, headers=headers)
    
    # Print response if not silent
    if not silent:
        print(r.text + "\n")

#######################################################################################
################################ extract_threads ######################################
#######################################################################################

# function to extract the threads from a list of messages
def extract_threads(messages_dict):
    thread_dict = {}
    thread_id = 1  # Starting thread ID

    # To keep track of messages that are already part of a thread
    seen_messages = set() 

    # Loop through each message
    for msg_id, msg in messages_dict.items():
        
        # Skip this message if it's already part of a thread
        if msg_id in seen_messages:
            continue
        
        # Extract the thread message IDs
        thread_message_ids = msg['thread_message_ids']
        
        # add threads
        thread_dict[thread_id] = thread_message_ids
        thread_id += 1
        
        # Mark all messages in this thread as seen
        seen_messages.update(thread_message_ids)
            
    return thread_dict

#######################################################################################
############################### fetch_missing_messages ################################
#######################################################################################

# Function to fetch missing messages in thread_dict and add them to msg dictionary
def fetch_missing_messages(thread_dict, msg):
    for thread_id, msg_list in thread_dict.items():
        for msg_id in msg_list:
            if msg_id not in msg:
                # Fetch missing message details
                fetched_msg = fetch_details(msg_id)
                
                # Add the fetched message to msg dictionary
                msg[msg_id] = fetched_msg



#######################################################################################
############################### delete_discussion #####################################
#######################################################################################

# Function to delete a discussion by its ID
def delete_discussion(api_token, discussion_id):
    # Define GraphQL URL
    url = 'https://api.github.com/graphql'
    
    # Define GraphQL query for deleting a discussion
    query = f'''mutation{{
        deleteDiscussion(input: {{ id: "{discussion_id}" }}) {{
            clientMutationId
        }}
    }}'''
    
    # Define JSON payload
    json_payload  = {'query': query}
    
    # Define headers
    headers = {'Authorization': f'token {api_token}'}
    
    # Make POST request
    r = requests.post(url=url, json=json_payload, headers=headers)
    
    # Check for errors
    if r.status_code == 200:
        print(f'Successfully deleted discussion with ID {discussion_id}.')
    else:
        print(f'Failed to delete discussion with ID {discussion_id}. Error: {r.text}')



#######################################################################################
############################### list_all_discussions ##################################
#######################################################################################

# Function to list all discussions by repository ID
def list_all_discussions(api_token, repository_id):
    # Define GraphQL URL
    url = 'https://api.github.com/graphql'

    # Define GraphQL query for fetching discussions
    query = f'''
    query {{
      node(id: "{repository_id}") {{
        ... on Repository {{
          discussions(first: 100) {{
            nodes {{
              id
              title
            }}
          }}
        }}
      }}
    }}
    '''
    
    # Define JSON payload
    json_payload  = {'query': query}

    # Define headers
    headers = {'Authorization': f'token {api_token}'}

    # Make POST request
    r = requests.post(url=url, json=json_payload, headers=headers)

    # Parse the JSON response
    discussions_data = json.loads(r.text)

    # Extract discussion ids and titles
    discussions = [(d['id'], d['title']) for d in discussions_data['data']['node']['discussions']['nodes']]

    return discussions

#######################################################################################
############################### get_chat_completion ###################################
#######################################################################################

def get_chat_completion(api_key, categories, message_text, model):

    # Set OpenAI API key
    openai.api_key = api_key
    
    # Construct the messages
    messages = [
        {"role": "system", "content": f"You are a machine which classifies emails by content. You can only speak 4 words = categories: {', '.join(categories)}    Your output is directly used as a string for the category. If you deviate from the 4 words, the program will fail and you will be punished. Even a . after the category can crash the program so stick exactly to the categories provided and do not deviate. Please include Webinars to Announcements. "},
        {"role": "user", "content": message_text}
    ]
    
    # Make API request
    chat_completion = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    
    # Extract and return the content
    return chat_completion["choices"][0]["message"]["content"]



###########################################################################################
############################### add_labels_to_discussion ##################################
###########################################################################################

# Function to add a set of labels to an existing discussion in GitHub
def add_labels_to_discussion(api_token, discussion_id, labels):
    # Define GraphQL URL
    url = 'https://api.github.com/graphql'
    
    # Convert the list of labels to GraphQL array format
    graphql_labels = json.dumps(labels)
    
    # Define GraphQL query for adding labels
    query = f'''
    mutation{{
        addLabelsToLabelable(input: {{ labelableId: "{discussion_id}", labelIds: {graphql_labels} }}) {{
            clientMutationId
        }}
    }}
    '''
    
    # Define JSON payload
    json_payload = {'query': query}
    
    # Define headers
    headers = {'Authorization': f'token {api_token}'}
    
    # Make POST request
    r = requests.post(url=url, json=json_payload, headers=headers)
    
    # Check for errors
    if r.status_code == 200:
        print(f'Successfully added labels to discussion with ID {discussion_id}.')
    else:
        print(f'Failed to add labels to discussion with ID {discussion_id}. Error: {r.text}')
