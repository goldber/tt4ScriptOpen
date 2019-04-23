'''
This script is used for Prarde TT41701 getting Cm and Cp raw data.
Usage
--tt4R --test.txt
test.txt : raw data file name
'''
import sys
import numpy as np
import RPi.GPIO as GPIO
import time
import lib.tt4Lib as tt4
from smbus2 import SMBusWrapper, i2c_msg

bInt = 37
TT4Addr = 0x24


def tt4ResumeScan():
    resumeCommand = [0x04, 0x00, 0x05, 0x00, 0x2F, 0x00, 0x04]
    success = 0x2F
    tt4.delayMs(1)
    while success != 0x1F:
        tt4.i2cw(TT4Addr, resumeCommand)
        try:
            GPIO.wait_for_edge(bInt, GPIO.FALLING, timeout=300)
            result = tt4.i2cr(TT4Addr, 5)
            success = result[2]
            print 'resume scan response {0}'.format(result)
        except KeyboardInterrupt:
            GPIO.cleanup()


def tt4SusScan():
    susCommand = [0x04, 0x00, 0x05, 0x00, 0x2F, 0x00, 0x03]
    success = 0x2F
    # tt4.i2cw(TT4Addr,susCommand)
    tt4.delayMs(1)
    while success != 0x1F:
        tt4.i2cw(TT4Addr, susCommand)
        try:
            # tt4.i2cw(TT4Addr,susCommand)
            GPIO.wait_for_edge(bInt, GPIO.FALLING, timeout=300)
            result = tt4.i2cr(TT4Addr, 5)
            success = result[2]
            print 'suspend scan response {0}'.format(result)
        except KeyboardInterrupt:
            GPIO.cleanup()


def tt4PanelScan():
    panelScan = [0x04, 0x00, 0x05, 0x00, 0x2F, 0x00, 0x2A]
    print 'start to do panel scan'
    statusResult = 0xFF
    while statusResult != 0x00:
        tt4.i2cw(TT4Addr, panelScan)
        try:
            GPIO.wait_for_edge(bInt, GPIO.FALLING, timeout=300)
            result = tt4.i2cr(TT4Addr, 6)
            statusResult = result[5]
            print result
        except KeyboardInterrupt:
            GPIO.cleanup()


def tt4GetSysInf():
    sysInfCmd = [0x04, 0x00, 0x05, 0x00, 0x2F, 0x00, 0x02]
    dataleng = 0x0000
    while dataleng != 0x3300:
        tt4.i2cw(TT4Addr, sysInfCmd)
        try:
            # tt4.i2cw(TT4Addr,sysInfCmd)
            # tt4.delayMs(1.5)
            # if GPIO.input(bInt)==0:
            GPIO.wait_for_edge(bInt, GPIO.FALLING, timeout=300)
            data = tt4.i2cr(TT4Addr, 3)
            dataleng = (data[0] << 8) + data[1]
            if dataleng == 0x3300:
                data = tt4.i2cr(TT4Addr, data[0])
                fwVer = (data[9] << 8) + data[10]
                fwRev = (data[11] << 16) + (data[12] << 8) + data[13]
                cfgVer = (data[14] << 8) + data[15]
                xNum = data[33]
                yNum = data[34]
                print 'fwVer :0x%04x' % fwVer
                print 'fwRev :0x%06x' % fwRev
                print 'cfgVer:0x%04x' % cfgVer
                print 'rxNum:0x%02x' % xNum
                print 'txNum:0x%02x' % yNum
                trNum = [xNum, yNum]
                return trNum
        except KeyboardInterrupt:
            GPIO.cleanup()


