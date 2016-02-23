'''
Counts of number of distinct cities users reviewed

Note: this script is formatted to run on the University of Michigan's Fladoop cluster; updates/changes may be required to run on different Spark clusters.

To run on Fladoop cluster:
spark-submit --master yarn-client --queue si601w16 process_data.py
'''
import simplejson as json
import math, sys, validators
from pyspark import SparkContext
from pyspark.sql import SQLContext, Row

sc = SparkContext(appName="PythonPosNegWords")
sqlContext = SQLContext(sc)

input_file = sc.textFile("hdfs:///user/jpgard/data.json") #note: this filepath may not be correct; needs to be tested
data_df = sqlContext.read.json("hdfs:///user/jpgard/data.json") #note: this filepath may not be correct; needs to be tested


def compare_review_lengths(data, outfile):
	'''
	Computes the average review length for high, low, and medium risk restaurants and returns a tuple containing the averages for each. Returns output as a .csv file.
	'''

def compare_n_photos(data, outfile):
	'''
	Calculates the average number of photos for high, low, and medium risk restaurants and returns a tuple containing the averages for each. Returns output as a .csv file.
	'''

	results = data['results']
	try: n_photos = data['n_photos']
	except KeyError: n_photos = 0


	return (results, (n_photos, 1)) 


def has_website(data):
	'''
	Computes percentage of restaurants at high, low, and medium risk levels that have websites listed on their Google Places entries.
	'''

	
	website = data['website']
	results = data['results']

	#check for valid url
	if validators.url(website) == True: 
		return (results , 1)
	else:
		return (results , 0)


def has_phone(data, outfile):
	'''
	Computes percentage of restaurants at high, low, and medium risk levels that have websites listed on their Google Places entries. Returns output as a .csv file.
	'''

	#need to check formatting of phone numbers; use regex to match?

def find_high_risk_words(data, outfile):
	'''
	Finds most common words in high-risk restaurant reviews (do I need to use IDF for this??)
	'''

def average_sentiment(data, outfile):
	'''
	Computes average sentiment of reviews of restaurants for high, medium, and low risk levels. Returns output as a .csv file.
	'''

def get_max_sentiment_reviews(data, outfile):
	'''
	Just for fun, if time -- this function finds the maximum sentiment reviews (most positive, most negative) and returns them in a text file :-)
	'''

def main(infile):
	
	indata = open('data.json', 'r')
	data = json.loads(indata.read())
	#call functions here, with different outfile names - i.e., 'has_website.csv'


#start data processing

#has_website

has_website_results = input_file.map(lambda line: json.loads(line)).flatmap(has_website).reduceByKey(lambda x,y: x + y).collect() # check this result, then write to csv

compare_n_photos_results = input_file.map(lambda line: json.loads(line)).flatmap(compare_n_photos).reduceByKey(lambda x,y: (x[0] + y[0], x[1] + y[1])).map(x[0], float(x[1][0])/float(x[1][1])).collect() #check this result, then write to csv
