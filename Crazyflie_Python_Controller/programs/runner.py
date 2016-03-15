from PID import PID


x = PID()

x.setKp(44);
y = x.getKp();
print "This is y ", y