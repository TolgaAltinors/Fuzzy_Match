#-------------------------------------------------------------------------------
# Name:        Check for Duplicates
# Purpose:
#
# Author:      Tolga.Altinors
#
# Created:     29/12/2019
# Copyright:   (c) Tolga.Altinors 2019
# Licence:     <your licence>
# pip3 install pandas
# pip3 install fuzzywuzzy
# pip3 install python-Levenshtein
#-------------------------------------------------------------------------------
import sys
import os
from datetime import datetime
import time
import logging
from collections import OrderedDict

import pandas as pd
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz


def format_tStamp(timestamp):
    """
    Format a timestamp for file names
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')


def assign_file_names(script_path):
    """
    Create 2 strings with a time stamp to be used as output file and log file.

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

    # # Create part of the output filename
    out_filename = "relateddata_"  
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
    
        # # number of rows
        num_of_input_records = df.shape[0] + 1
        logging.info(f"Number of records in file : {str(num_of_input_records)}")
        logging.info("")

        return df

    except FileNotFoundError:# as e:
        raise
        logging.error("Error reading the file", exc_info=True)
        print ("Error reading the file, check log for details")
    except pd.errors.EmptyDataError:
        raise
        logging.error("Empty file received.", exc_info=True)
        print ("Empty file received, check log for details")


def confirm_match_fields(df):
    """
    Ask the user for input and parse column selection against actual
    column list. Check that the user entry contains integer values and
    that these are within the upper boundary of actual column numbers.

    Args:
        df (data frame)      : data frame containing the file

    Returns:
        Returns a new list consisting of column names selected by the user.
    """

    logging.info("Asking user to select fields for matching purposes.")

    # # Get a list of headers
    list_of_columns = list(df.columns)

    return_list = []

    prompt = 'Select name fields for matching. Reply with a comma separated list of numbers. ie 0,1,2\n'

    # # Loop through collist_of_columnsumns in list and append to the prompt
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
            elif column_num < 0:
                print ("Field number entered is less than 0. This will be ignored. Number = ", column_num)
            else:
                return_list.append(list_of_columns[column_num])
                logging.info(list_of_columns[column_num])

        except ValueError:
            logging.info(f"Expected an integer as a column index. This entry will be ignored. {idx}" )
            print("Expected an integer as a column index. This entry will be ignored. => ", idx)

    logging.info("")

    logging.info(f"Selected {len(return_list)} columns for matching.")
    logging.info("")

    return return_list


def add_colums_and_sort(df, colums_for_matching):
    """
    Here we add additional columns to the data frame to aid matching.

    'match_key' = A merged column will be created from the values within
    the list that is passed to the function 'colums_for_matching'.
    The data frame will be sorted on this column.

    'match_level' = This will be set to empty but will get populated
    as the process continues.

    Args:
        df (data frame)      : Data frame of input records
        colums_for_matching (list) : Contains columns used for matching

    Returns:
        Returns a sorted version of the data frame with additional columns.
    """

    # # Add a new column to the data frame and the combination of user selected columns as values
    logging.info("Adding 'match_key' as a new column.")
    df['match_key'] = df[colums_for_matching].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

    # # Add another field to store the match field
    logging.info("Adding 'match_level' as a new column.")
    df['match_level'] = ""

    # # Sort data frame on the newly created column
    logging.info("Sorting the data frame on the 'match_key'")
    df_sorted = df.sort_values('match_key', ascending=True, inplace=False, kind='quicksort', na_position='last')

    # # Add new index to the data frame
    logging.info("Adding new index to data frame.")
    logging.info("")
    df_sorted = df_sorted.reset_index(drop=True)

    return df_sorted


