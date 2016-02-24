
# Code written by Josh Gardner for SI601_W16 at the University of Michigan
# Vader Sentiment Analyzer via :
#		Hutto, C.J. & Gilbert, E.E. (2014).
# 		VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. 
# 		Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.

#tf-idf code written with support from the following references:
# http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/
# http://aimotion.blogspot.com/2011/12/machine-learning-with-python-meeting-tf.html
# https://en.wikipedia.org/wiki/Tf%E2%80%93idf

import json, validators, nltk, math, string
from collections import defaultdict, Counter
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment 
from nltk.stem.snowball import SnowballStemmer


def filter_reviewed_only(data):
	'''
	Takes data as input, returns data dictionary with only restaurants with google places/review data.
	'''

	newdata = {}

	for each in data.items():
		
		if ('rating' or 'website' or 'formatted_phone_number' or 'user_ratings_total' or 'n_photos' or 'reviews') in each[1].keys():
			newdata[each[0]] = each[1]

	return newdata


def compare_n_photos(data):

	photo_counts = defaultdict(int)
	result_categories = set()
	output = []


	for each in data.items():

		n_photos = each[1]['n_photos']
		results = each[1]['results']

		photo_counts[results + '_counts'] += 1
		photo_counts[results + '_photos'] += n_photos
		result_categories.add(results)


	for result in result_categories:
		t = (result, photo_counts[result + '_counts'], photo_counts[result + '_photos'], float(photo_counts[result + '_photos'])/float(photo_counts[result + '_counts']))
		output.append(t)

	# return photo_counts
	return output

def compare_valid_website_rates(data):
	website_counts = defaultdict(int)
	result_categories = set()
	output = []

	for each in data.items():

		results = each[1]['results']
		result_categories.add(results)
		website = each[1].get('website')
		website_counts[results + '_counts'] += 1

		if website and (validators.url(website) == True): 
			website_counts[results + '_validWebsite'] += 1

	for result in result_categories:
		t = (result, website_counts[result + '_counts'], website_counts[result + '_validWebsite'], float(website_counts[result + '_validWebsite'])/float(website_counts[result + '_counts']))
		output.append(t)

	return output

def has_phone(data):
	phone_counts = defaultdict(int)
	result_categories = set()
	output = []

	for each in data.items():

		results = each[1]['results']
		result_categories.add(results)
		phone = each[1].get('formatted_phone_number')
		phone_counts[results + '_counts'] += 1

		if phone: 
			phone_counts[results + '_phoneListed'] += 1

	for result in result_categories:
		t = (result, phone_counts[result + '_counts'], phone_counts[result + '_phoneListed'], float(phone_counts[result + '_phoneListed'])/float(phone_counts[result + '_counts']))
		output.append(t)

	return output


def avg_rating(data):
	rating_totals = defaultdict(int)
	result_categories = set()
	output = []

	for each in data.items():
		results = each[1]['results']
		result_categories.add(results)
		rating = each[1].get('rating')

		if rating:
			rating_totals[results + '_n_reviews'] += 1
			rating_totals[results + '_total_stars'] += rating

	for result in result_categories:
		t = (result, rating_totals[result + '_n_reviews'], rating_totals[result + '_total_stars'], rating_totals[result + '_total_stars']/float(rating_totals[result + '_n_reviews']))
		output.append(t)

	return output


def avg_review_length(data):
	review_totals = defaultdict(int)
	result_categories = set()
	output = []

	for each in data.items():

		results = each[1]['results']
		result_categories.add(results)
		reviews_list = each[1].get('reviews')

		if reviews_list:

			n_reviews = len(reviews_list)
			review_lens = [len(nltk.word_tokenize(x[1])) for x in reviews_list]

			review_totals[results + '_n_reviews'] += n_reviews
			review_totals[results + '_n_tokens'] += sum(review_lens)

	for result in result_categories:
		t = (result, review_totals[result + '_n_reviews'], review_totals[result + '_n_tokens'], float(review_totals[result + '_n_tokens'])/float(review_totals[result + '_n_reviews']))
		output.append(t)

	return output


