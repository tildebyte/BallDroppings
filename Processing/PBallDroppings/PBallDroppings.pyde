"""
u or U    undo
e or E    delete picked vertex
r         frequency range -
R         frequency range +
f         friction -
F         friction +
g         config.gravity -
G         config.gravity +
- or _    ball drop rate -
= or +    ball drop rate +
b or B    move ball "emitter"
p         toggle pause
0         reset all variables
' '       reset balls & lines
"""

import config
from java.util import Vector
from bounceline import BounceLine
from ball import Ball

closestBounceLine = BounceLine()


def setup():
    size(600, 400, P3D)
    ellipseMode(CENTER)
    newBall()


def draw():
    background(0)
    config.newball_xlag += (config.newball_x - config.newball_xlag) / 10.0
    config.newball_ylag += (config.newball_y - config.newball_ylag) / 10.0
    if config.paused != 1:
        # Release a ball on a timer.
        if millis() - config.oldMillis > config.ball_drop_rate:
            newBall()
            config.oldMillis = millis()
    stroke(255, 255, 255)
    noFill()

    # Draw the mouse line in-progress.
    if (config.clickCount % 2) == 1 and config.mousestate_draggingvert == 0:
        beginShape(LINES)
        stroke(90, 90, 90)
        vertex(config.lastMouseDownX, config.lastMouseDownY)
        color(0, 0, 0)
        vertex(mouseX, mouseY)
        endShape()
    stroke(255, 255, 255)

    # Draw the lines while calculating the closest picking vertex.
    closeL = None
    closeLV = 0
    closeDist = 100000  # Very far to start.

    beginShape(LINES)
    for bounceLine in config.lines:
        # First draw the line.
        vertex(bounceLine.getX1(), bounceLine.getY1())
        vertex(bounceLine.getX2(), bounceLine.getY2())

        # Recalculating the closest line for both vertices only if we ain't
        # dragging one.
        if config.mousestate_draggingvert == 0:
            # v1
            xd = bounceLine.getX1() - mouseX
            yd = bounceLine.getY1() - mouseY
            dist = sqrt(xd * xd + yd * yd)
            if dist < closeDist:
                closeDist = dist
                closeL = bounceLine
                closeLV = 0

            # v2
            xd = bounceLine.getX2() - mouseX
            yd = bounceLine.getY2() - mouseY
            dist = sqrt(xd * xd + yd * yd)
            if dist < closeDist:
                closeDist = dist
                closeL = bounceLine
                closeLV = 1
    endShape()

    if config.mousestate_draggingvert == 0:
        # Am I free roaming, or am I dragging a vertex?
        # Commit local calculations globally.
        closestBounceLine = closeL
        config.closestBounceLineVertex = closeLV
        config.closestBounceLineDistance = closeDist

        # Draw closest vertex line.
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
        # Vet vertex to mouse position.
        if config.closestBounceLineVertex == 0:
            # Which side of the line?
            closestBounceLine.set1(mouseX, mouseY)
        else:
            closestBounceLine.set2(mouseX, mouseY)

        # Fix just in case
        if closestBounceLine.fixDirection() != 0:
            # Also adjust the line-siding if it got swapped.
            if config.closestBounceLineVertex == 0:
                config.closestBounceLineVertex = 1
            else:
                config.closestBounceLineVertex = 0

        # Then draw the vertex as you pull it.
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

    # For all the balls...
    for i in range(config.balls.size()):
        if config.balls.elementAt(i) is not None:
            ball = config.balls.elementAt(i)
            if (ball.getY() > height * 2) or (ball.getForceRadius() == 0):
                config.balls.set(i, None)
                config.emptyBalls.add(i)
                ball = None
            else:
                if config.paused == 0:
                    ball.applyForce(0, config.gravity)

                # For all the lines (for all the balls)...
                for j in range(config.lines.size()):
                    if config.paused == 0:
                        # Am I on one side when I was just on another side a
                        # second ago?
                        thisBounceLine = config.lines.elementAt(j)
                        result1 = thisBounceLine.whichSideY(ball.getX(),
                                                            ball.getY())
                        result2 = thisBounceLine.whichSideY(ball.getOldX(),
                                                            ball.getOldY())
                        if result1 == 3 or result2 == 3:
                            # Neither old or current sample is off the ledge.
                            pass
                        elif result1 != result2:
                            # But I have passed through the slope point.
                            # Then push me to the previous side.
                            ball.rollBackOnePos()
                            # Reflect my force in that direction.
                            theta = atan2(thisBounceLine.getY2() -
                                          thisBounceLine.getY1(),
                                          thisBounceLine.getX2() -
                                          thisBounceLine.getX1())
                            if thisBounceLine.getX1() > thisBounceLine.getX2():
                                ball.reflectInDirection(theta)
                            else:
                                ball.reflectInDirection(theta + PI)
                            # Then also reset my memory to give me 1 frame's
                            # worth of amnesia.
                            ball.amnesia()
                            # Send it a bounce message so it will make a noise.
                            ball.bounce()
                # Draw ball.
                pushMatrix()
                translate(ball.getX(), ball.getY())
                noStroke()
                fill(255, 255, 255)
                diam = (ball.getJitter() * 5.0 + 2) * 2
                ellipse(0, 0, diam, diam)
                popMatrix()
                if config.paused == 0:
                    ball.stepPhysics()

    # Draw ball dropping point.
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
        resetBalls()
        resetBounceLines()


