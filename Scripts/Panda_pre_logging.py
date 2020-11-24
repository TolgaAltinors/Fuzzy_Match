#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Tolga.Altinors
#
# Created:     20/12/2019
# Copyright:   (c) Tolga.Altinors 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import pandas as pd
from collections import OrderedDict

from difflib import SequenceMatcher
from fuzzywuzzy import fuzz


def some_bits():
    pass
    #df_sorted = df.sort_values(['given_name', 'surname', 'date_of_birth', 'sex'], axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')
    #print (df_sorted)

    # total number of rows and columns
    #print (df_sorted.shape)

    # count duplicate entries based on a field
    #print (df.given_name.duplicated().sum())

    # count entire rows that are duplicated
    #print (df.duplicated().sum())

    # display the duplicated rows
    #print (df.loc[df.duplicated(), :])

    # display the duplicated rows by keeping the first matches - can use last
    #print (df.loc[df.duplicated(keep='first'), :]) # mark for deletion
    #print (df.shape)
    #print (df.loc[df.duplicated(keep='last'), :])  # mark for deletion
    #print (df.shape)

    #print (df.loc[df.duplicated(keep=False), :]) # mark all dupes for deletion
    #print (df.shape)

    # Drop duplicates from the file
    #print (df.drop_duplicates(keep='first').shape)

    # check certain fields for duplicates
    #print (df.duplicated(subset=['surname', 'date_of_birth']).sum())
    #print (df.drop_duplicates(subset=['surname', 'date_of_birth']).shape)

    #df_exact_dupes = df.loc[df.duplicated(keep='first'), :]  # mark for deletion
    #df_with_no_exact_dupes = df.drop_duplicates(keep='first')

    #print ("*****************")
    #print (df.shape)
    #print (df_exact_dupes.shape)
    #print ("*****************")
    #print (df_with_no_exact_dupes.shape)

    # get first 5 rows
    #data = df.head()  

def confirm_match_fields(list_of_columns):
    """
    Ask the user for input and parse column selection against actual
    column list. Check that the user entry contains integer values and
    that these are within the upper boundary of actual column numbers.
    
    Args:
        list_of_columns (list)      : A list of columns from input data
    
    Returns:
        Returns a new list consisting of column names selected by the user.
    """

    return_list = []

    prompt = 'Select name fields for matching. Reply with a comma separated list of numbers. ie 0,1,2\n'

    # # Loop through columns in list and append to the prompt
    for idx, col in enumerate(list_of_columns):
        prompt = prompt + "({}) - {} \n".format(idx, col)

    # # Ask for user input and convert input to a list
    column_numbers_for_matching = (input(prompt)).split(',')
    
    # # Remove any duplicate entries without affecting the order
    column_numbers_for_matching = list(OrderedDict.fromkeys(column_numbers_for_matching))

    # # Set the column count
    column_count = len(list_of_columns)

    # # Map field indexes back to column names
    for idx in column_numbers_for_matching:

        # # Make sure value entered is a number and not greater than the actual column count
        try:
            column_num = int(idx)
            if column_num >= column_count:
                print ("Field number entered greater than expected. This will be ignored. Number = ", column_num) 
            else:
                return_list.append(list_of_columns[column_num])

        except ValueError:
            print("Expected an integer as a column index. This entry will be ignored. => ", idx)

    return return_list


def main(filename):

    # # Read the data into a pandas data frame
    df = pd.read_csv(filename)
    
    # # number of rows
    num_of_input_records = df.shape[0] + 1

    # df.index = pd.RangeIndex(start=1, stop=num_of_input_records, step=1)

    # # Get a list of headers
    column_names_list = list(df.columns)   

    # # Ask user for confirmation of fields to use for matching purposes
    column_names_list = confirm_match_fields(column_names_list)

    # # Add the original input sequence as a column - REMINDER - this is zero based so it is one out from actual position
    df['original_sequence'] = df.index

    # # Add a new column to the data frame and the combination of user selected columns as values
    df['match_column'] = df[column_names_list].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)    

    # # Sort data frame on the newly created column
    df_sorted = df.sort_values('match_column', ascending=True, inplace=False, kind='quicksort', na_position='last')

    # # Add new index to the data frame
    df_sorted = df_sorted.reset_index(drop=True)

    # # Add another field to store the match field
    df_sorted["match_level"] = ""

    # # Save data fram as a dictionary
    records_dict = df_sorted.to_dict('index')

    # # Store values of the dictionary values in a list
    records_list = []
    records_list = [ v for v in records_dict.values() ]

    # # Loop through list and compare the values
    num_of_input_records = len(records_list)

    print ("****************************")
    print (num_of_input_records)
    print ("****************************")
    for idx in range(num_of_input_records):

        if idx +1 >=  num_of_input_records:
            break

        first_string = records_list[idx]['match_column']

        second_string = records_list[idx +1]['match_column']

        #match_ratio = SequenceMatcher(a=first_string,b=second_string).ratio()
        match_ratio = fuzz.token_set_ratio(first_string, second_string)

 
        if int(match_ratio) > 88:
            print ("{} \t {} \t --> {}".format(first_string, second_string, match_ratio))



#    print (df_sorted)


if __name__ == '__main__':
    filename = "C:\\Data_Shed_Techical\\Input_Data\\DataShed_Technical_Test.csv"
    main(filename)
