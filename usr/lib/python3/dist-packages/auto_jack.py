
# common calls for both autojack and studio-controls
import configparser
import getopt
import glob
import json
import os
import shutil
import sys

from os.path import expanduser

global install_path
install_path = os.path.abspath(f"{sys.path[0]}/..")
#sys.path.insert(1,f"{install_path}/lib/python3/dist-packages")


global version
global config_path
global new_name
global old_name
config_path = "~/.config/autojack/"
#config_path = "~/software/Studio/controls-debug/"
new_name = f"{config_path}autojack.json"
old_name = f"{config_path}/autojackrc"

def hello():
    print(f"This is a test of the module: {install_path} Hello")


def version():
    global install_path
    version = "not installed"
    vfile = f"{install_path}/share/studio-controls/version"
    if os.path.isfile(vfile):
        with open(vfile, "r") as version_file:
            for line in version_file:
                version = line.strip()
                #return after first line
                return version
    return version
    

def get_default_dev():
    # Ideally, this is the HDA device
    # certainly it should be internal and not USB
    # priority:
    # HDA non-hdmi
    # other internal (pci, ac97)
    # firewire
    # HDMI
    # none
    # if none, and usbdev unset or empty
    # 1st USB should be appended
    tmpname = 'none'
    internal = "none"
    pci = "none"
    usb = "none"
    fw = "none"
    HDMI = 'none'
    print("Try to figure out a good default device")
    for adir in glob.glob("/proc/asound/card*/"):
        tmpname = 'none'
        if os.path.isfile(f"{adir}/id"):
            with open(f"{adir}/id", "r") as card_file:
                for line in card_file:
                    tmpname = line.rstrip()
        else:
            tmpname = "no-id"
        if os.path.isfile(f"{adir}/codec#0"):
                if tmpname != "HDMI" and tmpname != "NVidia":
                    internal = f"{tmpname},0,0"
                elif HDMI == 'none':
                    HDMI = f"{tmpname},0,0"
        elif os.path.isfile(f"{adir}/usbbus"):
            if usb == 'none':
                usb = f"{tmpname},0,0"
        elif os.path.exists(f"{adir}/firewire"):
            if fw == 'none':
                fw = f"{tmpname},0,0"
        elif pci == 'none':
            pci = f"{tmpname},0,0"
    if internal != 'none':
        return internal, usb
    if pci != 'none':
        return pci, usb
    if fw != 'none':
        return fw, usb
    if HDMI != 'none':
        return HDMI, usb
    return 'none', usb


def get_dev_name(testname):
    # convert from raw to devname
    global our_db
    if testname == 'none':
        return 'none'
    name, dev, sub = testname.split(',')
    for device in our_db['devices']:
        if our_db['devices'][device]['raw'] == name:
            return f"{device},{dev},{sub}"
        elif device == name:
            return testname
    return 'none'



def read_old():
    ''' read old config file. '''
    print("read old file")
    global config
    global def_config
    global version
    global default_device
    config = configparser.ConfigParser()
    def_config = config['DEFAULT']
    usbdev = 'none'

    default_device, usbonly = get_default_dev()
    if default_device == 'none':
        usbdev = usbonly
    # first set defaults, This makes sure there is always something to convert
    config['DEFAULT'] = {
        'JACK': "False",
        'DRIVER': "alsa",
        'CHAN-IN': "0",
        'CHAN-OUT': "0",
        'RATE': "48000",
        'FRAME': "1024",
        'PERIOD': "2",
        'CONNECT-MODE': "n",
        'ZFRAME': "512",
        'XDEV': "",
        'PULSE-IN': "pulse_in",
        'PULSE-OUT': "pulse_out",
        'PJ-IN-CON': 'system:capture_1',
        'PJ-OUT-CON': 'monitor',
        'PJ-IN-COUNT': '2',
        'PJ-OUT-COUNT': '2',
        'A2J': "True",
        'DEV': default_device,
        'USBAUTO': "True",
        'USB-SINGLE': "False",
        'USBDEV': usbdev,
        "PULSE": "True",
        "LOG-LEVEL": "15",
        "BLACKLIST": "",
        "PHONE-ACTION": "switch",
        "PHONE-DEVICE": default_device,
        "MONITOR": 'system:playback_1'
    }

    c_file = expanduser(old_name)
    if os.path.isfile(c_file):
        # config file exists, read it in
        config.read(c_file)
        # rename to *.old
        os.replace(c_file, f"{c_file}.bak")
    # fix some well known problems
    if def_config['MONITOR'] == "none":
        def_config['MONITOR'] = 'system:playback_1'
    if def_config['PJ-IN-CON'] == "0":
        def_config['PJ-IN-CON'] = "none"
    if def_config['PJ-OUT-CON'] == "0":
        def_config['PJ-OUT-CON'] = "none"
    if def_config['DEV'] == "default":
        def_config['DEV'] = default_device
    if not def_config['CONNECT-MODE'] in ['a', 'A', 'e', 'E']:
        def_config['CONNECT-MODE'] = "n"


