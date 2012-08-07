'''
Created on Jun 30, 2012

@author: jule64@gmail.com


to dos:
    - create earnings object and stick in it all the methods and db interaction
        e.g. should have methods like refreshdata(), addwatchlist(), getdata(), etc.
    - keep main function to handle user I/O and send instructions to earnings object



'''

#imports
#from bs4 import BeautifulSoup
#import datetime
#import urllib2
import gc
#import MySQLdb
#from time import sleep
#import random

import earnings


def main():
    
    e = earnings.Earnings()
    e.printd(2)
#    e.printd("r4d")
    e.close
    

#    today = datetime.date.today()
#    horizon=5 #nb forward days of earnings data

#    i=3
#    
#    while i < horizon + 1:
#        print "Day "+str(i)
#        if i > 0 and i < horizon:
#            sleep(round(random.uniform(4, 6),1)) #pause a random time between each calls to http://biz.yahoo.com/ to avoid suspicion... (probably unnecessary but just in case!)
#
#
#        earningsdate = datetime.date.today() + datetime.timedelta(days=i)
#      
#        try:
#            j=True
#            #load yahoo earnings html file into list object co_data
#            co_data = getsoupdata(today, earningsdate)
#        except:
#            j=False
#        
#        if j == True:
#            #store data in yahoo_e database
#            storedata(dbconn, co_data, earningsdate, "earnings")     
#        
#        
#        i += 1
#        
# 
#
#    mydata = retrievedata(dbconn)
#    prettyprint(mydata)
#    
#    
#    dbconn.close

    gc.collect()
    
    print "success"

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    main()
    