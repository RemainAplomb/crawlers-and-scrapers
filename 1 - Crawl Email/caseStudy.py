

# Installation guide(s)
# Python env:
#       (base) PS E:\assessment\VentureBNB> python --version
#       Python 3.9.12
# For imapclinet:
#       pip install imapclient
# For pandas:
#       pip install pandas
# For beautiful soup:
#       pip install beautifulsoup4


# Imports
import imapclient # to access email
import pandas as pd # for data manipulation
from bs4 import BeautifulSoup #For manipulating/extracting data from html email
import json # Just to retrieve our credentials
import re # For searching

# Initialize the global variables
PORT = 993
server = imapclient.IMAPClient('imap.gmail.com', port=PORT)

# Credentials
# Sample of credentials.JSON
# {
#     "email": "someRandomEmail@gmail.com",
#     "password": "someRandomAppPassword"
#   }
## To get app-selected password, follow these steps:
##      - Go to Manage Google Account -> 2-Step Verification -> App Password
##      - Select app that can be accessed by the password
##      - Select device where the password can be used
##      - Generate
## Note:
##      - Once no longer in use, remove the generated app password
##      - In a real-life application, the password should be more 
##        secured. Using a JSON file where the keys are stored would help. 
##        (Edit: Decided to add it afterall)
def load_credentials(file_path):
    with open(file_path, 'r') as file:
        credentials = json.load(file)
    return credentials["email"], credentials["password"]

def server_login():
    EMAIL, APP_PASSWORD = load_credentials("./credentials.JSON")

    server.login(EMAIL, APP_PASSWORD)
    server.select_folder('INBOX')

def server_logout():
    server.logout()

# Extract the specific header parts
# Pattern goes like {headername}: {someRandomValue}
def extract_header_value(headers, header_name):
    pattern = r'^{}:\s*(.*?)\r?$'.format(re.escape(header_name))
    match = re.search(pattern, headers, re.MULTILINE)
    # print(match.group(1))
    if match:
        return match.group(1).strip()
    return None





# 1 - Read in 20 emails from your personal email and pull out any emails that are from
#     "john@venturebnb.io" and include "Traveler Housing Request" in the subject line
# Parameters:
#   subject_keywords: What should be found in the email subject. Does not necessarily have to be exact. This parameter is a must
#   sender: the email of the sender. If left none, we will only search using subject keywords. Optional parameter
#   num_emails:
#           - If not direct search, it will look at the latest n number of emails. Where n is num_emails.
#           - If direct search, it will only take a maximum of n number of emails that matches the condition.
#   direct_search:
#           - If not direct search, it will have to manually loop through the latest n number of emails to look for matches
#           - If direct search, it will use the search function from imapclient
#   
def ReadInFurnishedFinderHousingRequestsEmails(subject_keywords=None, sender=None, num_emails=20, direct_search=False):
    # TODO: write the code for this function to return the emails that qualify
    if not subject_keywords:
        return []
    
    if not direct_search:
        # Retrieve the newest num_emails emails
        messages = server.search('ALL')[-num_emails:]

        # Fetch the content of the retrieved emails
        emails = []
        for msg_id in messages:
            # Extract email headers
            headers = server.fetch([msg_id], ['RFC822.HEADER'])
            email_headers = headers[msg_id][b'RFC822.HEADER']
            email_headers = email_headers.decode('utf-8')

            # Extract sender and subject from headers
            email_sender = extract_header_value(email_headers, 'From')
            email_subject = extract_header_value(email_headers, 'Subject')

            # print("Email sender: ", email_sender)
            # print("Email subject: ", email_subject)

            if email_sender and email_subject:
                # print(f"Sender: {email_sender}, Expected: {sender}")
                # print(f"Subject: {email_subject}, Expected Keywords: {subject_keywords}")
                if sender:
                    if sender in email_sender and subject_keywords in email_subject:
                        email_data = server.fetch([msg_id], ['BODY[]', 'FLAGS'])
                        email = email_data[msg_id][b'BODY[]']
                        emails.append(email)
                elif not sender:
                    if subject_keywords in email_subject:
                        email_data = server.fetch([msg_id], ['BODY[]', 'FLAGS'])
                        email = email_data[msg_id][b'BODY[]']
                        emails.append(email)
    else:
        # Determine the condition for searching
        if not sender:
            search_condition = f'SUBJECT "{subject_keywords}"'
        else:
            search_condition = f'SUBJECT "{subject_keywords}" FROM "{sender}"'

        # Search for emails with the specified subject and sender
        messages = server.search(search_condition)

        # Limit the number of retrieved emails
        messages = messages[:num_emails]

        # Fetch the content of the retrieved emails
        emails = []
        for msg_id in messages:
            email_data = server.fetch([msg_id], ['BODY[]', 'FLAGS'])
            email = email_data[msg_id][b'BODY[]']
            emails.append(email)

    return emails

