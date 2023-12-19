import os
import shutil

import requests
from bs4 import BeautifulSoup

base_path = 'https://pastpapers.co/cie/'


def fetch_table_content(url):
    # Fetch the HTML content from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {response.status_code}")
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
                if path and not path.startswith('https'):
                    if path.endswith(('.pdf', '.mp3', '.mp4')):
                        print("Downloading...", base_path + path)
                        # Download the file
                        handle_preview_download(base_path + path)
                    else:
                        print("Getting into...", base_path + path)
                        fetch_table_content(base_path + path)

        row_data = [col.text.strip() for col in columns]
        if row_data:
            table_data.append(row_data)

    return table_data

def handle_preview_download(url):
        # If the file with the same name already exists, skip downloading
    if os.path.exists('./downloads/' + url.split('/')[-1]):
        print(f"File already exists: {url.split('/')[-1]}")
        return None


    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {response.status_code}")
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
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the file: {response.status_code}")
        return None
    # Extract the file name from the URL
    file_name = url.split('/')[-1]
    # Save the file into './downloads' folder
    if (file_name.endswith('#view=FitH') or file_name.endswith('#view=FitV')):
        file_name = file_name[:-10]
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
url = 'https://pastpapers.co/cie/?dir=IGCSE/Chinese-Mandarin-Foreign-Language-0547'  # Replace with the actual URL
data = fetch_table_content(url)

if data:
    for row in data:
        # print(row)
        # print("end")
        row = '\t'.join(row)
