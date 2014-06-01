'''
Created on Dec 30, 2012

@author: morganeciot

Script to initialize the mongo database with historical data (6 months is hardcoded)
Usage: python Init.py

# TODO: make date an integer?  
# TODO: put code/files in separate directories (src/data)

'''

import sys, datetime, urllib2
import pymongo
import Update

# Function to go back x months in time
# 12 + month - x to avoid month 0
def back(today, interval):
    if today.month < interval:
        return (12 + today.month - interval), (today.year - 1)
    else:
        return (today.month - interval), today.year


# This program assumes that a MongoDB instance is running on the default host and port.
# To do this, open a terminal and type in mongod.
if __name__ == '__main__':
    
    up = Update.Update()
    
    # Get the current date and go back 6 months (default initialization value)
    today = datetime.date.today()
    startMonth, startYear = back(today, 6)
    startDate = datetime.date(startYear, startMonth, today.day)
    
    print "Beginning initialization:", len(up.symbols), "historical files to insert."
    errors = 0
    notFound = []
    counter = 0
    for symbol in up.symbols:
        try:
            # Create a new document for each symbol and insert into database
            obj = up.new(symbol)
            
            # Update information for this company for the past 6 months
            up.updateSingle(symbol, startDate, obj)
            
            # Update progress in console
            progress = (float(counter)/float(len(up.symbols)))*100
            sys.stdout.flush()
            sys.stdout.write("\rProgress:\t"+str(progress)+"%") 
            sys.stdout.flush()
            counter += 1
        except urllib2.HTTPError:
            notFound.append(symbol)
            continue
        except:
            errors += 1
            continue
        
    print "\nThere were", len(notFound), "HTTP Error 404 URL Not Found errors for the following symbols:"
    for nf in notFound:
        print nf
    print "There were", errors, "other unexpected errors."
    print "The historical data for", (len(up.symbols)-(len(notFound)+errors)), "symbols were successfully inserted into the database."
        
        