def mousePressed():
    if (config.closestBounceLineDistance <
            config.closestBounceLine_maxPickingDistance):
        config.mousestate_draggingvert = 1

        # Taking some notes for the undoable later on.
        if config.closestBounceLineVertex == 0:
            config.closestBounceLine_beginMoveX = closestBounceLine.getX1()
            config.closestBounceLine_beginMoveY = closestBounceLine.getY1()
        else:
            config.closestBounceLine_beginMoveX = closestBounceLine.getX2()
            config.closestBounceLine_beginMoveY = closestBounceLine.getY2()
    else:
        config.clickCount += 1
        if config.clickCount % 2 == 0:
            # Only draw something every 2 clicks.
            # Draw with mouse.
            if config.oldMouseX != -1 and config.oldMouseY != -1:
                # Load a line.
                bounceLine = BounceLine(config.oldMouseX, config.oldMouseY,
                                        mouseX, mouseY)
                # Register undoable.
                v = Vector()
                v.add(bounceLine)
                v.add("create_line")
                config.undoables.add(v)
                # Now here is a tweak that allows me never to have vertical
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
    xd = mouseX - config.lastMouseDownX
    yd = mouseY - config.lastMouseDownY
    if config.mousestate_draggingvert == 1:
        # Then we had been dragging something else.
        config.mousestate_draggingvert = 0
        config.clickCount = 0
        # Register undoable.
        v = Vector()
        v.add(config.closestBounceLineVertex)
        v.add(round(config.closestBounceLine_beginMoveX))
        v.add(round(config.closestBounceLine_beginMoveY))
        v.add(closestBounceLine)
        v.add("move_line")
        config.undoables.add(v)
    else:
        if sqrt(xd * xd + yd * yd) > 10:
            # 10 is the mouse drag movement margin for nondraggers.
            mousePressed()  # Nudge the line drawing.


def resetBalls():
    config.balls.removeAllElements()
    config.emptyBalls.removeAllElements()


def resetBounceLines():
    config.lines.removeAllElements()


def deletePickedVertex():
    if (config.closestBounceLineDistance <
            config.closestBounceLine_maxPickingDistance):
        # Register undoable.
        v = Vector()
        v.add(round(closestBounceLine.getX1()))
        v.add(round(closestBounceLine.getY1()))
        v.add(round(closestBounceLine.getX2()))
        v.add(round(closestBounceLine.getY2()))
        v.add("delete_line")
        config.undoables.add(v)
        # Then one of them is highlighted.
        config.lines.remove(closestBounceLine)
        closestBounceLine = None
        config.closestBounceLineDistance = 100000  # turn off picking!


def validBounceLine(bl):
    foundOne = 0
    for bounceLine in config.lines:
        if config.lines.get(i) == (bl):
            foundOne = 1
            break
    return foundOne


def newBall():
    # Load a ball.
    ball = Ball(config.newball_x, config.newball_y, config.balls.size())
    ball.applyForce(0.0001, 0)

    # Search for an empty spot in the list.
    if config.emptyBalls.size() > 0:
        config.balls.set(config.emptyBalls.remove(0), ball)
    else:
        # Else, you have to make one.
        config.balls.add(ball)


def undo():
    if config.undo_busy != 0:
        return
    else:
        config.undo_busy = 1
        if config.undoables.size() > 0:
            # Get the most recent undoable action.
            thisUndoable = config.undoables.remove(config.undoables.size() - 1)
            action = thisUndoable.remove(thisUndoable.size() - 1)

            # Get its variables and do the action.
            if action == "create_line":
                # Kill the line
                bounceLine = thisUndoable.remove(thisUndoable.size() - 1)
                if validBounceLine(bounceLine) != 0:
                    config.lines.remove(bounceLine)
                    bounceLine = None
            elif action == "move_line":
                # Move the line back.
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
