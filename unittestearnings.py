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
        #If the earnings page does not exist, __getPage will generate an Exception. Therefore in order
        #to test this condition I need to simulate an exception in __getPage by patching it and giving it an Exception side effect.
        #
        #In addition, before calling __getPage the SUT makes a call to __deleteData, which performs some deletions on the db.
        #Since I do not want to delete any data for this test I therefore need to patch __deleteData and give it a None return_value
        #so as to simulate that the deletion was carried out when the SUT calls this method

        mockeddeleteData.return_value = None
        mockedgetPage.side_effect=Exception('Oops error')

        self.assertRaises(earnings.DateNotAvailableError, self.e.printd)




if __name__ == "__main__":

    unittest.main(verbosity=2)
    