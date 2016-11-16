class Packet:
    def __init__(self, createTick):
        self.createTick = createTick
        self.startTick = 0
        self.hasLeft = False
        self.completionTime = 0

    def beginService(self, startTick):
        self.startTick = startTick

    def process(self, currentTick, serviceTime):
        processTime = currentTick - self.startTick
        if processTime >= serviceTime:
            self.hasLeft = True
            self.completionTime = currentTick - self.createTick
