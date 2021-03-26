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
        
class Test(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # get_data will get test data if 'testdata' dir
        # is not found in test/ dir
        get_data()
        # load full testdata set
        self.files = [
            'tests/testdata/harmonie_2021032306.00', 
            'tests/testdata/harmonie_2021032306.03',
            'tests/testdata/harmonie_2021032306.06',
            'tests/testdata/harmonie_2021032306.01',
            'tests/testdata/harmonie_2021032306.04',
            'tests/testdata/harmonie_2021032306.02',
            'tests/testdata/harmonie_2021032306.05'
        ]
        self.files3 = [
            'tests/testdata/harmonie_2021032306.00',
            'tests/testdata/harmonie_2021032306.01',
            'tests/testdata/harmonie_2021032306.02',
        ]
        self.data, _ = snowdrift.collectData(self.files)


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_input_data_params(self):
        # check that we have loaded parameters:
        # temp, snowac, snowground, temp, wind-u/v
        params = sorted(self.data.keys())
        self.assertEqual(params, ['snowac', 'snowground', 'temp', 'wind-u', 'wind-v'])

    def test_calculate_deps(self):
        # caculateDeps should add wind,
        # and delete u/v vectors
        data, _ = snowdrift.collectData(self.files3)
        snowdrift.calculateDeps(data)
        self.assertIn('wind', data)
        self.assertNotIn('wind-u', data)
        self.assertNotIn('wind-v', data)

    def test_snowdrift(self):
        # snowdrift algorithm should add,
        # snowage, mobility, driftacc, drift parameters,
        data, _ = snowdrift.collectData(self.files3)
        snowdrift.snowdrift(data)
        self.assertIn('snowage', data)
        self.assertIn('mobility', data)
        self.assertIn('driftacc', data)
        self.assertIn('drift', data)

    def test_input_data_sorting(self):
        # order of forecast data input should not affect
        # data loading...
        files1 = [
            'tests/testdata/harmonie_2021032306.00',
            'tests/testdata/harmonie_2021032306.01',
            'tests/testdata/harmonie_2021032306.02',
        ]
        files2 = [
            'tests/testdata/harmonie_2021032306.01',
            'tests/testdata/harmonie_2021032306.00',
            'tests/testdata/harmonie_2021032306.02',
        ]
        data1, _ = snowdrift.collectData(files1)
        data2, _ = snowdrift.collectData(files2)
        times1 = data1['temp']['times']
        times2 = data2['temp']['times']
        self.assertEqual(times1, times2)