# 2 - Loop through the emails and put the following information from each email into
#     a new row of a pandas dataframe: Tenant, Email Address, Phone Number, 
#     number of travelers, and dates.
def PullInformationFromEmailsAndPutIntoDataframe(emails):
    # TODO: write the code for this function to return the full dataframe

    dataframe = pd.DataFrame(columns=['Tenant', 'Email Address', 'Phone Number', 'Number of Travelers', 'Dates'])

    for email in emails:
        try:
            # Decode the email from bytes to string using UTF-8 encoding
            email = email.decode('utf-8')

            # Note:
            #   - Too many whitespaces, had to remove it
            email = email.replace('=\n', '').replace('\r', '').replace('=\n', '').replace('\r', '')

            soup = BeautifulSoup(email, 'html.parser')

            # Note:
            #   - In real-life application, adding id would certainly make it easier to crawl
            tenant = soup.find('p', string='Tenant:').find_next('p').text.strip() 
            email_address = soup.find('p', string='Email:').find_next('p').text.strip()
            phone_number = soup.find('p', string='Phone #:').find_next('p').text.strip()
            num_travelers = soup.find('p', string='Travelers:').find_next('p').text.strip()
            dates = soup.find('p', string='Dates:').find_next('p').text.strip()

            row = {
                'Tenant': tenant,
                'Email Address': email_address,
                'Phone Number': phone_number,
                'Number of Travelers': num_travelers,
                'Dates': dates
            }
            dataframe = pd.concat([dataframe, pd.DataFrame([row])], ignore_index=True)
        except Exception as e:
            print("Error: ", e)

    return dataframe