def make_db():
    ''' Stuff config into this db:
        Version: text
        log-level: int (20)
        JACK: # things that require restart
            Used: bool (False)
            driver: string (alsa)
            chan_in: int (2)
            chan_out: int (2)
            rate: int (48000)
            frame: int (1024)
            nperiods: int (2)
            connect_mode: char (' ')
            dev: string (1st internal non-hdmi)
            USBdev: string (blank)
        extra: # Stuff that can be changed without restart
            A2J: bool (True)
            A2J_U: bool (False)
            USBAUTO: bool (True)
            USBSingle: bool (False)
            Monitor: string (system:playback_1)
            Phone_action: string (none)
            Phone_device: string (default device)
        pulse:
            pulse_in:
                {
                name
                connection
                channels
                }...
            pulse_out:
                {
                name
                connection
                channels
                }...
        Devices:
            {
            name: string
                {
                number: int (-1 for unplugged)
                usb: bool
                internal: bool
                hdmi: bool
                rates: list
                sub:
                    {
                    number: int
                    playback: bool
                    capture: bool
                    play_chan: int
                    cap_chan: int
                    rate: int
                    frame: int
                    nperiods: int
                    hide: bool
                    }...
                }
            }...
    '''
    print("make new data base")
    global def_config
    global version
    global our_db
    global default_device

    our_db = {'version': 'none'}
    our_db['log-level'] = int(def_config['log-level'])
    if def_config['usbdev'] == '':
        def_config['usbdev'] = 'none'
    jack_db = {'on': bool(def_config['jack'] in ['True']), 'driver': def_config['driver'],
                'chan-in': int(def_config['chan-in']), 'chan-out': int(def_config['chan-out']),
                'rate': int(def_config['rate']), 'frame': int(def_config['frame']),
                'period': int(def_config['period']), 'connect-mode': def_config['connect-mode'],
                'dev': def_config['dev'], 'usbdev': def_config['usbdev'],
                'cap-latency': 0, 'play-latency': 0}

    extra_db = {'a2j': bool(def_config['a2j'] in ['True']), 'usbauto': bool(def_config['usbauto'] in ['True']),
                'usb-single': bool(def_config['usb-single'] in ['True']), 'monitor': def_config['monitor'],
                'phone-action': def_config['phone-action'], 'phone-device': def_config['phone-device'],
                'usbnext': 1
                }
    our_db['jack'] = jack_db
    our_db['extra'] = extra_db
    pulse_in_db = {}
    pulse_out_db = {}
    pulse_db = {'inputs': pulse_in_db, 'outputs': pulse_out_db}
    our_db['pulse'] = pulse_db
    for idx, bridge in enumerate(def_config['PULSE-IN'].split()):
        con = def_config['PJ-IN-CON'].split()
        if len(con) < (idx + 1):
            this_con = "none"
        else:
            this_con = def_config['PJ-IN-CON'].split()[idx]
        cnt = def_config['PJ-IN-COUNT'].split()
        if len(cnt) < (idx + 1):
            this_cnt = "2"
        else:
            this_cnt = def_config['PJ-IN-COUNT'].split()[idx]
        temp_db = {'connection': this_con, 'count': int(this_cnt)}
        pulse_in_db[bridge] = temp_db
    for idx, bridge in enumerate(def_config['PULSE-OUT'].split()):
        con = def_config['PJ-OUT-CON'].split()
        if len(con) < (idx + 1):
            this_con = "none"
        else:
            this_con = def_config['PJ-OUT-CON'].split()[idx]
        cnt = def_config['PJ-OUT-COUNT'].split()
        if len(cnt) < (idx + 1):
            this_cnt = "2"
        else:
            this_cnt = def_config['PJ-OUT-COUNT'].split()[idx]
        temp_db = {'connection': this_con, 'count': int(this_cnt)}
        pulse_out_db[bridge] = temp_db

    # Now devices we just want to add devices in the config file
    # studio-controls will add all devices it finds and autojack will
    # make it's own DB as well. We don't check if the rate, buffer,etc
    # makes sense, the other two programs will correct that and the old
    # style config file assumed jack master numbers anyway so we use
    # those.
    devices_db = {}
    our_db['devices'] = devices_db
    devicelist = []
    print("adding devices to devicelist")
    if default_device != 'none':
        devicelist.append(default_device)
    if def_config['DEV'] != 'none' and def_config['DEV'] not in devicelist:
        devicelist.append( def_config['DEV'])
    if (def_config['USBDEV'] != 'none') and (def_config['USBDEV'] not in devicelist):
        devicelist.append( def_config['USBDEV'])
    if def_config['PHONE-DEVICE'] != 'none' and def_config['PHONE-DEVICE'] not in devicelist:
        devicelist.append( def_config['PHONE-DEVICE'])
    print(f"adding devices from xdev: {str(def_config['XDEV'].split())} and blacklist: {str(def_config['BLACKLIST'].split())}")
    devicelist = devicelist + def_config['XDEV'].split() + def_config['BLACKLIST'].split()
    for rdev in devicelist:
        rdev_l = rdev.split(',')
        print(f"fleshing out device: {str(rdev_l)}")
        if len(rdev_l) == 3:
            dev, sub, ssub = rdev_l
            if dev not in devices_db:
                devices_db[dev] = make_dev_temp()
            dev_db = devices_db[dev]
            dev_db['raw'] = dev
            if dev == default_device.split(',')[0]:
                dev_db['internal'] = True
            if def_config['USBDEV'] != 'none' and dev == def_config['USBDEV'].split(',')[0]:
                devices_db['USB1'] = devices_db.pop(dev)
                dev_db = devices_db['USB1']
                extra_db['usbnext'] = 2
                dev_db['usb'] = True
                un, ud, us = def_config['USBDEV'].split(',')
                jack_db['usbdev'] = f"USB1,{ud},{us}"
            if sub not in dev_db['sub']:
                dev_db['sub'][sub] = make_sub_temp()
            sub_db = dev_db['sub'][sub]
            sub_db['name'] = rdev
            if rdev in def_config['XDEV'].split():
                sub_db['play-chan'] = 100
                sub_db['cap-chan'] = 100
            if rdev in def_config['BLACKLIST'].split():
                sub_db['hide'] = True
    our_db['znet'] = {}
    our_db['mnet'] = {"type": "jack", "count": 0}
    return

