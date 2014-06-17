import config


class Ball(object):
    def __init__(self, x=0, y=0, oldX=0, oldY=0, forceX=0, forceY=0, jitter=0):
        self.oldX = oldX
        self.x = x
        self.oldY = oldY
        self.y = y
        self.forceX = forceX
        self.forceY = forceY
        self.lastBounceTimes = [0.0 for _ in range(16)]
        self.jitter = jitter
        self.bounceTimeDelta = 10000
        self.tooMuchBouncingThreshold = 300

    def getOldX(self):
        return self.oldX

    def getOldY(self):
        return self.oldY

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setPos(self, x, y):
        self.x = x
        self.y = y

    def stepPhysics(self):
        # Apply the forces.
        self.oldX = self.x
        self.oldY = self.y
        self.x += self.forceX
        self.y += self.forceY
        self.forceX *= config.getFriction()
        self.forceY *= config.getFriction()
        if self.jitter > 0:
            self.jitter -= 0.1

    def applyForce(self, applyX, applyY):
        self.forceX += applyX
        self.forceY += applyY

    def reflectInDirection(self, reflectAngle):
        # Convert to polar.
        radius = self.getForceRadius()  # Pythagorean to find distance.
        theta = atan2(self.forceY, self.forceX)  # atan2 to find theta.
        theta += reflectAngle  # Then add the direction to it.
        # Convert it back to rect.
        self.forceX = radius * cos(theta)
        self.forceY = radius * sin(theta)

    def getForceRadius(self):
        # Pythag to find dist.
        return sqrt(self.forceX**2 + self.forceY**2)

    def bounce(self):
        for i in range(15, 0, -1):
            # Shift the queue...
            self.lastBounceTimes[i] = self.lastBounceTimes[i - 1]

        self.lastBounceTimes[0] = millis()  # ...then add the value.
        # Now check for unusual behavior.
        self.bounceTimeDelta = self.lastBounceTimes[0] - self.lastBounceTimes[15]

        if self.bounceTimeDelta < self.tooMuchBouncingThreshold:
            # Softeners for the balls.
            self.forceX = 0  # Make it still...
            self.forceY = 0  # ...if it misbehaved.

        else:
            # Keep force values sane.
            if 0.5 <= self.getForceRadius() <= 10:
                # Map to microtonal MIDI values.
                MIDI = map(self.getForceRadius(), 0.5, 10.0, 42.0, 127.0)
                # pan = map(self.x, 0, width, -1, 1)
                # Add the global MIDI offset.
                config.playSound(MIDI + config.getMIDIRange())
            self.jitter = self.getForceRadius()

    def amnesia(self):
        self.oldX = self.x
        self.oldY = self.y

    def rollBackOnePos(self):
        self.x = self.oldX
        self.y = self.oldY

    def getJitter(self):
        return self.jitter

    def getForceX(self):
        return self.forceX

    def getForceY(self):
        return self.forceY
