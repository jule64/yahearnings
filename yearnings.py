'''
Created on Jun 30, 2012

@author: jule64@gmail.com


to dos:
    - create earnings object and stick in it all the methods and db interaction
        e.g. should have methods like refreshdata(), addwatchlist(), getdata(), etc.
    - keep main function to handle user I/O and send instructions to earnings object



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





#returns number of elements in data_table, i.e. nb of companies releasing their results
#this helps define the upper boundary of data_table for further manipulation later
#def count_tb_elements():
#    t = True
#    index = 1
#    while t == True:
#        val = data_table('tr')[index].next_sibling
#        if val == None:
#            t = False
#        else: index += 1 #maybe do index += 1 instead
#    nb_elements = index
#    return nb_elements



#
# DB FUNCTIONS
#
def opendbcon(dbname):
    return MySQLdb.connect(host="localhost",user="root",passwd="jule",db=dbname)  
    

def sqlstm(stmkey):
    
    stm = {"selearnings":'''SELECT CO_NAME, CO_TICKER, CO_WHEN, DATE_EARNINGS, DATE_ADDED FROM `earnings_data`
                ORDER BY `DATE_EARNINGS` DESC''',
           "inswatchlist":'''INSERT INTO `watchlist` (NAME, CO_TICKER, DATE_ADDED)
                VALUES (%s,%s,%s)''',
           "insearnings":'''INSERT INTO `earnings_data` (CO_NAME, CO_TICKER, CO_WHEN, DATE_EARNINGS, DATE_ADDED)
                VALUES (%s,%s,%s,%s,%s)''',
           "delearnings":'''DELETE FROM `earnings_data` WHERE DATE_EARNINGS = %s''',
           "delallearnings":'''DELETE FROM `earnings_data`''',
           "selwatched":'''select DISTINCT `earnings_data`.`CO_NAME`, `earnings_data`.`CO_TICKER`, `earnings_data`.`CO_WHEN`,
                `earnings_data`.`DATE_EARNINGS`, `watchlist`.`NAME` AS `WATCHED_NAME`
                FROM `yahoo_e`.`earnings_data` JOIN `yahoo_e`.`watchlist`
                on (`earnings_data`.`CO_NAME` LIKE concat('%',`watchlist`.`NAME`,'%'))
                ORDER BY `earnings_data`.`DATE_EARNINGS` DESC''',
           }
    return stm[stmkey]




def storedata(dbconn, data, earningsdate, namedata="earnings"):
#    print co_data
#    dbconn = MySQLdb.connect(host="localhost",user="root",passwd="jule",db="yahoo_e")

    if namedata == "earnings":
        delstm = sqlstm("delearnings")
        stm = sqlstm("insearnings")
    elif namedata == "watchlist":
        stm = sqlstm("inswatchlist")
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
        stm = sqlstm("selearnings")
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
        stm = sqlstm("delallearnings")
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
    while data_table('tr')[i].next_sibling != None: #skipping first row of data, i.e data_table headings
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


def prettyprint(data):
    header = ('Name','Ticker','When','Date Earnings','Date Added')
    
    #replace colwidth with lenght col
    colwidth = dict(zip((0,1,2,3,4,5),(len(str(x)) for x in header)))
    
    for x in data:
        colwidth.update(( i, max(colwidth[i],len(str(el))) ) for i,el in enumerate(x))
    
    #widthpattern yields this format: %-10s ie 10 spaces after word 
    widthpattern = ' | '.join('%%-%ss' % colwidth[i] for i in xrange(0,5))
    
    #mapping successive row patterns to withpattern and printing results
    print '\n'.join((widthpattern % header,
                     '-|-'.join( colwidth[i]*'-' for i in xrange(5)),
                     '\n'.join(widthpattern % (a,b,c,d,e) for (a,b,c,d,e) in data)))
    


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
            sleep(round(random.uniform(4, 6),1)) #pause a random time between each calls to http://biz.yahoo.com/ to avoid suspicion... (probably unnecessary but just in case!)


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
        
 

    mydata = retrievedata(dbconn)
    prettyprint(mydata)
    
    
    dbconn.close

    gc.collect()

if __name__ == "__main__":
    main()
    


    