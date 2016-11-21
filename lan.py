import model
import math
import random
import multiprocessing
import sys

tickDuration = 0.00000005
TICKS = 200000000

def p_persistent_csmacd(p, nodes, non_persistent=False):
    collision_count = 0
    completed_packets = []
    transmitting_nodes = []
    for i in range(0, TICKS):
        # print "--------Transmitting Nodes at TICK %s --------" % i
        # for n in transmitting_nodes:
        #     print n.currentServicePacket.startTick
        # print "----------------------------------------------"
        for n in nodes:
            mediumFree = isMediumFree(transmitting_nodes, n, i)
            # handles the packet arrivals to Node's MD1 queue
            n.process_queue(i)
            if n.state == model.State.ReadyToTransmit:
                if mediumFree:
                    pOutcome = random.uniform(0, 1)
                    print pOutcome
                    print pOutcome < p
                    if pOutcome < p or p is 1:
                        # print "Overcome probability"
                        # print "Node %s went through at tick %s" % (n.position, i)
                        # go ahead and transmit
                        n.state = model.State.Transmitting
                        n.beginPacketTransmission(i)
                        transmitting_nodes.append(n)
                    else:
                        # Defer Transmission
                        n.state = model.State.Defer
                        n.waitDuration = 5  # default to 5 ticks - confirm if this is ok
                else:
                    if non_persistent:
                        n.state = model.State.ExponentialBackoff
            elif n.state == model.State.Defer:
                # print "waiting for %s more ticks..." % n.waitDuration
                if n.waitDuration == 0:
                    if mediumFree:
                        n.state = model.State.ReadyToTransmit
                    else:
                        n.state = model.State.ExponentialBackoff
                else:
                    n.fixedWait()
            elif n.state == model.State.ExponentialBackoff:
                n.backoffWait()

                if n.exponentialBackOff.isBackoffWaitComplete():
                    n.state = model.State.ReadyToTransmit

            elif n.state == model.State.Transmitting:
                transmittingPacket = n.currentServicePacket
                n.transmit(i)

                # transmission complete
                if n.state == model.State.Idle:
                    print "transmission complete"
                    completed_packets.append(transmittingPacket)
                    transmitting_nodes.remove(n)

            else:
                # do nothing if packet in idle state
                pass

        collision = detectCollision(transmitting_nodes, i)

        # if there is a collision, we want to put all the transmitting nodes
        # in exponential backoff
        if collision:
            for n in transmitting_nodes:
                n.state = model.State.ExponentialBackoff

            collision_count += 1
            transmitting_nodes = []

    print "Number of completed packets: %s" % len(completed_packets)
    print "Number of collisions: %s" % collision_count
    if len(completed_packets) > 0:
        throughput = len(completed_packets) * 1500 * 8 * 1.0 / TICKS

        totalDelay = 0
        for pk in completed_packets:
            totalDelay += pk.completionTime

        avgDely = totalDelay * 1.0 / len(completed_packets)

    else:
        throughput = None
        avgDely = None

    print "Throughput: %s" % throughput
    print "Average Delay: %s" % avgDely


def detectCollision(tNodes, currentTick):
    for k in range(0, len(tNodes) - 1):
        propDelay = getPropagationDelay(tNodes[k], tNodes[k + 1])
        # print "Propagation Delay: %s" % propDelay

        pTime1 = currentTick - tNodes[k].currentServicePacket.startTick
        pTime2 = currentTick - tNodes[k + 1].currentServicePacket.startTick

        # print "processing time node 1: %s" % pTime1
        # print "processing time node 2: %s" % pTime2

        if isProcessingTimeLongerThanPropogationDelay(propDelay, pTime1) or isProcessingTimeLongerThanPropogationDelay(propDelay, pTime2):
            print "collision"
            return True
    # no collision was detected
    return False


def isMediumFree(tNodes, currentNode, currentTick):
    for tNode in tNodes:
        propagationDelay = getPropagationDelay(tNode, currentNode)
        processTime = currentTick - tNode.currentServicePacket.startTick
        if isProcessingTimeLongerThanPropogationDelay(propagationDelay, processTime):
            return False

    return True


def isProcessingTimeLongerThanPropogationDelay(propagationDelay, processingTime):
    # let's check the equal sign condition!!!!
    return processingTime >= propagationDelay


def getPropagationDelay(node1, node2):
    return abs((node2.position - node1.position) * 10.0 / (2 * math.pow(10, 8)) / tickDuration)


def InitializeNodes(A, N, W, L):
    nodeList = []
    for i in range(0, N):
        n = model.Node(i, A, L, W, tickDuration)
        nodeList.append(n)

    return nodeList


def main():
    # non_persistent_pool()
    p_persistent_pool()
    # tests()

def p_persistent_pool():
    params = [2 , 4]

    p = multiprocessing.Pool(5)
    p.map(p_persistent_call, params)

def p_persistent_call(a):
    sys.stdout = open("P_Persistent_%s_pac_sec.txt" % a, "w")
    W = 1000000
    L = 1500 * 8
    N = 30
    nodes = InitializeNodes(a, N, W, L)
    print "P_PERSISTENT: N = %s, A = %s " % (N, a)
    p_persistent_csmacd(1, nodes)
    sys.stdout.close()

def non_persistent_pool():
    params = [60]

    p = multiprocessing.Pool(5)
    p.map(non_persistent_call, params)


def non_persistent_call(N):
    sys.stdout = open("Non_Persistent_%s.txt" % N, "w")
    W = 1000000
    L = 1500 * 8
    a = 20
    nodes = InitializeNodes(a, N, W, L)
    print "NON_PERSISTENT: N = %s, A = %s " % (N, a)
    p_persistent_csmacd(1, nodes, True)
    sys.stdout.close()

def p_persistent():
    N = 30
    W = 1000000
    L = 1500 * 8
    As = [10]

    Ps = [1]

    for a in As:
        print "A=%s" % a
        nodes = InitializeNodes(a, N, W, L)
        for p in Ps:
            print "p=%s" % p
            p_persistent_csmacd(p, nodes)

    print "Complete"


def non_persistent():
    Ns = [100, 80, 60, 40, 20]
    W = 1000000
    L = 1500 * 8
    As = [20, 6]

    for n in Ns:
        for a in As:
            nodes = InitializeNodes(a, n, W, L)
            print "N=%s" % n
            print "A=%s" % a
            p_persistent_csmacd(1, nodes, True)

    print "Complete"


if __name__ == '__main__':
    main()
