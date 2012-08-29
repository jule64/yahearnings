'''
Created on Aug 6, 2012

@author: jule64@gmail.com
'''
import earnings
from earnings import Earnings
import unittest
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


    


class TestDependencies(unittest.TestCase):


#    def setUp(self):
#        self.e = Earnings()


    #Test Web Page Exists
    @patch.object(earnings.Earnings, '_Earnings__deleteData')
    @patch.object(earnings.Earnings, '_Earnings__getPage')
    def testEarningsDataExist(self,mocked_getPage,mocked_deleteData):
        "should raise DateNotAvailableError exception if earnings page does not exist"

        #Test explanations:
        #If the requested earnings page does not exist, __getPage will generate an Exception. A url exception 
        #could be achieved by providing specific input parameters in printd, however should the url returned
        #with those parameters become available in the future, the test would fail without even changing the code
        #which is not good. Therefore for this test to be stable over time I decided to patch __getPage and give it 
        #a url Exception side effect to simulate a broken link. 
        #
        #In addition, before calling __getPage the SUT makes a call to __deleteData, which performs some deletions on the db.
        #Since I do not want to delete any data for this test I therefore patched __deleteData and gave it a None return_value below
        #so as to simulate that the deletion has been carried out when the SUT calls this method
        
        self.e = Earnings()
        mocked_deleteData.return_value = None
        mocked_getPage.side_effect=Exception('Oops error')

        self.assertRaises(earnings.DateNotAvailableError, self.e.printd)

    #Test database connection is available
    @patch.object(earnings.MySQLdb, 'connect')
    def testDbConnProblem(self,mocked_dbconn):
        "Should raise DbConnectionError exception if SUT unable to connect to MySQL server"

        #mock db conn call and give Except side effect
        mocked_dbconn.side_effect = Exception()
        self.assertRaises(earnings.DbConnectionError,earnings.Earnings)
        

        
        
        


if __name__ == "__main__":

    unittest.main(verbosity=2)
    