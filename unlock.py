#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SkyEmie_' 💜 https://github.com/SkyEmie
emha-koeln, bbb0
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
import time

##########################################################################################################################
CONF_FILE       = 'unlock.conf'
UNLOCKCODE_FILE = 'unlock_code.txt'
PLATFORM        = 'unknown'

##########################################################################################################################
def cls():
    # Todo:
    #print('INFO', PLATFORM)
    #if args.verbose:
    #    print('VERBOSE', PLATFORM)
    
    if PLATFORM == 'Windows':
        os.system('cls')
    elif PLATFORM == 'Linux':
        os.system('clear')

def testADBDevice(sSN="0"):
  
    found = ''
   
    
    while(found == ''):
       print('INFO: Waiting for device...')
       result = runOS("adb devices")
       found = result.stdout
       time.sleep(1)
       cls()
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
    print('      in this case select \'0\'')
    print ('Select device: ')
    for i in range(0, len(devs)):
        iDevs.append(i)
        result = runOS('adb -s '+devs[i]+' shell getprop ro.product.manufacturer', 3)
        print(i, devs[i], result.stdout[:-1] )   
    iDev = input(iDevs)
    
    return(devs[int(iDev)])

def testFastbootDevice(sSN="0"):
  
    found = ''
    sSearchSN = sSN
  
    #if sSN == 'unknown':
    #    sSN='0'
    iCount = 0
    
    while(found == ''):
       cls()
       print('INFO: Waiting for device...')
       result = runOS("fastboot devices")
       found = result.stdout
       time.sleep(1)
       iCount += 1
       if iCount == 20:
           print('INFO: Counldn\'t detect any device')
           input('Press Enter to exit...\n')
           exit(-1)
           
       
       #print(result.stdout)
    sDevList = found.split('\n')
    
    devs = []
    iDevs = []
    
    for i in sDevList:
        if not i == 'fastboot':
            if 'fastboot' in i:
                print('INFO: Found device', i[:16] ) 
                devs.append(i[:16])
                
                if str(sSN) == str(i[:16]):
                    return(sSN)
            
    print('INFO: Couldn\'t find your device')#, sSearchSN)
    #print(len(devs)) 
    #print(devs) 
    print ('Selecet device: ')
    for i in range(0, len(devs)):
        iDevs.append(i)
        print(i, devs[i])   
    iDev = input(iDevs)
    
    return(devs[int(iDev)])
    
def runOS(cmd, iOUT=0):

    sCmd = cmd
    cmd = cmd.split(' ')

    try:
       result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
       #DEBUG
       if args.verbose:
           if iOUT == 0:
               print('Shell Result for:', sCmd)
               print('Returncode:', str(result.returncode))
               print(result.stdout, result.stderr)
       elif iOUT == 1:
           print(sCmd)
           print(result.stdout, result.stderr)       
       #else:
           
       return(result)

    except subprocess.CalledProcessError as e:
       raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    

def tryUnlockBootloader(checksum):

    unlock      = False
    save        = 0
    
    #algoOEMcode = 1000000000000000 #base
   
    if config['DEFAULT']['algoOEMcode']:
        algoOEMcode     = int(config['DEFAULT']['algoOEMcode'])
    else: 
        algoOEMcode     = int(config['DEFAULT']['base'])
    #clear       = 0
    #os.system('clear')
    cls()

    while(unlock == False):
       
        cmd = 'fastboot oem unlock '+ str(algoOEMcode).rjust(16,'0')
        print("Bruteforceing... " + cmd)
        if args.verbose:
            print("    algoOEMcode: " + str(algoOEMcode))
            print("       checksum: " + str(checksum))
            print("             ... (next save in "+str(200-save)+")")
        
        result = runOS(cmd)

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
            
            config['DEFAULT']['algoOEMcode'] = str(algoOEMcode)
            with open(CONF_FILE, 'w') as f:
                config.write(f)
            # bak = open("unlock_code.txt", "w")
            # bak.write("If you need to pick up where you left off,\nchange the algoOEMcode variable with #base comment to the following value :\n"+str(algoOEMcode))
            # bak.close()

        algoOEMcode = algoIncrementChecksum(algoOEMcode, checksum)

        if algoOEMcode > 9999999999999999:
            #input('> 9999999999999999 Press Enter...')
            algoOEMcode =  int(config['DEFAULT']['base'])
            checksum += 1
            if checksum > 9:
                print('INFO: Giving up.')
                input('Press Enter to exit')
                exit(-1)
            config['DEFAULT']['checksum'] = str(checksum)
            with open(CONF_FILE, 'w') as f:
                config.write(f)
               
               
def algoIncrementChecksum(genOEMcode, checksum):
    genOEMcode+=int(checksum+math.sqrt(imei)*1024)
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

PLATFORM = platform.system()

########
# args
# Todo
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--imei', help='use this as IMEI (TODO)')
parser.add_argument('-b', '--base', help='use this as base (TODO)')
parser.add_argument('-o', '--oem' , help='use this as last OEM Code (TODO)')
parser.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
parser.add_argument('--lock', help='lock your device (TODO)')
args = parser.parse_args()

########
# config
config = configparser.ConfigParser()
config['DEFAULT'] = { 'SN': '',
                      'imei': '',
                      'checksum': '0',
                      'base': '1000000000000000',
                      'algoOEMcode': ''}
if not path.exists(CONF_FILE):
    with open(CONF_FILE, 'w') as f:
        config.write(f)

config.read(CONF_FILE)

########
# main
cls()
print('Second Unlock Bootloader\n')
print('based on:  Unlock Bootloader script - By SkyEmie_\'')
print('\n  (Please enable USB DEBBUG and OEM UNLOCK if the device doesn\'t appear..)\n')
print('  /!\ All data will be erased /!\\\n')

input('Press Enter to show detected devices...')

if not config['DEFAULT']['SN']:
    cls()
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
    cls()
    print('INFO: found SN in', CONF_FILE+":", config['DEFAULT']['SN'])
    SN = config['DEFAULT']['SN']
    
#print(SN)
    
if str(SN) == '0000000000000000':
                  
    input('Press Enter to search with fastboot')
else:
    input('Press Enter to reboot your device '+SN+' in bootloader-mode...\n')

runOS('adb -s '+SN+' reboot bootloader', 1)



SN = testFastbootDevice(SN)
    
config['DEFAULT']['SN'] = str(SN)
with open(CONF_FILE, 'w') as f:
    config.write(f)
print('INFO: Working on device', SN)

input('Press Enter to continue... ')


cls()

# IMEI
if not config['DEFAULT']['imei']:
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
    print('INFO:   checksum is', CONF_FILE+":", config['DEFAULT']['checksum'])
    print('INFO: last code was', CONF_FILE+":", config['DEFAULT']['algoOEMcode'])
    
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
    
#if args.verbose:
#    cls()
#    runOS('fastboot oem get-product-model')
#    input('Press Enter ...')

#if args.verbose:
#    cls()
#    runOS('fastboot oem fastboot oem get-psid')
#    input('Press Enter ...')

input('Press Enter to start\n')
codeOEM = tryUnlockBootloader(checksum)

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
