from datetime import datetime, date
import time

ts = time.time()
dt = datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
x = str(dt + ": " + "Total Flight Time: " + str(int(4.7 - 2.6)) + " seconds")
# Open a file
fo = open("foo.txt", "a")
fo.write( x);

# Close opend file
fo.close()
