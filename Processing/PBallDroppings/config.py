from ddf.minim import Minim
from java.util import Vector
from bumpy_instrument import BumpyInstrument

# Config module for PBallDroppings.
balls = Vector()  # Make a list of balls.
lines = Vector()  # Make a list of lines.
emptyBalls = Vector()  # Make a queue for recyclable ball spots.
undoables = Vector()
newball_x = 300
newball_y = 0
newball_xlag = 100
newball_ylag = 0
gravity = 0.04
ball_drop_rate = 3300
oldMillis = 0
clickCount = 0
mousestate_draggingvert = 0
oldMouseX = -1
oldMouseY = -1
lastMouseDownX = 0
lastMouseDownY = 0
closestBounceLineVertex = 0
closestBounceLine_maxPickingDistance = 20
closestBounceLine_beginMoveX = 0
closestBounceLine_beginMoveY = 0
closestBounceLineDistance = 0
undo_busy = 0
paused = 0
minim = Minim(this)
# bufferSize is the audio buffer length, which directly translates to
# latency (interactivity, really). Less-powerful machines will need a
# larger buffer at the expense of a decrease in responsiveness.
bufferSize = 256
out = minim.getLineOut(Minim.STEREO, bufferSize)
_MIDIRange = 12
_friction = 0.99997


def getMIDIRange():
    return _MIDIRange


def setMIDIRange(MIDIRange):
    global _MIDIRange
    _MIDIRange = MIDIRange


def getFriction():
    return _friction


def setFriction(friction):
    global _friction
    _friction = friction


def resetVars():
    global ball_drop_rate
    global setFriction
    global gravity
    global setMIDIRange
    global newball_x
    global newball_y
    global newball_xlag
    global newball_ylag

    ball_drop_rate = 3300
    setFriction(0.99997)
    gravity = 0.04
    setMIDIRange(12)
    newball_x = 300
    newball_y = 0
    newball_xlag = 100
    newball_ylag = 0


def playSound(rate):
    # BumpyInstrument is a Minim Instrument class (in a separate file).
    # 'out.playNote()' - (start time (in quarter notes), duration
    #                                            (in quarter notes), Instrument)
    # 'BumpyInstrument()' - (frequency in Hz, amplitude (unknown units;
    #                                                        generally 0 - 1))
    out.playNote(0.0, 0.9, BumpyInstrument(rate, 0.08, out))
