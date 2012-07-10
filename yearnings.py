'''
Created on Jun 30, 2012

@author: jule64@gmail.com


to dos:
    - create function to calc n-foward days of weeks and build result into 
    yahoo earnings url for querying
    - create getday(x) function to return x days from now (default x = 0)
    then call getpage(y) with y = getday(x)
    



'''

#imports
from bs4 import BeautifulSoup
import datetime
import urllib2
import gc
import MySQLdb
from time import sleep
import random


def getPage(earningsdate):   #function that returns contents of yahoo earnings web page
    
    url = "http://biz.yahoo.com/research/earncal/"+earningsdate.strftime("%Y%m%d")+".html"
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return response.read()



#
# DB FUNCTIONS
#
def opendbcon(dbname):
    return MySQLdb.connect(host="localhost",user="root",passwd="jule",db=dbname)  
    

def storedata(dbconn, data, earningsdate, namedata = "earnings"):
#    print co_data
#    dbconn = MySQLdb.connect(host="localhost",user="root",passwd="jule",db="yahoo_e")

    if namedata == "earnings":
        delstm = """DELETE FROM `earnings_data` WHERE DATE_EARNINGS = %s"""
        stm = """INSERT INTO `earnings_data` (CO_NAME, CO_TICKER, CO_WHEN, DATE_EARNINGS, DATE_ADDED)
        VALUES (%s,%s,%s,%s,%s)"""
    elif namedata == "watchlist":
        
        stm = """INSERT INTO `watchlist` (NAME, CO_TICKER, DATE_ADDED)
        VALUES (%s,%s,%s)"""
    else:
        return

    c = dbconn.cursor()
    print earningsdate
    c.execute(delstm,(earningsdate))
    dbconn.commit()

    c.executemany(stm,data)
    dbconn.commit()
 

 
def retrievedata(dbconn, option="earnings_data"):   
    
    #prepare select statement
    if option == "earnings_data":
        stm = """SELECT * FROM `earnings_data`"""
    else:
        return
    #setup db cursor object
    c = dbconn.cursor()
    #run query
    c.execute(stm)
    #retrieve results
    qres = c.fetchall()
    
    return qres



def printdata(data):    
    for r in range(0,len(data)):
        printable = ""
        lendata = len(data[0])
        for v in range(0,lendata):
            if v < (lendata - 1):
                separator = ", "
            else:
                separator = ""
            
            printable = printable + str(data[r][v]) + separator
        print printable
    
def deletedata(dbconn, option="earnings_data",rowfilter="all"):
    if option == "earnings_data" and rowfilter=="all":
        stm = """DELETE FROM `earnings_data`"""
    else:
        return
    #setup db cursor object
    c = dbconn.cursor()
    #run query
    c.execute(stm)
    dbconn.commit()



def getsoupdata(today, earningsdate):
    global data_table
    #create soup object with web contents form yahoo earnings
    
    soup = BeautifulSoup(getPage(earningsdate))
    #identify table with earnings data in soup object and make new soup object with it
    data_table = soup('table')[6]

    #call count_tb_elements() and store result into new var
#    upper_range = count_tb_elements()

    #store earnings data into co_data list object
    co_data = []
    i = 2
    while data_table('tr')[i].next_sibling <> None: #skipping first row of data, i.e data_table headings
        try:
            co_name = data_table('tr')[i].td.string
        except:
            co_name = "NA"
        try:
            co_ticker = data_table('tr')[i].a.string
        except:
            co_ticker = "NA"
        try:
            co_when = data_table('tr')[i].small.string
            if co_when == None:
                co_when = "NA"
        except:
            co_when = "NA"
        co_data.append(((co_name),(co_ticker),(co_when),(today),(earningsdate)))
        
        i += 1

    return co_data


def addtowatchlist(name):
    return


#MAIN program starts here
def main():
    
    dbconn = opendbcon("yahoo_e")

    today = datetime.date.today()
    horizon=5 #nb forward days of earnings data

    i=3
    
    while i < horizon + 1:
        print "Day "+str(i)
        if i > 0 and i < horizon:
            sleep(round(random.uniform(4, 6),1)) #pause a random time between each calls to http://biz.yahoo.com/ to avoid suspicion... (not sure that's necessary but I don't want trouble!)


        earningsdate = datetime.date.today() + datetime.timedelta(days=i)
      
        try:
            j=True
            #load yahoo earnings html file into list object co_data
            co_data = getsoupdata(today, earningsdate)
        except:
            j=False
        
        if j == True:
            #store data in yahoo_e database
            storedata(dbconn, co_data, earningsdate, "earnings")     
        
        
        i += 1
        
 
    




#next steps
#create db table for watchlist
#check main table against names in watchlist
#produce list of companies earnings by date (up to 5 days) with companies from watchlist at top.


    mydata = retrievedata(dbconn)
#    print mydata
    
#    print "\n".join (map (lambda (x, y): "%s\t%s" % ("\t".join (x), y), mydata) )
    
    dbconn.close

    gc.collect()

if __name__ == "__main__":
    main()
    
    
