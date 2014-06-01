'''
Created on Jan 4, 2013

@author: morganeciot

TODO: Check that most recent stock is last
'''

import pymongo
import urllib2
import datetime
import sys

class Update():
    def __init__(self):
        self.today = datetime.date.today()
        # Create a MongoClient to the running mongod instance and get the relevant database
        self.collection = pymongo.MongoClient().gaetan.stocks
        self.symbols = self.symbols()
        
    # Generate the list of symbols
    def symbols(self):
        symbols = open("symbol_list.txt").read().split(',')
        return [sym.replace("'", '').strip().replace('[', '').replace(']', '') for sym in symbols]
    
    # Certain symbol strings must be url-encoded. Ex: ALR$B --> ALR$24B     
    # This could be improved for future use with other potential url-incompatible strings
    # What about periods? 
    def urlEncode(self, string):
        try: 
            return string.replace('$', '$24')
        except:
            return string
    
    # Function essentially following the recipe at http://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
    # For initialization, assumes you won't encounter 31st vs. 30th vs. leap year problems
    def generateURL(self, startMonth, startYear, startDay): 
        # Add the number of the month minus 1, add the number of the day, add the year.
        fromDate = "&a="+str(startMonth-1)+"&b="+str(startDay)+"&c="+str(startYear)
        interval = "&g=d" # Daily intervals
        return  (fromDate+interval+"&ignore=.csv")
    
    # Get the next possible trading day after a certain date, taking into account weekends 
    def next_trading_day(self, date):
        week = date.weekday()
        if 4 <= week <= 6:
            return date+datetime.timedelta(days=(7-week))
        else:
            return date+datetime.timedelta(days=1)

    # Return the timestamp variable (last time these stocks were updated) for a company
    # Should return the next day to avoid adding repeat information 
    # If last updated day is a weekend, should return the following Monday 
    def lastUpdated(self, company):
        last = self.collection.find_one({"company": company})[u'lastUpdate']
        parts = last.split('-')
        last = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
        return self.next_trading_day(last)

    # Check to see if a company exists in database
    def exists(self, company): return self.collection.find_one({"company":company})
    
    # Update a company's document object with new data
    def upate(self, mongobj, new_data):
        old_data = mongobj[u'data']
        old_data.reverse()      # Most recent stock is last 
        new_data.reverse()
        allData = old_data+new_data
        mongobj['data'] = allData
        self.collection.save(mongobj)
    
    # Update a single company
    # Metadata: Date,Open,High,Low,Close,Volume,Adj Close
    def updateSingle(self, company, lastUpdate, mongobj):
        hist_url = self.generateURL(lastUpdate.month, lastUpdate.year, lastUpdate.day)
        url = "http://ichart.yahoo.com/table.csv?s="+self.urlEncode(company)+hist_url
        data = (urllib2.urlopen(url).read()).split('\n')
        # Remove first line, which just has metadata
        data = data[1:]
        if len(data) == 0:
            print "No new information to update for", company
            return
        new_data = []
        for day in data:
                try:
                    day = day.split(',')
                    # Create a new document for each symbol and add it to the symbol document
                    day_data = {"date": day[0], "open": float(day[1]), "high": float(day[2]), "low": float(day[3]), "close": float(day[4]), "volume": float(day[5]), "adj_close":float(day[6])} 
                    new_data.append(day_data)
                except:
                    continue
        # Now update the company's document with this new data  
        self.update(mongobj, new_data)
    
    def create(self, comp): return {"company": comp, "lastUpdate": str(datetime.date.today()), "data": []}
    
    def insert(self, doc): return self.collection.insert(doc)
        
    def lookup(self, ID): return self.collection.find_one({"_id":ID})
    
    # Handle new companies
    def new(self, comp): 
        doc = self.create(comp)
        ID = self.insert(doc)
        return self.lookup(ID)
    
    # Get data from the current day using http://code.google.com/p/yahoo-finance-managed/wiki/csvQuotesDownload
    # Returns open, high, low, close 
    def today(self, comp, mongobj):
        url = 'http://download.finance.yahoo.com/d/quotes.csv?s='+comp+'&f=o0h0g0l1&e=.csv'
        data = urllib2.urlopen(url).read().strip().split(',')
        day_data = {"date": str(datetime.date.today()), "open": float(data[0]), "high": float(data[1]), "low": float(data[2]), "close": float(data[3])}
        self.update(mongobj, [day_data])
        
    # Determine if only need to go back one day when updating (or to last friday)
    def missingLatest(self, lastUpdate): return (self.next_trading_day(lastUpdate) == datetime.date.today())
        
    # Basic update method. If there is a new company insert new document into the database with today's data 
    def update(self, sym):
        mongobj = self.exists(sym)
        if mongobj:
            last = self.lastUpdated(sym)
            if self.missingLatest(last):
                self.today(sym, mongobj)
            else:
                self.updateSingle(sym, last, mongobj)
        else:
            mongobj = self.new(sym)
            self.today(sym, mongobj)
    
    # Update all the companies.
    def updateAll(self):
        counter = 0
        errors = 0
        for sym in self.symbols:
            try:
                self.update(sym)
                counter += 1
            except:
                errors += 1
            progress = (float(counter)/float(len(self.symbols)))*100
            sys.stdout.write("\rProgress:\t"+str(progress)+"%") 
            sys.stdout.flush()
        print ""
        if errors > 50:
            print "There were", errors, "errors while updating. You may want to try updating again."
        else:
            print "There were", errors, "errors while updating."
        print counter, "companies were updated."
        
                
                