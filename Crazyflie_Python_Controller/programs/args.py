import sys

input = ""

try:
	input = sys.argv[1];
	print "This is input", input
except getopt.GetoptError:
    print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)