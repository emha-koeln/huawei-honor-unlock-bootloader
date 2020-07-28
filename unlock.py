#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SkyEmie_' 💜 https://github.com/SkyEmie
emha.koeln
"""

import time
#from flashbootlib import test
import os
import math
import subprocess
from subprocess import PIPE, run
import platform

##########################################################################################################################

PLATFORM ='unknown'

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
    algoOEMcode = 1000000000000000 #base
    
    save        = 0
    #clear       = 0
    os.system('clear')

    while(unlock == False):
        #os.system("title Bruteforce is running.. "+str(algoOEMcode)+" "+str(save))
        print("Bruteforce is running... " + str(algoOEMcode)+" "+str(save))

        cmd = 'fastboot oem unlock '+ str(algoOEMcode)
        result = runOS(cmd)
     
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
            #if i.lower() == 'failed':
            #    print('Failed: ', i)

            #else:
            #    print('i: ', i)

            #time.sleep(1)

        #if clear == 5:
        #    clear = 0
        #    os.system('clear')

        if save == 200:
            save = 0
            bak = open("unlock_code.txt", "w")
            bak.write("If you need to pick up where you left off,\nchange the algoOEMcode variable with #base comment to the following value :\n"+str(algoOEMcode))
            bak.close()

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
input(' Press any key to detect device..\n')

PLATFORM = platform.system()

#os.system('adb devices')
runOS('adb devices')

imei     = int(input('Type IMEI digit :'))

checksum = luhn_checksum(imei)
input('Press any key to reboot your device..\n')

runOS('adb reboot bootloader')
input('Press any key when your device is ready.. (This may take time, depending on your cpu/serial port)\n')

codeOEM = tryUnlockBootloader(checksum)
input('Press any key ..\n')

# toDo
runOS('fastboot getvar unlocked')
runOS('fastboot reboot')

print('\n\nDevice unlock ! OEM CODE : '+codeOEM)
print('(Keep it safe)\n')
input('Press any key to exit..\n')
exit()
