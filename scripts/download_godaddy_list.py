#!python
import shutil
import urllib.request as request
from contextlib import closing
from urllib.error import URLError
import os
import arrow
import zipfile
import json

service_name = "godaddy"
list_url = "ftp://auctions@ftp.godaddy.com/all_listings_ending_tomorrow.json.zip"
filename = "all_listings_ending_tomorrow"
date_format = "M-DD-YYYY"
timezone = "America/New_York"
local = arrow.now(timezone)
scripts_dir = os.path.dirname(os.path.abspath(__file__))
lists_dir = os.path.join(scripts_dir, '..', 'lists')

# download dates
tomorrow = local.shift(days=1).format(date_format)

def in_x_days(num_days):
	return local.shift(days=num_days).format(date_format)
	
all_download_times = [tomorrow]

def reformat(name):
	domains = []
	
	with open(f"{lists_dir}/{service_name}/{name}.json", 'r') as fx:
		jsonData = json.load(fx)
		for domain in jsonData['data']:
			domains.append(domain['domainName'].lower())
	
	with open(f"{lists_dir}/{service_name}/{name}.txt", 'w') as fx:
		fx.write("\n".join(domains))
	
	os.remove(f"{lists_dir}/{service_name}/{name}.json")

if not os.path.exists(f"{lists_dir}/{service_name}"):
	os.makedirs(f"{lists_dir}/{service_name}")
for dl_time in all_download_times:
	url = list_url
	try:
		with closing(request.urlopen(url)) as r:
			source_path = os.path.join(f"{lists_dir}/{service_name}", f"{filename}.json")
			dest_path = os.path.join(f"{lists_dir}/{service_name}", f"{dl_time}.json")
			zip_path = os.path.join(f"{lists_dir}/{service_name}", f"{dl_time}.zip")
			path = os.path.join(f"{lists_dir}/{service_name}", f"{dl_time}.txt")
			if not os.path.exists(path):
				with open(zip_path, 'wb') as f:
					shutil.copyfileobj(r, f)
				with zipfile.ZipFile(zip_path, 'r') as zip_ref:
					zip_ref.extractall(f"{lists_dir}/{service_name}")
				os.rename(source_path, dest_path)
				os.remove(zip_path)
				reformat(dl_time)
				print(f"Downloaded {service_name} list: {dl_time}")
	except URLError as e:
		print(f"Could not download {service_name} list: {dl_time}")
		if e.reason.find('No such file or directory') >= 0:
			raise Exception('FileNotFound')
		else:
			raise Exception(f'Something else happened. "{e.reason}"')