#!/usr/bin/python
import argparse
import serial
import threading
from antaus.package import *

antaus_errors = {
1: "NOT_AVAILABLE",
2: "VAR_UNKNOWN",
3: "BAD_PACKET_FORMAT",
4: "VAR_OUT_OF_BOUNDS",
5: "UNKNOWN_COMMAND"
}

antaus_vars = {
1: ("FAULT_CODE", "U16", False),
2: ("OUT_POWER", "F4", False),
3: ("LOCK_STATE", "U16", False),
5: ("SHUTTER", "U16", True),
6: ("POWER_TRIM", "U16", True),
8: ("TRIG_LEVEL", "F4", True),
9: ("TRIG_COUPLING", "U16", True),
10: ("TRIG_ATT", "U16", True),
11: ("TRIG_TERM", "U16", True),
12: ("FULL_RUN", "U16", True),
16: ("TRIG_MODE","U16", True),
17: ("BASE_DIVIDER","U16", True),
18: ("REF_FREQ","F4",False),
19: ("BASE_FREQ","F4",False),
20: ("BASE_DIVIDER_MIN","U16", False),
21: ("BASE_DIVIDER_MAX","U16", False),
22: ("OUT_DIVIDER","U16", True),
23: ("OUT_BURST","U16", True),
60: ("PULSE_DURATION","I16", True),
}

var_commands = {}
for cid in antaus_vars:
    var_commands[antaus_vars[cid][0]] = cid

antaus_states = {
0x0001: "STATE_STOP",
0x0002: "STATE_READY_TO_RUN",
0x0004: "STATE_PRE_RUN",
0x0008: "STATE_RUN",
0x0010: "STATE_PREP_FOR_STOP",
0x0020: "STATE_FAULT",
0x0040: "STATE_TEST_RUN",
0x0080: "STATE_INIT",
}

def packet_desc(packet):
    if packet.cmd == COMMANDS.error:
        err_string = antaus_errors[packet.cid] if packet.cid in antaus_errors.keys() else "???"
        return "ERROR(%d):%s"%(packet.cid, err_string)
    if packet.cmd == COMMANDS.ping:
        return "PING"
    if packet.cmd == COMMANDS.dev_run:
        return "DEV_RUN"
    if packet.cmd == COMMANDS.dev_stop:
        return "DEV_STOP"
    if packet.cmd == COMMANDS.dev_fault_reset:
        return "DEV_FAULT_RESET"
    if packet.cmd == COMMANDS.dev_eeprom:
        return "DEV_EEPROM"
    if packet.cmd == COMMANDS.dev_state_info:
        state = packet.parse_state()
        if state in antaus_states:
            state_name = antaus_states[state]
        else:
            state_name = "Unknown state"
        return "DEV_STATE_INFO 0x%04x(%s)"%(state,state_name)
    if packet.cmd == COMMANDS.var_value:
        if packet.cid in antaus_vars.keys():
            var_name = antaus_vars[packet.cid][0]
        else:
            var_name = "unkn"
        var_value = packet.parse_val()
        return "VAR_VALUE %d(%s) = %s"%(packet.cid, var_name, str(var_value))
    return "UNKN"

def serial_reader(com, killswitch):
    parser = serial_parser()
    while True:
        data = com.read()
        for c in data:
            packet = parser.parse(c)
            if packet:
                print ("RX:", "[" ,binascii.hexlify(packet.serialize()),"]", packet, packet_desc(packet))
        if killswitch.is_set():
            break

def cmd_send(com,pkt):
    print ("TX:", pkt, "[", binascii.hexlify(pkt.serialize()), "]")
    com.write(pkt.serialize())

def CONTROL(command):
    dev_addr = 0x100
    dev_bus = 0

#    parser = argparse.ArgumentParser()
#    parser.add_argument('-c','--com',type=str,required=True,help="COM port")
#    args = parser.parse_args()

    com_name = "COM8"
    com = serial.Serial(com_name,baudrate=9600,timeout=0.3)
 
# serial port reader thred
    serial_reader_killswitch = threading.Event()
    serial_reader_th = threading.Thread( target=serial_reader, args=(com, serial_reader_killswitch) )
    serial_reader_th.start()


#        command = input().split()

    if len(command)<1:
        print('Unknown command!')

#        print("command:",command)

    if command[0].upper() == 'EXIT':
        serial_reader_killswitch.set()
        serial_reader_th.join()
        com.close()

    if command[0].upper() == 'PING':
        cmd_send(com, sproto_packet(dev_bus, dev_addr, COMMANDS.ping, 0))

    if command[0].upper() == 'STATE':
        cmd_send(com, sproto_packet(dev_bus, dev_addr, COMMANDS.dev_get_state_info, 0))

    if command[0].upper() == 'RUN':
        cmd_send(com, sproto_packet(dev_bus, dev_addr, COMMANDS.dev_set_run, 0))

    if command[0].upper() == 'STOP':
        cmd_send(com, sproto_packet(dev_bus, dev_addr, COMMANDS.dev_set_stop, 0))

    if command[0].upper() == 'FAULT_RESET':
        cmd_send(com, sproto_packet(dev_bus, dev_addr, COMMANDS.dev_set_fault_reset, 0))

    if command[0].upper() in var_commands:
        cid = var_commands[command[0].upper()]

        if len(command)<2 or command[1]=="?":
            cmd_send(com, sproto_packet(dev_bus, dev_addr, COMMANDS.get_var_value, cid))
        else:
            (var_name, var_type, var_writable) = antaus_vars[cid]
            if not var_writable:
                print (command[0].upper(),"is read-only var")
            else:
                try:
                    if var_type == "F4":
                        val = float(command[1])
                    else:
                        val = int(command[1])
                    pk = sproto_packet(dev_bus, dev_addr, COMMANDS.set_var_value, cid)
                    pk.pack_value(var_type, val)
                    cmd_send(com, pk)
                except:
                    print ("Local error executing command")

    # else:
    #     print ("Unknown command!")

# cleanup
    serial_reader_killswitch.set()
    serial_reader_th.join()
    com.close()