import urllib
from nltk import word_tokenize, pos_tag
import string


def build_query(token):
    encoded_query = urllib.parse.quote(token + ' *')
    params = {'corpus': 'eng-us', 'query': encoded_query, 'topk': 100, 'format': 'tsv'}
    params = '&'.join('{}={}'.format(name, value) for name, value in params.items())
    query = 'https://api.phrasefinder.io/search?' + params
    return query


async def run_query(token, session):
    try:
        response = await get_response(token, session)
        rows = response.split('\n')
        result = []

        for row in rows:
            if len(row):
                frequency, sourceNoun, targetNoun, text = parse_response(row)
                if sourceNoun:
                    result.append((frequency, sourceNoun, targetNoun, 'n', 'n', text))
        return result

    except Exception as err:
        # print(f'Exception occured in run_query: {err}')
        print(err)
        pass


async def get_response(token, session):
    url = build_query(token)
    async with session.get(url) as response:
        assert response.status == 200
        return await response.text()


def parse_response(response_text):
    response_text = response_text.split('\t')
    text = response_text[0]
    tokenized_text = [word[:-2] for word in text.split()]
    try:
        tagged = pos_tag(tokenized_text)
        frequency = response_text[1]
        sourceNoun, targetNoun = nounNounFinder(tagged)
        # To avoid rows with punctuations identified as nouns
        if sourceNoun and isValid(sourceNoun) and isValid(targetNoun):
            return frequency, sourceNoun, targetNoun, ' '.join(tokenized_text)
    except Exception as err:
        print(f'Exception occured in parse response: {err}')
        print(response_text)
        pass

    return None, None, None, None


def isValid(word):
    alphabets = string.ascii_lowercase
    if len(word) > 1 and (word[0] in alphabets):
        return 1
    else:
        return 0


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
