# Web Crawling using Selenium

## Brief Description

    Folder Name: 2 - Crawl Web Novel Site
    Environment:
        - Python 3.9.12

## Installation/Dependencies

### Selenium

To crawl websites efficiently, we will need to install
Selenium. It is done using this command:

```
pip install selenium
```

### Pandas

Since we will need to put our crawled data into a dataframe,
We will need the pandas library:

```
pip install pandas
```

### Pillow

To handle images, we will need the pillow library:

```
pip install Pillow
```

Please note that you will need to have the folder "downloads".
If not, the images and csv will have nowhere to be placed.

## Automatic directory creation

If you want to automatically create the folder where you
will palce your images and csv, you can do this:

```
import os

""" Creating a directory """
def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

create_dir(DOWNLOAD_FOLDER)
```
