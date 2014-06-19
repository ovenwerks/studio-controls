#!/usr/bin/python

import sys
import os
from traceback import print_exc

import dbus

''' Create functions for reading and setting each available parameter
'''


service_name = 'org.jackaudio.service'
object_path = '/org/jackaudio/Controller'
control_interface_name = 'org.jackaudio.JackControl'
configure_interface_name = 'org.jackaudio.Configure'

class JackDBus():
    def __init__(self):
        bus = dbus.SessionBus()

        self.controller = bus.get_object(service_name, object_path)
        self.control_iface = dbus.Interface(self.controller, dbus_interface=control_interface_name)
        self.configure_iface = dbus.Interface(self.controller, dbus_interface=configure_interface_name)

    def ctl(self, command):
        if command == "exit":
            self.control_iface.Exit()
        elif command == "start":
            self.control_iface.StartServer()
        elif command == "stop":
            self.control_iface.StopServer()
        elif command == "restart":
            pass
        elif command == "status":
            if self.control_iface.IsStarted():
                return "Started"
            else:
                return "Not Started"
        elif command == "switch_master_driver":
            self.control_iface.SwitchMaster()
        elif command == "is_manually_activated":
            if self.control_iface.IsManuallyActivated():
                pass
        elif command == "driver_list":
                is_range, is_strict, is_fake_values, values = self.configure_iface.GetParameterConstraint(['engine', 'driver'])
                for value in values:
                    print value[1]
        elif command == 'get_driver':
                isset, default, value = self.configure_iface.GetParameterValue(['engine', 'driver'])
                return value
        elif command == "get_driver_parameters":
            get_parameters(self.configure_iface, ['driver'])
        elif command == "get_samplerate":
            get_parameter("rate")
        else:
            pass

    def get_parameters(self):
        params = self.configure_iface.GetParametersInfo(['driver'])
                
        #print params
        for param in params:
            typestr = dbus_typesig_to_type_string(param[0])
            name = param[1]
            #print name
            descr = param[2]
            #print descr
            isset, default, value = self.configure_iface.GetParameterValue(['driver'] + [name])
            #print typestr
            if bool(isset):
                isset = "set"
            else:
                isset = "notset"
            value = dbus_type_to_python_type(value)
            default = dbus_type_to_python_type(default)

            print "%20s: %s (%s:%s:%s:%s)" %(name, descr, typestr, isset, default, value)

    def get_parameter(self, param):
#        params = self.configure_iface.GetParametersInfo(['driver'])
                
        isset, default, value = self.configure_iface.GetParameterValue(['driver'] + [param])
        param_value = dbus_type_to_python_type(value)

        return param_value

# rate: Sample rate (uint:set:48000:48000)


# rate: Sample rate (uint:set:48000:48000)


