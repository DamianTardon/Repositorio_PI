#Python3 test program for GDS-1000U/AU
#
import time
from struct import unpack
import sys
import pyvisa

def getBlockData(): #Used to get block data.
    global inBuffer
    global headerlen
    inBuffer=dso.read_bytes(10)
    length=len(inBuffer)
    headerlen = 2 + int(chr(inBuffer[1]))
    pkg_length = int(inBuffer[2:headerlen]) + headerlen #Block #48008[..8bytes..][..8000bytes raw data...]
    print("Data transferring...  ")
    print('pkg_length=%d'%pkg_length)
        
    pkg_length=pkg_length-length
    while True:
        print('%8d\r' %pkg_length, end='')
        if(pkg_length==0):
            break
        else:
            if(pkg_length > 100000):
                length=100000
            else:
                length=pkg_length
            try:
                buf=dso.read_bytes(length)
            except:
                print('KeyboardInterrupt!')
                dso.closeIO()
                sys.exit(0)
            num=len(buf)
            inBuffer+=buf
            pkg_length=pkg_length-num

if __name__ == '__main__':
    global inBuffer
    global headerlen
    rm = pyvisa.ResourceManager()
    dso = rm.open_resource('COM25')  # Please check your port number!
    dso.timeout = 5000
    dso.read_termination = '\n'
    dso.write_termination = '\n'
    idn = dso.query('*IDN?')
    print(idn)

    ch = 1
    div = dso.query(':CHAN%d:SCAL?'%ch)    #Get vertical scale.
    vdiv = float(div)
    print('Vertical scale: %.2f'%(vdiv))

    while True:
        while True:  # Waiting for waveform ready.
            dso.write(':ACQ1:STAT?')
            state = dso.read()
            if(state[0] == '1'):
                break
            time.sleep(0.1)
        print('Waveform ready!')

        dso.write(":ACQ%d:MEM?" % ch) # Get CH1 waveform raw data
        getBlockData()
        time.sleep(1)
        print(inBuffer[:headerlen])
        dt=unpack('>f', inBuffer[headerlen : headerlen+4]) # Sampling period.
        print("Sampling period:%.2e (sec)" % dt)  #Print sampling period.
        waveform = unpack('>%sh' % (int(len(inBuffer[headerlen+8:])/2)), inBuffer[headerlen+8:])
        num = len(waveform)
        print('Number of samples = %d'%num)
        data = [0]*num
        for i in range(num):
            data[i] = waveform[i]*vdiv/25
        print(data[0: 10])
#        print(data[1980: 2000])
