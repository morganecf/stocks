'''
Created on Dec 28, 2012

@author: morganeciot

Usage: run python Update.py to update list of stock ticker symbols from NASDAQ ftp site
`      run python Update.py -h to view command-line options
This will overwrite files in your cwd. Files are called nasdaq_symbols.txt and other_symbols.txt
'''


'''
TODO: fix specified-file difference bug 
'''

import urllib2
from optparse import OptionParser
from sets import Set

def main():
    parser = OptionParser()
    parser.add_option("-d", help="View new symbols added, if any")
    parser.add_option("--diff", dest="filename", help="View new symbols added for a particular file (should be either nasdaq_symbols or other_symbols")
    
    (options, args) = parser.parse_args()
    
    if len(args) == 0:
        # If a filename is specified, find stats for just that file
        if options.filename:
            if options.filename == "nasdaq_symbols.txt":
                differences("nasdaq_symbols.txt")
            elif options.filename == "other_symbols.txt":
                differences("other_symbols.txt")
            else:
                print "Wrong filename."
                parser.print_help()
        # If a filename isn't specified, find stat differences for both files
        else:
            differences("nasdaq_symbols.txt", filename2="other_symbols.txt")
    
    # If there are no arguments, simply perform the update
    else:
        update()

# Used for extracting only the symbols
# This can also be used as a general utility function by calling Symbols.parse(file), where filename is a list 
# May be necessary to first remove first and last line: list[1:len(list)-2]
def parse(filename): return [line.split('|')[0] for line in filename] 

# Finds the different symbols added before and after the update, if any
def differences(filename, filename2=None):
    # Logical path for -d command (no filename specified, so assess both files)
    if filename2:
        b1 = open(filename).read().splitlines()
        b2 = open(filename2).read().splitlines()
        before = b1[1:len(b1)-2]+b2[1:len(b2)-2]
        update()
        a1 = open(filename).read().splitlines()
        a2 = open(filename).read().splitlines()
        after = a1[1:len(a1)-2]+a2[1:len(a2)-2]
    # Otherwise, find stats for only the filename specified
    else:
        before = open(filename).read().splitlines()
        # Start at index=1 to omit first line of file, which contains metadata
        # Also omit the last line (file creation time)
        before = before[1:len(before)-2]
        update()
        after = open(filename).read().splitlines()
        after = after[1:len(after)-2]
    before = parse(before)
    after = parse(after)
    
    # Get elements belonging to after but not before (i.e., new symbols added)
    added = list(Set(after).difference(Set(before)))
    
    # Gets elements belonging to before but not after (i.e., symbols that have been discarded)
    discarded = list(Set(before).difference(Set(after)))
    
    print ""
    print "There were", len(added), "symbols added to the NASDAQ stock list"
    print "There were", len(discarded), "symbols removed from the NASDAQ stock list"
    print ""
    print "==============ADDED=============="
#    for symbol in added:
 #       print symbol
    print ""
    print "==============REMOVED=============="
 #   for symbol in discarded:
 #       print symbol
    print ""
    
    print ""
    print "Number of symbols before:", len(before)
    print "Number of symbols after:", len(after)

def update():
    # Connect to the ftp site and write the data to files  
    # Only basic error handling done here
    try:
        nasdaq_listed = urllib2.urlopen("ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt").read()
        other_listed = urllib2.urlopen("ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt").read()
        f1 = open('nasdaq_symbols.txt', 'w')
        f2 = open('other_symbols.txt', 'w')
        f1.write(nasdaq_listed)
        f2.write(other_listed)
        f1.close()
        f2.close()
        NL = len(open('nasdaq_symbols.txt').read().splitlines())
        OL = len(open('other_symbols.txt').read().splitlines())
        print "Two symbol files successfully updated."
        print "Current number of nasdaq symbols:", NL
        print "Current number of other symbols:", OL
        print "Total number of symbols:", (NL + OL)
        print ""
        print "Now writing only symbols to a file called symbol_list.txt"
        getSymbols()
    except:
        print "Something went wrong."

def getSymbols():
    f1 = open('nasdaq_symbols.txt').read().splitlines()
    f2 = open('other_symbols.txt').read().splitlines()
    symbols = parse(f1[1:len(f1)-2]) + parse(f2[1:len(f2)-2])
    symbols = str(symbols)
    symbol_file = open('symbol_list.txt', 'w')
    symbol_file.write(symbols)
    symbol_file.close()
    
