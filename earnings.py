
#from yearnings import opendbcon, retrievedata, sqlstm

import MySQLdb
import datetime
from bs4 import BeautifulSoup
import urllib2
import sys, traceback
import re


#**********************************
#Exception classes
#**********************************

class Error(Exception): """Base class for exceptions in this module."""; pass

class DateNotAvailableError(Error): pass

class DbConnectionError(Error): pass

class DictValueError(Error): pass

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




        




#**********************************
#Main class
#**********************************

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
        try:
            self.__dbconn = MySQLdb.connect(host="localhost",user="root",passwd="jule",db="yahoo_e")
        except:
            raise DbConnectionError, "Python is unable to connect to the yahoo_e database.\nPlease verify that MySQL Server is running"

        #store earnings data into a self.__earndata list object
        self.__earningsdata = []
        
        
    def __del__(self):
            self.close()
        
        
    def close(self):
        #If self.__dbconn has not been successfully instantiated in self.__init__ then
        #the code below will skip the __dbconn.close statement
        if hasattr(self,'_Earnings__dbconn'):
            self.__dbconn.close   
        

    
    def __prettyprint(self, option):

 
        datainfo = {"earnings":(('Name','Ticker','When','Date Earnings','Date Added'),self.__earningsdata),
                    }


        if option not in datainfo:
            raise KeyError, str(option) + " is not a key value in prettyprint"
        
        header = datainfo[option][0]
        
        
        #statement below generates a tuple of nbers from 0 to header.len()
        collist = tuple([i for i in range(header.__len__() + 1)])
        
        #this allows the colwidth dict to adjust to nber of columns in colnames
        colwidth = dict(zip(collist,(len(str(x)) for x in header)))
        
        for x in datainfo[option][1]:
            colwidth.update(( i, max(colwidth[i],len(str(el))) ) for i,el in enumerate(x))
        
        #widthpattern yields this format: %-10s ie 10 spaces after word 
        widthpattern = ' | '.join('%%-%ss' % colwidth[i] for i in xrange(0,5))
        
        #mapping successive row patterns to withpattern and printing results
        print '\n'.join((widthpattern % header,
                         '-|-'.join( colwidth[i]*'-' for i in xrange(5)),
                         '\n'.join(widthpattern % collist for collist in datainfo[option][1])))


     
    def __sqlstm(self, stmkey):
        stm = {"inswatchlist":'''INSERT INTO `watchlist` (NAME, CO_TICKER, DATE_ADDED)
		            VALUES (%s,%s,%s)''',
		       "storeearnings":('''INSERT INTO `earnings_data` (CO_NAME, CO_TICKER, CO_WHEN, DATE_EARNINGS, DATE_ADDED)
		            VALUES (%s,%s,%s,%s,%s)''',self.__earningsdata),
		       "delday":('''DELETE FROM `earnings_data` WHERE DATE_EARNINGS = %s''',self.__dateearnings),
               "selearnings":('''SELECT CO_NAME, CO_TICKER, CO_WHEN, DATE_EARNINGS, DATE_ADDED FROM `earnings_data`
                     WHERE DATE_EARNINGS = %s''',self.__dateearnings),
               "selwatched":('''select DISTINCT `earnings_data`.`CO_NAME`, `earnings_data`.`CO_TICKER`, `earnings_data`.`CO_WHEN`,
                    `earnings_data`.`DATE_EARNINGS`, `watchlist`.`NAME` AS `WATCHED_NAME`
                    FROM `yahoo_e`.`earnings_data` JOIN `yahoo_e`.`watchlist`
                    on (`earnings_data`.`CO_NAME` LIKE concat('%%',`watchlist`.`NAME`,'%%'))
                    WHERE `earnings_data`.`DATE_EARNINGS` = %s''',self.__dateearnings),
               "selexwatched":('''select DISTINCT `earnings_data`.`CO_NAME`, `earnings_data`.`CO_TICKER`, `earnings_data`.`CO_WHEN`,
                    `earnings_data`.`DATE_EARNINGS`, "" AS `WATCHED_NAME`
                    FROM `yahoo_e`.`earnings_data` LEFT JOIN `yahoo_e`.`WATCHLISTRET`
                    on (`earnings_data`.`CO_NAME` = `WATCHLISTRET`.`CO_NAME`)
                    WHERE `WATCHLISTRET`.`CO_NAME` is null AND `earnings_data`.`DATE_EARNINGS` = %s
                    ORDER BY `earnings_data`.`CO_NAME`''',self.__dateearnings),
		       }
        return stm[stmkey]




    def __dbExecute(self, option):
        
        #NB: the return type of deletestms[key] needs to be a tuple hence
        #TODO: ensure statements in __sqlstm are up to date
        execstms = {
                   "delday":self.__sqlstm("delday"),
                   "storeearnings":self.__sqlstm("storeearnings"),
                   "getearnings":self.__sqlstm("selearnings"),
                   "getwatched":self.__sqlstm("selwatched"),
                   "getexwatched":(self.__sqlstm("selexwatched")),                   
                   }
        
        #Exception handling
        #TODO: raise exception if key not in deletestms AND
        #if return value of deletestms is not a tuple
        if option not in execstms:
            raise KeyError, str(option) + " is not a key value in execstms"
        
        
        #setup db cursor object
        c = self.__dbconn.cursor()

        #run query
        #NB: since the number of arguments in execute can vary from one to two
        #I need to add the '*' in order to assign the values returned 
        #by execstms dynamically into execute
        
        execstm = execstms[option]
        

            
        #TODO REAL UGLY IMPROVE!    
        
        if re.search('^get',option):
            if len(execstm) == 1:
                c.execute(execstm[0])
                self.__earningsdata = c.fetchall()
            else:
                c.execute(*execstm)
                self.__earningsdata = c.fetchall()
        else:
            if len(execstm) > 1:
                if type(execstm[1]) is list:
                    c.executemany(*execstm)
            else:
                c.execute(*execstm)



        #commit query results to db
        self.__dbconn.commit()



    def __getPage(self):   #function that returns contents of yahoo earnings web page

        url = "http://biz.yahoo.com/research/earncal/"+self.__dateearnings.strftime("%Y%m%d")+".html"
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()


    

    def __getsoupdata(self):
        
        #obtains earnings data from yahoo earnings and
        #store that data into the yahoo_e database
        
        try:
            soup = BeautifulSoup(self.__getPage())
        except:
            raise DateNotAvailableError, "there are no earnings data available for " + str(self.__dateearnings)
        
        self.souptable = soup('table')[6]
        

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
            self.__earningsdata.append(((co_name),(co_ticker),(co_when),(self.__today),(self.__dateearnings)))
            
            i += 1
    