def check_for_matches(records_dict, match_ratio):
    """
    This is where we use two string matching libraries to determine whether
    entries are similar / related with the aid of the trusted 'loop'.

    'SequenceMatcher' = comes with the standard library

    'fuzz.token_set_ratio' = this needs installing as 
        python install fuzzywuzzy

    I used two matching libraries as some of the results were contradicting.

    The idea here is that we loop through the sorted records comparing
    the current index to the next ie list[x] with list[x+1]

    If list[x] and list[x+1] is a match then
        we either mark it as
            list[x] as the 'First in matching set' 
        unless it was flagged as a duplicate previously 
            list[x] is flagged as 'Duplicate'

    If not a match then 
        we either mark it as
            list[x] is flagged as 'Unique'
        unless it was flagged as a duplicate previously 
            list[x] is flagged as 'Duplicate'

    list[x+1] is stored in a variable to keep track of whether the index was
    marked as 'Duplicate' before.

    Args:
        records_dict (dict frame)      : Dictionary with input data
        match_ratio (int)              : Integer holding the match score

    Returns:
        Returns a list.
    """

    logging.info(f"Checking for duplicates based on match ratio > {match_ratio}")
    logging.info("")

    # # Store values of the dictionary values in a list
    # # This will give me a list with dictionary index as keys
    records_list = []
    records_list = [ v for v in records_dict.values() ]

    # # Now for the loopy stuff
    # # Loop through list and compare the values
    num_of_input_records = len(records_list)

    # # Variable to track whether an index is marked as a 'Duplicate'
    dupe_idx = -1

    for idx in range(num_of_input_records):

        # # Set the break point for when the end is reached
        if idx +1 >=  num_of_input_records:
            # # Catch the last index
            if idx != dupe_idx:
                records_list[idx]['match_level'] = "Unique"
            else:
                records_list[idx]['match_level'] = "Duplicate"

            break

        # # Retrieve the names in index = idx and idx + 1
        current_field = records_list[idx]['match_key']
        next_field = records_list[idx + 1]['match_key']

        #dob_is_equal = records_list[idx]['date_of_birth'] == _records_list[idx + 1]['date_of_birth']

        # # The match ratio using the SequenceMatcher
        match_ratio_1 = SequenceMatcher(a=current_field,b=next_field).ratio()
        match_ratio_1 = match_ratio_1 * 100

        # # The match ratio using the fuzzywuzzy library
        match_ratio_2 = fuzz.token_set_ratio(current_field, next_field)

        # # Check that both ratios are greater than the default set
        if int(match_ratio_1) > match_ratio and int(match_ratio_2) > match_ratio:

            if idx != dupe_idx:
                records_list[idx]['match_level'] = "First in matching set"
            else:
                records_list[idx]['match_level'] = "Duplicate"

            logging.info(u"{0} (index-{1}) --> {2} (index-{3})".format(current_field, idx, next_field, idx + 1))

            # # Store the dupe record index so we can assign correct flag
            dupe_idx = idx + 1

        else:
            if idx != dupe_idx:
                records_list[idx]['match_level'] = "Unique"
            else:
                records_list[idx]['match_level'] = "Duplicate"

    return records_list


def output_to_file(records_list, out_file):
    '''
    Here we convert the list back to a data frame to aid with 
    filtering output.

    A little clarification on terminology that I used, hopefully:

    'first in matching set' = is one of the records that has a related entry in the file.

    'Duplicate' = would be the accompanying entry to the above.

    'matching sets' = would be records flagged as 'first in matching set' and 'Duplicate'.

    'Unique' = would be records that are not related to the above 'matching sets'.

    So if you wanted to have a clean file then an an output of
    'first in matching set' + 'Unique set' will give you that.

    If you wanted to compare the matches then an output of
    'matching sets' will help you.

    Args:
        records_list (list)        : List of input records
        out_file (string)          : Contains the base file name

    Returns:
    '''

    # # Convert list back to a data frame
    try:
        df = pd.DataFrame(records_list)
    except Exception as e:
        logging.error("Error converting list into data frame", exc_info=True)
        print ("Error converting list into data frame, check log for details")
        raise

    # # Let's do some stats. Flag records based on their 'match_level'
    count_match_level_splits(df)

    # # # # # # # # # # # # # # # # # # # #
    # # Flag matching sets and output to csv
    matching_sets = ['First in matching set', 'Duplicate']
    df_matching_sets = df[df.match_level.isin(matching_sets)]
    df_matching_sets = df_matching_sets.drop(['match_key'], axis=1)
    csv_out_file = out_file + "matching_sets.csv"

    logging.info("Outputting matching sets. This can be used to evaluate the quality of the matches.")
    logging.info("This set includes records flagged as 'First in matching set' and 'Duplicate'.")

    write_to_csv(df_matching_sets, csv_out_file)

    # # # # # # # # # # # # # # # # # # # #
    # # Flag duplicate records and output to csv
    is_dupe =  df['match_level']=='Duplicate'
    df_dupes = df[is_dupe]
    df_dupes = df_dupes.drop(['match_key'], axis=1)
    csv_out_file = out_file + "duplicates.csv"

    logging.info("Outputting duplicate records.")
    logging.info("This set includes records flagged as 'Duplicate' only.")

    write_to_csv(df_dupes, csv_out_file)

    # # # # # # # # # # # # # # # # # # # #
    # # Flag clean records and output to csv
    clean_sets = ['First in matching set', 'Unique']
    df_clean_sets = df[df.match_level.isin(clean_sets)]
    df_clean_sets = df_clean_sets.drop(['match_key', 'match_level'], axis=1)
    csv_out_file = out_file.replace("relateddata_", "unrelateddata.csv")

    logging.info("Outputting clean records.")
    logging.info("This set includes records flagged as 'First in matching set', 'Unique.")

    write_to_csv(df_clean_sets, csv_out_file)