def make_dev_temp():
    ''' make a biolerplate device with no sub '''
    dev_temp = {'number': -1, 'usb': False, "internal": False, 'hdmi': False, 'firewire': False,
                'rates': ['32000', '44100', '48000', '88200', '96000', '192000'],
                'min_latency': 16, 'id':'none', 'bus': 'none', 'sub': {}}
    return dev_temp

def make_sub_temp():
    ''' make a template for a sub device '''
    global def_config
    sub_temp = {'name': 'none', 'playback': True, 'capture': True,
                'rate': int(def_config['RATE']), 'frame': int(def_config['FRAME']),
                'nperiods': int(def_config['PERIOD']), 'hide': False,
                'cap-latency': 0, 'play-latency': 0}
    return sub_temp

def write_new():
    ''' write new config file '''
    print("write new config file")
    global our_db
    #print(json.dumps(our_db, indent = 4))
    c_file = expanduser(new_name)
    if not os.path.isfile(c_file):
        # either first run or old version
        c_dir = expanduser(config_path)
        if not os.path.isdir(c_dir):
            os.makedirs(c_dir)

    with open(c_file, 'w') as json_file:
        json.dump(our_db, json_file, indent = 4)
        json_file.write("\n")
    return


def usb_duplicate(device):
    #find out if this is a duplicate
    global our_db
    check_db = our_db['devices'][device]
    for good_dev in our_db['devices']:
        if len(good_dev) > 3 and good_dev[0:3] == 'USB' and good_dev[3].isdigit():
            good_db = our_db['devices'][good_dev]
            if good_db['raw'] == check_db['raw']:
                if check_db['id'] == 'none':
                    return good_dev
                if [good_db['id'], good_db['bus']] == [check_db['id'], check_db['bus']]:
                    return good_dev
    return 'none'



