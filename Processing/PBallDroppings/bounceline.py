class BounceLine(object):
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fixDirection()

    def getX1(self):
        return self.x1

    def getY1(self):
        return self.y1

    def getX2(self):
        return self.x2

    def getY2(self):
        return self.y2

    def set1(self, x, y):
        self.x1 = x
        self.y1 = y

    def set2(self, x, y):
        self.x2 = x
        self.y2 = y

    def whichSideY(self, x, y):
        # Get the slope; 'm' in y = mx + b
        m = float(self.y2 - self.y1) / (self.x2 - self.x1)
        b = self.y1 - m * self.x1

        # Now find out if it's hitting the line seg, and not the entire ray.
        if self.x1 < x or x < self.x2:
            # If fallen outside...
            return 3
        else:
            # Here is whether or not it's above the line.
            if (x * m + b) > y:
                return 1
            else:
                return 0

    def fixDirection(self):
        # This makes sure that x1 is always the smallest of the pair.
        # Swap everyone.
        swapReport = 0

        if self.x1 < self.x2:
            t = self.x1
            self.x1 = self.x2
            self.x2 = t
            t = self.y1
            self.y1 = self.y2
            self.y2 = t
            swapReport = 1
        else:
            swapReport = 0

        # Also fix verticality.
        if self.x1 == self.x2:
            self.x1 += 0.1

        return swapReport
