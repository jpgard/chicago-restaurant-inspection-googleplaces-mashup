import requests, json, sys, re, csv
from collections import defaultdict




def get_reviews(placeid):
	'''
	Fetches reviews using Google Places API, returning a list of reviews. 

	Note: not all restaurants have reviews. Google limits the output to a maximum of five reviews.
	'''
	baseurl = 'https://maps.googleapis.com/maps/api/place/details/json?' 
	api_url = baseurl + 'placeid=' + placeid + '&key=' + api_key
	data = requests.get(api_url)
	output = []
	rjson = data.json()

	reviews = rjson['result']['reviews']

	for review in reviews:
		output.append((review['rating'], review['text']))

	return output


def place_search_for_id(api_key, query, latitude, longitude):
	'''
	Finds Google place ID using name, latitude, and longitude. This place id is needed to search for reviews and other information in Google Places.

	Adjust parameters below as necessary.
	'''

	baseurl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
	location = latitude + ',' + longitude
	radius = '1000' #radius, in meters, to search around lat & long -- helps to avoid restaurants w/duplicate names
	api_url = baseurl +  '&query=' + query + '&location' + location + '&radius' + radius + '&key=' + api_key
	data = requests.get(api_url)

	rjson = data.json()
	try: 
		place_id = rjson['results'][0]['place_id']
	except IndexError:
		place_id = None

	return place_id

def make_data(infile):
	'''
	Reads data from Chicago Food Inspections csv file and organizes into dictionary.
	'''

	data = defaultdict(dict)

	rawdata = open(infile)
	lines = csv.reader(rawdata)

	for line in lines:
		
		try:
			

			inspection_id = line[0]
			
			#create dictionary with inspection id as key
			data[inspection_id]['name'] = line[2]
			data[inspection_id]['facility_type'] = line[4]
			data[inspection_id]['risk'] = re.findall(r'\d+', line[5])
			data[inspection_id]['address'] = line[6]
			city = line[7]
			# state = line[8] no state needed -- all in Illinios
			data[inspection_id]['ZIP'] = line[9]
			data[inspection_id]['inspection_date'] = line[10]
			data[inspection_id]['inspection_type'] = line[11]
			data[inspection_id]['results'] = line[12]
			data[inspection_id]['violationstext'] = line[13] #note: this is raw text; may want to split into list of separate violations (they are a numbered list--numbered by rule?)
			data[inspection_id]['lat'] = line[14]
			data[inspection_id]['long'] = line[15]
		except IndexError:
			print 'excluding line: \n'
			print line

	return data



def reviewsToData(data):
	'''
	takes dictionary of places as input in format produced by make_data; looks up Google Places reviews and adds them to dictionary entry for that place in data.
	'''

	counter = 0

	for item in data.items():
		
		id = place_search_for_id(api_key, item[1]['name'], item[1]['lat'], item[1]['long'])

		if id:
			print "%s - Building data for %s ID: %s" % (counter, item[1]['name'], id)

			try: 
				reviews = get_reviews(id)
				data[item[0]]['reviews'] = reviews
			except KeyError:
				print 'No reviews for %s' % (item[1]['name'])
				#continue
		counter += 1

	return data

def main():
	
	infile = sys.argv[1]

	outfile = sys.argv[2]

	api_key = sys.argv[3]



	data = make_data(infile)
	
	data = reviewsToData(data)

	with open(outfile, 'w') as fp:
		json.dump(data, fp)


    # TO READ DATA:

    # with open('data.json', 'r') as fp:
    # 	data = json.load(fp)


	# testid = place_search_for_id("CHEESIES PUB & GRUB", '41.94002724', '-87.65373273')

	# print "ID: " + testid
	# print "REVIEWS: "
	# for item in get_reviews(testid):
	# 	print item






if __name__ == '__main__':
	main()




