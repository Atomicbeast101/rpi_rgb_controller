import requests
import sys
import random

URL = 'http://{}:5000/rgb/api/'.format(sys.argv[1])
if sys.argv[3] == 'set':
	num = random.choice([1, 2, 3])
	if num == 1:
		URL += 'set_color?token={}&red=255.0&green=0.0&blue=0.0'.format(sys.argv[2])
	elif num == 2:
		URL += 'set_color?token={}&red=0.0&green=255.0&blue=0.0'.format(sys.argv[2])
	else:
		URL += 'set_color?token={}&red=0.0&green=0.0&blue=255.0'.format(sys.argv[2])
elif sys.argv[3] == 'lowb':
	URL += 'set_brightness?token={}&brightness=150'.format(sys.argv[2])
elif sys.argv[3] == 'highb':
	URL += 'set_brightness?token={}&brightness=255'.format(sys.argv[2])
elif sys.argv[3] == 'on':
	URL += 'toggle?token={}&activate=on'.format(sys.argv[2])
elif sys.argv[3] == 'off':
	URL += 'toggle?token={}&activate=off'.format(sys.argv[2])
else:
	print('Dont understand your demand.')

r = requests.post(url=URL)
print(r.text)
