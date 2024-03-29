import os
import shutil

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

base_path = 'https://pastpapers.co/cie/'

# Create a requests session
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


def fetch_table_content(url):
    try:
        # Fetch the HTML content from the URL with timeout and session
        response = session.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table element (assuming there's only one table)
    table = soup.find('table')

    # Check if a table was found
    if not table:
        print("No table found on the webpage")
        return None

    # Extract rows from the table
    rows = table.find_all('tr')

    # Extract data from each row
    table_data = []
    for row in rows:
        columns = row.find_all('td')
        for col in columns:
            # find nested <a> tag in col
            link = col.find('a')
            # access href attribute of link
            if link:
                path = link.get('href')
                # If link isn't ends with a file extension or doesn't start with https
                if path and not path.startswith('https') and path != '..':
                    if path.endswith(('.pdf', '.mp3', '.mp4')):
                        print("Downloading...", base_path + path)
                        # Download the file
                        handle_preview_download(base_path + path)
                    else:
                        # if path is the subpath of current url, skip
                        if path.startswith(url):
                            continue
                        print("Getting into...", base_path + path)
                        fetch_table_content(base_path + path)

    return table_data

def handle_preview_download(url):
        # If the file with the same name already exists, skip downloading
    if os.path.exists('./downloads/' + url.split('/')[-1]):
        print(f"File already exists: {url.split('/')[-1]}")
        return None

    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table element (assuming there's only one table)
    table = soup.find('iframe')

    # get the src attribute of iframe
    path = table.get('src')

    # download the file
    download_file(path)



def download_file(url):
    # Download the file
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the file: {response.status_code}")
        return None

    # Extract the file name from the URL
    file_name = url.split('/')[-1]

    # Save the file into './downloads' folder
    if (file_name.endswith('#view=FitH') or file_name.endswith('#view=FitV')):
        file_name = file_name[:-10]
        
    # If the file is empty, skip downloading
    if len(file_name) == 0:
        print(f"File is empty: {url}")
        return None
    
    # Append the file name and download url and file size into a csv file
    if not os.path.exists('./downloads/links.csv') or os.path.getsize('./downloads/links.csv') == 0:
        with open('./downloads/links.csv', 'w') as f:
            f.write('file_name,url,file_size\n')
    with open('./downloads/links.csv', 'a') as f:
        f.write(file_name + ',' + url + ',' + str(len(response.content)) + '\n')
    with open('./downloads/' + file_name, 'wb') as f:
        f.write(response.content)


def house_keeping():
    folder = './downloads'
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # delete file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # delete folder
                # Create .gitignore file
                with open('./downloads/.gitignore', 'w') as f:
                    f.write('.*\n')
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

# Clear downloads folder before downloading
# house_keeping()


# Example usage
url = 'https://pastpapers.co/cie/?dir=IGCSE/Chinese-First-Language-0509'  # Replace with the actual URL
data = fetch_table_content(url)

if data:
    for row in data:
        row = '\t'.join(row)
