import unittest
import os
import urllib
import time
import snowdrift

def get_data():
    # if testdata dir does not exist, then get testdata from cloud
    if not os.path.isdir("tests/testdata"):
        print("\nGetting testdata:")
        urllib.urlretrieve("https://s3.eu-west-2.amazonaws.com/share.bitvinci.is/testdata/snowdrift_testdata.zip", "tests/testdata.zip")
        # extract the zipped data
        os.system("cd tests; unzip testdata.zip")
        
class TestForecast(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # get_data will get test data if 'testdata' dir
        # is not found in test/ dir
        get_data()

    def setUp(self):
        # load testdata...git
        files = ['tests/testdata/harmonie_2021032306.00', 
            'tests/testdata/harmonie_2021032306.03',
            'tests/testdata/harmonie_2021032306.06',
            'tests/testdata/harmonie_2021032306.01',
            'tests/testdata/harmonie_2021032306.04',
            'tests/testdata/harmonie_2021032306.02',
            'tests/testdata/harmonie_2021032306.05'
        ]
        self.data = snowdrift.collectData(files)


    def tearDown(self):
        pass

    def test_01(self):
        pass
