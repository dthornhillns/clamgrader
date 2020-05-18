import fins.udp
import os

# fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD,address,bytes,1)
# mem_area[0] = fins_instance.memory_area_read(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD,address)


# get PLCIP from user
PLCIP = '192.168.251.1'

# these next few lines is just an algorithm for windows to get the ethernet ip of your computer so it can get the node from it
#os.system('cmd /c "ipconfig > C:/Users/Public/Documents/ipconfig.txt"')
#ipconfig = open("C:/Users/Public/Documents/ipconfig.txt", "r")
word = str()
charcnt = 0
COMPIP = "192.168.251.10"
checkip = False

# break the IP's apart to get the nodes from them
PLCNODE = int(PLCIP.split(".")[3])
COMPNODE = int(COMPIP.split(".")[3])

# init fins connection
fins_instance = fins.udp.UDPFinsConnection()
# plc ip to connect to
fins_instance.connect(PLCIP)
# last number in the ip of each device
fins_instance.dest_node_add = PLCNODE
fins_instance.srce_node_add = COMPNODE

# init spl with gas variable
spl = 2
# clear the message that may or may not be used
message = [0, 0, 0, 0]
while spl != 3:
    # prompt user for decision
    spl = input("0=Read, 1=Write, 2=Clear, 3=Leave: ")
    spl = int(spl)
    # cases
    # if user wants to read from registers
    if spl == 0:
        # prompt amount to read
        length = input("How many registers would you like to read? ")
        # for the amount to read
        for i in range(int(length)):
            # calculate address starting at 0
            address = bytes(1) + bytes([i]) + bytes(1)
            # read from memory
            i = fins_instance.memory_area_read(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD, address)
            # print it
            print(i[14] * 256 + i[15], end=' ')
        print('\n')

    # if user wants to write to memory
    if spl == 1:
        # prompt for classification
        boo = input("Classification= ")
        # convert to word (high byte, low byte) and add to message
        message[3] = bytes(1) + bytes([int(boo)])
        print("Integer inputs should less than or equal to 65535")
        # prompt user for value
        # area = input("Area= ")
        area = 500
        # convert to high and low byte
        area = [int(int(area) / 256), int(int(area) % 256)]
        # add to message
        message[0] = bytes([area[0]]) + bytes([area[1]])
        # repeat process for data needed
        x = input("X= ")
        x = [int(int(x) / 256), int(int(x) % 256)]
        message[1] = bytes([x[0]]) + bytes([x[1]])
        y = input("Y= ")
        y = [int(int(y) / 256), int(int(y) % 256)]
        message[2] = bytes([y[0]]) + bytes([y[1]])
        # for message
        for i in range(len(message)):
            # calculate address
            address = bytes(1) + bytes([i]) + bytes(1)
            # write to memory
            fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD, address, message[i], 1)
    # if user wants to clear the memory
    if spl == 2:
        # for the 45 chosen registers
        for i in range(0, 45):
            # get address
            address = bytes(1) + bytes([i]) + bytes(1)
            # write 0 to address
            fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD, address, b'\x00\x00', 1)
print("Goodbye")
# end of program
