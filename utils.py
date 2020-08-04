import urllib

import requests


def build_query(token):
	encoded_query = urllib.parse.quote(token + ' *')
	params = {'corpus': 'eng-us', 'query': encoded_query, 'topk': 100, 'format': 'tsv'}
	params = '&'.join('{}={}'.format(name, value) for name, value in params.items())
	query = 'https://api.phrasefinder.io/search?' + params
	return query


def get_response(query):
	response = requests.get(query)
	return response


def nounNounFinder(taggedText):
	POScolumn = [item[1] for item in taggedText]
	wordColumn = [item[0] for item in taggedText]
	pattern = ['of', 'is', 'was', 'were', 'am', 'had', 'will', 'are', 'have']

	for i in range(len(POScolumn) - 1):
		firstNounIndex = i
		secondNounIndex = i + 1

		indexCheck = lambda x: (x < len(POScolumn))
		isNoun = lambda x: indexCheck(x) and POScolumn[x].startswith('NN')
		isDeterminant = lambda x: indexCheck(x) and POScolumn[x] == 'DT'
		isPartOfPattern = lambda x: indexCheck(x) and wordColumn[x] in pattern
		isAdjective = lambda x: indexCheck(x) and POScolumn[x] == 'JJ'
		patternMatches = lambda x: isNoun(x) or isPartOfPattern(x) or isDeterminant(x) or isAdjective(x)

		# Check for metaphor patterns consisting of only two consecutive nouns
		if isNoun(firstNounIndex) and isNoun(secondNounIndex) and not isNoun(secondNounIndex + 1):
			sourceNounIndex = secondNounIndex
			targetNounIndex = firstNounIndex
			return wordColumn[sourceNounIndex], wordColumn[targetNounIndex]

		# Check for metaphor patterns of type 'noun-is-noun' and 'noun-of-noun'
		if isNoun(firstNounIndex) and isPartOfPattern(secondNounIndex):
			candidateFound = False
			while patternMatches(secondNounIndex):
				if not isNoun(secondNounIndex + 1):
					if isNoun(secondNounIndex):
						candidateFound = True
						break
				secondNounIndex += 1

			if candidateFound:
				# Only in case of 'noun-of-noun' pattern the first noun is the source
				if 'of' in wordColumn[firstNounIndex:secondNounIndex + 1]:
					sourceNounIndex = firstNounIndex
					targetNounIndex = secondNounIndex
				else:
					sourceNounIndex = secondNounIndex
					targetNounIndex = firstNounIndex

				return wordColumn[sourceNounIndex], wordColumn[targetNounIndex]

	return None, None
