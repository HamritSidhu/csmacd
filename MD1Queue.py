class MD1Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, packet):
        self.queue.append(packet)

    def dequeue(self):
        if not self.isEmpty():
            return self.queue.pop(0)
        return None

    def size(self):
        return len(self.queue)

    def isEmpty(self):
        return self.size() == 0
