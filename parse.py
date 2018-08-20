import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from time import sleep
from datetime import datetime, timedelta
import random

df = pd.DataFrame(columns=["freq", "name", "start", "end", "language", "pwr", "city", "longitude", "latitude", "bearing", "distance"])

def lookup(f, wd, tme):

	url = "http://www.short-wave.info/index.php"
	r = requests.get(url, params={"freq": f})

	s = BeautifulSoup(r.text, "lxml")
	table = s.find("table", id="output")

	stations = []
	table_text=[]

	if table is None:
		return

	for tr in table.findAll('tr'):
		table_text=[]
		tds = tr.findAll('td')
		for td in tds:
			table_text.append(td.get_text())
		stations.append(table_text)


	time_ref = datetime.strptime(tme, "%H:%M")

	for row in stations:
		if row != []:
			if row[8].startswith("?"):
				row[8] = row[8].replace('?', "Unknown")

			start = datetime.strptime(row[2], "%H:%M")
			end = datetime.strptime(row[3], "%H:%M")

			if intimeperiod(start, end, time_ref) and str(wd) in list(row[4]):

				t = re.findall("[\w ]+[^ ]*?(?=Latitude|Longitude|Bearing|Distance|$)", row[8])

				try:
					print("{0} - [{1}-{2}] - {3} - {4} - {5}kW - [{6} - {7} - {8} - {9} - {10}]".format(row[1], row[2], row[3], row[4], row[5], row[6], t[0], t[1], t[2], t[3], t[4]))

					global df
					df = df.append({"freq":f, "name":row[1], "start":row[2], "end":row[3], "language":row[5], "pwr":row[6], "city":t[0], "longitude":t[1], "latitude":t[2], "bearing":t[3], "distance":t[4]}, ignore_index=True)
				except:
					print("regex has failed")

def intimeperiod(start, end, ref):
	if end < start:
		end += timedelta(days=1)

	return ref >= start and ref <= end

if __name__ == '__main__':

	d = pd.read_csv("input.csv")

	for index, row in d.iterrows():
		lookup(row["f"], row["day"], row["time"])
		sleep(random.randint(5, 20))

	with open('stations.csv', 'w') as f:
		df.to_csv(f, header=True)