def write_to_csv(df, out_file_name):
    """
    Outputs data frame as csv file.
    Adds filename and quantity to the log

    Args:
        df (dataframe)         : data frame containing data
        out_file_name (string) : string holding output file

    Returns:
        Nothing
    """
    num_of_records = df.shape[0]
    try:
        df.to_csv(out_file_name, header=True, index=False, mode='w')
        logging.info(f"{num_of_records} of records output to {out_file_name}")
        logging.info("")
    except Exception as e:
        logging.error("Error writing data frame to csv", exc_info=True)
        print ("Error writing data frame to csv. Check log for details.")
        raise


def count_match_level_splits(df):
    '''
    Count the levels of matching based on column 'match_level' and
    update the log and console

    Args:
        df (dataframe)         : data frame containing data

    Returns:
        Nothing
    '''
    # # Total number of records
    number_of_records = df.shape[0]

    # # Count 'first in matching sets'
    number_of_first_in_sets = df.query('match_level == "First in matching set"').match_level.count()

    # # Count Duplicates
    number_of_duplicates = df.query('match_level == "Duplicate"').match_level.count()

    # # Count uniques
    number_of_uniques = df.query('match_level == "Unique"').match_level.count()

    logging.info("")
    message = f"Total number of input records = {number_of_records}"
    logging.info(message)
    print (message)

    message = f"Total number of 'first in matching set's = {number_of_first_in_sets}"
    logging.info(message)
    print (message)

    message = f"Total number of duplicate records = {number_of_duplicates}"
    logging.info(message)
    print (message)

    message = f"Total number of uniques / unrelated records = {number_of_uniques}"
    logging.info(message)
    print (message)
    logging.info("")

    # #  Check every record in data frame has an entry in 'match_level'
    total = number_of_first_in_sets + number_of_duplicates + number_of_uniques
    if total == number_of_records:
        logging.info("The total of split quantities reconcile with total.")
        logging.info(f"{number_of_first_in_sets} + {number_of_duplicates} + {number_of_uniques} = {number_of_records}")
    else:
        logging.warning("The total of split quantities does not reconcile with total.")
        logging.warning(f"{number_of_first_in_sets} + {number_of_duplicates} + {number_of_uniques} != {number_of_records}")
        print ("The total of split quantities does not reconcile with total.")

    logging.info("")


def main(file_name, match_ratio):

    # # get script path and set log
    script_path = os.path.abspath(__file__)

    # # Assign output file and log file names
    out_file, log_file = assign_file_names(script_path)

    # # set up basic logging.
    logging.basicConfig(handlers=[logging.FileHandler(log_file, 'w', 'utf-8')], format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    # # Read input file in as data frame
    df = read_input_into_data_frame(file_name)

    # # Get user to select which colums to use as a match key
    colums_for_matching = confirm_match_fields(df)

    # # Add key fields to data frame and sort on key
    df_sorted = add_colums_and_sort(df, colums_for_matching)

    # # Save data frame as a dictionary with index as key
    records_dict = df_sorted.to_dict('index')

    # # Check for duplicate / similar entries
    records_list = check_for_matches(records_dict, match_ratio)

    # # Output related data to files
    output_to_file(records_list, out_file)

    logging.info("Script finished processing.")
    print ("Please cheeck log file for matches and breakdown.")

if __name__ == '__main__':

    # # Hard coded params
    file_name = r"C:\Input_Data\Test_Data.csv"
    match_ratio = 90

    # # Run main function
    main(file_name, match_ratio)
