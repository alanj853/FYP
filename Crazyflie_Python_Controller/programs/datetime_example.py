import time
from datetime import datetime, date

def method1(time_in_seconds):
    current_time = time.time();
    print "Will hover for ", time_in_seconds, " secs" ;
    target_time = current_time + time_in_seconds;
    print "starting to hover..."
    while current_time <= target_time:
        current_time = time.time();

    print "done";
    ts = time.time()
    dt = datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
    x = dt
    print x
    
method1(1);
