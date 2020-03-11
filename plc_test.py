import fins.udp
import time

finsInst=fins.udp.UDPFinsConnection()
finsInst.connect("192.168.3.10")
finsInst.dest_node_add=10
finsInst.srce_node_add=25

#mem_area=finsInst.memory_area_read(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x00\xc8\x00',10)
mem_area=finsInst.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x00\x00\x00',b'\xff\xff',1)
print("--- FINS HEADER---")
for i in range(0,10):
    print("HEAD(%d): %x" % (i,mem_area[i]))
print("--- COMMAND/RESPONSE CODE---")
for i in range(10,14):
    print("RESP(%d): %x" % (i,mem_area[i]))
print("--- PAYLOAD---")
for i in range(14,len(mem_area)):
    print("DATA(%d): %x" % (i,mem_area[i]))
print("yahhoo!")

