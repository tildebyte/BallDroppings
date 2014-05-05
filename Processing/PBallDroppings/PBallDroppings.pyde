"""
u or U    undo
e or E    delete picked vertex
r    frequency range -
R    frequency range +
f    friction -
F    friction +
g    config.gravity -
G    config.gravity +
- or _    ball drop rate -
= or +    ball drop rate +
b or B    move ball "emitter"
p    toggle pause
0    reset all variables
' '    reset balls & lines
"""

import config
from java.util import Vector
from BounceLine import BounceLine
from Ball import Ball

closestBounceLine = BounceLine()


def setup():
    size(600, 400, P3D)
    # frameRate(30)
    ellipseMode(CENTER)
    newBall()


def stop():
    super.stop()


def draw():
    global closestBounceLine

    background(0)

    config.newball_xlag += (config.newball_x - config.newball_xlag) / 10.0
    config.newball_ylag += (config.newball_y - config.newball_ylag) / 10.0

    if config.paused != 1:
        # release a ball on a timer
        if millis() - config.oldMillis > config.ball_drop_rate:
            newBall()
            config.oldMillis = millis()

    stroke(255, 255, 255)
    noFill()

    # draw the mouse line in - progress
    if (config.clickCount % 2) == 1 and config.mousestate_draggingvert == 0:
        beginShape(LINES)
        stroke(90, 90, 90)
        vertex(config.lastMouseDownX, config.lastMouseDownY)
        color(0, 0, 0)
        vertex(mouseX, mouseY)
        endShape()

    stroke(255, 255, 255)
    # draw the lines while calculating the closest picking vertex.
    closeL = None
    closeLV = 0
    closeDist = 100000  # very far to start.

    beginShape(LINES)
    for i in range(config.lines.size()):
        # first draw the line.
        thisBounceLine = config.lines.elementAt(i)
        vertex(thisBounceLine.getX1(), thisBounceLine.getY1())
        vertex(thisBounceLine.getX2(), thisBounceLine.getY2())

        # recalculating the closest line for both vertices only if we ain't
        # dragging one.
        if config.mousestate_draggingvert == 0:
            # v1
            xd = thisBounceLine.getX1() - mouseX
            yd = thisBounceLine.getY1() - mouseY
            dist = sqrt(xd * xd + yd * yd)

            if dist < closeDist:
                closeDist = dist
                closeL = thisBounceLine
                closeLV = 0

            # v2
            xd = thisBounceLine.getX2() - mouseX
            yd = thisBounceLine.getY2() - mouseY
            dist = sqrt(xd * xd + yd * yd)

            if dist < closeDist:
                closeDist = dist
                closeL = thisBounceLine
                closeLV = 1
    endShape()

    if config.mousestate_draggingvert == 0:
        # am i free roaming, or am i dragging a vertex?
        # commit local calculations globally.
        closestBounceLine = closeL
        config.closestBounceLineVertex = closeLV
        config.closestBounceLineDistance = closeDist

        # draw closest vertex line.
        if (closestBounceLine is not None and
                config.closestBounceLineDistance <
                config.closestBounceLine_maxPickingDistance):
            pushMatrix()

            if config.closestBounceLineVertex == 0:
                translate(closestBounceLine.getX1(),
                          closestBounceLine.getY1())
            else:
                translate(closestBounceLine.getX2(),
                          closestBounceLine.getY2())

            noStroke()
            fill(255)
            rect(-3, -3, 6, 6)
            stroke(255)
            noFill()
            popMatrix()
    else:
        # set vertex to mouse position.
        if config.closestBounceLineVertex == 0:
            # which side of the line?
            closestBounceLine.set1(mouseX, mouseY)
        else:
            closestBounceLine.set2(mouseX, mouseY)

        # fix just in case
        if closestBounceLine.fixDirection() != 0:
            # also adjust the line - siding if it got swapped.
            if config.closestBounceLineVertex == 0:
                config.closestBounceLineVertex = 1
            else:
                config.closestBounceLineVertex = 0

        # then draw the vertex as you pull it.
        pushMatrix()

        if config.closestBounceLineVertex == 0:
            translate(closestBounceLine.getX1(), closestBounceLine.getY1())
        else:
            translate(closestBounceLine.getX2(), closestBounceLine.getY2())

        noStroke()
        fill(255)
        rect(-3, -3, 6, 6)
        noFill()
        stroke(255)
        popMatrix()

    # for all the balls . . .
    for i in range(config.balls.size()):
        if config.balls.elementAt(i) is not None:
            ball = config.balls.elementAt(i)

            if (ball.getY() > height * 2) or (ball.getForceRadius() == 0):
                config.balls.set(i, None)
                config.emptyBalls.add(i)
                ball = None
            else:
                if config.paused == 0:
                    # config.gravity
                    ball.applyForce(0, config.gravity)

                # for all the lines (for all the config.balls) ...
                for j in range(config.lines.size()):
                    if config.paused == 0:
                        # am i on one side when i was just on another side a
                        # second ago?
                        thisBounceLine = config.lines.elementAt(j)
                        result1 = thisBounceLine.whichSideY(ball.getX(),
                                                            ball.getY())
                        result2 = thisBounceLine.whichSideY(ball.getOldX(),
                                                            ball.getOldY())

                        if result1 == 3 or result2 == 3:
                            # neither old or current sample is off the ledge.
                            pass
                        elif result1 != result2:
                            # but i have passed through the slope point.
                            # then push me to the previous side
                            ball.rollBackOnePos()
                            # reflect my force in that direction
                            theta = atan2(thisBounceLine.getY2() -
                                          thisBounceLine.getY1(),
                                          thisBounceLine.getX2() -
                                          thisBounceLine.getX1())

                            if thisBounceLine.getX1() > thisBounceLine.getX2():
                                ball.reflectInDirection(theta)
                            else:
                                ball.reflectInDirection(theta + PI)

                            # then also reset my memory to give me 1 frame's
                            # worth of amnesia.
                            ball.amnesia()
                            #send it a bounce message so it will make a noise.
                            ball.bounce()

                # draw ball
                pushMatrix()
                translate(ball.getX(), ball.getY())
                noStroke()
                fill(255, 255, 255)
                diam = (ball.getJitter() * 5.0 + 2) * 2
                ellipse(0, 0, diam, diam)
                popMatrix()

                if config.paused == 0:
                    ball.stepPhysics()

    # draw ball dropping point.
    pushMatrix()
    translate(config.newball_xlag, config.newball_ylag)
    stroke(90, 90, 90)
    noFill()
    ellipse(0, 0, 11, 11)
    popMatrix()


