from os import path

''' constants '''
NAME_OF_THE_FILE="messages.txt"
END_OF_PACKET='\n'

PACKET_FOR_LESYA="end"

''' main function '''
def main(PathToFile=NAME_OF_THE_FILE):

    packets = ReadFromFile(PathToFile)
    dictionary = PacketsToDictionary(packets)

    for item in dictionary:
        NewFile(item + ".txt", dictionary[item])

''' function to read data (packets) from the file '''
def ReadFromFile(PathToFile):

    if not path.isfile(PathToFile):
        return
    else:
        f = open(PathToFile, 'r')
        return f.readlines()

''' function to separete packets among receivers '''
''' this function calls another function 'GetReceiver' to know receiver (-s) which need this packet '''
''' then all the data (packets) appends to the dictionary to the appropriate receiver ''' 
def PacketsToDictionary(packets):

    dict = {'I': [], 'D': [], 'O': [], 'L': []}

    for packet in packets:
        receivers = GetReceiver(packet.strip(END_OF_PACKET))
        if receivers:
            for receiver in receivers:
                dict[receiver].append(packet)

    return dict

''' function to get the appropriate receiver'''
def GetReceiver(packet):

    receivers = []

    if not packet:
        return

    if packet.split()[-1] == PACKET_FOR_LESYA:
        receivers.append('L')

    if len(packet) % 2 == 0:
        receivers.append('I')
    elif packet[0].isupper():
        receivers.append('D')
    elif not receivers:
        receivers.append('O')

    return receivers

''' function to create new files for all receivers '''
def NewFile(PathToFile, packets):

    file = open(PathToFile, 'w')
    file.writelines(packets)

if __name__ == "__main__":
    main()