def tt4GetMutual(txNum, rxNum):
    mrGetRepCmd = [0x04, 0x00, 0x0A, 0x00, 0x2F, 0x00, 0x2B, 0x00, 0x00, 0x7B, 0x00, 0x00]
    mdGetRepCmd = [0x04, 0x00, 0x0A, 0x00, 0x2F, 0x00, 0x2B, 0x00, 0x00, 0x7B, 0x00, 0x02]
    totalByte = (txNum * rxNum)
    mrGetData = np.zeros((1, totalByte))
    mdGetData = np.zeros((1, totalByte))

    try:
        print 'start to do get mutual raw'
        tt4PanelScan()
        tt4.delayMs(10)
        countByte = 0
        index = 0
        while countByte < totalByte:  # read mutual raw data;
            tt4.i2cw(TT4Addr, mrGetRepCmd)
            tt4.delayMs(1.5)
            if GPIO.input(bInt) == 0:
                result = tt4.i2cr(TT4Addr, 2)
                print result
                packetLength = (result[1] << 8) + result[0]
                result = tt4.i2cr(TT4Addr, packetLength)
                thisSensByte = (result[8] << 8) + result[7]
                countByte = countByte + thisSensByte
                print 'countByte byte:{0}'.format(countByte)
                print 'This sense total byte:{0}'.format(packetLength)
                mrGetRepCmd[7] = countByte & 0x00FF  # offset value
                mrGetRepCmd[8] = (countByte >> 8) & 0xFF  # offset value
                count = 0
                while count < (thisSensByte * 2):
                    mrGetData[0][index] = int((result[count + 11] << 8) + result[count + 10])  # fF/10
                    count = count + 2
                    index = index + 1

        print 'start to do get mutual diff'
        tt4PanelScan()
        tt4.delayMs(10)
        countByte = 0
        index = 0
        while countByte < totalByte:  # read mutual diff;
            tt4.i2cw(TT4Addr, mdGetRepCmd)
            tt4.delayMs(1.5)
            if GPIO.input(bInt) == 0:
                result = tt4.i2cr(TT4Addr, 2)
                print result
                packetLength = (result[1] << 8) + result[0]
                result = tt4.i2cr(TT4Addr, packetLength)
                thisSensByte = (result[8] << 8) + result[7]
                countByte = countByte + thisSensByte
                print 'countByte byte:{0}'.format(countByte)
                print 'This sense total byte:{0}'.format(packetLength)
                mdGetRepCmd[7] = countByte & 0x00FF  # offset value
                mdGetRepCmd[8] = (countByte >> 8) & 0xFF  # offset value
                count = 0
                while count < (thisSensByte * 2):
                    mdGetData[0][index] = int((result[count + 11] << 8) + result[count + 10])  # fF/10
                    if mdGetData[0][index] > 60000:
                        mdGetData[0][index] = mdGetData[0][index] - 65536
                    count = count + 2
                    index = index + 1

    except KeyboardInterrupt:
        GPIO.clearnup()

    return mrGetData, mdGetData

def tt4D():
    fprint = 0
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print 'no tx or rx number arguments or wrong arguments'
        GPIO.cleanup()
        sys.exit()

    elif len(sys.argv) == 3:
        print 'with save to file arguments'
        # txNum=int(sys.argv[2][2:])
        # rxNum=int(sys.argv[3][2:])
        filename = sys.argv[2][2:]
        print 'fileName:{0}'.format(filename)
        fo = open(filename, "w")
        fprint = 1

    tt4.TT4Init()
    tt4.delayMs(10)
    tt4ResumeScan()
    tt4.delayMs(10)
    tt4SusScan()
    tt4.delayMs(10)
    [txNum, rxNum] = tt4GetSysInf()
    totalByte = txNum * rxNum
    mrData = np.zeros((1, totalByte))
    mdData = np.zeros((1, totalByte))

    while True:
        print 'Initial get:%s' % time.time()

        try:
            if fprint == 1:
                fo.write('\n')
                fo.write('mutual raw page start \n')

            mrData, mdData = tt4GetMutual(txNum, rxNum)
            index = 0
            while index < (totalByte):
                print '{0},'.format(mrData[0][index]),
                if fprint == 1:
                    fo.write('{0},'.format(mrData[0][index]))
                index = index + 1
                if index % txNum == 0:
                    print ''
                    if fprint == 1:
                        fo.write('\n')
            print ''

            if fprint == 1:
                fo.write('\n')
                fo.write('mutual diff page start \n')
            index = 0
            while index < (totalByte):
                print '{0},'.format(mdData[0][index]),
                if fprint == 1:
                    fo.write('{0},'.format(mdData[0][index]))
                index = index + 1
                if index % txNum == 0:
                    print ''
                    if fprint == 1:
                        fo.write('\n')
            print ''

        except KeyboardInterrupt:
            print 'exit :%s' % time.time()
            GPIO.cleanup()
            if fprint == 1:
                fo.close()
            break
