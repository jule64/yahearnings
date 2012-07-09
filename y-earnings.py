'''
Created on Jun 30, 2012

@author: julienmonnier


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


def getfdate(earningsdate):    #function that return formated date for url processing
#        today = datetime.date.today()
#        rawdate = today + datetime.timedelta(days=day)
        fdate = earningsdate.strftime("%Y%m%d")
        return fdate
    
#    for day in range(0,i):
#        rawdate = today + datetime.timedelta(days=day)
#        fdate = rawdate.strftime("%Y%m%d")
#        urldates.append(fdate)



def getPage(earningsdate):   #function that returns contents of yahoo earnings web page
    
    url = "http://biz.yahoo.com/research/earncal/"+getfdate(earningsdate)+".html"
     
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return response.read()
 




#returns number of elements in data_table, i.e. nb of companies releasing their results
#this helps define the upper boundary of data_table for further manipulation later
def count_tb_elements():
    t = True
    index = 1
    while t == True:
        val = data_table('tr')[index].next_sibling
        if val == None:
            t = False
        else: index = index + 1 #maybe do index += 1 instead
    nb_elements = index
    return nb_elements



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
    upper_range = count_tb_elements()

    #store earnings data into co_data list object    
    co_data = []
    for i in range(2, upper_range): #skipping first row of data, i.e data_table headings
        co_name = data_table('tr')[i].td.string
        co_ticker = data_table('tr')[i].a.string
        co_when = data_table('tr')[i].small.string
        co_data.append(((co_name),(co_ticker),(co_when),(today),(earningsdate)))      
    return co_data


def addtowatchlist(name):
    return


#MAIN program starts here
def main():

    dbconn = opendbcon("yahoo_e")
    
    today = datetime.date.today()
    horizon=2 #nb forward days of earnings data

    for i in range(2,horizon): #0 returns no time delta below function,i.e. today   
        earningsdate = datetime.date.today() + datetime.timedelta(days=i)
        #load yahoo earnings html file into list object co_data
        co_data = getsoupdata(today, earningsdate)
    
        #store data in yahoo_e database
        storedata(dbconn, co_data, earningsdate, "earnings")
        
        #    #print value of upper_range
        #    print ("nb of companies is "+str(upper_range))
    




#next steps
#create db table for watchlist
#check main table against names in watchlist
#produce list of companies earnings by date (up to 5 days) with companies from watchlist at top.


    mydata = retrievedata(dbconn)
    printdata(mydata)
    
    dbconn.close

    gc.collect()

if __name__ == "__main__":
    main()
    
    