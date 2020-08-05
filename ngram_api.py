import pandas as pd
import os, sys
import string

import asyncio
from aiohttp import ClientSession


from utils import run_query

read_dir = ["./adjNoun", "./verbNoun"]
write_dir = "./nounNoun"


def getfiles(dir):
    files = []
    for (dirpath, _, filenames) in os.walk(dir):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))

    sorted(files)
    return files


adj_noun_files = getfiles(read_dir[0])
verb_noun_files = getfiles(read_dir[1])
save_dir = "./nounNoun"
filename = "./kmeans_nounNoun_essays_metaphors.csv"
response_file = "response.txt"
data = pd.read_csv(filename, delimiter=',')
sources = data.identified_sources

tokens = set()
for file in adj_noun_files:
    nouns = list(pd.read_csv(file, delimiter='\t').iloc[:, 2])
    for noun in nouns:
        noun = str(noun).lower()
        tokens.add(noun)

for file in verb_noun_files:
    nouns = list(pd.read_csv(file, delimiter='\t').iloc[:, 2])
    for noun in nouns:
        noun = str(noun).lower()
        tokens.add(noun)

for i, row in enumerate(sources):
    if not pd.isna(row):
        all_sources = row.strip().split(';')
        for source in all_sources:
            tokens.add(str(source).lower())


print(f'No of Tokens: {len(tokens)}')
tokens = sorted(tokens)
# starting_letters = ['w', 'x', 'y', 'z']
# tokens = [token for token in tokens if str(token).startswith('w') or str(token).startswith('x')
#           or str(token).startswith('y') or str(token).startswith('z')]
# print(f'filtered tokens: {len(tokens)}')


async def print_responses():
    async with ClientSession() as session:
        result = await asyncio.gather(*[run_query(token, session) for token in tokens])
        return result


loop = asyncio.get_event_loop()
bigrams = loop.run_until_complete(print_responses())
loop.close()


ptr = 0
starting_letters = string.ascii_lowercase
for starting_letter in starting_letters:
    with open(os.path.join(write_dir, 'nn_'+starting_letter+'.txt'), 'a') as f:
        # for i, token in enumerate(tokens):
        while ptr < len(tokens) and tokens[ptr].startswith(starting_letter):
            if bigrams[ptr] and len(bigrams[ptr]):
                for bigram in bigrams[ptr]:
                    f.write('\t'.join([str(i) for i in bigram]))
                    f.write('\n')
            ptr += 1
        print(f'file {starting_letter} written')

