import pandas as pd
import os, sys

read_dir = "./nounNoun"
save_dir = "./nn"


def remove_duplicates(filename):
    data = pd.read_csv(os.path.join(read_dir, filename), delimiter='\t')
    ptr = 0
    new_file = os.path.join(save_dir, filename)
    with open(new_file, 'w') as f:
        while ptr < len(data):
            count = 0
            start_ptr = ptr

            while ptr < len(data) and str(data.iloc[ptr, 1]) == str(data.iloc[start_ptr, 1]) \
                    and str(data.iloc[ptr, 2]) == str(data.iloc[start_ptr, 2]):
                count += data.iloc[ptr, 0]
                ptr += 1

            row = [count, data.iloc[start_ptr, 1], data.iloc[start_ptr, 2], 'n', 'n']
            f.write('\t'.join([str(i) for i in row]))
            f.write('\n')

    return


for (dirpath, _, filenames) in os.walk(read_dir):
    for filename in filenames:
        print(f'Removing duplicates from {filename}: ', end=" ")
        remove_duplicates(filename)
        print('Completed')
