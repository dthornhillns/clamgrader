import time
from threading import Thread
import fins.udp
import struct
import array


class PlcIntegration:

    def __init__(self, pollTime, ip, destNode, srcNode):
        self.stopped = False
        self.pollTime = pollTime
        self.targetsRequested = False
        self.finsInstance = fins.udp.UDPFinsConnection()
        self.finsInstance.connect(ip)
        self.finsInstance.dest_node_add = destNode
        self.finsInstance.srce_node_add = srcNode

    def start(self):
        Thread(target=self.doWork, args=()).start()
        return self

    def doWork(self):

        while not self.stopped:
            self.targetsRequested = self.isPlcRequestingTargets()
            time.sleep(self.pollTime)

    def stop(self):
        self.stopped = True

    def isPlcRequestingTargets(self):
        mem_area = self.finsInstance.memory_area_read(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD, b'\x00\xc8\x00', 1)
        print("%d %s" %(int(mem_area[15]),bool(mem_area[15])))
        return bool(mem_area[15])
        #return False

    def sendTargets(self, clamTargets):
        buffer = bytearray()

        for target in clamTargets:
            targetStruct=struct.pack(">hhhh",
                                      target.classification,
                                      int(target.areaSquareMm),
                                      target.x,
                                      target.y
                                      )
            buffer+=targetStruct

        size = int(len(buffer)/2)
        mem_area = self.finsInstance.memory_area_write(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD, write_bytes=buffer, number_of_items=size)