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


async def get_responses(tokens):
    async with ClientSession() as session:
        result = await asyncio.gather(*[run_query(token, session) for token in tokens])
        return result


ptr = 0
starting_letters = string.ascii_lowercase
bigrams_df = pd.DataFrame()
loop = asyncio.get_event_loop()
for starting_letter in starting_letters:
    queried_tokens = []
    while ptr < len(tokens) and tokens[ptr].startswith(starting_letter):
        queried_tokens.append(tokens[ptr])
        ptr += 1

    bigrams = loop.run_until_complete(get_responses(queried_tokens))
    for bigram in bigrams:
        if bigram and len(bigram):
            bigrams_df = bigrams_df.append(pd.DataFrame(bigram))
    print(f'Starting letter: {starting_letter} done')
loop.close()

bigrams_df = bigrams_df.sort_values(by=[bigrams_df.columns[1], bigrams_df.columns[2]],
                                    key=lambda col: col.str.lower())
ptr = 0
for starting_letter in starting_letters:
    with open(os.path.join(write_dir, 'nn2_'+starting_letter+'.txt'), 'w') as f:

        while ptr < len(bigrams_df) and str(bigrams_df.iloc[ptr, 1]).startswith(starting_letter):
            f.write('\t'.join([str(i) for i in bigrams_df.iloc[ptr]]))
            f.write('\n')
            ptr += 1
        print(f'file {starting_letter} written')
