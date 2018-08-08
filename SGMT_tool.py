# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 14:15:31 2018

@author: 9yu6990
"""

import os
import pandas as pd
import re

# IMPORT .csv FILES THAT ARE IN FORMAT OF SGMT SIZES H218.csv FILE 

# counts number of differences between 2 size grids by taking sum of both size
# lengths and then subtracting every pair of like sizes between both size grids
def count_differences(size_1, size_2):
    counter = 0
    union = len(size_1) + len(size_2)
    min_size = min(size_1, size_2)
    max_size = max(size_1, size_2)
    for size in min_size:
        if size in max_size:
            counter = counter + 1
    diff = union - 2 * counter
    return diff

# cross checks every size in smaller size grid with size in larger size grid
# and then counts the number of sizes in smaller size grid that exist in larger
# size grid, if counter = length(min_size) then we know min_size is subset
def is_subset(size_1, size_2):
    counter = 0
    min_size = min(size_1, size_2)
    max_size = max(size_1, size_2)
    for size in min_size:
        if size in max_size:
            counter = counter + 1
    if counter == len(min_size):
        return True
    else:
        return False

# used to compare the pc9_count %s per size and evaluate if %_a is significantly
# greater than %_b
def not_significant(percent_a, percent_b):
    min_percent = min(percent_a, percent_b)
    max_percent = max(percent_a, percent_b)
    if max_percent / min_percent >= 10:
        return True
    else:
        return False

# insert file_path
file_path = os.path.normpath('//sfonetapp3220a/Global_MPIM/Global_Reporting_and_Analytics/Advanced_Analytics/Size_Grid_Model_Predictions/SGMT Sizes H218.csv')

SGMT_data = pd.read_csv(file_path)
SGMT_data['Submitted Plan QTY'] = SGMT_data['Submitted Plan QTY'].apply(str).apply(lambda x: x.replace(',','')).apply(pd.to_numeric)

df = pd.DataFrame(columns = ['brand', 'consumer', 'planning_group', 'category', 'pc5', 'pc9', 'sizes'])

# appends sizes into list for every size marked with "X"
for i in range(len(SGMT_data)):
    sizes = []
    for column in SGMT_data:
        if SGMT_data[column][i] == "X":
            sizes.append(column)
    df.loc[i] = [SGMT_data['Brand'][i], SGMT_data['Consumer'][i], SGMT_data['Planning Group'][i], SGMT_data['Category'][i], SGMT_data['PC5'][i], SGMT_data['PC9'][i], sizes]

# changes sizes list into str format for future aggregations
df['identifier'] = df[['consumer', 'planning_group', 'pc5']].apply(lambda x: ' '.join(x.dropna().astype(str)),axis=1) 
df['sizes'] = df[['sizes']].apply(lambda x: ' '.join(x.astype(str)), axis=1)

# filters out TOPS
df_2 = df[df.category != 'TOPS'].reset_index().drop(['shipments'], axis=1)

df_size_pc9_count = df_2.groupby(['identifier', 'sizes']).count().reset_index().drop(['brand', 'consumer', 'planning_group', 'category', 'pc5'], axis=1)
df_identifier_pc9_count = df_size_pc9_count.groupby(['identifier']).sum().reset_index()

df_3 = pd.merge(df_identifier_pc9_count, df_size_pc9_count, on = ['identifier'])
df_3['total_pc9_count'] = df_3['pc9_x']
df_3['size_pc9_count'] = df_3['pc9_y']
df_3 = df_3.drop(['pc9_x', 'pc9_y'], axis=1) 

df_2 = pd.merge(df_2, df_3, on = ['identifier', 'sizes']).reset_index().drop(['level_0', 'index'], axis=1)
df_2['size_significance'] = df_2['size_pc9_count'] / df_2['total_pc9_count'] * 100

# changes sizes str back into list 
for i in range(len(df_2)):
    df_2['sizes'][i] = re.sub("[^\w]", " ",  df_2['sizes'][i]).split()

df_2.to_csv('pre_algorithm.csv')

running_total = 0
identifier_stops = [] # the indices that differentiate distinct identifiers
identifier_index = 0
size_number = 1
index_list = [] # list of rows to harmonize

for i in range(len(df_2) - 1):
    if df_2['identifier'][i] == df_2['identifier'][i+1]:
        size_number = size_number + 1
    else:
        running_total = running_total + size_number
        identifier_stops.append(running_total)
        size_number = 1

running_total = running_total + size_number
identifier_stops.append(running_total)
        
for i in range(len(df_2) - 1):
    if df_2['identifier'][i] == df_2['identifier'][i+1]:
        # _a variables are associated with index i
        size_a = df_2['sizes'][i]
        percent_a = df_2['size_significance'][i]
        for n in range(i + 1, identifier_stops[identifier_index]):
            # _b variables are associated with index n
            size_b = df_2['sizes'][n]
            percent_b = df_2['size_significance'][n]
            # print(str(i) + ' ' + str(n) + ' ' + str(count_differences(size_a, size_b)) + ' ' + str(is_subset(size_a, size_b)))
            if count_differences(size_a, size_b) <= 3 and is_subset(size_a, size_b):
                if size_a == size_b:
                    index_list.append(n)
                else:
                    if min(size_a, size_b) == size_a:
                        index_list.append(i)
                    if min(size_a, size_b) == size_b:
                        index_list.append(n)
            if count_differences(size_a, size_b) <= 3 and not is_subset(size_a, size_b) and not_significant(percent_a, percent_b):
                if min(percent_a, percent_b) == percent_a:
                    index_list.append(i)
                if min(percent_a, percent_b) == percent_b:
                    index_list.append(n)
    else:
        identifier_index = identifier_index + 1

index_list = sorted(list(set(index_list)))

final_df = df_2.drop(df_2.index[index_list]).reset_index()

final_df.to_csv('post_algorithm.csv')