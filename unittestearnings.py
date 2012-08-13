'''
Created on Aug 6, 2012

@author: jule64@gmail.com
'''
import earnings
from earnings import Earnings
import unittest
#import urllib2

from mock import patch, Mock



class TestEarningsArgs(unittest.TestCase):


    def setUp(self):
        self.e = Earnings()

    
    def testIncorrectParam(self):
        '''should raise error when integer not present in param or char found after first character in param'''
        values = ("rr","r3k","34r")
        for v in values:
            self.assertRaises(earnings.ParamError, self.e.printd, param=v)


    def testIncorrectWatchlistValue(self):
        '''should raise error when watchlist parameter is different from True or False'''
        values = ("F"," ","1")
        for v in values:
            self.assertRaises(earnings.WatchlistParamError, self.e.printd, watchlist=v)


    


class TestWebData(unittest.TestCase):


    def setUp(self):
        self.e = Earnings()

    @patch.object(earnings.Earnings, '_Earnings__deleteData')
    @patch.object(earnings.Earnings, '_Earnings__getPage')
    def testEarningsDataExist(self,mockedgetPage,mockeddeleteData):
        "should raise DateNotAvailableError exception if earnings page does not exist"
       
        #Test explanations:
        #If the requested earnings page does not exist, __getPage will generate an Exception. However due to the difficulty
        #of finding a broken link based on user inputs I decided to mock __getPage to simulate the broken link Exception.
        #I achieve this by patching __getPage using the patch decorator above and by giving it a side effect = Exception.
        #
        #In addition, before calling __getPage the SUT makes a call to __deleteData, which performs some deletions on the db.
        #Since I do not want to delete any data for this test I therefore patched __deleteData and gave it a None return_value below
        #so as to simulate that the deletion has been carried out when the SUT calls this method

        mockeddeleteData.return_value = None
        mockedgetPage.side_effect=Exception('Oops error')

        self.assertRaises(earnings.DateNotAvailableError, self.e.printd)




if __name__ == "__main__":

    unittest.main(verbosity=2)
    