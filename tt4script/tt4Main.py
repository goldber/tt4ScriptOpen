#!/usr/bin/python
import sys
import numpy as np
import RPi.GPIO as GPIO
import time
import lib.tt4PrintRep as tt4P
import lib.tt4R as tt4R
import lib.tt4D as tt4D
import lib.tt4Lib as tt4
from smbus2 import SMBusWrapper, i2c_msg
"""
This Python code is for Parade TT41701 IC get report 
usage 
Case1 to print the coordinate data
python tt4Main.py --tt4P --filename.txt (print the result to file)
python tt4Main.py --tt4P (do not print to file)

Case 2

Case 3

Case 4 to get the Cm and Cp self test data
python tt4Main.py --tt4R --37 --27 --filename.txt
python tt4Main.py --tt4R --37 --27

"""

def main():
    if len(sys.argv) < 2: 
        print 'no argument'
        sys.exit()
    elif sys.argv[1].startswith('--'):
        n=sys.argv[1][2:]
        print n
        
    while tt4.switch(n):
        if tt4.case('tt4P'):
            print "Start to do the tt4P test."
            tt4P.tt4PrintRep()
            break
        if tt4.case('tt4A'):
            print "Start to do the tt4A test."
            break
        if tt4.case('tt4L'):
            print "Start to do the tt4L test."
            break
        if tt4.case('tt4R'):
            print "Start to do the tt4R test."
            tt4R.tt4R()
            break
        if tt4.case('tt4D'):
            print "Start to do the tt4D test."
            tt4D.tt4D()
            break
        print "No argument is not allowded."
        break        
       

if __name__== "__main__":
    main()  
