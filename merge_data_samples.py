'''
Merges data from two sets of google-scraped data.
'''


import json
from collections import defaultdict

output_data = defaultdict(dict)

indata_1 = open('sample_1.json', 'r')
data1 = json.loads(indata_1.read())
indata_1.close()

indata_2 = open('sample_2.json', 'r')
data2 = json.loads(indata_2.read())
indata_2.close()

for item in data1.items():
	name = item[0]
	output_data[name].update(item[1])
	output_data[name].update(data2[name])


import ipdb; ipdb.set_trace()

with open('final_data.json', 'w') as fp:
			json.dump(output_data, fp)