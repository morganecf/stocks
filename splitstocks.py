
f = open("advfn_stocks.txt").read().splitlines()
stocks = []
for line in f:
	stocks.append(line.split("\t")[1])

#print stocks

f2 = open("sample").read()
f2 = f2.replace("'", '"')
print f2