'''            elif arg == 'ds':
                if index >= len(sys.argv):
                    print "driver select command requires driver name argument"
                    sys.exit()

                arg = sys.argv[index]
                index += 1

                print "--- driver select \"%s\"" % arg
                configure_iface.SetParameterValue(['engine', 'driver'], dbus.String(arg))
            elif arg == 'dp':
                print "--- get driver parameters (type:isset:default:value)"
                get_parameters(configure_iface, ['driver'])
            elif arg == 'dpd':
                if index >= len(sys.argv):
                    print "get driver parameter long description command requires parameter name argument"
                    sys.exit()

                param = sys.argv[index]
                index += 1

                print "--- get driver parameter description (%s)" % param
                type_char, name, short_descr, long_descr = configure_iface.GetParameterInfo(['driver', param])
                print long_descr,
            elif arg == 'dps':
                if index + 1 >= len(sys.argv):
                    print "driver parameter set command requires parameter name and value arguments"
                    sys.exit()



                param = sys.argv[index]
                index += 1
                value = sys.argv[index]
                index += 1

                print "--- driver param set \"%s\" -> \"%s\"" % (param, value)

                type_char, name, short_descr, long_descr = configure_iface.GetParameterInfo(['driver', param])
                configure_iface.SetParameterValue(['driver', param], python_type_to_jackdbus_type(value, type_char))
            elif arg == 'dpr':
                if index >= len(sys.argv):
                    print "driver parameter reset command requires parameter name argument"
                    sys.exit()

                param = sys.argv[index]
                index += 1

                print "--- driver param reset \"%s\"" % param
                configure_iface.ResetParameterValue(['driver', param])
            elif arg == 'ep':
                print "--- get engine parameters (type:isset:default:value)"
                get_parameters(configure_iface, ['engine'])
            elif arg == 'epd':
                if index >= len(sys.argv):
                    print "get engine parameter long description command requires parameter name argument"
                    sys.exit()

                param_name = sys.argv[index]
                index += 1

                print "--- get engine parameter description (%s)" % param_name

                type_char, name, short_descr, long_descr = configure_iface.GetParameterInfo(['engine', param_name])
                print long_descr,
            elif arg == 'eps':
                if index + 1 >= len(sys.argv):
                    print "engine parameter set command requires parameter name and value arguments"
                    sys.exit()

                param = sys.argv[index]
                index += 1
                value = sys.argv[index]
                index += 1

                print "--- engine param set \"%s\" -> \"%s\"" % (param, value)

                type_char, name, short_descr, long_descr = configure_iface.GetParameterInfo(['engine', param])
                configure_iface.SetParameterValue(['engine', param], python_type_to_jackdbus_type(value, type_char))
            elif arg == 'epr':
                if index >= len(sys.argv):
                    print "engine parameter reset command requires parameter name"
                    sys.exit()

                param = sys.argv[index]
                index += 1

                print "--- engine param reset \"%s\"" % param

                type_char, name, short_descr, long_descr = configure_iface.GetParameterInfo(['engine', param])
                configure_iface.ResetParameterValue(['engine', param])
            elif arg == 'il':
                print "--- internals list"
                is_leaf, internals = configure_iface.ReadContainer(['internals'])
                for internal in internals:
                    print internal
            elif arg == 'ip':
                print "--- get internal parameters (type:isset:default:value)"

                if index >= len(sys.argv):
                    print "internal parameters command requires internal name argument"
                    sys.exit()

                internal_name = sys.argv[index]
                index += 1

                get_parameters(configure_iface, ['internals', internal_name])
            elif arg == 'ipd':
                if index + 1 >= len(sys.argv):
                    print "get internal parameter long description command requires internal and parameter name arguments"
                    sys.exit()

                name = sys.argv[index]
                index += 1
                param = sys.argv[index]
                index += 1

                print "--- get internal parameter description (%s)" % param
                type_char, name, short_descr, long_descr = configure_iface.GetParameterInfo(['internals', name, param])
                print long_descr
            elif arg == 'ips':
                if index + 2 >= len(sys.argv):
                    print "internal parameter set command requires internal, parameter name and value arguments"
                    sys.exit()

                internal_name = sys.argv[index]
                index += 1
                param = sys.argv[index]
                index += 1
                value = sys.argv[index]
                index += 1

                print "--- internal param set \"%s\" -> \"%s\"" % (param, value)

                type_char, name, short_descr, long_descr = configure_iface.GetParameterInfo(['internals', internal_name, param])
                configure_iface.SetParameterValue(['internals', internal_name, param], python_type_to_jackdbus_type(value, type_char))
            elif arg == 'ipr':
                if index + 1 >= len(sys.argv):
                    print "reset internal parameter command requires internal and parameter name arguments"
                    sys.exit()

                internal_name = sys.argv[index]
                index += 1
                param = sys.argv[index]
                index += 1

                print "--- internal param reset \"%s\"" % param

                configure_iface.ResetParameterValue(['internals', internal_name, param])
            elif arg == 'iload':
                print "--- load internal"

                if index >= len(sys.argv):
                    print "load internal command requires internal name argument"
                    sys.exit()

                name = sys.argv[index]
                index += 1
                result = control_iface.LoadInternal(name)
            elif arg == 'iunload':
                print "--- unload internal"

                if index >= len(sys.argv):

                    print "unload internal command requires internal name argument"
                    sys.exit()

                name = sys.argv[index]
                index += 1
                result = control_iface.UnloadInternal(name)
            elif arg == 'asd':
                print "--- add slave driver"

                if index >= len(sys.argv):
                    print "add slave driver command requires driver name argument"
                    sys.exit()

                name = sys.argv[index]
                index += 1
                result = control_iface.AddSlaveDriver(name)
            elif arg == 'rsd':
                print "--- remove slave driver"

                if index >= len(sys.argv):
                    print "remove slave driver command requires driver name argument"
                    sys.exit()

                name = sys.argv[index]
                index += 1
                result = control_iface.RemoveSlaveDriver(name)
            else:
                print "Unknown command '%s'" % arg
        except dbus.DBusException, e:
            print "DBus exception: %s" % str(e)'''



#    def configure(self, *args):
#        pass


def bool_convert(str_value):
    if str_value.lower() == "false":
        return False

    if str_value.lower() == "off":
        return False

    if str_value.lower() == "no":
        return False

    if str_value == "0":
        return False

    if str_value.lower() == "(null)":
        return False

    return bool(str_value)

def dbus_type_to_python_type(dbus_value):
    if type(dbus_value) == dbus.Boolean:
        return bool(dbus_value)
    if type(dbus_value) == dbus.Int32 or type(dbus_value) == dbus.UInt32:
        return int(dbus_value)
    return dbus_value

def python_type_to_jackdbus_type(value, type_char):
    type_char = str(type_char)

    if type_char == "b":
        return bool_convert(value);
    elif type_char == "y":
        return dbus.Byte(value);
    elif type_char == "i":
        return dbus.Int32(value)
    elif type_char == "u":
        return dbus.UInt32(value)

    return value

def dbus_type_to_type_string(dbus_value):
    if type(dbus_value) == dbus.Boolean:
        return "bool"
    if type(dbus_value) == dbus.Int32:
        return "sint"
    if type(dbus_value) == dbus.UInt32:
        return "uint"
    if type(dbus_value) == dbus.Byte:
        return "char"
    if type(dbus_value) == dbus.String:
        return "str"

    return None                         # throw exception here?

def dbus_typesig_to_type_string(type_char):
    type_char = str(type_char)
    if type_char == 'i':
        return "sint"
    if type_char == 'u':
        return "uint"
    if type_char == 'y':
        return "char"
    if type_char == 's':
        return "str"
    if type_char == 'b':
        return "bool"

    print 'shit'
    return None                         # throw exception here?

