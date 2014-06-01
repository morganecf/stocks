'''
Created on Dec 30, 2012

@author: morganeciot

interface class 

can choose querying parameters (filters)
ex:
    date or date range
    company, companies
    price range

create way to enter data by hand (ex: AGII)
create symbol->company name 

open, high, low, close

TODO: put some of update methods (like creating a connection, finding something, etc) in utils program
'''

import Update, Symbols
import pymongo

'''
example pattern:
find all stocks where for 3 days or more in a row the close < open (red) -- within past 10 days. 
after x amount of red days, |close - low| is at least 2x greater than difference between open and close of that same day
'''

def connect(): return pymongo.MongoClient().gaetan.stocks

def closeLowDiff(doc): return abs(doc[u'close']-doc[u'low'])

def openCloseDiff(doc): return abs(doc[u'open'] - doc[u'close'])

# Red day: if the close is less than open
def red(doc): return doc[u'close'] < doc[u'open']

# See if there are min days in a row or more that satisfy a function 
# Return this last day (maximizing number of days in a row that satisfy function)
def consecutive(list, function, min):
    pointer = 0
    max = 0
    max_index = 0
    for index, item in enumerate(list):
        if function(item):
            pointer += 1
            if max < pointer: 
                max = pointer
                max_index = index
        else:
            pointer = 0
    if max > min:
        return index
    else:
        return None

def algorithm_helper(company, limit=10, min=3):
    collection = connect()
    obj = collection.find_one({"company":company})
    L = obj[u'data']
    end = len(L)
    lastDay = consecutive(L[end-(limit+1):end], red, min)
    if lastDay:
        return closeLowDiff(L[lastDay]) >= 2*openCloseDiff(L[lastDay])
    return False

def algorithm(symbols):
    found = []
    for sym in symbols:
        if algorithm_helper(sym):
            found.append(sym)
    return found


if __name__ == '__main__':
    print "Hello."
    print "Updating symbols..."
    # Update symbol list
    Symbols.main()
    # Update database
    up = Update.Update()
    print "Updating database..."
    up.updateAll()
     
    found = algorithm(up.symbols)
    print "Symbols that satisfy algorithm:"
    for f in found:
        print f
    