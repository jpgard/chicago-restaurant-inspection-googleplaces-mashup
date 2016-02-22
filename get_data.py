'''
Assembles dataset for analysis. Requires an inputfile formatted in a structure identical to the City of Chicago's Food Inspection dataset here: https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5

Takes .csv file of food inspection data and Google API key as inputs, and generates a new JSON data structure of the relevant data elements from the Food Inspections dataset as well as the Google Places entry for that restaurant.

To call, use 'python get_data.py Food_Inspections.csv output_file.json YOUR_GOOGLE_API_KEY'
'''

import requests, json, sys, re, csv, time
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
	Note: this only records the most recent inspection for each restaurant. This will produce a final list of approximately 21,520 restaurants (as of 2/22/2016).
	'''

	data = defaultdict(dict)

	rawdata = open(infile)
	lines = csv.reader(rawdata)
	next(lines)

	for line in lines:

		try:	
			
			#create dictionary with restaurant name as key
			restaurant_name = line[2]
			inspection_date = time.strptime(line[10], "%m/%d/%Y")
			
			#check if this is newest or first entry; if it is, add to data; otherwise, do nothing
			if (not data[restaurant_name]) or (data[restaurant_name]['inspection_date'] < inspection_date):

				data[restaurant_name]['inspection_date'] = inspection_date
				data[restaurant_name]['inspection_id'] = line[0]
				data[restaurant_name]['facility_type'] = line[4]
				data[restaurant_name]['risk'] = re.findall(r'\d+', line[5])
				data[restaurant_name]['address'] = line[6]
				city = line[7]
				# state = line[8] no state needed -- all in Illinios
				data[restaurant_name]['ZIP'] = line[9]
				data[restaurant_name]['inspection_type'] = line[11]
				data[restaurant_name]['results'] = line[12]
				data[restaurant_name]['violationstext'] = line[13] #note: this is raw text; may want to split into list of separate violations (they are a numbered list--numbered by rule?)
				data[restaurant_name]['lat'] = line[14]
				data[restaurant_name]['long'] = line[15]

		except IndexError:

			print 'excluding line: \n'
			print line

		except TypeError:
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
			review_data = get_reviews(id, api_key)
			data[item[0]].update(review_data)
			

		counter += 1

	return data

def main():
	
	infile = sys.argv[1]
	outfile = sys.argv[2]
	api_key = sys.argv[3]
	data = make_data(infile)
	import ipdb; ipdb.set_trace()	
	data = reviewsToData(data, api_key)

	with open(outfile, 'w') as fp:
		json.dump(data, fp)


if __name__ == '__main__':
	main()




