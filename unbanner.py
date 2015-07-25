#!/usr/bin/env python3
import hashlib
import os
from os.path import expanduser
home = expanduser("~")

DEBUG = False

def normalize_path(path):
    # Remove quotes, convert backslash to slash, and add trailing slash.
    if path[0] == '"':
        path = path[1:]
    if path[-1] == '"':
        path = path[:-1]

    path = path.replace('\\', '/')

    if path[-1] != '/':
        path = path + '/'

    return path


def bytes2int(inbytes):
    return int.from_bytes(inbytes, byteorder='big')

def int2bytes(inpt, size):
    return bytes.fromhex(hex(inpt)[2:].zfill(2 * size))


def make_msg(cfc):
    msg = b'WcCf$$$\x08$$$$$$$$$$$\x07$$$\x02@unbanned.wii%%%$$$$$$$$PHDBAA\
fPmyZrVKFh%2f005946485fddd737d997d8063e2481$$$$https://amw.w\
c24.wii.com/cgi-bin/account.cgi%%%%%$$$$http://rcw.wc24.wii.\
com/cgi-bin/check.cgi%%%%%$$$$$$$https://mtw.wc24.wii.com/cg\
i-bin/receive.cgi%%%%%$$$$https://mtw.wc24.wii.com/cgi-bin/d\
elete.cgi%%%%%$$$$$https://mtw.wc24.wii.com/cgi-bin/send.cgi\
%%%%%%%%%%%%%%%%%%%$$$$$$$'
    msg = msg.replace(b'%', b'$' * 16)    # data compression for the terminally incompetent
    msg = msg.replace(b'$', b'\00')

    msg = msg[0:8] + cfc + msg[16:]

    # calculate the checksum
    checksum = 0
    
    for idx in range(0, len(msg), 4):
        # big endian = "normal" order
        checksum += bytes2int(msg[idx:idx+4])
        checksum &= 0xffffffff

    msg += int2bytes(checksum, 4)

    return msg


def trymkdir(a):
    try:
        os.mkdir(a)
    except OSError:
        pass
    return


def do_it():
    eula = '''Console ID changer 3.14, by jimbo1qaz 2014 - Edited by PokeAcer549.
THIS IS NOT A NAND GENERATOR! It only changes a couple of identifiers!

IMPORTANT: Close Dolphin/get your nand ready before continuing, and do not reopen it until this
program is finished modifying your profile.'''
    print(eula)
    print('')

    # GET MODMII PATH
    profile_path = ''
    while profile_path == '':
        print('Path to Dolphin profile (or Dolphin program folder if using portable mode)')
        print('You can drag the profile folder (or program folder) into this window')
        profile_path = home + "/" #Change this path to that of your Dolphin folder
    print('')

    profile_path = normalize_path(profile_path)

    hashed = os.urandom(256)

    os.chdir(profile_path)
    trymkdir('Wii')

    # LET DOLPHIN REGENERTATE THE MAC ADDRESS
    with open('Config/Dolphin.ini') as f:
        cfg = [line for line in f]

    with open('Config/Dolphin.ini', 'w') as f:
        for line in cfg:
            if not line.lower().startswith('wirelessmac'):
                f.write(line)


    # LET DOLPHIN REGENERATE THE SERIAL NUMBER
    # AND DELETE DWC_AUTHDATA
    for del_path in ['Wii/title/00000001/00000002/data/setting.txt',
                     'Wii/shared2/DWC_AUTHDATA']:
        try:
            os.remove(del_path)
        except OSError:
            pass

    # MAKE THE CONSOLE FRIEND CODE
    cfc_int = bytes2int(hashed[10:20]) % (10 ** 16) # generate a console friend code
    if not DEBUG:
        cfc_int = cfc_int // (2**31 - 19) * (2**31 - 19)
    cfc = int2bytes(cfc_int, 8)                     # 64-bit int = 8 bytes
    if DEBUG:
        print(cfc)
    # cfc bytes

    # PATCH NWC24MSG.CFG
    print('Now patching files.')
    print('')
    msg = make_msg(cfc)

    # Write nwc24msg to disk
    trymkdir('Wii/shared2')
    trymkdir('Wii/shared2/wc24')
    with open('Wii/shared2/wc24/nwc24msg.cfg', 'wb') as file:
        file.write(msg)
    with open('Wii/shared2/wc24/nwc24msg.cbk', 'wb') as file:
        file.write(msg)
    
    # We're done.
    print('We\'re done.')
    print()
    print('Note that you may need to create a new profile in your game, or possibly')
    print('delete your game save entirely in order to clear the game identifier(s).')
    print('For Mario Kart Wii, you must use a new license. No need to wipe the save file.')
    print()
    print('Press Enter to exit.')

    input()

if __name__ == '__main__':
    do_it()
