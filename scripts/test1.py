import requests
import json

headers = {'User-Agent': 'Mozilla/5.0'}

# Crossref API
print('=== Crossref API ===')
url = 'https://api.crossref.org/works?query.bibliographic=Sustainability+Analytics+and+Modeling&rows=5'
r = requests.get(url, headers=headers, timeout=30)
print('Status:', r.status_code)
data = r.json()
for item in data['message']['items']:
    print('Title:', item.get('title'))
    print('Container:', item.get('container-title'))
    print('Published:', item.get('published'))
    print('Pages:', item.get('page'))
    print('DOI:', item.get('DOI'))
    print('---')
