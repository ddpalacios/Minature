import requests
from bs4 import BeautifulSoup

url = 'https://www.noiiz.com/sounds/instruments/97'

# Send an HTTP request to the website
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the 'a' tags with href attribute containing '.wav'
    wav_links = soup.find_all('a', href=lambda href: href and href.endswith('.wav'))

    # Print the WAV file links
    for link in wav_links:
        print(link['href'])
else:
    print(f"Request failed with status code: {response.status_code}")
