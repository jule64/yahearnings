'''
Created on Aug 6, 2012

@author: jule64@gmail.com
'''
import earnings
from earnings import Earnings
import unittest


#TODO:   check pydoc for how to put setUp and tearDown methods in InitTestCase
#        instead of TestParam (currently this raises an "self.e not found" error)
class InitTestCase(unittest.TestCase):
    
    pass
#    def setUp(self):
#        self.e = Earnings()
#        
#    def tearDown(self):
#        self.e.close



class TestParam(unittest.TestCase):

    def setUp(self):
        self.e = Earnings()
        
    def tearDown(self):
        self.e.close
    
    def test_notintegerparam(self):
        """should raise error when integer not present in param or char found 
        after first character in param"""
        values = ("rr","r3k","34r")
        for v in values:
            self.assertRaises(earnings.ParamError, self.e.printd(),v)


    def test_paramoneday(self):
        '''dayslist should hold only one integer if
        param is an integer'''
        
        knownvalues = ((2,2),
                       (3,3),
                       (5,5))

        
        for param,returnval in knownvalues:
            result = self.e.printd(param,False)
            self.assertEqual(returnval, result)

        
    def test_paramonerangedays(self):
        '''dayslist should hold a range of integers if
        param is an integer preceded by "r"'''
        


    def test_printexception(self):
        '''__print should raise an exception if param is not an integer
        or if the first character is a char other than "r"
        or if it contains a char after
        the first character'''
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()