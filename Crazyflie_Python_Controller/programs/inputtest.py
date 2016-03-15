import sys, tty, termios,time



def getInput():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
        finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch



current_time = time.time();
target_time = current_time + 10;
while current_time < target_time:
    current_time = time.time()
    char = getInput()
    print "Key pressed: %s" % char
    if char == "A" or char == "a":
	print "True"

print "Done"