#        return self.edata


       
    def __printday(self,daynum,watchlist):
        
        self.__dateearnings = self.__today + datetime.timedelta(daynum)
        
        
#        if self.__dateearnings >= self.__today:
#
#            # 1- delete earnings data in db by earnings date
#            self.__dbExecute("delday")
#            
#            # 2- retrieve data from yahoo! earnings webpage and store in db        
#            self.__getsoupdata()
#            self.__dbExecute("storeearnings")
       

        # 3- retrieve data from db and print
        #     retrieve and print either watchlist only or watchlist and second part list
        #     based on value of watchlist param
        for exestr in ("getwatched","getexwatched"):
            self.__dbExecute(exestr)
            self.__prettyprint("earnings")        


    def __print(self,param,watchlist):
        '''this method implements printd.  It is made private to
        ensure that all its methods and
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
        
        #Generate custom exception if watchlist value is incorrect
        if watchlist not in (True, False):
            raise WatchlistParamError, watchlist
        
        #At this point we have checked that all input parameters are valid
        
        
        
        #depending on value of rangetype, dayslist will be a list containing either a single day
        #or a range of days

        dayslist = [g for i,g in enumerate(([days],[i for i in range(days+1)])) if i == rangetype][0]
        
        self.__today = datetime.date.today()

        
        #days to print
        for daynum in dayslist:
            self.__printday(daynum,watchlist)
            
            
            
        
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
    
    
    
    
    def addtowatchlist(self, name):
        pass


    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #this line runs the main method with default values
    Earnings().printd(-1)

    
    