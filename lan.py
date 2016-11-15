import model
import math
import random

tickDuration = 0.0001
TICKS = 100000000

def p_persistent_csmacd(p, nodes):
	completed_packets = []
	for i in range(0, TICKS):
		mediumFree = isMediumFree(nodes)  
		for n in nodes:
			n.process_queue(i) # handles the packet arrivals to Node's MD1 queue
			if n.state == model.State.ReadyToTransmit:
				if mediumFree:
					pOutcome = random.uniform(0,1)
					if pOutcome < p:
						# go ahead and transmit
						n.state = model.State.Transmitting
						n.beginPacketTransmission(i)
					else:
						# Defer Transmission
						n.state = model.State.Defer
						n.waitDuration = 5 # default to 5 ticks - confirm if this is ok
			elif n.state == model.State.Defer:
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

				#transmission complete
				if n.state == model.State.Idle:
					print "transmission complete"
					completed_packets.append(transmittingPacket)

			else:
				# do nothing if packet in idle state
				pass

		transmitting_nodes = []
		for n in nodes:
			if n.state == model.State.Transmitting:
				transmitting_nodes.append(n)

		collision = detectCollision(transmitting_nodes, i)

		# if there is a collision, we want to put all the transmitting nodes
		# in exponential backoff 
		if collision:
			for n in nodes:
				n.state = model.State.ExponentialBackoff
	
	print len(completed_packets)
	if len(completed_packets) > 0:
		throughput = len(completed_packets)*1500*8*1.0/TICKS
		
		totalDelay = 0
		for pk in completed_packets:
			totalDelay += pk.completionTime

		avgDely = totalDelay*1.0/len(completed_packets)
		
	else:
		throughput = 0
		avgDely = 0


	print "Throughput: %s"%throughput
	print "Average Delay: %s" % avgDely

	
def detectCollision(tNodes, currentTick):
	for k in range(0, len(tNodes) - 1):
		propDelay = (tNodes[k].position - tNodes[k+1].position)*10.0/(2*10^8)/tickDuration

		if (currentTick - tNodes[k].currentServicePacket.startTick) >= propDelay:
			print "collision"
			return True
			

	# no collision was detected
	return False


def isMediumFree(nodes):
	for n in nodes:
		if n.state == model.State.Transmitting:
			return False

	return True

def InitializeNodes(A, N, W, L):
	nodeList = []
	for i in range(0, N):
		n = model.Node(i, A, L, W, tickDuration)
		nodeList.append(n)

	return nodeList

def main():
	N = 30
	W = 1*10^6
	L = 1500*8
	As = [10]

	
	Ps = [0.01,0.1,1]

	for a in As:
		print "A=%s"%a
		nodes = InitializeNodes(a, N, W, L)
		for p in Ps:
			print "p=%s"%p
			p_persistent_csmacd(p, nodes)

	print "Complete"
	#tests()

def tests():
	W = 1*10^6
	L = 1500*8
	A = 10

	node1 = model.Node(1,A,L,W, tickDuration)
	node2 = model.Node(2,A,L,W, tickDuration)
	
	nodeList = [node1, node2]
	mediumFree = isMediumFree(nodeList)
	print mediumFree == True
	
	node1.process_queue(0)
	print node1.state == model.State.ReadyToTransmit
	
	node2.process_queue(0)
	print node2.state == model.State.ReadyToTransmit

	
	print mediumFree == True

	node1.process_queue(1)
	node2.process_queue(1)

	print node1.state == model.State.ReadyToTransmit
	print node2.state == model.State.ReadyToTransmit

	if mediumFree:
		pOutcome = random.uniform(0,1)
		if pOutcome < 1:
			# go ahead and transmit
			node1.state = model.State.Transmitting
			node1.beginPacketTransmission(1)
		else:
			# Defer Transmission
			node1.state = model.State.Defer
			node1.waitDuration = 5 # default

	print node1.state

	print node1.currentServicePacket.startTick
	if node1.state == model.State.Transmitting:
		node1.transmit(node1.serviceTime+1)
		print node1.currentServicePacket.hasLeft

	mediumFree = isMediumFree(nodeList)
	print mediumFree == False
		
	if node1.state == model.State.Transmitting:
		cpk = node1.currentServicePacket
		node1.transmit(node1.serviceTime+2)
		print node1.state
		print node1.currentServicePacket == None
		print cpk.completionTime

	node1.process_queue(node1.nextArrivalTick)
	print node1.state == model.State.ReadyToTransmit

	mediumFree = isMediumFree(nodeList)
	print mediumFree == True

	node1.beginPacketTransmission(10)
	node2.beginPacketTransmission(10)

	print node1.state == model.State.Transmitting
	print node2.state == model.State.Transmitting

	print detectCollision(nodeList, 10) == True

	node1.state = model.State.ExponentialBackoff
	node2.state = model.State.ExponentialBackoff
	node1.backoffWait()
	node2.backoffWait()

	print node1.exponentialBackOff.isBackoffWaitComplete() == False
	print node2.exponentialBackOff.isBackoffWaitComplete() == False

	# for testing set it to small value
	node1.exponentialBackOff.Tb = 10

	for i in range(0, 10):
		node1.backoffWait()

	print node1.state == model.State.ExponentialBackoff
	print node1.exponentialBackOff.isBackoffWaitComplete() == False

	node1.backoffWait()
	print node1.exponentialBackOff.isBackoffWaitComplete() == True





if __name__ == '__main__':
	main()