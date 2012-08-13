
#from yearnings import opendbcon, retrievedata, sqlstm

import MySQLdb
import datetime
from bs4 import BeautifulSoup
import urllib2
import sys, traceback

#Exceptions
class Error(Exception): """Base class for exceptions in this module."""; pass

class ParamError(Error):

    def __init__(self,param):
        self.value = ('"' + param + '"' + " is not a valid argument.  param should be an integer preceded or not by " + '"' + "r" + '"')
    def __str__(self):
        return self.value

    
class WatchlistParamError(Error):
    
    def __init__(self,watchlist):
        self.value = ('"' + watchlist + '"' + " is not a valid argument for watchlist. Use either True or False (default)")
    def __str__(self):
        return self.value

class DateNotAvailableError(Error):
    pass



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
        #TODO create test for db conn not available
        self.__dbconn = MySQLdb.connect(host="localhost",user="root",passwd="jule",db="yahoo_e")
#        self.__today = datetime.date.today()
#        self.__earningsdate = self.__today
        
        #init data object that stores db data
        self.data = []
#        self.__today = ""
        
    def __del__(self):
            self.close()
        
    def close(self):
        self.__dbconn.close
    
    def __sqlstm(self, stmkey):
        stm = {"selearnings":'''SELECT CO_NAME, CO_TICKER, CO_WHEN, DATE_EARNINGS, DATE_ADDED FROM `earnings_data`
		            ORDER BY `DATE_EARNINGS` DESC''',
		       "inswatchlist":'''INSERT INTO `watchlist` (NAME, CO_TICKER, DATE_ADDED)
		            VALUES (%s,%s,%s)''',
		       "insearnings":'''INSERT INTO `earnings_data` (CO_NAME, CO_TICKER, CO_WHEN, DATE_EARNINGS, DATE_ADDED)
		            VALUES (%s,%s,%s,%s,%s)''',
		       "delearningsbydate":'''DELETE FROM `earnings_data` WHERE DATE_EARNINGS = %s''',
		       "delallearnings":'''DELETE FROM `earnings_data`''',
		       "selwatched":'''select DISTINCT `earnings_data`.`CO_NAME`, `earnings_data`.`CO_TICKER`, `earnings_data`.`CO_WHEN`,
		            `earnings_data`.`DATE_EARNINGS`, `watchlist`.`NAME` AS `WATCHED_NAME`
		            FROM `yahoo_e`.`earnings_data` JOIN `yahoo_e`.`watchlist`
		            on (`earnings_data`.`CO_NAME` LIKE concat('%',`watchlist`.`NAME`,'%'))
		            ORDER BY `earnings_data`.`DATE_EARNINGS` DESC''',
		       }
        return stm[stmkey]

       
    def storedata(self, __earningsdate, namedata="earnings"):
    #    print self.edata
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
            stm = self.__sqlstm("selearnings")
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
    
    def __deleteData(self, option="earnings_data"):
        if option == "earnings_data":
            stm = self.__sqlstm("delearningsbydate")
        else:
            return
                
#        stm = datatables[option]
        
        #setup db cursor object
        c = self.__dbconn.cursor()
        #run query
        c.execute(stm,(self.__earningsdate))
        self.__dbconn.commit()




    def __getPage(self):   #function that returns contents of yahoo earnings web page

        url = "http://biz.yahoo.com/research/earncal/"+self.__earningsdate.strftime("%Y%m%d")+".html"
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    

    
    
    def __getsoupdata(self):
        

        
        
        #create soup object with web contents form yahoo earnings
        

        #identify table with earnings data in soup object and make new soup object with it
        #TODO raise DateNotAvailableError if this line breaks e g with 
        #http://biz.yahoo.com/research/earncal/20121124.html 
        
        try:
            soup = BeautifulSoup(self.__getPage())
        except:
            raise DateNotAvailableError, "there are no earnings data available for " + str(self.__earningsdate)
        
        self.souptable = soup('table')[6]
        
        #call count_tb_elements() and store result into new var
        #upper_range = count_tb_elements()
    
        #store earnings data into self.edata list object
        self.edata = []
        i = 2
        while self.souptable('tr')[i].next_sibling != None: #skipping first row of data, i.e data_table headings
            try:
                co_name = self.souptable('tr')[i].td.string
            except:
                co_name = "NA"
            try:
                co_ticker = self.souptable('tr')[i].a.string
            except:
                co_ticker = "NA"
            try:
                co_when = self.souptable('tr')[i].small.string
                if co_when == None:
                    co_when = "NA"
            except:
                co_when = "NA"
            self.edata.append(((co_name),(co_ticker),(co_when),(self.__today),(self.__earningsdate)))
            
            i += 1
    
#        return self.edata
    
    
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
        

        
        self.__earningsdate = self.__today + datetime.timedelta(day)
        
        

        
        # 1- delete earnings data in db by earnings date 
        self.__deleteData()
        
        
        # 2- retrieve data from yahoo! earnings webpage and store in db        
        self.__getsoupdata()        
        
        

        # 3- retrieve data from db and print
        #     retrieve and print either watchlist only or watchlist and second part list
        #     based on value of watchlist param   

    def __print(self,param,watchlist):
        '''this is the private version of printd
        making this method private ensure that all its methods and
        variables are hidden from client code
        '''
                
        #test for day range or single day
        #range should not be more than 7 days
        #single day should not be more than 20 days ahead
        
        param = str(param)
        
        
        if param[0] == 'r':
            rangetype = 1

            days = param[1:]
        else: rangetype = 0; days = param
        
        #Generate custom exception if int conversion not working
        try:
            days = int(days)

        except:
            raise ParamError, param
        
        if watchlist not in (True, False):
            raise WatchlistParamError, watchlist  
        
        
        #depending on value of rangetype, dayslist will be a list containing either a single day
        #or a range of days

        dayslist = [g for i,g in enumerate(([days],[i for i in range(days+1)])) if i == rangetype][0]
        
        self.__today = datetime.date.today()
                
        
        #days to print
        for day in dayslist:
            self.__printsingle(day,watchlist)
            
                
        
        
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
    Earnings().printd()

    
    