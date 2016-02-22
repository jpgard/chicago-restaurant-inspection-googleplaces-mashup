import requests, json, sys, re, csv
from collections import defaultdict




def get_reviews(placeid, api_key):
	'''
	Fetches reviews using Google Places API, returning a dictionary of data from the google places entry including all of the elements in data_elements, plus n_photos (number of photos), . 

	Note: not all restaurants have reviews. Google limits the output to a maximum of five reviews.
	'''
	baseurl = 'https://maps.googleapis.com/maps/api/place/details/json?' 
	api_url = baseurl + 'placeid=' + placeid + '&key=' + api_key
	data = requests.get(api_url)
	output = {}
	rjson = data.json()

	data_elements = ['rating', 'website', 'formatted_phone_number', 'user_ratings_total']

	for e in data_elements:
		output[e] = rjson['result'].get(e)

	try: output['n_photos'] = len(rjson['result'].get('photos'))
	except TypeError: output['n_photos'] = 0

	if rjson['result'].get('reviews'):
		reviews_raw = rjson['result'].get('reviews')
		
		reviewtuples = []
		for review in reviews_raw:
			reviewtuples.append((review['rating'], review['text'], review['time']))
		output['reviews'] = reviewtuples


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



def reviewsToData(data, api_key):
	'''
	takes dictionary of places as input in format produced by make_data; looks up Google Places reviews and adds them to dictionary entry for that place in data.
	'''

	counter = 0

	for item in data.items():
		
		id = place_search_for_id(api_key, item[1]['name'], item[1]['lat'], item[1]['long'])

		if id:
			print "%s - Building data for %s ID: %s" % (counter, item[1]['name'], id)

			# try: 
			review_data = get_reviews(id, api_key)
			data[item[0]].update(review_data)
			# import ipdb; ipdb.set_trace()

			# except KeyError:
			# 	print 'No reviews for %s' % (item[1]['name'])

		counter += 1

	return data

def main():
	
	infile = sys.argv[1]
	outfile = sys.argv[2]
	api_key = sys.argv[3]
	data = make_data(infile)	
	data = reviewsToData(data, api_key)

	with open(outfile, 'w') as fp:
		json.dump(data, fp)


if __name__ == '__main__':
	main()




