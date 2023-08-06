import binascii
import struct

crc7_syndrome_table = [
	0x00, 0x09, 0x12, 0x1b, 0x24, 0x2d, 0x36, 0x3f,
	0x48, 0x41, 0x5a, 0x53, 0x6c, 0x65, 0x7e, 0x77,
	0x19, 0x10, 0x0b, 0x02, 0x3d, 0x34, 0x2f, 0x26,
	0x51, 0x58, 0x43, 0x4a, 0x75, 0x7c, 0x67, 0x6e,
	0x32, 0x3b, 0x20, 0x29, 0x16, 0x1f, 0x04, 0x0d,
	0x7a, 0x73, 0x68, 0x61, 0x5e, 0x57, 0x4c, 0x45,
	0x2b, 0x22, 0x39, 0x30, 0x0f, 0x06, 0x1d, 0x14,
	0x63, 0x6a, 0x71, 0x78, 0x47, 0x4e, 0x55, 0x5c,
	0x64, 0x6d, 0x76, 0x7f, 0x40, 0x49, 0x52, 0x5b,
	0x2c, 0x25, 0x3e, 0x37, 0x08, 0x01, 0x1a, 0x13,
	0x7d, 0x74, 0x6f, 0x66, 0x59, 0x50, 0x4b, 0x42,
	0x35, 0x3c, 0x27, 0x2e, 0x11, 0x18, 0x03, 0x0a,
	0x56, 0x5f, 0x44, 0x4d, 0x72, 0x7b, 0x60, 0x69,
	0x1e, 0x17, 0x0c, 0x05, 0x3a, 0x33, 0x28, 0x21,
	0x4f, 0x46, 0x5d, 0x54, 0x6b, 0x62, 0x79, 0x70,
	0x07, 0x0e, 0x15, 0x1c, 0x23, 0x2a, 0x31, 0x38,
	0x41, 0x48, 0x53, 0x5a, 0x65, 0x6c, 0x77, 0x7e,
	0x09, 0x00, 0x1b, 0x12, 0x2d, 0x24, 0x3f, 0x36,
	0x58, 0x51, 0x4a, 0x43, 0x7c, 0x75, 0x6e, 0x67,
	0x10, 0x19, 0x02, 0x0b, 0x34, 0x3d, 0x26, 0x2f,
	0x73, 0x7a, 0x61, 0x68, 0x57, 0x5e, 0x45, 0x4c,
	0x3b, 0x32, 0x29, 0x20, 0x1f, 0x16, 0x0d, 0x04,
	0x6a, 0x63, 0x78, 0x71, 0x4e, 0x47, 0x5c, 0x55,
	0x22, 0x2b, 0x30, 0x39, 0x06, 0x0f, 0x14, 0x1d,
	0x25, 0x2c, 0x37, 0x3e, 0x01, 0x08, 0x13, 0x1a,
	0x6d, 0x64, 0x7f, 0x76, 0x49, 0x40, 0x5b, 0x52,
	0x3c, 0x35, 0x2e, 0x27, 0x18, 0x11, 0x0a, 0x03,
	0x74, 0x7d, 0x66, 0x6f, 0x50, 0x59, 0x42, 0x4b,
	0x17, 0x1e, 0x05, 0x0c, 0x33, 0x3a, 0x21, 0x28,
	0x5f, 0x56, 0x4d, 0x44, 0x7b, 0x72, 0x69, 0x60,
	0x0e, 0x07, 0x1c, 0x15, 0x2a, 0x23, 0x38, 0x31,
	0x46, 0x4f, 0x54, 0x5d, 0x62, 0x6b, 0x70, 0x79
]

def crc7(init, bfr):
    crc = init
    for c in bfr:
        idx = ((crc<<1) ^ c) & 0xFF
        crc = crc7_syndrome_table[idx]
    return crc


class COMMANDS:
    error = 8

    get_var_value = 42
    var_value = 43
    set_var_value = 52

    ping = 91

    dev_set_run = 93
    dev_run = 94
    dev_set_stop = 95
    dev_stop = 96

    dev_get_state_info = 99
    dev_state_info = 100

    dev_set_fault_reset = 103
    dev_fault_reset = 104

    dev_set_eeprom = 105
    dev_eeprom = 106 

    impulse = 160
    impulse_response = 161



