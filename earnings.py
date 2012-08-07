
#from yearnings import opendbcon, retrievedata, sqlstm

import MySQLdb
import datetime
from bs4 import BeautifulSoup
import urllib2
import sys

#Exceptions
class ParamError(Exception): pass




class Earnings():
    '''
    Handles web scraping, db calls and printing methods related to
    getting earnings data
    public methods are
        - print(day from __today or range of days from __today, all companies (default) 
        or watched items only): prints earnings data
        - addwatched(company name): add new company to watched list
        - getwatched(): print list of wahtched companies

    '''
    
    def __init__(self):
        #open connection to db
        self.__dbconn = MySQLdb.connect(host="localhost",user="root",passwd="jule",db="yahoo_e")
        self.__today = datetime.date.today()
        self.__earningsdate = self.__today
        
        #init data object that stores db data
        self.data = []
        
    def close(self):
        self.__dbconn.close
    
    def sqlstm(self, stmkey):
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

       
    def storedata(self, __earningsdate, namedata="earnings"):
    #    print co_data
    #    __dbconn = MySQLdb.connect(host="localhost",user="root",passwd="jule",db="yahoo_e")
    
        if namedata == "earnings":
            delstm = self.sqlstm("delearnings")
            stm = self.sqlstm("insearnings")
        elif namedata == "watchlist":
            stm = self.sqlstm("inswatchlist")
        else:
            return
    
        c = self.__dbconn.cursor()
        c.execute(delstm,(__earningsdate))
        self.__dbconn.commit()
    
        c.executemany(stm,self.data)
        self.__dbconn.commit()
 
    def retrievedata(self, option="earnings_data"):   
        
        #NOTE
        #this one is ugly.  need improve
        
        #prepare select statement
        if option == "earnings_data":
            stm = self.sqlstm("selearnings")
        else:
            return
        #setup db cursor object
        c = self.__dbconn.cursor()
        #run query
        c.execute(stm)
        #retrieve results
        qres = c.fetchall()
        
        return qres



    def printdata(self, data):    
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
    
    def deletedata(self, option="earnings_data",rowfilter="all"):
        if option == "earnings_data" and rowfilter=="all":
            stm = self.sqlstm("delallearnings")
        else:
            return
        #setup db cursor object
        c = self.__dbconn.cursor()
        #run query
        c.execute(stm)
        self.__dbconn.commit()
    
    

    
    
    def getsoupdata(self, __earningsdate):
        
        def getPage(self, __earningsdate):   #function that returns contents of yahoo earnings web page
    
            url = "http://biz.yahoo.com/research/earncal/"+__earningsdate.strftime("%Y%m%d")+".html"
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            return response.read()
        
        
        #create soup object with web contents form yahoo earnings
        
        soup = BeautifulSoup(getPage(__earningsdate))
        #identify table with earnings data in soup object and make new soup object with it
        self.data_table = soup('table')[6]
    
        #call count_tb_elements() and store result into new var
        #upper_range = count_tb_elements()
    
        #store earnings data into co_data list object
        co_data = []
        i = 2
        while self.data_table('tr')[i].next_sibling != None: #skipping first row of data, i.e data_table headings
            try:
                co_name = self.data_table('tr')[i].td.string
            except:
                co_name = "NA"
            try:
                co_ticker = self.data_table('tr')[i].a.string
            except:
                co_ticker = "NA"
            try:
                co_when = self.data_table('tr')[i].small.string
                if co_when == None:
                    co_when = "NA"
            except:
                co_when = "NA"
            co_data.append(((co_name),(co_ticker),(co_when),(self.__today),(__earningsdate)))
            
            i += 1
    
        return co_data
    
    
    def prettyprint(self, what="earnings"):

        
        colnames = {"earnings":('Name','Ticker','When','Date Earnings','Date Added'),
                    }
        
        
        header = colnames[what]
        
        
        #statement below generates a tuple of nbers from 0 to header.len()
        collist = tuple([i for i in range(header.__len__() + 1)])
        
        #this allows the colwidth dict to adjust to nber of columns in colnames
        colwidth = dict(zip(collist,(len(str(x)) for x in header)))
        
        for x in self.data:
            colwidth.update(( i, max(colwidth[i],len(str(el))) ) for i,el in enumerate(x))
        
        #widthpattern yields this format: %-10s ie 10 spaces after word 
        widthpattern = ' | '.join('%%-%ss' % colwidth[i] for i in xrange(0,5))
        
        #mapping successive row patterns to withpattern and printing results
        print '\n'.join((widthpattern % header,
                         '-|-'.join( colwidth[i]*'-' for i in xrange(5)),
                         '\n'.join(widthpattern % collist for collist in self.data)))
        
    
    
    def addtowatchlist(self, name):
        pass

       
        
    def __printsingle(self,day,watchlist):
        
        self.__earningsdate = self.__today() + datetime.timedelta(day)
        
        #first delete previously stored data for that date if any
        #second retrieve data from yahoo! earnings webpage and store in db
        #third retrieve data from db and print

    def __print(self,*args):
        '''this is the private version of printd
        making this method private ensure that all its methods and
        variables are hidden from client code
        '''
                
        #test for day range or single day
        #range should not be more than 7 days
        #single day should not be more than 20 days ahead
        
        param = str(args[0])
        watchlist = args[1]
        
        
        if param[0] == 'r':
            rangetype = 1

            days = param[1:]
        else: rangetype = 0; days = param
        
        #Generate error if int conversion not working
        try:
            days = int(days)
        except:
            raise ParamError, "param should be an integer preceeded or not by 'r'"
        
        #depending on value of rangetype, dayslist will be a list containing either a single day
        #or a range of days
        dayslist = [g for i,g in enumerate(([days],[i for i in range(days+1)])) if i == rangetype][0]
#        print dayslist
        
        
        
        #days to print
#        sys.exit()
#        for day in dayslist:
#            self.__printsingle(day,watchlist)
            
                
        
        
    def printd(self,param=0,watchlist=False):
        '''
        this is the main public method that retrieves and prints earnings data.
         
        the following args can be provided:
        
        - 'param' (default = 0):
            param can take two forms: 
                - a day,e.g. param=1, for tomorrow's date 
                - a range of days, in which case the number must be preceded
                by 'r', e.g. r3 (for a three days range from tomorrow)
            Note if param is a range, it returns always at least the current day's earnings
            Note param defaults to 0, i.e. todays earnings date
        
        - 'watchlist':
            = False (default) : shows companies included in watchlist followed by those companies not included in the
            watchlist
            = True : shows those companies included in watchlist only
        '''
        #this calls the private version of this method to keep all internal variables and 
        #methods hidden from the client code
        
        self.__print(param,watchlist)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    Earnings().printd("r4")
    