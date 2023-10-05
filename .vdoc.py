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
import openai
import requests
import time
import json
import random
import re
import pandas as pd
from bs4 import BeautifulSoup
from pprint import pprint

# import own custom functions
from functions import *
#
#
#
#
#
# define pats and api tokens safely via gitignored file 
from my_secrets import gh_api_token
from my_secrets import ai_api_token
#
#
#
#
#
# define if we want to actually create discussions or just test
create_dis_bool = False

# Define repository and category IDs
repository_id = 'R_kgDOKYhvWw'
category_id = 'DIC_kwDOKYhvW84CZobi'

# add headers to requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'
}

# define time until the request times out
timeout = 60

# define max number of retries when scraping
retries = 3

# define sleep time
sleep_time = 0.1

# Hardcoded dictionary for email classification categories
category_dict = {
    "Announcements": "DIC_kwDOKYhvW84CZvWP",
    "Open Positions": "DIC_kwDOKYhvW84CZvWQ",
    "Technicalities": "DIC_kwDOKYhvW84CZvWX",
    "Others": "DIC_kwDOKYhvW84CZvWY"
}

# define categories for eamil classification
categories = list(category_dict.keys())

# define chatgpt model
model = "gpt-3.5-turbo"
# model = "gpt-4"

# sample vector of message IDs
n_msg = 100
recent_id = 8691
my_array = list(range(1, recent_id))
msg_ids = random.sample(my_array, n_msg)
#
#
#
#
#
#
#
#| results: asis
# Convert numerics to strings and paste 0 in front
msg_ids = [str(num).zfill(5) for num in msg_ids]

# show
msg_ids

# Initialize an empty dictionary to hold the msg information
msg = {}

# Loop through each msg id, extract the details and append
for id in msg_ids:

    # Fetch the details
    single_msg = fetch_details(
        msg_number = id,
        headers = headers,
        timeout = timeout,
        retries = retries
    )

    # sleep for n seconds
    time.sleep(sleep_time)

    # Append to msg
    msg[id] = single_msg


# Extract threads
thread_dict = extract_threads(msg)

# Fetch any missing messages in the threads
fetch_missing_messages(
    thread_dict = thread_dict,
    msg = msg,
    headers = headers,
    timeout = timeout,
    retries = retries,
    first_only = True
)

# print the result
pprint(thread_dict, indent=4)
#
#
#
#
#
#
#
# init data list
data_list = []

# Loop through each element in the dictionary
for thread_id, thread_info in thread_dict.items():

    # define initial message id
    inital_msg_id = thread_info['ids'][0]

    # retrieve initial thread starting message
    cur_msg = msg[inital_msg_id]

    # store data from message
    data = {
        'id': cur_msg['id'],
        'date': cur_msg['date'],
        'subject': cur_msg['subject'],
        'message': cur_msg['message']
    }
    
    # append data to list
    data_list.append(data)

# Convert the list of dictionaries into a pandas DataFrame
df = pd.DataFrame(data_list)

# add empty column for labels and category
df['category'] = ''
df['labels'] = ''

# Save the DataFrame to a CSV file
df.to_csv('train_df_raw.csv', index=False)

# print the result
pprint(df, indent=4)
#
#
#
