
# common calls for both autojack and studio-controls
import configparser
import fcntl
import getopt
import glob
import json
import os
import re
import shutil
import sys
import time

from os.path import expanduser

global install_path
install_path = os.path.abspath(f"{sys.path[0]}/..")
global vers
vers = "not installed"

global config_path
global log
global new_name
global old_name
global temp_name
# config_path = "~/software/Studio/controls-debug/"
config_path = "~/.config/autojack/"
new_name = f"{config_path}autojack.json"
old_name = f"{config_path}/autojackrc"
temp_name = f"{config_path}/temp_aj.json"
# log = False

def version():
    ''' get the version we are running as. Used mostly to detect
    if a new version has been installed but the old version
    of autojack is still running. Rather than restart autojack
    right away, stopping audio, studio-controls will do so at
    the next apply, jack start or stop '''
    global install_path
    global vers
    if vers == "not installed":
        vfile = f"{install_path}/share/studio-controls/version"
        if os.path.isfile(vfile):
            with open(vfile, "r") as version_file:
                for line in version_file:
                    vers = line.strip()
                    # return after first line
                    return vers
    return vers

def check_user():
    """ Check that user is a human and is not root
    """
    uid = os.getuid()
    if uid == 0:
        print("JACK should never be run as root: goodbye")
        os._exit(0)
    elif uid < 1000:
        print("Studio controls is not meant to be run as a system process")
        os._exit(0)


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
    global log
    tmpname = 'none'
    internal = "none"
    pci = "none"
    usb = "none"
    fw = "none"
    HDMI = 'none'
    if log:
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


