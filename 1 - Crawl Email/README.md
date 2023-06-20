# Email Crawling

## Brief Description

    Folder Name: 1 - Crawl Email
    Environment:
        - Python 3.9.12

## Installation/Dependencies

### imapclient

We will need imapclient to login to our gmail account.
To do that, use pip to install:

```
pip install imapclient
```

Another thing to note, google has now increased its security.
As such, we will need to either turn off 2-factor authentication
or create an app specific password.

I suggest creating an app specific password, you can do it by:

```
    - Go to Manage Google Account -> 2-Step Verification -> App Password
    - Select app that can be accessed by the password
    - Select device where the password can be used
    - Generate
```

### Pandas

Since we will need to put our crawled data into a dataframe,
We will need the pandas library:

```
pip install pandas
```

### Beautiful Soup

The beautiful soup will allow us to manipulate the email that
have html. Install it using this command:

```
pip install beautifulsoup4
```

## Edit credentials.JSON

The credentials.JSON will contain the details of our account.
You will need to edit it to suit your needs:

```
{
    "email": "someRandomEmail@gmail.com",
    "password": "someRandomPassword"
}
```
