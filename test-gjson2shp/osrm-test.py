import requests
start = '50.12345,8.12345'
stop = '50.23456,8.23456'

headers = {'User-Agent': 'Your User-Agent verification'}
url = 'http://router.project-osrm.org/viaroute?loc=' + start + '&loc=' + stop
response = requests.get(url, headers=headers)

print(response)