def check_devices():
    global our_db
    print("Checking Devices")

    dev_list = list(our_db['devices'])
    for device in dev_list:
        dev_db = our_db['devices'][device]
        # device raw is the alsa device
        if not 'raw' in dev_db:
            dev_db['raw'] = device
        if not 'number' in dev_db:
            dev_db['number'] = -1
        if not 'id' in dev_db:
            dev_db['id'] = 'none'
        if not 'bus' in dev_db:
            dev_db['bus'] = 'none'
        if not 'firewire' in dev_db:
            dev_db['firewire'] = False
        if not 'hdmi' in dev_db:
            dev_db['hdmi'] = False
        if not 'internal' in dev_db:
            dev_db['internal'] = False
        if not 'firewire' in dev_db:
            dev_db['firewire'] = False
        if not 'usb' in dev_db:
            dev_db['usb'] = False
        if not 'rates' in dev_db:
            dev_db['rates'] = ["32000", "44100", "48000", "88200", "96000", "192000"]
        if not 'min_latency' in dev_db:
            dev_db['min_latency'] = 16

        if dev_db['hdmi']:
            dev_db['min_latency'] = 4096
        elif dev_db['internal']:
            dev_db['min_latency'] = 128
        elif dev_db['firewire']:
            dev_db['min_latency'] = 256
        elif dev_db['usb']:
            dev_db['min_latency'] = 32
            if len(device) < 4 or not (device[0:3] == 'USB' and device[3].isdigit()):
                # check for duplicate
                # dup means raw, id and bus match
                if  not usb_duplicate(device) == 'none':
                    our_db['devices'].pop(device)
                    continue
                else:
                    new_dev = f"USB{our_db['extra']['usbnext']}"
                    our_db['extra']['usbnext'] = our_db['extra']['usbnext'] + 1
                    our_db['devices'][new_dev] = our_db['devices'].pop(device)
                    dev_db = our_db['devices'][new_dev]
                    if our_db['jack']['usbdev'] != 'none':
                        un, ud, us = our_db['jack']['usbdev'].split(',')
                        if un == device:
                            our_db['jack']['usbdev'] = f"{new_dev},{ud},{us}"
        for sub in dev_db['sub']:
            sub_db = dev_db['sub'][sub]
            if not 'playback' in sub_db:
                sub_db['playback'] = False
            else:
                sub_db['playback'] = bool(str(sub_db['playback']) in ['True', 'true'])
            if not 'capture' in sub_db:
                sub_db['capture'] = False
            else:
                sub_db['capture'] = bool(str(sub_db['capture']) in ['True', 'true'])
            if not 'play-chan' in sub_db:
                if dev_db['usb'] and (not our_db['extra']['usb-single']):
                    sub_db['play-chan'] = 100
                elif device == get_default_dev()[0].split(',')[0]:
                    sub_db['play-chan'] = 100
                elif device == our_db['jack']['dev'].split(',')[0]:
                    sub_db['play-chan'] = 100
                else:
                    sub_db['play-chan'] = 0
            else:
                sub_db['play-chan'] = int(sub_db['play-chan'])
            if not 'cap-chan' in sub_db:
                if dev_db['usb']:
                    sub_db['cap-chan'] = 100
                elif device == get_default_dev()[0].split(',')[0]:
                    sub_db['cap-chan'] = 100
                elif device == our_db['jack']['dev'].split(',')[0]:
                    sub_db['cap-chan'] = 100
                else:
                    sub_db['cap-chan'] = 0
            else:
                sub_db['cap-chan'] = int(sub_db['cap-chan'])
            if not 'rate' in sub_db:
                sub_db['rate'] = 48000
            else:
                sub_db['rate'] = int(sub_db['rate'])
            if not 'frame' in sub_db:
                sub_db['frame'] = 1024
            else:
                sub_db['frame'] = int(sub_db['frame'])
            if not 'nperiods' in sub_db:
                sub_db['nperiods'] = 2
            else:
                sub_db['nperiods'] = int(sub_db['nperiods'])
            if not 'hide' in sub_db:
                sub_db['hide'] = False
            else:
                sub_db['hide'] = bool(str(sub_db['hide']) in ['True', 'true'])
            if not 'name' in sub_db:
                sub_db['name'] = f"{dev_db['raw']},{sub},0"
            if not 'cap-latency' in sub_db:
                sub_db['cap-latency'] = 0
            if not 'play-latency' in sub_db:
                sub_db['play-latency'] = 0
            if not 'play-pid' in sub_db:
                sub_db['play-pid'] = 0
            if not 'cap-pid' in sub_db:
                sub_db['cap-pid'] = 0


