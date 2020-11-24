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
import os
import argparse
from datetime import datetime
import time
import logging
from collections import OrderedDict

import pandas as pd
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

    # # Add the original input sequence as a column - REMINDER - this is zero based so it is one out from actual position
    #df['original_sequence'] = df.index

    # # Lets save exact dupes in a separate data frame
    # # This will reduce the data set that we need to work on
    #df_exact_dupes = df_sorted.loc[df_sorted.duplicated(keep='first'), :]
    
    # # Populate the match level with 'Exact Match'
    #df_exact_dupes.loc[:, 'match_level'] = 'Exact Match'

    # # The remainder of the data frame
    #df_minus_exact_dupes = df_sorted.drop_duplicates(keep='first')

    # # Output the exact matches to a file
    #df_exact_dupes.to_csv(out_file, sep=',', index=False, encoding='utf-8')

    #df_minus_exact_dupes = df_minus_exact_dupes.reset_index(drop=True)


def format_tStamp(timestamp):
    """
    Format a timestamp for file names
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')


def assign_file_names(script_path):
    """
    Create 2 strings with a time stamp to be used as output file and lof file.

    Args:
        script_path (string)      : A string containing the script path

    Returns:
        Returns filenames for output and log file
    """

    # # get a time stamp for log / out file name
    dt_now = datetime.now()
    log_date = format_tStamp(time.mktime(dt_now.timetuple()))

    # # split full path
    path, file = os.path.split(script_path)

    # # Create log filename
    log_filename = "app_{}.{}".format(log_date, 'log')
    log_filename = os.path.join(path, log_filename)

    # # Create output filename
    out_filename = "relateddata_{}.{}".format(log_date, 'csv')
    out_filename = os.path.join(path, out_filename)

    return out_filename, log_filename


def read_input_into_data_frame(file_name): 
    """
    Read in csv file and return a data frame.

    Args:
        file_name (string)      : A string containing the filename

    Returns:
        Returns a data frame
    """
    
    logging.info(f"Reading file in to a data frame : {file_name}")

    # # Read the data into a pandas data frame
    try:
        df = pd.read_csv(file_name)
    except Exception as e:
        logging.error("Exception whilst reading file", exc_info=True)
        print ("Error during reading the file, check log for details")
        exit()
    
    # # number of rows
    num_of_input_records = df.shape[0] + 1
    logging.info(f"Number of records in file : {str(num_of_input_records)}")
    logging.info("")
    
    return df


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

    logging.info("Asking user to select fields for matching purposes.")

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
                logging.info(list_of_columns[column_num])

        except ValueError:
            logging.info(f"Expected an integer as a column index. This entry will be ignored. {idx}" )
            print("Expected an integer as a column index. This entry will be ignored. => ", idx)

    return return_list


def main(file_name, match_ratio):

    # # get script path and set log
    script_path = os.path.abspath(__file__)

    # # Assign output file and log file names
    out_file, log_file = assign_file_names(script_path)

    # # set up basic logging.
    logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    # # Read input file in as data frame
    df = read_input_into_data_frame(file_name)

    # # Get a list of headers
    column_names_list = list(df.columns)

    # # Ask user for confirmation of fields to use for matching purposes
    column_names_list = confirm_match_fields(column_names_list)

    # # Add a new column to the data frame and the combination of user selected columns as values
    df['match_column'] = df[column_names_list].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

    # # Add another field to store the match field
    df["match_index"] = ""

    # # Sort data frame on the newly created column
    df_sorted = df.sort_values('match_column', ascending=True, inplace=False, kind='quicksort', na_position='last')

    # # Add new index to the data frame
    df_sorted = df_sorted.reset_index(drop=True)

    # # Save data frame as a dictionary with index as key
    records_dict = df_sorted.to_dict('index')

    # # Store values of the dictionary values in a list
    # # This will give me a list with dictionary keys
    records_list = []
    records_list = [ v for v in records_dict.values() ]

    # # Now for the loopy stuff
    # # Loop through list and compare the values
    num_of_input_records = len(records_list)

    for idx in range(num_of_input_records):

        # # Set the break point for when the end is reached
        if idx +1 >=  num_of_input_records:
            break

        # # Variable to toggle between matches found or not
        match_found = True

        # # Integer to help us get the next entries in the list
        idx_plus = 1

        # # String to store any matching indexes
        idx_str = ''

        while match_found:
            # # Retrieve the names in index = idx and idx + idx_plus
            first_string = records_list[idx]['match_column']
            second_string = records_list[idx + idx_plus]['match_column']

            # # The match ratio using the SequenceMatcher
            match_ratio_1 = SequenceMatcher(a=first_string,b=second_string).ratio()
            match_ratio_1 = match_ratio_1 * 100

            # # The match ratio using the fuzzywuzzy library
            match_ratio_2 = fuzz.token_set_ratio(first_string, second_string)

            # # Check that both ratios are greater than the default set
            if int(match_ratio_1) > match_ratio and int(match_ratio_2) > match_ratio:
                if idx_plus == 1:
                    records_list[idx]['match_index'] = str(idx + idx_plus)
                else:
                    idx_str = records_list[idx]['match_index'] + "," + str(idx + idx_plus)
                    records_list[idx]['match_index'] = str(idx_str)

                idx_plus+=1
                #print ("{} \t {} \t --> {}".format(first_string, second_string, match_ratio))
            else:
                match_found = False



if __name__ == '__main__':

    # # Hard coded params
    file_name = "C:\\Data_Shed_Techical\\Input_Data\\DataShed_Technical_Test.csv"
    match_ratio = 90

    # # Run main function
    main(file_name, match_ratio)
