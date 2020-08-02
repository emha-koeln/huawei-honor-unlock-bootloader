#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
emha-koeln, SkyEmie, bbb0
"""

import time
#from flashbootlib import test
import os
from os import path 

import math
import subprocess
from subprocess import PIPE, run

import platform
import configparser
import argparse
#import time

##########################################################################################################################
VERSION         = '0.1.1.20200802'
CONF_FILE       = 'subls.conf'
UNLOCKCODE_FILE = 'unlock_code.txt'
PLATFORM        = 'unknown'

##########################################################################################################################
## system and plattform

def cls():
   
    if PLATFORM == 'Windows':
        os.system('cls')
    elif PLATFORM == 'Linux':
        os.system('clear')

def runOS(cmd, iVerboselevel=1): #0silent 1stdout/err 2cmd and stdout7err 3 was verbose

    sCmd = cmd
    cmd = cmd.split(' ')

    try:
       result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
       #if args.verbose:
       if iVerboselevel == 1:
           #print(sCmd)
           print(result.stdout, result.stderr)       

       elif iVerboselevel == 2:
           print(sCmd)
           print(result.stdout, result.stderr)    

       elif iVerboselevel == 3:
           print('Shell Result for:', sCmd)
           print('Returncode:', str(result.returncode))
           print(result.stdout, result.stderr)
           
       return(result)

    except subprocess.CalledProcessError as e:
       raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
##########################################################################################################################
## adb and fastboot

def testADBDevice(sSN="0"):
  
    found = ''
    iDev = 0
    
    while(found == ''):
       #print('adb devices: Waiting for devices...')
       result = runOS("adb devices", 2)
       found = result.stdout
       time.sleep(1)
       
    #print(result.stdout)
    sDevList = found.split('\n')
    
    devs = ['0000000000000000']
    iDevs = []
    #print(sDevList)
    
    for i in sDevList:
        if not i == 'device': 
            if not i == 'List of devices attached':
                if 'device' in i:
                    devs.append(i[:16])
                    #print('INFO: Found device', i[:16] )
    #print(len(devs)) 
    #print(devs) 
    print('INFO: maybe your device isn\'t found by adb because it\'s already in bootloader-mode')
    print('      in this case select \'0\' or simply press Enter')
    print ('Select device: ')
    for i in range(0, len(devs)):
        iDevs.append(i)
        result = runOS('adb -s '+devs[i]+' shell getprop ro.product.manufacturer', 0)
        print(i, devs[i], result.stdout[:-1] )   
 
    iDev = input(iDevs)# or '0') doesn't work here...?
    #print('hmmmmmmmmm', iDev)
    if iDev == '':
        iDev = 0
    
    return(devs[int(iDev)])

def testFastbootDevice(sSN="0"):
  
    found = ''
 
    #if sSN == 'unknown':
    #    sSN='0'
    iCount = 0
    
    while(found == ''):
       cls()
       print('INFO: Waiting for devices...', 20-iCount)
       result = runOS("fastboot devices", 3)
       found = result.stdout
       time.sleep(1)
       
       if iCount == 20:
           print('INFO: Counldn\'t detect any device with > fastboot devices')
           input('Press Enter to exit...\n')
           exit(-1)
       iCount += 1    
       
       #print(result.stdout)
    sDevList = found.split('\n')
    
    devs = []
    iDevs = []
    
    for i in sDevList:
        if not i == 'fastboot':
            if 'fastboot' in i:
                print('fastboot: Found device', i[:16] ) 
                devs.append(i[:16])
                
                if str(sSN) == str(i[:16]):
                    print('INFO: Found your device', i[:16])
                    return(sSN)
            
    print('INFO: Couldn\'t find your device', sSN)
    #print(len(devs)) 
    #print(devs) 
    print('Select device: ')
    for i in range(0, len(devs)):
        iDevs.append(i)
        print(i, devs[i])   
    iDev = input(iDevs or '0')
    if iDev == '':
        iDev = 0     
    #if args.verbose:
    #    cls()
    #    runOS('fastboot oem get-product-model')
    #    input('Press Enter ...')
  
    return(devs[int(iDev)])

##########################################################################################################################
## init luhn

def initLuhn():
    # IMEI
    if args.imei:
        print('INFO: using', args.imei, 'as IMEI')
        imei     = args.imei
        checksum = luhn_checksum(imei)
        print('INFO: Luhn checksum is: '+str(checksum))
        input('wait')
    
    elif not config['DEFAULT']['imei']:
        print('Enter IMEI:')
        imei     = int(input('Type IMEI digit :'))
        checksum = luhn_checksum(imei)
        print('INFO: Luhn checksum is: '+str(checksum))
        config['DEFAULT']['imei'] = str(imei)
        config['DEFAULT']['checksum'] = str(checksum)
        with open(CONF_FILE, 'w') as f:
           config.write(f)
    else:
        print('INFO: found IMEI in', CONF_FILE+":", config['DEFAULT']['imei'])
        print('        checksum in', CONF_FILE+":", config['DEFAULT']['checksum'])
        
        
        if args.base:
            print('                   new base -b:', args.base)
        else:
            print('      last code was', CONF_FILE+":", config['DEFAULT']['algoOEMcode'])
        
        if not int(config['DEFAULT']['checksum']) == int(luhn_checksum(config['DEFAULT']['imei'])):
            print('INFO: Luhn checksum\('+str(luhn_checksum(config['DEFAULT']['imei']))+
                  '\) is not equal to saved one\('+str(config['DEFAULT']['checksum']+'\)'))
                                                       
            print('INFO: This is ok, if your are continuing from a previous run')
            
        yn = input('(Y/n) Press Enter to continue with last run or \'n\' to enter new IMEI: ')
        if not yn.lower() == 'n':
            print('INFO: continuing with last IMEI, checksum')
            imei = int(config['DEFAULT']['imei'])
            checksum = int(config['DEFAULT']['checksum']) 
            print('INFO: IMEI', imei)
            print('INFO: checksum', checksum)
        else:
            print('Enter new IMEI:')
            imei     = int(input('Type IMEI digit :'))
            checksum = luhn_checksum(imei)
            print('INFO: Luhn checksum is: '+str(checksum))
            config['DEFAULT']['imei'] = str(imei)
            config['DEFAULT']['checksum'] = str(checksum)
            with open(CONF_FILE, 'w') as f:
                config.write(f)
    return checksum
    
    
    
##########################################################################################################################
## init numeric

def initNumeric():   
    
    lastNum = 0
    if not config['DEFAULT']['lastNumeric']:
       lastNum     = input('Enter new number to start from: (Default=0)')
       if lastNum == '':
           lastNum = 0
       config['DEFAULT']['lastNumeric'] = str(lastNum)
       with open(CONF_FILE, 'w') as f:
           config.write(f)
    else:       
        print('INFO: found a saved number from last run in', CONF_FILE+":", config['DEFAULT']['lastNumeric'])
        default = str(config['DEFAULT']['lastNumeric'])
        #print(default)
        lastNum = str(input('Press Enter to continue with last run or enter a new start number: ') or 'n')
        #                    or default))
        
        if lastNum.lower() == 'n':
           print('INFO: continuing with last run')
           lastNum = int(config['DEFAULT']['lastNumeric'])
           print('INFO: lastNumeric', lastNum)
    
        else:
           print('INFO: continuing with', lastNum)
           config['DEFAULT']['lastNumeric'] = str(lastNum)
           with open(CONF_FILE, 'w') as f:
              config.write(f)
        
        #if not yn.lower() == 'n':
        #   print('INFO: continuing with last run')
        #   lastNum = int(config['DEFAULT']['lastNumeric'])
        #   print('INFO: lastNumeric', lastNum)
    
        #else:
        #   lastNum     = int(input('Enter new number to start from:'))
        #   config['DEFAULT']['lastNumeric'] = str(lastNum)
        #   with open(CONF_FILE, 'w') as f:
         #      config.write(f)
           
    return(int(lastNum)) 
    
    
##########################################################################################################################
## tryUnlockBootloader numeric

def tryUnlockNumeric(algoOEMcode):   
    
    #algoOEMcode = int(algoOEMcode)
    unlock      = False
    save        = 0 
    cls()

    while(unlock == False):
       
        cmd = 'fastboot oem unlock '+ str(algoOEMcode).rjust(16,'0')
        
        if args.verbose:
            print("Bruteforceing... " + cmd)
            print("        methode: Numeric")
            print("    algoOEMcode: " + str(algoOEMcode))
            print("             ... (next save in "+str(200-save)+")")
        else:
            print("Bruteforceing... " + cmd)
            
        result = runOS(cmd, 0)

        # ToDo: 
        # if result.returncode == 0:
        sprout = result.stdout + ' ' + result.stderr
        sdrout = sprout.replace('\n', ' ').split(' ')

        if not result.returncode == 1:
            print('INFO: ', sdrout)
            input('Press Enter...\n')
            for i in sdrout:
                if i.lower() == 'success':
                    print('INFO: ', i)
                    bak = open(UNLOCKCODE_FILE, "w")
                    bak.write("Your saved bootloader code : "+str(algoOEMcode)+"\nDEBUG sprout was: "+str(sprout))
                    bak.close()
                    input('Press Enter...\n')
                    return(algoOEMcode)
                elif i.lower() == 'reboot':
                    print('INFO: ', i)
                    print('\n\nSorry, your bootloader has additional protection that other models don\'t have\nI can\'t do anything.. :c\n\n')
                    input('Press Enter to exit..\n')
                    exit()
        else:
            if args.verbose:
                for i in sdrout:
                    if i.lower() == 'waiting':
                        print('INFO: ', i, 'for device...')
            
        save  +=1

        if save == 200:
            save = 0
            
            config['DEFAULT']['lastNumeric'] = str(algoOEMcode)
            with open(CONF_FILE, 'w') as f:
                config.write(f)
            # bak = open("unlock_code.txt", "w")
            # bak.write("If you need to pick up where you left off,\nchange the algoOEMcode variable with #base comment to the following value :\n"+str(algoOEMcode))
            # bak.close()

        algoOEMcode += 1

    
##########################################################################################################################
## tryUnlockBootloader luhn

def tryUnlockBootloader(checksum):

    #algoOEMcode = 1000000000000000 #base
    unlock      = False
    save        = 0 
         
    if args.base:
        algoOEMcode     = int(args.base)
    elif config['DEFAULT']['algoOEMcode']:
        algoOEMcode     = int(config['DEFAULT']['algoOEMcode'])
    else: 
        algoOEMcode     = int(config['DEFAULT']['base'])
    #clear       = 0
    #os.system('clear')
    cls()

    while(unlock == False):
       
        cmd = 'fastboot oem unlock '+ str(algoOEMcode).rjust(16,'0')
        
        if args.verbose:
            print("Bruteforceing... " + cmd)
            print("        methode: Luhn-Checksum")
            print("    algoOEMcode: " + str(algoOEMcode))
            print("       checksum: " + str(checksum))
            print("             ... (next save in "+str(200-save)+")")
        else:
            print("Bruteforceing... " + cmd + "(checksum=" + str(checksum) +")")
            
        result = runOS(cmd, 0)

        # ToDo: 
        # if result.returncode == 0:
        sprout = result.stdout + ' ' + result.stderr
        sdrout = sprout.replace('\n', ' ').split(' ')

        if not result.returncode == 1:
            print('INFO: ', sdrout)
            input('Press Enter...\n')
            for i in sdrout:
                if i.lower() == 'success':
                    print('INFO: ', i)
                    bak = open(UNLOCKCODE_FILE, "w")
                    bak.write("Your saved bootloader code : "+str(algoOEMcode)+"\nDEBUG sprout was: "+str(sprout))
                    bak.close()
                    input('Press Enter...\n')
                    return(algoOEMcode)
                elif i.lower() == 'reboot':
                    print('INFO: ', i)
                    print('\n\nSorry, your bootloader has additional protection that other models don\'t have\nI can\'t do anything.. :c\n\n')
                    input('Press Enter to exit..\n')
                    exit()
        else:
            if args.verbose:
                for i in sdrout:
                    if i.lower() == 'waiting':
                        print('INFO: ', i, 'for device...')
            
        save  +=1

        if save == 200:
            save = 0
            
            if not args.imei and not args.base:
            
                config['DEFAULT']['algoOEMcode'] = str(algoOEMcode)
                with open(CONF_FILE, 'w') as f:
                    config.write(f)
                # bak = open("unlock_code.txt", "w")
                # bak.write("If you need to pick up where you left off,\nchange the algoOEMcode variable with #base comment to the following value :\n"+str(algoOEMcode))
                # bak.close()

        algoOEMcode = algoIncrementChecksum(algoOEMcode, checksum)

        if algoOEMcode > 9999999999999999:
            #input('> 9999999999999999 Press Enter...')
            if args.base:
                algoOEMcode = args.base
            else:
                algoOEMcode = int(config['DEFAULT']['base'])
            checksum += 1
            if str(checksum)[-1:] == str(luhn_checksum(imei)):
                print('INFO: Giving up.')
                input('Press Enter to exit')
                exit(-1)
            checksum = int(str(checksum)[-1:])    
            config['DEFAULT']['checksum'] = str(checksum)[-1:]
            with open(CONF_FILE, 'w') as f:
                config.write(f)
               
               
##########################################################################################################################
## algo and luhn checksum               
               
def algoIncrementChecksum(genOEMcode, checksum):
    if args.imei:
        genOEMcode+=int(checksum+math.sqrt(int(args.imei))*1024)
    else:    
        genOEMcode+=int(checksum+math.sqrt(int(config['DEFAULT']['imei']))*1024)
    return(genOEMcode)


def luhn_checksum(imei):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(imei)
    oddDigits = digits[-1::-2]
    evenDigits = digits[-2::-2]
    checksum = 0
    checksum += sum(oddDigits)
    for i in evenDigits:
        checksum += sum(digits_of(i*2))
    return checksum % 10


##########################################################################################################################
## start here

PLATFORM = platform.system()

#def main():
########
# args
# Todo
parser = argparse.ArgumentParser(
#        prog='skubls.py',
        description=('''\
         Note that command-line arguments are not stored!
         ''')
        )
parser.add_argument('-s', '--sn', help='use this as serialnumber')
parser.add_argument('-m', '--method', choices=['luhn', 'numeric'],
                    help='use this as brute-force method')
parser.add_argument('-i', '--imei', help='use this as IMEI')
parser.add_argument('-b', '--base', help='use this as base')
#parser.add_argument('-o', '--oem' , help='use this as last OEM Code (TODO)')
parser.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
parser.add_argument('--lock', help='lock your device (TODO)')
args = parser.parse_args()

########
# config
# Todo
config = configparser.ConfigParser()
config['DEFAULT'] = { 'SN': '',
                      'imei': '',
                      'methode': 'luhn',
                      'checksum': '0',
                      'base': '1000000000000000',
                      'algoOEMcode': '',
                      'lastNumeric': ''}

if not path.exists(CONF_FILE):
    with open(CONF_FILE, 'w') as f:
        config.write(f)

config.read(CONF_FILE)

########
# 'main'
cls()
#print(args)
#parser.print_help()
#print("Running '{}'".format(__file__))

print('Second Unlock Bootloader script '+VERSION)
print('usage: subls.py [-h] [-m {luhn,numeric}] [-i IMEI] [-b BASE] [-v] [--lock LOCK]\n')
print('#########################################################################################')
print('based on:  ')
print('                   Unlock Bootloader script - By SkyEmie_\'')
print('                   with ideas from bbb0, taskula from github')
print('\n  (Please enable USB DEBBUG and OEM UNLOCK if the device doesn\'t appear..)')
#print('\n                      (Try to enable MY_MIND = too)')
print('\n           /!\ All data will or may or could or should be erased /!\\\n')
print('#########################################################################################\n')

# TODO: let the user decide
#yn = input('Enter \'Yes\' to continue')
#if not yn == 'Yes':
#    print('')
#    exit(-1)
input('Press [Enter] if you know, what you are going to do')


#########
## go on

cls()
print('STEP 1: run > adb devices to detect and reboot your device into fastboot-mode')
input('Press [Enter] to run > adb devices')
#cls()

if args.sn:
    print('INFO: > adb devices wasn\'t executed')
    print('      Using -s', args.sn)
    SN = args.sn

elif not config['DEFAULT']['SN']:
    #cls()
    runOS('adb devices', 1)
    SN = testADBDevice()
    # if args.verbose:
    #input('Press Enter ...')
    if not SN == '0000000000000000':
        config['DEFAULT']['SN'] = str(SN)
        with open(CONF_FILE, 'w') as f:
            config.write(f)
    #print('INFO: Working on device', SN)
else:
    #cls()
    print('INFO: > adb devices wasn\'t executed')
    print('      found SN in', CONF_FILE+":", config['DEFAULT']['SN'])
    SN = config['DEFAULT']['SN']

input('Press [Enter] continue with device '+ SN)
cls()

#print(SN)
print('STEP 2: run > fastboot to detect and select your device')
    
if str(SN) == '0000000000000000':
    #print('WARNING: All adb-devices will reboot!')              
    input('Press Enter continue')
    #runOS('adb reboot bootloader', 1)
else:
    input('Press [Enter] to reboot or find your device '+SN+' into bootloader-mode...\n')
    runOS('adb -s '+SN+' reboot bootloader', 1)

SN = testFastbootDevice(SN)
    
config['DEFAULT']['SN'] = str(SN)
with open(CONF_FILE, 'w') as f:
    config.write(f)
#print('INFO: Working on device', SN)

input('Press [Enter] to continue... ')
cls()
if args.method:
    print('STEP 3: Choose brutforce methode:', args.method)
    if args.method == 'luhn':
        codeOEM = tryUnlockBootloader(initLuhn())
    elif args.method == 'numeric':  
        codeOEM = tryUnlockNumeric(initNumeric())
else:
    print('STEP 3: Choose brutforce methode:')
    print('0 Last run ('+config['DEFAULT']['methode']+')')
    print('1 Luhn Checksum')
    print('2 Numeric:')
    num = input('[0, 1, 2]' or '0')
    if num == '1':
        config['DEFAULT']['methode'] = str('luhn')
        with open(CONF_FILE, 'w') as f:
            config.write(f)
        codeOEM = tryUnlockBootloader(initLuhn())
        
    elif num == '2':
        config['DEFAULT']['methode'] = str('numeric')
        with open(CONF_FILE, 'w') as f:
            config.write(f)
        codeOEM = tryUnlockNumeric(initNumeric())
        
    else:
        if config['DEFAULT']['methode'] == 'luhn':
            codeOEM = tryUnlockBootloader(initLuhn())
        elif config['DEFAULT']['methode'] == 'numeric':
            codeOEM = tryUnlockNumeric(initNumeric())

print('Device unlocked! OEM CODE: '+codeOEM)
print('INFO: OEM CODE saved in', UNLOCKCODE_FILE)

input('Press Enter to read unlock state\n')
runOS('fastboot getvar unlocked')

input('Press Enter to reboot your device\n')
runOS('fastboot reboot')

input('Press Enter\n')
print('\n\nDevice unlock ! OEM CODE : '+codeOEM)
print('(Keep it safe)\n')

input('Press Enter to exit..\n')
exit()
    
#if __name__ == "__main__":
#        main()
        