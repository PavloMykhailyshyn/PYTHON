from sys import argv
from c_code import ReadData
import re
import json
import scapy.all as scapy
import threading

# receiver`s name

IVAN    = 0
DMYTRO  = 1
OSTAP   = 2
LESYA   = 3

# global constants

UDP_PROTOCOL        = "udp"
UDP_PORT            =  5555

END_OF_PACKET       = '\n'
PACKET_FOR_LESYA    = "end"

DEFAULT_TIMEOUT     =  1

DECODE_FORMAT       = "utf-8"
RECEIVER_FILE       = "receivers.json"

NUM_OF_INPUT_ARGS   =  2

EXIT_SUCCESS        =  0
EXIT_FAILURE        = -1

FILE_NAME_ARG       =  1

# regular expressions

LEN_REGEXP          = '^([^END_OF_PACKET]{2})+$'
FIRST_UPPER_REGEXP  = '^[A-Z]+.*?$'
LAST_WORD_REGEXP    = '^.*?\s{}$'

def packet_parser(packets, receivers):
    """ parsing @packets to all @receivers """
    for packet in packets:

        if re.match(LAST_WORD_REGEXP.format(PACKET_FOR_LESYA), packet):
            receivers[LESYA].append_packet(packet)

        if re.match(LEN_REGEXP, packet):
            receivers[IVAN].append_packet(packet)
            continue
        elif re.match(FIRST_UPPER_REGEXP, packet):
            receivers[DMYTRO].append_packet(packet)
            continue

        receivers[OSTAP].append_packet(packet)

    return receivers

def read_ip_addr(file_name):
    """ reading @ip from json file """
    with open(file_name) as ip_file:
        json_data = json.load(ip_file)
        return json_data

def get_packets(file_name):
    """ getting all data from file (our @packets) """
    packets = []
    packets = [ line for line in (ReadData(file_name)).split(END_OF_PACKET) if line != '' ]
    return packets

class Receiver:
    """ class which stores all data for every @receiver """
    __receiver_name = ""
    __receiver_ip = ""

    def __init__(self, name, ip):

        self.__receiver_name = name
        self.__receiver_ip = ip
        self.__receiver_packets = []

    def append_packet(self, packet):

        self.__receiver_packets.append(packet)

    def __ping(self):

        answer, no_answer = scapy.sr(
            scapy.IP(dst = self.__receiver_ip) / scapy.ICMP(),
            timeout = DEFAULT_TIMEOUT,
            verbose = False)
        return bool(answer)

    def __sniff_packets(self, packet):

        msg = packet.getlayer(scapy.Raw).load.decode(DECODE_FORMAT)
        caught_packtes = scapy.sniff(filter = UDP_PROTOCOL, timeout = DEFAULT_TIMEOUT)
        for packet in caught_packtes:
            packet_load = packet.getlayer(scapy.Raw).load

            if packet.getlayer(scapy.IP).dst == self.__receiver_ip and \
                            packet_load.decode(DECODE_FORMAT) == msg:
                print('Sent \'{}\' to {}'.format(msg, self.__receiver_name))
            else:
                print('Wasn\'t sent \'{}\' to {}'.format(msg, self.__receiver_name))

    def send_packets(self):

        for packet in self.__receiver_packets:
            if self.__ping():
                packet = scapy.IP(dst = self.__receiver_ip) / scapy.UDP(sport = UDP_PORT, dport = UDP_PORT)
                packet.payload = END_OF_PACKET.join(self.__receiver_packets)
                thread = threading.Thread(target=self.__sniff_packet, args = (packet,))
                thread.start()
                scapy.send(packet)
                thread.join()
            else:
                print "Receiver {} not response (ip: {})".format(self.__receiver_name,
                                                             self.__receiver_ip)

def main():

    if len(argv) != NUM_OF_INPUT_ARGS:
        return EXIT_FAILURE

    file_name = argv[FILE_NAME_ARG]

    json_data = read_ip_addr(RECEIVER_FILE)

    receivers = []
    for receiver in json_data.items():
        name, ip = receiver
        receivers.append(Receiver(name.encode(DECODE_FORMAT), ip.encode(DECODE_FORMAT)))

    packets = get_packets(file_name)
    packet_parser(packets, receivers)

    for receiver in receivers:
        receiver.send_packets()

    return EXIT_SUCCESS

if __name__ == "__main__":
    main()