def keyPressed():
    if key == 'u' or key == 'U':
        if config.undoables.size() > 0:
            undo()

    if key == 'B' or key == 'b':
        config.newball_x = mouseX
        config.newball_y = mouseY

    elif key == 'r':
        config.setMIDIRange(config.getMIDIRange() - 4)

    elif key == 'R':
        config.setMIDIRange(config.getMIDIRange() + 4)

    elif key == 'f':
        # *Decrease* the effect of friction
        config.setFriction(config.getFriction() + 0.0001)

    elif key == 'F':
        # *Increase* the effect of friction
        config.setFriction(config.getFriction() - 0.0001)

    elif key == 'g':
        config.gravity -= 0.001

    elif key == 'G':
        config.gravity += 0.001

    elif key == 'e' or key == 'E':
        deletePickedVertex()

    elif key == 'p' or key == 'P':
        if config.paused == 0:
            config.paused = 1
        else:
            config.paused = 0

    elif key == '0':
        config.resetVars()

    elif key == '-' or key == '_':
        config.ball_drop_rate += 100

    elif key == '=' or key == '+':
        config.ball_drop_rate -= 100

    if key == ' ':
        # else kill both the lines and the balls.
        resetBalls()
        resetBounceLines()

    # Debug dump
    # if key == 'D':
    #     # Whatever one wants: line locations, angles... ball frequencies...
    #     for i in range(config.balls.size()):
    #         if config.balls.elementAt(i) is not None:
    #             print("Ball {0} forceRadius: {1}".
    #                   format(i, config.balls.elementAt(i).force))
    #             print("Ball {0} rate: {1}".
    #                   format(i, config.balls.elementAt(i).rate))


def mousePressed():
    global closestBounceLine

    if (config.closestBounceLineDistance <
            config.closestBounceLine_maxPickingDistance):
        config.mousestate_draggingvert = 1

        # taking some notes for the undoable later on.
        if config.closestBounceLineVertex == 0:
            config.closestBounceLine_beginMoveX = closestBounceLine.getX1()
            config.closestBounceLine_beginMoveY = closestBounceLine.getY1()

        else:
            config.closestBounceLine_beginMoveX = closestBounceLine.getX2()
            config.closestBounceLine_beginMoveY = closestBounceLine.getY2()

    else:
        config.clickCount += 1

        if config.clickCount % 2 == 0:
            # only draw something every 2 clicks.
            # draw with mouse
            if config.oldMouseX != -1 and config.oldMouseY != -1:
                # load a line
                bounceLine = BounceLine(config.oldMouseX, config.oldMouseY,
                                        mouseX, mouseY)
                # register undoable
                v = Vector()
                v.add(bounceLine)
                v.add("create_line")
                config.undoables.add(v)
                # now here is a tweak that allows me never to have vertical
                # ones because they mess with the math slope finding.
                fabs = bounceLine.getX1() - bounceLine.getX2()

                if fabs < 4:
                    if bounceLine.getX1() < bounceLine.getX2():
                        bounceLine.set1(bounceLine.getX1() - 3,
                                        bounceLine.getY1())

                    else:
                        bounceLine.set1(bounceLine.getX1() + 3,
                                        bounceLine.getY1())

                config.lines.add(bounceLine)

    config.oldMouseX = mouseX
    config.oldMouseY = mouseY
    config.lastMouseDownX = mouseX
    config.lastMouseDownY = mouseY


