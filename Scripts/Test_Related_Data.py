import unittest
from unittest import mock
import pandas as pd
import Related_Data


class TestRelated_Data(unittest.TestCase):

    def test_input_file(self):

        with self.assertRaises(FileNotFoundError):

            #Related_Data.read_input_into_data_frame('C:\Data_Shed_Techical\Input_Data\DataShed_Technical_Test.csv')

            Related_Data.read_input_into_data_frame('C:\Data_Shed_Techical\Input_Data\DataShed_TechnicalTest.csv')

        with self.assertRaises(pd.errors.EmptyDataError):

            Related_Data.read_input_into_data_frame('C:\Data_Shed_Techical\Input_Data\Test_Empty_File.csv')



if __name__ == '__main__':
    unittest.main()