def make_db():
    ''' read old config file. '''
    global config
    global def_config
    global old_name
    global our_db
    global log

    if log:
        print("set some reasonable defaults")
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

    if log:
        print("read old style file if it exists")
    c_file = expanduser(old_name)
    if os.path.isfile(c_file):
        # config file exists, read it in
        config.read(c_file)
        # rename to *.bak so we don't use it again
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
            connect_mode: char ('n')
            dev: string (1st internal non-hdmi)
            USBdev: string (blank)
            cap-latency: 0,
            play-latency: 0
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
                name:
                    connection: "none",
                    count: 2
            pulse_out:
                name: {
                    connection: "none",
                    count: 2
        Devices:
            {}
    '''
    if log:
        print("make up to date config file")
    our_db = {'version': version()}
    our_db['log-level'] = int(def_config['log-level'])
    if def_config['usbdev'] == '':
        def_config['usbdev'] = 'none'
    jack_db = {'on': bool(def_config['jack'] in ['True']),
               'driver': def_config['driver'],
               'chan-in': int(def_config['chan-in']),
               'chan-out': int(def_config['chan-out']),
               'rate': int(def_config['rate']),
               'frame': int(def_config['frame']),
               'period': int(def_config['period']),
               'connect-mode': def_config['connect-mode'],
               'dev': def_config['dev'],
               'usbdev': def_config['usbdev'],
               'cap-latency': 0, 'play-latency': 0}

    extra_db = {'a2j': bool(def_config['a2j'] in ['True']),
                'usbauto': bool(
                    def_config['usbauto'] in ['True']),
                'usb-single': bool(
                    def_config['usb-single'] in ['True']),
                'monitor': def_config['monitor'],
                'phone-action': def_config['phone-action'],
                'phone-device': def_config['phone-device']
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
    our_db['znet'] = {}
    our_db['mnet'] = {"type": "jack", "count": 0}

    # Now devices we just want to add devices in the config file
    # Since get_devices should start with the current db, create one
    # from what device the old config knows about
    devices_db = {}
    our_db['devices'] = devices_db
    devicelist = []
    if log:
        print("adding devices to devicelist")
    if default_device != 'none':
        devicelist.append(default_device)
    if def_config['DEV'] != 'none' and def_config['DEV'] not in devicelist:
        devicelist.append(def_config['DEV'])
    if (def_config['USBDEV'] != 'none') and (
            def_config['USBDEV'] not in devicelist):
        devicelist.append(def_config['USBDEV'])
    if def_config['PHONE-DEVICE'] != 'none' and def_config[
            'PHONE-DEVICE'] not in devicelist:
        devicelist.append(def_config['PHONE-DEVICE'])
    if log:
        print(
            f"adding devices from xdev: "
            "{ str(def_config['XDEV'].split())}"
            "and blacklist: "
            "{str(def_config['BLACKLIST'].split())}")
    devicelist = devicelist + \
        def_config['XDEV'].split() + def_config['BLACKLIST'].split()

    for rdev in devicelist:
        rdev_l = rdev.split(',')
        if log:
            print(f"fleshing out device: {str(rdev_l)}")
        if len(rdev_l) == 3:
            dev, sub, ssub = rdev_l
            dev_db = make_dev_temp()
            if def_config[
                    'USBDEV'] != 'none' and dev == def_config[
                    'USBDEV'].split(',')[0]:
                if 'USB1' not in devices_db:
                    devices_db['USB1'] = dev_db
                    dev_db['usb'] = True
                    un, ud, us = def_config['USBDEV'].split(',')
                    jack_db['usbdev'] = f"USB1,{ud},{us}"
                else:
                    dev_db = devices_db['USB1']
            else:
                if dev not in devices_db:
                    dev_db = make_dev_temp()
                    devices_db[dev] = dev_db
                else:
                    dev_db = devices_db[dev]
            dev_db['raw'] = dev
            if sub not in dev_db['sub']:
                dev_db['sub'][sub] = make_sub_temp()
            sub_db = dev_db['sub'][sub]
            sub_db['name'] = rdev
            if rdev in def_config['XDEV'].split():
                sub_db['play-chan'] = 100
                sub_db['cap-chan'] = 100
            if rdev in def_config['BLACKLIST'].split():
                sub_db['hide'] = True
    return


def make_dev_temp():
    ''' make a biolerplate device with no sub '''
    dev_temp = {'number': -1, 'usb': False,
                "internal": False, 'hdmi': False,
                'firewire': False,
                'rates': ['32000', '44100', '48000',
                          '88200', '96000', '192000'],
                'min_latency': 16, 'id': 'none',
                'bus': 'none', 'sub': {}}
    return dev_temp


def make_sub_temp():
    ''' make a template for a sub device '''
    global def_config
    sub_temp = {'name': 'none', 'playback': True,
                'capture': True,
                'rate': int(def_config['RATE']),
                'frame': int(def_config['FRAME']),
                'nperiods': int(def_config['PERIOD']),
                'hide': False,
                'cap-latency': 0, 'play-latency': 0}
    return sub_temp


def write_new():
    ''' write new config file '''
    if log:
        print("write new config file")
    global our_db
    global new_name
    global config_path
    global temp_name
    # print(json.dumps(our_db, indent = 4))
    c_file = expanduser(new_name)
    ck_file = expanduser(temp_name)
    count = 0
    while count < 10:
        if not os.path.isfile(ck_file):
            break
        # someone is writing, wait
        if log:
            print("File is being written don't write yet")
        time.sleep(.5)
        count += 1
    c_dir = expanduser(config_path)
    if not os.path.isdir(c_dir):
        os.makedirs(c_dir)
    with open(ck_file, 'w') as json_file:
        if json_file.writable():
            fcntl.lockf(json_file, fcntl.LOCK_EX)
        json.dump(our_db, json_file, indent=4)
        json_file.write("\n")
        json_file.flush()
        os.fsync(json_file.fileno())
        # Release the lock on the file.
        if json_file.writable():
            fcntl.lockf(json_file, fcntl.LOCK_UN)
        if os.path.exists(c_file):
            os.remove(c_file)
        os.rename(ck_file, c_file)


def usb_duplicate(device):
    # find out if this is a duplicate
    global log
    global our_db
    ret = 'none'
    check_db = our_db['devices'][device]
    for good_dev in our_db['devices']:
        if device == good_dev:
            # this is always a duplicate of itself
            continue
        if len(good_dev) > 3 and good_dev[
                0:3] == 'USB' and good_dev[3].isdigit():
            good_db = our_db['devices'][good_dev]
            if check_db['id'] == 'none':
                ret = good_dev
            if check_db['id'] == good_db['id']:
                # same kind of device
                if good_db['bus'] == check_db['bus']:
                    ret = good_dev
    if log:
        print(f"Dup check returns: {ret}")
    return ret


def usb_number():
    # get a free usb number
    global our_db
    numbers = []
    for dev in our_db['devices']:
        if len(dev) > 3 and dev[0:3] == 'USB' and dev[3].isdigit():
            # this is usb
            numbers.append(int(dev[3:]))
    for n in range(1, 20):
        if n not in numbers:
            return n


def check_devices(our_db):
    ''' take an exsiting db['devices'] db and make sure it agrees
    with the actual devices in the machine. If a listing in the db
    does not have a real card right now, card is set to -1 (unplugged)
    otherwsie card is set to current card number (so we don't duplicate it)
    if there are devices not in the list they are added according
    to settings'''
    global log

    dev_list = list(our_db['devices'])
    for device in dev_list:
        # do sanity check
        dev_db = our_db['devices'][device]
        dev_db['number'] = -1
        if 'raw' not in dev_db:
            dev_db['raw'] = device
        if 'id' not in dev_db:
            dev_db['id'] = 'none'
        if 'bus' not in dev_db:
            dev_db['bus'] = 'none'
        if 'hdmi' not in dev_db:
            dev_db['hdmi'] = False
        if 'internal' not in dev_db:
            dev_db['internal'] = False
        if 'firewire' not in dev_db:
            dev_db['firewire'] = False
        if 'usb' not in dev_db:
            dev_db['usb'] = False
        if 'rates' not in dev_db:
            dev_db['rates'] = ["32000", "44100",
                               "48000", "88200", "96000", "192000"]
        if 'min_latency' not in dev_db:
            dev_db['min_latency'] = 16
        if dev_db['hdmi']:
            dev_db['min_latency'] = 4096
        elif dev_db['internal']:
            dev_db['min_latency'] = 128
        elif dev_db['firewire']:
            dev_db['min_latency'] = 256
        elif dev_db['usb']:
            dev_db['min_latency'] = 32
            if len(device) < 4 or not (
                    device[0:3] == 'USB' and device[3].isdigit()):
                # check for duplicate
                # dup means id and bus match
                if usb_duplicate(device) != 'none':
                    our_db['devices'].pop(device)
                    continue
                else:
                    new_dev = f"USB{str(usb_number())}"
                    our_db['devices'][new_dev] = our_db['devices'].pop(device)
                    dev_db = our_db['devices'][new_dev]
                    if our_db['jack']['usbdev'] != 'none':
                        usb_split = our_db['jack']['usbdev'].split(',')
                        if len(usb_split) == 3:
                            un, ud, us = usb_split
                            if un == device:
                                our_db['jack']['usbdev'] = f"{new_dev},{ud},{us}"
            dup = usb_duplicate(device)
            if dup != 'none':
                print(f"dupcheck for {device} returns {dup}")
                our_db['devices'].pop(device)
                continue

        for sub in dev_db['sub']:
            sub_db = dev_db['sub'][sub]
            if 'playback' not in sub_db:
                sub_db['playback'] = False
            else:
                sub_db['playback'] = bool(
                    str(sub_db['playback']) in ['True', 'true'])
            if 'capture' not in sub_db:
                sub_db['capture'] = False
            else:
                sub_db['capture'] = bool(
                    str(sub_db['capture']) in ['True', 'true'])
            if 'play-chan' not in sub_db:
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
            if 'cap-chan' not in sub_db:
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
            if 'rate' not in sub_db:
                sub_db['rate'] = 48000
            else:
                sub_db['rate'] = int(sub_db['rate'])
            if 'frame' not in sub_db:
                sub_db['frame'] = 1024
            else:
                sub_db['frame'] = int(sub_db['frame'])
            if 'nperiods' not in sub_db:
                sub_db['nperiods'] = 2
            else:
                sub_db['nperiods'] = int(sub_db['nperiods'])
            if 'hide' not in sub_db:
                sub_db['hide'] = False
            else:
                sub_db['hide'] = bool(str(sub_db['hide']) in ['True', 'true'])
            if 'name' not in sub_db:
                sub_db['name'] = f"{dev_db['raw']},{sub},0"
            if 'cap-latency' not in sub_db:
                sub_db['cap-latency'] = 0
            if 'play-latency' not in sub_db:
                sub_db['play-latency'] = 0
            sub_db['play-pid'] = 0
            sub_db['cap-pid'] = 0
            if "description" not in sub_db:
                sub_db['description'] = "unknown"

    # now find the real number
    if os.path.exists("/proc/asound/cards"):
        with open("/proc/asound/cards", "r") as cards_file:
            for line in cards_file:
                # last one is highest dev number
                sub = line.rstrip()[1:]
                sub2 = sub.split(" ")
                first_el = line.rstrip()[1:].split(" ")[0]
                if first_el.isdigit():
                    ndevs = int(first_el)
    else:
        return our_db
    ndevs += 1
    for x in range(0, ndevs):
        # card loop
        rates = ['32000', '44100', '48000', '88200', '96000', '192000']
        drates = []
        cname = ""
        usb = False
        bus = 'none'
        d_id = 'none'
        cdescription = 'unknown'
        # first get device raw name
        if os.path.exists(f"/proc/asound/card{str(x)}"):
            if os.path.isfile(f"/proc/asound/card{str(x)}/id"):
                with open(f"/proc/asound/card{str(x)}/id", "r") as card_file:
                    for line in card_file:
                        # only need one line
                        cname = line.rstrip()
            else:
                cname = str(x)
        else:
            # not all numbers may be used
            continue
        # now check for USB device remembering to go by id/bus not raw name
        if os.path.exists(f"/proc/asound/card{str(x)}/usbid"):
            usb = True
            with open(f"/proc/asound/card{str(x)}/usbid", "r") as id_file:
                for line in id_file:
                    d_id = line.strip()
            if os.path.isfile(
                    f"/proc/asound/card{str(x)}/usbbus"):
                with open(
                        f"/proc/asound/card{str(x)}/usbbus",
                        "r") as bus_file:
                    for line in bus_file:
                        oldbus = line.strip().split('/')[0]
            if os.path.isfile(f"/proc/asound/card{str(x)}/stream0"):
                line0 = True
                with open(
                        f"/proc/asound/card{str(x)}/stream0",
                        "r") as desc_file:
                    for line in desc_file:
                        if line0:
                            prebus = line.strip().split(' at ')[1]
                            bus = line.strip().split(' at ')[1].split(', ')[0]
                            cdescription = line.strip().split(' at ')[0]
                            line0 = False
                        if 'Rates:' in line:
                            fnd_rates = line.split()[1:]
                            for rate in fnd_rates:
                                rate = rate.split(',')[0]
                                if rate not in drates:
                                    drates.append(rate)
        # find this device in db or add to db
        found_name = ""
        for dev in our_db['devices']:
            dev_db = our_db['devices'][dev]
            if usb and [dev_db['id'], dev_db['bus']] == [d_id, bus]:
                # this is the device...
                dev_db['usb'] = True
                found_name = dev
                break
            elif usb and [dev_db['id'], dev_db['bus']] == [d_id, oldbus]:
                # this is an old style device... well maybe
                # check if it already has a number
                dev_db['usb'] = True
                found_name = dev
                break
            elif usb and [dev_db['id'], dev_db['bus']] == ['none', 'none']:
                # really old style
                if dev_db['raw'] == cname:
                    found_name = dev
                    dev_db['usb'] = True
                    break
            elif dev == cname:
                dev_db['raw'] = cname
                dev_db['usb'] = False
                dev_db['number'] = x
                found_name = dev
                break
        if found_name == "":
            if log:
                print("device not found")
            if usb:
                found_name = f"USB{usb_number()}"
                our_db['devices'][found_name] = {
                    'number': x, 'usb': True,
                    "internal": False,
                    'hdmi': False, 'firewire': False,
                    'min_latency': 32,
                    'rates': drates, 'raw': cname,
                    'id': d_id, 'bus': bus, 'sub': {}}
            else:
                found_name = cname
                our_db['devices'][cname] = {
                    'number': x, 'usb': False,
                    "internal": False,
                    'hdmi': False, 'firewire': False,
                    'min_latency': 16,
                    'rates': ['32000', '44100', '48000',
                              '88200', '96000', '192000'],
                    'raw': cname, 'id': 'none',
                    'bus': 'none', 'sub': {}}

        # print(f"{cname}")

        ''' get device info from system files '''
        dev_db['internal'] = False
        dev_db['firewire'] = False
        dev_db['min_latency'] = 16
        dev_db['hdmi'] = bool(dev_db['raw'] in ['HDMI', 'NVidia'])
        if 'id' not in dev_db:
            dev_db['id'] = 'none'
        if 'bus' not in dev_db:
            dev_db['bus'] = 'none'
        sub = 0
        if dev_db['usb']:
            dev_db['raw'] = cname
            dev_db['number'] = x
            dev_db['id'] = d_id
            dev_db['bus'] = bus
            dev_db['min_latency'] = 32
        elif os.path.exists(
                f"/proc/asound/card{str(x)}/codec#0"):
            dev_db['internal'] = True
            dev_db['min_latency'] = 128
            # can get supported rates from file above
            with open(
                    f"/proc/asound/card{str(x)}/codec#0",
                    "r") as card_file:
                node = False
                for line in card_file:
                    if 'Node' in line:
                        node = True
                        if 'Digital' in line and not dev_db['hdmi']:
                            node = False
                    if node and 'rates' in line:
                        fnd_rates = line.split()[2:]
                        for rate in fnd_rates:
                            if rate not in drates:
                                drates.append(rate)
        if len(drates):
            rates = drates

        elif os.path.exists(f"/proc/asound/card{str(x)}/firewire"):
            dev_db['firewire'] = True
            dev_db['min_latency'] = 256

        if dev_db['hdmi']:
            dev_db['min_latency'] = 4096

        dev_db['rates'] = rates

        for y in range(0, 20):
            cap = False
            play = False
            cap_pid = 0
            play_pid = 0
            dname = ""
            if os.path.exists(f"/proc/asound/card{str(x)}/pcm{str(y)}p"):
                play = True
                if os.path.exists(
                        f"/proc/asound/card{str(x)}/pcm{str(y)}p/sub0"):
                    with open(
                            f"/proc/asound/card{str(x)}/"
                            f"pcm{str(y)}p/sub0/status",
                            "r") as info_file:
                        for line in info_file:
                            if re.match("^owner_pid",
                                        line.rstrip()):
                                play_pid = int(line.rstrip().split(": ", 1)[1])
                    with open(f"/proc/asound/card{str(x)}/"
                              f"pcm{str(y)}p/sub0/info",
                              "r") as info_file:
                        for line in info_file:
                            clean_line = line.rstrip()
                            if re.match("^name:", clean_line):
                                line_list = clean_line.split(": ", 1)
                                if len(line_list) > 1:
                                    dname = line_list[1]

            if os.path.exists(f"/proc/asound/card{str(x)}/pcm{str(y)}c"):
                cap = True
                if os.path.exists(f"/proc/asound/card{str(x)}"
                                  f"/pcm{str(y)}c/sub0"):
                    with open(f"/proc/asound/card{str(x)}"
                              f"/pcm{str(y)}c/sub0/status",
                              "r") as info_file:
                        for line in info_file:
                            if re.match("^owner_pid", line.rstrip()):
                                cap_pid = int(line.rstrip().split(": ", 1)[1])
                    with open(f"/proc/asound/card{str(x)}"
                              f"/pcm{str(y)}c/sub0/info",
                              "r") as info_file:
                        for line in info_file:
                            clean_line = line.rstrip()
                            if re.match("^name:", clean_line):
                                line_list = clean_line.split(": ", 1)
                                if len(line_list) > 1:
                                    dname = line_list[1]
            # print(f"cap: {str(cap)}  play:{str(play)}")
            if cap or play:
                if str(y) not in dev_db['sub']:
                    dev_db['sub'][str(y)] = {'playback': play, 'capture': cap}

                sub_db = dev_db['sub'][str(y)]
                sub_db['play-pid'] = play_pid
                sub_db['cap-pid'] = cap_pid
                if 'playback' not in sub_db:
                    sub_db['playback'] = play
                if 'capture' not in sub_db:
                    sub_db['capture'] = cap
                if "play-chan" not in sub_db:
                    if dev_db['usb'] and our_db['extra']['usbauto']:
                        sub_db['play-chan'] = 100
                    else:
                        sub_db['play-chan'] = 0
                if 'cap-chan' not in sub_db:
                    if dev_db['usb'] and our_db['extra']['usbauto']:
                        sub_db['cap-chan'] = 100
                    else:
                        sub_db['cap-chan'] = 0
                if "rate" not in sub_db:
                    jackrate = str(our_db['jack']['rate'])
                    if jackrate not in dev_db['rates']:
                        sub_db['rate'] = 48000
                        if ('48000' not in rates) and len(rates):
                            sub_db['rate'] = int(rates[0])
                    else:
                        sub_db['rate'] = our_db['jack']['rate']
                if 'frame' not in sub_db:
                    sub_db['frame'] = 1024
                    if 1024 < dev_db['min_latency']:
                        sub_db['frame'] = dev_db['min_latency']
                if 'nperiods' not in sub_db:
                    sub_db['nperiods'] = 2
                if 'hide' not in sub_db:
                    sub_db['hide'] = False
                if 'name' not in sub_db or sub_db['name'] == 'none':
                    sub_db['name'] = f"{found_name},{str(y)},0"
                if "cap-latency" not in sub_db:
                    sub_db['cap-latency'] = 0
                if "play-latency" not in sub_db:
                    sub_db['play-latency'] = 0
                if dev_db['usb']:
                    sub_db['description'] = cdescription
                else:
                    sub_db['description'] = dname
    return our_db


def check_new(no_check=False):
    global log
    global new_name
    global our_db
    global temp_name
    if log:
        print(f"checking config file for compatability with version {version()}")
    c_file = expanduser(new_name)
    ck_file = expanduser(temp_name)
    count = 0
    while count < 10:
        if not os.path.isfile(ck_file):
            break
        # someone is writing, wait
        if log:
            print("File is being written don't read yet")
        time.sleep(.5)
        count += 1
    time.sleep(.5)
    if os.path.isfile(c_file) and os.path.getsize(c_file) > 100:
        # config file exists, read it in
        with open(c_file) as f:
            our_db = json.load(f)
    else:
        print(f"Error, {c_file} not found. Make one.")
        make_db()
        check_db()
        return

    if our_db['version'] != version():
        # see if saved file with our version exists
        if os.path.isfile(f"{c_file}.{version()}"):
            print(
                "A config file for this version exists: "
                f"{c_file}.{version()} Using it")
            shutil.copyfile(f"{c_file}.{version()}", c_file)
            return
        if log:
            print(f"config file is version: {our_db['version']} updating")
            print(f"saving old config file to: {c_file}.{our_db['version']}")
        shutil.copyfile(c_file, f"{c_file}.{our_db['version']}")
    if no_check:
        return
    check_db()


def check_db():
    global our_db
    # check all parameters for sanity
    if log:
        print("checking data base")
    our_db['version'] = version()
    if 'log-level' not in our_db:
        our_db['log-level'] = 15
    if 'jack' not in our_db:
        our_db['jack'] = {}
    if 'extra' not in our_db:
        our_db['extra'] = {}
    if 'pulse' not in our_db:
        our_db['pulse'] = {}
    if 'devices' not in our_db:
        our_db['devices'] = {}
    if 'znet' not in our_db:
        our_db['znet'] = {}
    if 'mnet' not in our_db:
        our_db['mnet'] = {'type': 'jack', 'count': 0}

    extra_db = our_db['extra']

    # check_devices should be universal.
    our_db = check_devices(our_db)
    if log:
        print(" Devices checked, continue data base check")

    jack_db = our_db['jack']
    if 'on' not in jack_db:
        jack_db['on'] = False
    else:
        jack_db['on'] = bool(str(jack_db['on']) in ['True', 'true'])

    if 'driver' not in jack_db:
        jack_db['driver'] = "alsa"

    if 'chan-in' not in jack_db:
        jack_db['chan-in'] = 1
    else:
        jack_db['chan-in'] = int(jack_db['chan-in'])

    if 'chan-out' not in jack_db:
        jack_db['chan-out'] = 1
    else:
        jack_db['chan-out'] = int(jack_db['chan-out'])

    if 'rate' not in jack_db:
        jack_db['rate'] = 48000
    else:
        jack_db['rate'] = int(jack_db['rate'])

    if 'frame' not in jack_db or not str(jack_db['frame']).isnumeric():
        jack_db['frame'] = 1024
    else:
        jack_db['frame'] = int(jack_db['frame'])

    if 'period' not in jack_db:
        jack_db['period'] = 2
    else:
        jack_db['period'] = int(jack_db['period'])

    if 'connect-mode' not in jack_db:
        jack_db['connect-mode'] = 'n'
    else:
        if jack_db['connect-mode'] not in ['a', 'A', 'o', 'O']:
            jack_db['connect-mode'] = "n"

    if 'dev' not in jack_db:
        jack_db['dev'] = get_default_dev()[0]

    if ('usbdev' not in jack_db) or (
            jack_db['usbdev'] == "") or jack_db['usbdev'] == 'none':
        if jack_db['dev'] == 'none':
            jack_db['usbdev'] = get_default_dev()[1]
        else:
            jack_db['usbdev'] = 'none'
    else:
        jack_db['usbdev'] = get_dev_name(jack_db['usbdev'])

    if 'cap-latency' not in jack_db:
        jack_db['cap-latency'] = 0
    else:
        jack_db['cap-latency'] = int(jack_db['cap-latency'])

    if 'play-latency' not in jack_db:
        jack_db['play-latency'] = 0
    else:
        jack_db['play-latency'] = int(jack_db['play-latency'])

    if 'a2j' not in extra_db:
        extra_db['a2j'] = True
    else:
        extra_db['a2j'] = bool(str(extra_db['a2j']) in ['True', 'true'])

    if 'a2j_u' not in extra_db:
        extra_db['a2j_u'] = False
    else:
        extra_db['a2j_u'] = bool(str(extra_db['a2j_u']) in ['True', 'true'])

    if 'usbauto' not in extra_db:
        extra_db['usbauto'] = True
    else:
        extra_db['usbauto'] = bool(
            str(extra_db['usbauto']) in ['True', 'true'])

    if 'usb-single' not in extra_db:
        extra_db['usb-single'] = False
    else:
        extra_db['usb-single'] = bool(str(extra_db['usb-single'])
                                      in ['True', 'true'])

    if 'monitor' not in extra_db:
        extra_db['monitor'] = "system:playback_1"

    if 'phone-action' not in extra_db:
        extra_db['phone-action'] = "switch"

    if 'phone-device' not in extra_db:
        # we could use system but default is most likely to
        # have ph jack we can detect
        extra_db['phone-device'] = get_default_dev()[0]

    if 'phone-left' not in extra_db:
        extra_db['phone-left'] = '1'

    pulse_db = our_db['pulse']
    if 'inputs' not in pulse_db:
        pulse_db['inputs'] = {}
    else:
        for bridge in pulse_db['inputs']:
            if "connection" not in pulse_db['inputs'][bridge]:
                pulse_db['inputs'][bridge]['connection'] = 'none'
            elif pulse_db['inputs'][bridge]['connection'].isdigit():
                pulse_db['inputs'][bridge][
                    'connection'] = "system:capture_"
                f"{pulse_db['inputs'][bridge]['connection']}"
            if 'count' not in pulse_db['inputs'][bridge]:
                pulse_db['inputs'][bridge]['count'] = 2
            else:
                pulse_db['inputs'][bridge]['count'] = int(
                    pulse_db['inputs'][bridge]['count'])

    if 'outputs' not in pulse_db:
        pulse_db['outputs'] = {}
    else:
        for bridge in pulse_db['outputs']:
            if "connection" not in pulse_db['outputs'][bridge]:
                pulse_db['outputs'][bridge]['connection'] = 'none'
            elif pulse_db['outputs'][bridge]['connection'].isdigit():
                pulse_db['outputs'][bridge][
                    'connection'] = "system:playback_"
                f"{pulse_db['outputs'][bridge]['connection']}"
            if 'count' not in pulse_db['outputs'][bridge]:
                pulse_db['outputs'][bridge]['count'] = 2
            else:
                pulse_db['outputs'][bridge]['count'] = int(
                    pulse_db['outputs'][bridge]['count'])

    write_new()


def convert(quiet=True):

    global config_path
    global install_path
    global log
    global new_name
    global old_name
    global our_db

    log = bool(not quiet)
    c_file = expanduser(new_name)
    if log:
        print(f"Search for: {c_file}")
    if os.path.isfile(c_file):
        if log:
            print("config file found, check it")
        check_new()
    else:
        if log:
            print("Config file not found, Create one")

        make_db()
        check_db()
    return our_db