def avg_review_vaderSentiment(data):
	
	sentiment_totals = defaultdict(int)
	result_categories = set()
	output = []

	for each in data.items():

		results = each[1]['results']
		result_categories.add(results)
		reviews_list = each[1].get('reviews')

		if reviews_list:

			n_reviews = len(reviews_list)
			review_sentiments = [vaderSentiment(x[1].encode('utf8')) for x in reviews_list]

			sentiment_totals[results + '_n_reviews'] += n_reviews
			sentiment_totals[results + '_pos_sentiment'] += sum([i['pos'] for i in review_sentiments])
			sentiment_totals[results + '_neg_sentiment'] += sum([i['neg'] for i in review_sentiments])
			sentiment_totals[results + '_neu_sentiment'] += sum([i['neu'] for i in review_sentiments])
			sentiment_totals[results + '_compound_sentiment'] += sum([i['compound'] for i in review_sentiments])

	for result in result_categories:
		t = (result, sentiment_totals[result + '_n_reviews'], float(sentiment_totals[result + '_pos_sentiment'])/float(sentiment_totals[result + '_n_reviews']), float(sentiment_totals[result + '_neg_sentiment'])/float(sentiment_totals[result + '_n_reviews']) ,float(sentiment_totals[result + '_compound_sentiment'])/float(sentiment_totals[result + '_n_reviews']))
		output.append(t)

	return output


def max_review_vaderSentiment(data, n, min_length):

	vader_reviews = {}
	
	pos_reviews = []
	neg_reviews = []


	for each in data.items():

		reviews_list = each[1].get('reviews')

		if reviews_list:

			review_sentiments = [(x[1].encode('utf8'), vaderSentiment(x[1].encode('utf8'))) for x in reviews_list if (len(nltk.word_tokenize(x[1])) >= min_length)]

			for r in review_sentiments:
				vader_reviews[r[0]] = (r[1]['neg'], r[1]['pos'])

	top_neg = sorted(vader_reviews.items(), key = lambda x: x[1][0], reverse = True)[0:n+1]
	top_pos = sorted(vader_reviews.items(), key = lambda x: x[1][1], reverse = True)[0:n+1]





	return top_pos, top_neg


def tf_idf(data, n):

	#initialize stemmer; snowball stemmer used here due to better performance than Porter stemmer
	stemmer = SnowballStemmer("english")

	#initialize data structures
	results_terms = defaultdict(list)
	pass_tf = defaultdict(float)
	fail_tf = defaultdict(float)
	pwc_tf = defaultdict(float)
	oob_tf = defaultdict(float)
	bnl_tf = defaultdict(float)
	nr_tf = defaultdict(float)
	ne_tf = defaultdict(float)
	idf = defaultdict(int)
	tf_idf = defaultdict(dict)

	#tokenize reviews, applying relevant transformation/preprocessing (stemming, remove capitalization, remove punctuation) and add to relevant 'document' data structure by result category

	for each in data.items():

		results = each[1]['results']
		reviews_list = each[1].get('reviews')

		if reviews_list:
			review_tokens = [stemmer.stem(token.lower()) for x in reviews_list for token in nltk.word_tokenize(x[1]) if not token in string.punctuation]

			if results == 'Pass':
				results_terms['pass_terms'].extend(review_tokens)

			elif results == 'Fail':
				results_terms['fail_terms'].extend(review_tokens)

			elif results == 'Out of Business':
				results_terms['oob_terms'].extend(review_tokens)

			elif results == 'Pass w/ Conditions':
				results_terms['pwc_terms'].extend(review_tokens)
			elif results == 'No Entry':
				results_terms['ne_terms'].extend(review_tokens)

			elif results == 'Not Ready':
				results_terms['nr_terms'].extend(review_tokens)

			elif results == 'Business Not Located':
				results_terms['bnl_terms'].extend(review_tokens)

	#collect counts of individual tokens by result category, and calculate total number of terms by category to compute term frequency

	pass_counts = Counter(results_terms['pass_terms'])
	fail_counts = Counter(results_terms['fail_terms'])
	pwc_counts = Counter(results_terms['pwc_terms'])
	oob_counts = Counter(results_terms['oob_terms'])
	bnl_counts = Counter(results_terms['bnl_terms'])
	nr_counts = Counter(results_terms['nr_terms'])
	ne_counts = Counter(results_terms['ne_terms'])

	pass_tokens = len(results_terms['pass_terms'])
	fail_tokens = len(results_terms['fail_terms'])
	pwc_tokens = len(results_terms['pwc_terms'])
	oob_tokens = len(results_terms['oob_terms'])
	bnl_tokens = len(results_terms['bnl_terms'])
	nr_tokens = len(results_terms['nr_terms'])
	ne_tokens = len(results_terms['ne_terms'])

	#compute term frequency for each term in each results category

	for i in pass_counts.items():
		pass_tf[i[0]] = float(i[1])/float(pass_tokens)

	for i in fail_counts.items():
		fail_tf[i[0]] = float(i[1])/float(fail_tokens)

	for i in pwc_counts.items():
		pwc_tf[i[0]] = float(i[1])/float(pwc_tokens)

	for i in oob_counts.items():
		oob_tf[i[0]] = float(i[1])/float(oob_tokens)

	for i in bnl_counts.items():
		bnl_tf[i[0]] = float(i[1])/float(bnl_tokens)

	for i in nr_counts.items():
		nr_tf[i[0]] = float(i[1])/float(nr_tokens)

	for i in ne_counts.items():
		ne_tf[i[0]] = float(i[1])/float(ne_tokens)

	#compute idf for all tokens by collecting all tokens from all documents and taking log(n_documents/1+n_documents_containing_word)

	alltokens = pass_counts.keys() + fail_counts.keys() + pwc_counts.keys() + oob_counts.keys() + bnl_counts.keys() + nr_counts.keys() + ne_counts.keys()

	document_token_list = [pass_counts.keys(), fail_counts.keys(), pwc_counts.keys(), oob_counts.keys(), bnl_counts.keys(), nr_counts.keys(), ne_counts.keys()]
	
	for token in alltokens:
		idf[token] = math.log(float(7)/float(1 + sum([1 for c in document_token_list if token in c])))

	#use tf and idf scores to compute tf_idf for each token in each document

	for token in pass_counts.keys():
		tf_idf['pass'][token] = pass_tf[token]*idf[token]
	for token in fail_counts.keys():
		tf_idf['fail'][token] = fail_tf[token]*idf[token]
	for token in pwc_counts.keys():
		tf_idf['pwc'][token] = pwc_tf[token]*idf[token]
	for token in oob_counts.keys():
		tf_idf['oob'][token] = oob_tf[token]*idf[token]
	for token in bnl_counts.keys():
		tf_idf['bnl'][token] = bnl_tf[token]*idf[token]
	for token in nr_counts.keys():
		tf_idf['nr'][token] = nr_tf[token]*idf[token]
	for token in ne_counts.keys():
		tf_idf['ne'][token] = ne_tf[token]*idf[token]

	output = []

	for each in tf_idf.items():
		print each[0]
		print '\n'
		print sorted(each[1].items(), key = lambda x: x[1], reverse = True)[0:n]
		output.append((each[0], sorted(each[1].items(), key = lambda x: x[1], reverse = True)[0:n]))

	return output
	# import ipdb; ipdb.set_trace() 