if __name__ == "__main__":
    server_login()
    print("\n===============================================================\n")
    # Test 1
    # No sender info
    # with subject keywords
    # Not direct search
    # look into latest 100 emails
    emails = ReadInFurnishedFinderHousingRequestsEmails(subject_keywords="Traveler Housing Request", num_emails=20)
    # print(len(emails))
    
    dataframe = PullInformationFromEmailsAndPutIntoDataframe(emails)
    print('Test 1: (subject_keywords="Traveler Housing Request", num_emails=20)')
    print(dataframe)

    print("\n===============================================================\n")

    # Test 2
    # No sender info
    # with subject keywords
    # Not direct search
    # look into latest 100 emails
    emails = ReadInFurnishedFinderHousingRequestsEmails(subject_keywords="Traveler Housing Request", num_emails=100)
    # print(len(emails))
    
    dataframe = PullInformationFromEmailsAndPutIntoDataframe(emails)
    print('Test 2: (subject_keywords="Traveler Housing Request", num_emails=100)')
    print(dataframe)

    print("\n===============================================================\n")

    # Test 3
    # With sender info
    # with subject keywords
    # Not direct search
    # look into latest 100 emails
    emails = ReadInFurnishedFinderHousingRequestsEmails(subject_keywords="Traveler Housing Request", sender="software@venturebnb.io", num_emails=100)
    # print(len(emails))
    
    dataframe = PullInformationFromEmailsAndPutIntoDataframe(emails)
    print('Test 3: (subject_keywords="Traveler Housing Request", sender="software@venturebnb.io", num_emails=100)')
    print(dataframe)

    print("\n===============================================================\n")

    # Test 4
    # With sender info
    # with subject keywords
    # Use direct search (will only take matching emails by directly using the given condition to search)
    # look into latest 100 emails
    emails = ReadInFurnishedFinderHousingRequestsEmails(subject_keywords="Traveler Housing Request", sender="software@venturebnb.io", direct_search=True, num_emails=100)
    # print(len(emails))
    
    dataframe = PullInformationFromEmailsAndPutIntoDataframe(emails)
    print('Test 4: (subject_keywords="Traveler Housing Request", sender="software@venturebnb.io", direct_search=True, num_emails=100)')
    print(dataframe)

    print("\n===============================================================\n")

    # Test 5
    # With sender info
    # with subject keywords
    # Use direct search (will only take matching emails by directly using the given condition to search)
    # look into latest 100 emails
    emails = ReadInFurnishedFinderHousingRequestsEmails(subject_keywords="Traveler Housing Request", sender="john@venturebnb.io", direct_search=True, num_emails=100)
    # print(len(emails))
    
    dataframe = PullInformationFromEmailsAndPutIntoDataframe(emails)
    print('Test 5: (subject_keywords="Traveler Housing Request", sender="john@venturebnb.io", direct_search=True, num_emails=100)')
    print(dataframe)

    print("\n===============================================================\n")

    # Test 6
    # No sender info
    # with subject keywords
    # Use direct search (will only take matching emails by directly using the given condition to search)
    # look into latest 100 emails
    emails = ReadInFurnishedFinderHousingRequestsEmails(subject_keywords="Traveler Housing Request", direct_search=True, num_emails=100)
    # print(len(emails))
    
    dataframe = PullInformationFromEmailsAndPutIntoDataframe(emails)
    print('Test 6: (subject_keywords="Traveler Housing Request", direct_search=True, num_emails=100)')
    print(dataframe)

    print("\n===============================================================\n")

    server_logout()

"""
Testing caseStudy.py: 

(base) PS E:\assessment\venturebnb> python caseStudy.py

===============================================================

Test 1: (subject_keywords="Traveler Housing Request", num_emails=20)
Empty DataFrame
Columns: [Tenant, Email Address, Phone Number, Number of Travelers, Dates]
Index: []

===============================================================

Test 2: (subject_keywords="Traveler Housing Request", num_emails=100)
         Tenant     Email Address Phone Number Number of Travelers                     Dates
0    Mark Frank    mark@yahoo.com   8284763558                   2  03/26/2023 -- 05/13/2023
1  Lauren James  lauren@yahoo.com   8284763558                   2  03/26/2023 -- 05/13/2023

===============================================================

Test 3: (subject_keywords="Traveler Housing Request", sender="software@venturebnb.io", num_emails=100)
         Tenant     Email Address Phone Number Number of Travelers                     Dates
0    Mark Frank    mark@yahoo.com   8284763558                   2  03/26/2023 -- 05/13/2023
1  Lauren James  lauren@yahoo.com   8284763558                   2  03/26/2023 -- 05/13/2023

===============================================================

Test 4: (subject_keywords="Traveler Housing Request", sender="software@venturebnb.io", direct_search=True, num_emails=100)
         Tenant     Email Address Phone Number Number of Travelers                     Dates
0    Mark Frank    mark@yahoo.com   8284763558                   2  03/26/2023 -- 05/13/2023
1  Lauren James  lauren@yahoo.com   8284763558                   2  03/26/2023 -- 05/13/2023

===============================================================

Test 5: (subject_keywords="Traveler Housing Request", sender="john@venturebnb.io", direct_search=True, num_emails=100)
Empty DataFrame
Columns: [Tenant, Email Address, Phone Number, Number of Travelers, Dates]
Index: []

===============================================================

Test 6: (subject_keywords="Traveler Housing Request", direct_search=True, num_emails=100)
         Tenant     Email Address Phone Number Number of Travelers                     Dates
0    Mark Frank    mark@yahoo.com   8284763558                   2  03/26/2023 -- 05/13/2023
1  Lauren James  lauren@yahoo.com   8284763558                   2  03/26/2023 -- 05/13/2023

===============================================================
"""