def mouseReleased():
    global closestBounceLine

    xd = mouseX - config.lastMouseDownX
    yd = mouseY - config.lastMouseDownY

    if config.mousestate_draggingvert == 1:
        # then we had been dragging something else.
        config.mousestate_draggingvert = 0
        config.clickCount = 0
        # register undoable
        v = Vector()
        v.add(config.closestBounceLineVertex)
        v.add(round(config.closestBounceLine_beginMoveX))
        v.add(round(config.closestBounceLine_beginMoveY))
        v.add(closestBounceLine)
        v.add("move_line")
        config.undoables.add(v)

    else:
        if sqrt(xd * xd + yd * yd) > 10:
            # 10 is the mouse drag movement margin for nondraggers
            mousePressed()  # nudge the line drawing.


def resetBalls():
    config.balls.removeAllElements()
    config.emptyBalls.removeAllElements()


def resetBounceLines():
    config.lines.removeAllElements()


def deletePickedVertex():
    global closestBounceLine

    if (config.closestBounceLineDistance <
            config.closestBounceLine_maxPickingDistance):
        # register undoable
        v = Vector()
        v.add(round(closestBounceLine.getX1()))
        v.add(round(closestBounceLine.getY1()))
        v.add(round(closestBounceLine.getX2()))
        v.add(round(closestBounceLine.getY2()))
        v.add("delete_line")
        config.undoables.add(v)
        # then one of them is highlighted.
        config.lines.remove(closestBounceLine)
        closestBounceLine = None
        config.closestBounceLineDistance = 100000  # turn off picking!


def validBounceLine(bounceLine):
    foundOne = 0
    for i in range(config.lines.size()):
        if config.lines.get(i) == (bounceLine):
            foundOne = 1
            break

    return foundOne


def newBall():
    # load a ball.
    ball = Ball(config.newball_x, config.newball_y, config.balls.size())
    ball.applyForce(0.0001, 0)

    # search for an empty spot in the list
    if config.emptyBalls.size() > 0:
        config.balls.set(config.emptyBalls.remove(0), ball)
    else:
        # else, you have to make one.
        config.balls.add(ball)


def undo():
    if config.undo_busy != 0:
        return
    else:
        config.undo_busy = 1
        if config.undoables.size() > 0:
            # get the most recent undoable action.
            thisUndoable = config.undoables.remove(config.undoables.size() - 1)
            action = thisUndoable.remove(thisUndoable.size() - 1)

            # get its variables and do the action.
            if action == "create_line":
                # kill the line
                bounceLine = thisUndoable.remove(thisUndoable.size() - 1)

                if validBounceLine(bounceLine) != 0:
                    config.lines.remove(bounceLine)
                    bounceLine = None
            elif action == "move_line":
                # move the line back.
                bounceLine = thisUndoable.remove(thisUndoable.size() - 1)

                if validBounceLine(bounceLine) != 0:
                    y = thisUndoable.remove(thisUndoable.size() - 1)
                    x = thisUndoable.remove(thisUndoable.size() - 1)
                    which = thisUndoable.remove(thisUndoable.size() - 1)

                    if which == 0:
                        bounceLine.set1(x, y)
                    else:
                        bounceLine.set2(x, y)
            elif action == "delete_line":
                y2 = thisUndoable.remove(thisUndoable.size() - 1)
                x2 = thisUndoable.remove(thisUndoable.size() - 1)
                y1 = thisUndoable.remove(thisUndoable.size() - 1)
                x1 = thisUndoable.remove(thisUndoable.size() - 1)
                bounceLine = BounceLine(x1, y1, x2, y2)
                config.lines.add(bounceLine)
            else:
                println("Undoable action unknown: " + action)

            thisUndoable = None
        config.undo_busy = 0