class sproto_packet:
    def __init__ (self,ch=0,addr=0,cmd=0,cid=0,cdata=b''):
        self.ch = ch
        self.addr = addr
        self.cmd = cmd
        self.cid = cid
        self.cdata = cdata

        
    def __str__ (self):
        return "<packet: ch:%d addr:0x%x cmd:%d cid:%d cdata:%s>"%(self.ch,self.addr,self.cmd,self.cid,binascii.hexlify(self.cdata) if self.cdata else 'NONE')

    def unserialize(self,string):
        dt = string # [ord(x) for x in string]

        m =    [ dt[1+0] | (0x80 if (dt[8] & (1<<0)) else 0) ] # ch
        m +=   [ dt[1+1] | (0x80 if (dt[8] & (1<<1)) else 0) ] # sz
        m +=   [ dt[1+2] | (0x80 if (dt[8] & (1<<2)) else 0) ] # addr 
        m +=   [ dt[1+3] | (0x80 if (dt[8] & (1<<3)) else 0) ] # addr 
        m +=   [ dt[1+4] | (0x80 if (dt[8] & (1<<4)) else 0) ] # addr
        m +=   [ dt[1+5] | (0x80 if (dt[8] & (1<<5)) else 0) ] # addr 
        m +=   [ dt[1+6] | (0x80 if (dt[8] & (1<<6)) else 0) ] # cdata

        m +=   [ dt[9+0] | (0x80 if (dt[16] & (1<<0)) else 0) ] # cdata
        m +=   [ dt[9+1] | (0x80 if (dt[16] & (1<<1)) else 0) ] # cdata
        m +=   [ dt[9+2] | (0x80 if (dt[16] & (1<<2)) else 0) ] # cdata
        m +=   [ dt[9+3] | (0x80 if (dt[16] & (1<<3)) else 0) ] # cdata
        m +=   [ dt[9+4] | (0x80 if (dt[16] & (1<<4)) else 0) ] # cdata
        m +=   [ dt[9+5] | (0x80 if (dt[16] & (1<<5)) else 0) ] # cdata
        m +=   [ dt[9+6] | (0x80 if (dt[16] & (1<<6)) else 0) ] # cdata

        m = bytes(m) # "".join([chr(x) for x in m])
        (self.ch,sz,self.cid,self.cmd,self.addr,self.cdata) = struct.unpack("<BBBBH8s",m)
        self.cdata = self.cdata[0:sz]

    def serialize(self):
        def hibits (s):
            bin = "".join(['1' if x&0x80 else '0' for x in s])
            return int(bin[::-1],2)
        s = struct.pack("<BBBBH8s",self.ch,len(self.cdata),self.cid,self.cmd,self.addr,self.cdata.ljust(8,b'\xaa'))
        m = bytes([213])
        m += bytes([(x&0x7f) for x in s[0:7]]  + [hibits(s[0:7])])
        m += bytes([(x&0x7f) for x in s[7:14]] + [hibits(s[7:14])])
        m += bytes([crc7(213,m)])
        return m

    def parse_val(self):
        if len(self.cdata)!=6: 
            return None

        (var_type,dec_pow,bin) = struct.unpack("<BB4s",self.cdata)
        if var_type == 3: #s16
            fmt = '<h'
        elif var_type == 4: #u16
            fmt = '<H'
        elif var_type == 7: #f4
            fmt = '<f'
        elif var_type == 5: #u32
            fmt = '<l'
        elif var_type == 6: #u32
            fmt = '<L'
        else:
            fmt = None

        if fmt:
            value = struct.unpack(fmt,bin[0:struct.calcsize(fmt)])[0]
        else:
            value = None

        return value

    def parse_state(self):
        return struct.unpack("<H", self.cdata[0:2])[0]

    def pack_value(self,fmt,value):
        if fmt == "U8":
            self.cdata = struct.pack("<BBB",2,0,value).ljust(6)
        elif fmt == "I8":
            self.cdata = struct.pack("<BBb",1,0,value).ljust(6)
        elif fmt == "U16":
            self.cdata = struct.pack("<BBH",4,0,value).ljust(6)
        elif fmt == "I16":
            self.cdata = struct.pack("<BBh",3,0,value).ljust(6)
        elif fmt == "U32":
            self.cdata = struct.pack("<BBL",6,0,value).ljust(6)
        elif fmt == "I32":
            self.cdata = struct.pack("<BBl",5,0,value).ljust(6)
        elif fmt == "F4":
            self.cdata = struct.pack("<BBf",7,0,value).ljust(6)


class serial_parser:
    def parser_wait_head(self,c):
        self.parser_data = b''
        if c == 213:
            self.parser_data += bytes([c])
            return (self.parser_collect_data, None)
        else:
            return (self.parser_wait_head, None)

    def parser_collect_data(self,c):
        if (c & 0x80):
            return (self.parser_wait_head,None)
        self.parser_data += bytes([c])
        if len(self.parser_data) == 17:
            return (self.parser_check_crc,None)
        else:
            return (self.parser_collect_data,None)

    def parser_check_crc(self,c):
        if crc7(213,self.parser_data) == c:
            return (self.parser_wait_head,self.parser_data)
        else:
            return (self.parser_wait_head,None)

    def parse(self,c):
        (self.parser,packet) = self.parser(c)
        #return self.unpack_7bit(packet)
        if packet:
            pk = sproto_packet()
            pk.unserialize(packet)
            return pk
        return None

    def __init__ (self):
        self.parser = self.parser_wait_head
        self.parser_data = b''