def check_new():
    global new_name
    global our_db
    global version
    print(f"checking config file for compatability with version {version}")
    c_file = expanduser(new_name)
    if os.path.isfile(c_file):
        # config file exists, read it in
        with open(c_file) as f:
            our_db = json.load(f)
    else:
        print(f"Error, {c_file} not found.")
        # set to 0 to not cause errors that stop something
        return

    if our_db['version'] != version:
        # see if saved file with our version exists
        if os.path.isfile(f"{c_file}.{version}"):
            print(f"A config file for this version exists: {c_file}.{version} Using it")
            shutil.copyfile(f"{c_file}.{version}", c_file)
            return
        print(f"config file is version: {our_db['version']} updating")
        print(f"saving old config file to: {c_file}.{our_db['version']}")
        shutil.copyfile(c_file, f"{c_file}.{our_db['version']}")
    check_db()

def check_db():
    global our_db
    global version
    # check all parameters for sanity
    print("checking data base")
    our_db['version'] = version
    if not 'log-level' in our_db:
        our_db['log-level'] = 15
    if not 'jack' in our_db:
        our_db['jack'] = {}
    if not 'extra' in our_db:
        our_db['extra'] = {}
    if not 'pulse' in our_db:
        our_db['pulse'] = {}
    if not 'devices' in our_db:
        our_db['devices'] = {}
    # these two are new for 2.2 (in 2.1.60 +)
    if not 'znet' in our_db:
        our_db['znet'] = {}
    if not 'mnet' in our_db:
        our_db['mnet'] = {'type': 'jack', 'count': 0}

    extra_db = our_db['extra']

    if not 'usbnext' in extra_db:
        extra_db['usbnext'] = 1
    else:
        extra_db['usbnext'] = int(extra_db['usbnext'])

    check_devices()
    print(" Devices checked, continue data base check")

    jack_db = our_db['jack']
    if not 'on' in jack_db:
        jack_db['on'] = False
    else:
        jack_db['on'] = bool(str(jack_db['on']) in ['True', 'true'])

    if not 'driver' in jack_db:
        jack_db['driver'] = "alsa"

    if not 'chan-in' in jack_db:
        jack_db['chan-in'] = 1
    else:
        jack_db['chan-in'] = int(jack_db['chan-in'])

    if not 'chan-out' in jack_db:
        jack_db['chan-out'] = 1
    else:
        jack_db['chan-out'] = int(jack_db['chan-out'])

    if not 'rate' in jack_db:
        jack_db['rate'] = 48000
    else:
        jack_db['rate'] = int(jack_db['rate'])

    if not 'frame' in jack_db:
        jack_db['frame'] = 1024
    else:
        jack_db['frame'] = int(jack_db['frame'])

    if not 'period' in jack_db:
        jack_db['period'] = 2
    else:
        jack_db['period'] = int(jack_db['period'])

    if not 'connect-mode' in jack_db:
        jack_db['connect-mode'] = 'n'
    else:
        if not jack_db['connect-mode'] in ['a', 'A', 'o', 'O']:
            jack_db['connect-mode'] = "n"

    if not 'dev' in jack_db:
        jack_db['dev'] = get_default_dev()[0]

    if (not 'usbdev' in jack_db) or (jack_db['usbdev'] == "") or jack_db['usbdev'] == 'none':
        if jack_db['dev'] == 'none':
            jack_db['usbdev'] = get_default_dev()[1]
        else:
            jack_db['usbdev'] = 'none'
    else:
        jack_db['usbdev'] = get_dev_name(jack_db['usbdev'])

    if not 'cap-latency' in jack_db:
        jack_db['cap-latency'] = 0
    else:
        jack_db['cap-latency'] = int(jack_db['cap-latency'])

    if not 'play-latency' in jack_db:
        jack_db['play-latency'] = 0
    else:
        jack_db['play-latency'] = int(jack_db['play-latency'])

    if not 'a2j' in extra_db:
        extra_db['a2j'] = True
    else:
        extra_db['a2j'] = bool(str(extra_db['a2j']) in ['True', 'true'])

    if not 'a2j_u' in extra_db:
        extra_db['a2j_u'] = False
    else:
        extra_db['a2j_u'] = bool(str(extra_db['a2j_u']) in ['True', 'true'])

    if not 'usbauto' in extra_db:
        extra_db['usbauto'] = True
    else:
        extra_db['usbauto'] = bool(str(extra_db['usbauto']) in ['True', 'true'])

    if not 'usb-single' in extra_db:
        extra_db['usb-single'] = False
    else:
        extra_db['usb-single'] = bool(str(extra_db['usb-single']) in ['True', 'true'])

    if not 'monitor' in extra_db:
        extra_db['monitor'] = "system:playback_1"

    if not 'phone-action' in extra_db:
        extra_db['phone-action'] = "switch"

    if not 'phone-device' in extra_db:
        extra_db['phone-device'] = get_default_dev()[0]

    pulse_db = our_db['pulse']
    if not 'inputs' in pulse_db:
        pulse_db['inputs'] = {}
    else:
        for bridge in pulse_db['inputs']:
            if not "connection" in pulse_db['inputs'][bridge]:
                pulse_db['inputs'][bridge]['connection'] = 'none'
            elif pulse_db['inputs'][bridge]['connection'].isdigit():
                pulse_db['inputs'][bridge]['connection'] = f"system:capture_{pulse_db['inputs'][bridge]['connection']}"
            if not 'count' in pulse_db['inputs'][bridge]:
                pulse_db['inputs'][bridge]['count'] = 2
            else:
                pulse_db['inputs'][bridge]['count'] = int(pulse_db['inputs'][bridge]['count'])

    if not 'outputs' in pulse_db:
        pulse_db['outputs'] = {}
    else:
        for bridge in pulse_db['outputs']:
            if not "connection" in pulse_db['outputs'][bridge]:
                pulse_db['outputs'][bridge]['connection'] = 'none'
            elif pulse_db['outputs'][bridge]['connection'].isdigit():
                pulse_db['outputs'][bridge]['connection'] = f"system:playback_{pulse_db['outputs'][bridge]['connection']}"
            if not 'count' in pulse_db['outputs'][bridge]:
                pulse_db['outputs'][bridge]['count'] = 2
            else:
                pulse_db['outputs'][bridge]['count'] = int(pulse_db['outputs'][bridge]['count'])

    write_new()


def convert():

    global config_path
    global new_name
    global old_name
    global version
    global install_path

    version = version()

    c_file = expanduser(new_name)
    print(f"Search for: {c_file}")
    if os.path.isfile(c_file):
        print("config file found, check it")
        # Found a config file, test it
        check_new()
    else:
        print("Config file not found, Create one")
        # no usable config file found.
        # - search for pre json config and convert
        # - or use defaults and create one
        # - if force is True then use .bak on file name

        read_old()
        make_db()
        check_db()


