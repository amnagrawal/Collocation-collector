import pandas as pd

from utils import build_query, get_response, nounNounFinder
from nltk import word_tokenize, pos_tag

# print(response.text)
filename = "./kmeans_nounNoun_essays_metaphors.csv"
response_file = "response.txt"
# tokens = ['flow', 'tax']	#dummy tokens
# TODO: uncomment this when done with parsing the response
data = pd.read_csv(filename, delimiter=',')
sources = data.identified_sources
tokens = set()
for i, row in enumerate(sources):
    if not pd.isna(row):
        all_sources = row.strip().split(';')
        tokens.update(all_sources)

with open(response_file, 'w') as f:
    print(f'Total: {len(tokens)}')
    for i, token in enumerate(tokens):
        query = build_query(token)
        response = get_response(query)
        print(i, end=" ")
        if not i % 50:
            print()
        f.write(response.text)

print("Response file written")

response_df = pd.read_csv(response_file, header=None, delimiter='\t')
nounNounList = []
for row in response_df.iterrows():
    text = row[1][0]
    tokenized_text = [word[:-2] for word in text.split()]
    tagged = pos_tag(tokenized_text)
    frequency = row[1][1]
    sourceNoun, targetNoun = nounNounFinder(tagged)
    if sourceNoun:
        nounNounList.append((frequency, sourceNoun, targetNoun))

print(len(nounNounList))
with open('nounNoun1.txt', 'w') as f:
    for row in nounNounList:
        f.write('\t'.join([str(i) for i in row]))
        f.write('\n')
