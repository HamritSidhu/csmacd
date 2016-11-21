import MD1Queue
import RandomGenerator
import random
import Packet
import math
from enum import Enum

class State(Enum):
    Idle = 1
    ReadyToTransmit = 2
    Transmitting = 3
    ExponentialBackoff = 4
    Defer = 5


class BinaryExponentialBackoff:
    def __init__(self, W, tickDuration):
        self.iteration = 0
        self.Tp = 512*1.0/W/tickDuration
        self.Tb = 0
        self.isWaiting = False

    def beginBackoffIteration(self):
        R = random.randint(0, (math.pow(2, self.iteration))-1)
        if R is 0:
            R = 1
        self.Tb = int(round(R*self.Tp))
        # print "self Tb : %s" % self.Tb
        self.isWaiting = True

    def wait(self):
        if self.isWaiting:
            if self.Tb > 0:
                self.Tb -= 1
            else:
                self.isWaiting = False
        else:
            self.iteration += 1
            if self.iteration < 10:
                self.beginBackoffIteration()
            else:
                raise Exception()

    def isBackoffWaitComplete(self):
        return not self.isWaiting

    def reset(self):
        self.iteration = 0


class Node:
    def __init__(self, position, A, L, W, tickDuration):
        self.position = position
        self.state = State.Idle
        self.arrivalRate = A
        self.nextArrivalTick = RandomGenerator.randomExponential(A, tickDuration)
        self.currentServicePacket = None
        self.serviceTime = L*1.0/W/tickDuration
        self.tickDuration = tickDuration
        self.queue = MD1Queue.MD1Queue()
        self.exponentialBackOff = BinaryExponentialBackoff(W, tickDuration)
        self.waitDuration = 0

    def process_queue(self, currentTick):
        # if at currentArrivalTick, create a new packet and enqueue
        if currentTick == self.nextArrivalTick:
            newPacket = Packet.Packet(currentTick)
            self.queue.enqueue(newPacket)
            self.nextArrivalTick += RandomGenerator.randomExponential(self.arrivalRate, self.tickDuration)

        # checks if there is a packet ready to transmit
        if self.currentServicePacket is None:
            currentServicePacket = self.queue.dequeue()
            if currentServicePacket is not None:
                self.state = State.ReadyToTransmit
                self.currentServicePacket = currentServicePacket
            else:
                self.state = State.Idle

    def backoffWait(self):
        try:
            self.exponentialBackOff.wait()
        except Exception:
            self.dropPacket()
            self.state = State.Idle
            self.exponentialBackOff.reset()

    def fixedWait(self):
        self.waitDuration -= 1

    def dropPacket(self):
        self.currentServicePacket = None
        self.State = State.Idle

    def beginPacketTransmission(self, currentTick):
        self.state = State.Transmitting
        self.currentServicePacket.beginService(currentTick)

    def transmit(self, currentTick):
        if self.currentServicePacket.hasLeft:
            # packet complete
            # print "packet complete"
            self.currentServicePacket = None
            self.state = State.Idle
            self.exponentialBackOff.reset()
        else:
            self.currentServicePacket.process(currentTick, self.serviceTime)