def write_output(data, headers, outfile):
	'''
	Takes a list of tuples (data) and list of headers (headers) and writes them to a csv
	'''

	outfile = open(outfile, 'w')
	outfile.write(', '.join(headers) + ' \n')
	for item in data:
		line = ', '.join(str(i) for i in item) + ' \n'
		outfile.write(line)
	outfile.close()



def main(indata):
	indata = open(indata, 'r')
	data = json.loads(indata.read())
	indata.close()

	#filter to only include restaurants with at least some google review data
	reviewed_data = filter_reviewed_only(data)

	photo_counts = compare_n_photos(reviewed_data)
	write_output(photo_counts, headers = ['Result', 'Num_result', 'Total Photos', 'Avg_num_photos'], outfile = 'compare_n_photos.csv')

	valid_website_rates = compare_valid_website_rates(reviewed_data)
	write_output(valid_website_rates, headers = ['Result', 'Num_result', 'Num_valid_websites', 'Valid_website_rates'], outfile = "compare_valid_website_rates.csv")
	# import ipdb; ipdb.set_trace()

	phone_rates = has_phone(reviewed_data)
	write_output(phone_rates, headers = ['Result', 'Num_result', 'Num_phone_listed', 'Phone_listed_rate'], outfile = "compare_phone_rates.csv")

	arl = avg_review_length(data)
	write_output(arl, headers = ['Result', 'n_reviews', 'n_tokens', 'avg_review_length'], outfile = "compare_avg_review_length.csv")

	sent = avg_review_vaderSentiment(data)
	write_output(sent, headers = ['Result', 'n_reviews', 'avg_pos_sentiment', 'avg_neg_sentiment', 'avg_compound_sentiment'], outfile = "compare_avg_sentiment.csv")
	
	ratings = avg_rating(reviewed_data)
	write_output(ratings, headers = ['Result', 'n_reviews', 'total_stars', 'avg_rating'], outfile = "compare_avg_rating.csv")

	top_pos,top_neg = max_review_vaderSentiment(reviewed_data, 10, 30)
	with open('max_sentiment_reviews.txt', 'w') as f:
		f.write("TOP POSITIVE REVIEWS + \n")
		f.write('\n'.join([str(x) for x in top_pos]) + '\n')
		f.write("TOP NEGATIVE REVIEWS + \n")
		f.write('\n'.join([str(x) for x in top_neg]) + '\n')

	x = tf_idf(reviewed_data, 20)
	with open('tf_idf.txt', 'w') as f:
		for i in x:
			f.write(i[0] + '\n')
			f.write(str([(y[0], y[1])  for y in i[1]]))
			f.write('\n')



if __name__ == '__main__':
	main('final_data.json')
