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

##########################################################################################################################
CONF_FILE = 'unlock.conf'
PLATFORM ='unknown'

##########################################################################################################################

def runOS(cmd):

    sCmd = cmd
    cmd = cmd.split(' ')

    try:
       result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
       #DEBUG
       print('Shell Result for:', sCmd)
       print('Returncode: '+str(result.returncode))
       print(result.stdout, result.stderr)
       
       return(result)

    except subprocess.CalledProcessError as e:
       raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    

def tryUnlockBootloader(checksum):

    unlock      = False
    save        = 0
    
    algoOEMcode = 1000000000000000 #base
   
    if config['DEFAULT']['algoOEMcode']:
        algoOEMcode     = int(config['DEFAULT']['algoOEMcode'])
    else: 
        algoOEMcode     = int(config['DEFAULT']['base'])
    #clear       = 0
    os.system('clear')

    while(unlock == False):
  
        print("Bruteforce is running... " + str(algoOEMcode)+" "+str(save))

        cmd = 'fastboot oem unlock '+ str(algoOEMcode).rjust(16,'0')
        result = runOS(cmd)

        # ToDo: 
        # if result.returncode == 0:
     
        sprout = result.stdout + ' ' + result.stderr
        sdrout = sprout.replace('\n', ' ').split(' ')
        save  +=1

        for i in sdrout:
           #print("sdrout spli = ", i)#, " ", sdrout)
            if i.lower() == 'success':
                print('INFO: ', i)
                bak = open("unlock_code.txt", "w")
                bak.write("Your saved bootloader code : "+str(algoOEMcode)+"\nDEBUG sprout was: "+str(sprout))
                bak.close()
                input('Press any key\n')
                return(algoOEMcode)
            #elif i.lower() == 'reboot':
            elif i.lower() == 'reboot':
                print('INFO: ', i)
                print('\n\nSorry, your bootloader has additional protection that other models don\'t have\nI can\'t do anything.. :c\n\n')
                input('Press any key to exit..\n')
                exit()

        if save == 200:
            save = 0
            
            config['DEFAULT']['algoOEMcode'] = str(algoOEMcode)
            with open(CONF_FILE, 'w') as f:
                config.write(f)
            # bak = open("unlock_code.txt", "w")
            # bak.write("If you need to pick up where you left off,\nchange the algoOEMcode variable with #base comment to the following value :\n"+str(algoOEMcode))
            # bak.close()

        algoOEMcode = algoIncrementChecksum(algoOEMcode, checksum)


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

print('\n\n           Unlock Bootloader script - By SkyEmie_\'')
print('\n\n  (Please enable USB DEBBUG and OEM UNLOCK if the device isn\'t appear..)')
print('  /!\ All data will be erased /!\\\n')
input(' Press Enter to detect device..\n')


config = configparser.ConfigParser()
config['DEFAULT'] = {'imei': '',
                      'base': '1000000000000000',
                      'algoOEMcode': ''}
if not path.exists(CONF_FILE):
    with open(CONF_FILE, 'w') as f:
        config.write(f)

config.read(CONF_FILE)

#os.system('adb devices')
runOS('adb devices')

if not config['DEFAULT']['imei']:
    imei     = int(input('Type IMEI digit :'))
    config['DEFAULT']['imei'] = str(imei)
    with open(CONF_FILE, 'w') as f:
       config.write(f)
else:
    imei = int(config['DEFAULT']['imei'])  
    print('INFO: found IMEI in', CONF_FILE+":", imei)
    
checksum = luhn_checksum(imei)
input('Press Enter to reboot your device..\n')

runOS('adb reboot bootloader')
input('Press any key when your device is ready.. (This may take time, depending on your cpu/serial port)\n')

codeOEM = tryUnlockBootloader(checksum)
print('Device unlocked! OEM CODE: '+codeOEM)
input('Press Enter\n')

# toDo
runOS('fastboot getvar unlocked')
runOS('fastboot reboot')

print('\n\nDevice unlock ! OEM CODE : '+codeOEM)
print('(Keep it safe)\n')
input('Press any key to exit..\n')
exit()
