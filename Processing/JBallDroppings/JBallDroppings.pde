/*
CTRL-Z    undo
e or E or DEL or BKSPCE    delete picked vertex
r    frequency range -
R    frequency range +
f    friction -
F    friction +
g    gravity -
G    gravity +
- or _    ball drop rate -
= or +    ball drop rate +
b or B    move ball "emitter"
p    toggle pause
0    reset all variables
' '    reset balls & lines
*/

import java.util.*;
import ddf.minim.*;
import ddf.minim.ugens.*;

Vector balls;
Vector lines;
int oldMouseX;
int oldMouseY;
int lastMouseDownX;
int lastMouseDownY;
float oldMillis=0;
long clickCount=0;
long ball_drop_rate = 3000;
int fullScreenMode = 1;
Vector emptyBalls;
BounceLine closestBounceLine=null;
int closestBounceLineVertex=0;
float closestBounceLine_maxPickingDistance = 20;
float closestBounceLineDistance = 0;
int mousestate_draggingvert=0;
Vector undoables;
int undoables_max=256;
float closestBounceLine_beginMoveX=0;
float closestBounceLine_beginMoveY=0;
int newball_x = 300;
int newball_y = 0;
float newball_xlag = 100;
float newball_ylag = 0;
int undo_busy=0;
int paused = 0;
float gravity = 0.01f;
Minim minim;
AudioOutput out;
int bufferSize = 256;

public float _MIDIRange = 12.0;
public float _friction = 0.99997f;

public float getMIDIRange(){
    return _MIDIRange;
}

public void setMIDIRange(float MIDIRange){
    _MIDIRange = MIDIRange;
}

public float getFriction(){
    return _friction;
}

public void setFriction(float f){
    _friction = f;
}

void initSound(){
    minim = new Minim(this);
    // bufferSize is the audio buffer length, which directly translates to
    // latency (interactivity, really). Less-powerful machines will need a
    // larger buffer at the expense of a decrease in responsiveness.
    out = minim.getLineOut(Minim.STEREO, bufferSize);
}

void playSound(float rate){
    // BumpyInstrument is a Minim Instrument class (in a separate file).
    // 'out.playNote()' - start time (in quarter notes), duration
    //                                          (in quarter notes), Instrument
    // 'BumpyInstrument()' - frequency in Hz, amplitude (unknown units;
    //                                                        generally 0 - 1)
    out.playNote(0.0, 0.9, new BumpyInstrument(rate, 0.08));
}

void setup(){
    size(600, 400, P3D);
    oldMouseX = -1;
    oldMouseY = -1;
    undoables = new Vector();
    balls = new Vector();//make a new list of balls.
    lines = new Vector();//make a new list of lines.
    emptyBalls = new Vector(); //make a new queue for recyclable ball spots.
    ellipseMode(CENTER);
    initSound();
    Ball b = new Ball(newball_x, newball_y, balls.size());
    balls.add((Object)b);
}

public void stop(){
    super.stop();
}

void draw(){
    background(0);
    int i;
    newball_xlag += (newball_x - newball_xlag)/10.0f;
    newball_ylag += (newball_y - newball_ylag)/10.0f;

    if(paused!=1){
        //release a ball on a timer
        if(millis()-oldMillis > ball_drop_rate ){
            newBall();
            oldMillis = millis();
        }
    }

    stroke(255,255,255);
    noFill();

    //draw the mouse line in-progress
    if(clickCount%2==1 && mousestate_draggingvert==0){
        beginShape(LINES);
        stroke(90,90,90);
        vertex(lastMouseDownX,lastMouseDownY);
        color(0,0,0);
        vertex(mouseX,mouseY);
        endShape();
    }

    stroke(255,255,255);
    //draw them lines while calculating the closest picking vertex.
    BounceLine closeL=null;
    int closeLV=0;
    float closeDist=100000;//very far to start.
    beginShape(LINES);

    for(i=0;i<lines.size();i++){
        //first draw the line.
        BounceLine thisBounceLine = (BounceLine)(lines.elementAt(i));
        vertex(thisBounceLine.getX1(), thisBounceLine.getY1());
        vertex(thisBounceLine.getX2(),thisBounceLine.getY2());

        //recalculating the closest line for both vertices only if we ain't dragging one.
        if ( mousestate_draggingvert==0){
            //v1
            float xd = thisBounceLine.getX1() - mouseX;
            float yd = thisBounceLine.getY1() - mouseY;
            float dist = sqrt(xd*xd+yd*yd);

            if ( dist < closeDist){
                closeDist = dist;
                closeL = thisBounceLine;
                closeLV = 0;
            }

            //v2
            xd = thisBounceLine.getX2() - mouseX;
            yd = thisBounceLine.getY2() - mouseY;
            dist = sqrt(xd*xd+yd*yd);

            if ( dist < closeDist){
                closeDist = dist;
                closeL = thisBounceLine;
                closeLV = 1;
            }
        }
    }

    endShape();

    if ( mousestate_draggingvert==0){
        //am i free roaming, or am i dragging a vertex?
        //commit local calculations globally.
        closestBounceLine = closeL;
        closestBounceLineVertex = closeLV;
        closestBounceLineDistance = closeDist;

        //draw closest vertex line.
        if(closestBounceLine!=null && closestBounceLineDistance < closestBounceLine_maxPickingDistance){
            pushMatrix();

            if(closestBounceLineVertex==0){
                translate(closestBounceLine.getX1(),closestBounceLine.getY1());
            }
            else {
                translate(closestBounceLine.getX2(),closestBounceLine.getY2());
            }

            noStroke();
            fill(255);
            rect(-3,-3,6,6);
            stroke(255);
            noFill();
            popMatrix();
        }
    }
    else {
        //set vertex to mouse position.
        if(closestBounceLineVertex==0){
            //which side of the line?
            closestBounceLine.set1(mouseX,mouseY);
        }
        else {
            closestBounceLine.set2(mouseX,mouseY);
        }

        //fix just in case
        if(closestBounceLine.fixDirection()!=0){
            //also adjust the line-siding if it got swapped.
            if(closestBounceLineVertex==0)closestBounceLineVertex=1;
            else closestBounceLineVertex=0;
        }
        //then draw the vertex as you pull it.
        pushMatrix();

        if(closestBounceLineVertex==0){
            translate(closestBounceLine.getX1(),closestBounceLine.getY1());
        }
        else {
            translate(closestBounceLine.getX2(),closestBounceLine.getY2());
        }

        noStroke();
        fill(255);
        rect(-3,-3,6,6);
        noFill();
        stroke(255);
        popMatrix();
    }

    //for all the balls . . .
    for(i=0;i<balls.size();i++){

        if(balls.elementAt(i)!=null){
            Ball b = (Ball)(balls.elementAt(i));

            if(b.getY() > height *2 || b.getForceRadius()==0){
                balls.set(i,null);
                emptyBalls.add((Object)new Integer(i));
                b = null;
            }
            else {
                if(paused==0){
                    //gravity
                    b.applyForce(0,gravity);
                }

                //for all the lines (for all the balls) ...
                for(int j=0;j< lines.size() ;j++){

                    if(paused==0){
                        //am i on one side when i was just on another side a second ago?
                        BounceLine thisBounceLine = (BounceLine)(lines.elementAt(j));
                        int result1 = thisBounceLine.whichSideY(b.getX(),b.getY());
                        int result2 = thisBounceLine.whichSideY(b.getOldX(),b.getOldY());

                        if( result1==3 || result2==3 ){
                            //neither old or current sample is off the ledge.
                        }
                        else if(result1!=result2){
                            //but i have passed through the slope point.
                            //then push me to the previous side
                            b.rollBackOnePos();
                            //reflect my force in that direction
                            float theta = atan2(thisBounceLine.getY2()-thisBounceLine.getY1(),
                            thisBounceLine.getX2()-thisBounceLine.getX1()  );

                            if(thisBounceLine.getX1()>thisBounceLine.getX2()){
                                b.reflectInDirection(theta);
                            }
                            else {
                                b.reflectInDirection(theta+PI);
                            }

                            //then also reset my memory to give me 1 frame's worth of amnesia.
                            b.amnesia();
                            b.bounce();//send it a bounce message so it will make a noise.
                        }
                    }
                }
                //draw ball
                pushMatrix();
                translate( b.getX(), b.getY());
                noStroke();
                fill(255,255,255);
                float diam=(b.getJitter()*5.0f+2)*2;
                ellipse(0,0,diam,diam);
                popMatrix();

                if(paused==0){
                    b.stepPhysics();
                }
            }
        }
    }
    //draw ball dropping point.
    pushMatrix();
    translate( newball_xlag , newball_ylag);
    stroke(90,90,90);
    noFill();
    ellipse(0,0,11,11);
    popMatrix();
}

void keyPressed(){
    int k = key;
    int i;

    if(k==26){
        //CTRL-Z - undo
        if(undoables.size()>0){
            undo();
        }
    }

    if(k==127||k==8){
        //DELETE or BACKSPACE
        deletePickedVertex();
    }

    if (k=='B'||k=='b'){
        newball_x = mouseX;
        newball_y = mouseY;
    }
    else if(k=='r'){
        setMIDIRange(getMIDIRange() - 4);
    }
    else if(k=='R'){
        setMIDIRange(getMIDIRange() + 4);
    }
    else if(k=='f'){
        // *Decrease* the effect of friction
        setFriction(getFriction()+0.0001f);
    }
    else if(k=='F'){
        // *Increase* the effect of friction
        setFriction(getFriction()-0.0001f);
    }
    else if(k=='g'){
        gravity-=0.001;
    }
    else if(k=='G'){
        gravity+=0.001;
    }
    else if(k=='e'||k=='E'){
        deletePickedVertex();
    }
    else if(k=='p'||k=='P'){
        if(paused==0)paused=1;
        else paused = 0;
    }
    else if(k=='0'){
        resetVars();
    }
    else if(k == '-' || k == '_'){
        //-
        ball_drop_rate +=100;
    }
    else if(k == '=' || k == '+'){
        //+
        ball_drop_rate -= 100;
    }

    if(k==' ') {
        // else kill both the lines and the balls.
        resetBalls();
        resetBounceLines();
    }
}

void mousePressed(){
    if(closestBounceLineDistance < closestBounceLine_maxPickingDistance){
        mousestate_draggingvert=1;

        //taking some notes for the undoable later on.
        if(closestBounceLineVertex==0){
            closestBounceLine_beginMoveX = closestBounceLine.getX1();
            closestBounceLine_beginMoveY = closestBounceLine.getY1();
        }
        else {
            closestBounceLine_beginMoveX = closestBounceLine.getX2();
            closestBounceLine_beginMoveY = closestBounceLine.getY2();
        }
    }
    else {
        clickCount++;

        if(clickCount%2==0){
            //only draw something every 2 clicks.
            //draw with mouse
            if(oldMouseX!=-1 && oldMouseY!=-1){
                //load a new line
                BounceLine l = new BounceLine(oldMouseX,oldMouseY,mouseX,mouseY);
                //register undoable
                Vector v=new Vector();
                v.add((Object)l);
                v.add((Object)"create_line");
                undoables.add((Object)v);
                //now here is a tweak that allows me never to have verticle ones
                //because they mess up with the math slope finding.
                float fabs = l.getX1() - l.getX2();

                if(fabs < 4){
                    if(l.getX1() < l.getX2()){
                        l.set1(l.getX1()-3,l.getY1());
                    }
                    else {
                        l.set1(l.getX1()+3,l.getY1());
                    }
                }
                lines.add((Object)l);
            }
        }
    }
    oldMouseX = mouseX;
    oldMouseY = mouseY;
    lastMouseDownX = mouseX;
    lastMouseDownY = mouseY;
}

void mouseReleased(){
    float xd = mouseX - lastMouseDownX;
    float yd = mouseY - lastMouseDownY;

    if ( mousestate_draggingvert==1){
        //then we had been dragging something else.
        mousestate_draggingvert=0;
        clickCount = 0;
        //register undoable
        Vector v=new Vector();
        v.add(new Integer(closestBounceLineVertex));
        v.add(new Integer((int)round(closestBounceLine_beginMoveX)));
        v.add(new Integer((int)round(closestBounceLine_beginMoveY)));
        v.add((Object)closestBounceLine);
        v.add((Object)"move_line");
        undoables.add((Object)v);
    }
    else {
        if ( sqrt(xd*xd+yd*yd) > 10 ){
            //10 is the mouse drag movement margin for nondraggers
            mousePressed();//nudge the new line drawing.
        }
    }
}

void resetBalls(){
    balls.removeAllElements();
    emptyBalls.removeAllElements();
}

void resetBounceLines(){
    lines.removeAllElements();
}

void resetVars(){
    ball_drop_rate = 3000;
    setFriction(0.99997f);
    gravity = 0.01f;
    setMIDIRange(12);
    newball_x = 300;
    newball_y = 0;
    newball_xlag = 100;
    newball_ylag = 0;
}

void deletePickedVertex(){
    if( closestBounceLineDistance < closestBounceLine_maxPickingDistance){
        //register undoable
        Vector v=new Vector();
        v.add(new Integer((int)round(closestBounceLine.getX1())));
        v.add(new Integer((int)round(closestBounceLine.getY1())));
        v.add(new Integer((int)round(closestBounceLine.getX2())));
        v.add(new Integer((int)round(closestBounceLine.getY2())));
        v.add((Object)"delete_line");
        undoables.add((Object)v);
        //then one of them is highlighted.
        lines.remove((Object)closestBounceLine);
        closestBounceLine = null;
        closestBounceLineDistance=100000;//turn off picking!
    }
}

int validBounceLine(BounceLine l){
    int foundOne = 0;

    for(int i=0;i<lines.size();i++){
        if(lines.get(i)==((Object)l)){
            foundOne=1;
            break;
        }
    }
    return foundOne;
}

void newBall(){
    //load a new ball.
    Ball b = new Ball(newball_x,newball_y, balls.size());
    b.applyForce(0.0001,0);

    //search for an empty spot in the list
    if(emptyBalls.size()>0){
        balls.set( ((Integer)emptyBalls.remove(0)).intValue(),(Object)b);
    }
    else {
        //else, you have to make a new one.
        balls.add((Object)b);
    }
}

void undo(){
    if(undo_busy!=0){
        return;
    }
    else{
        undo_busy=1;

        if(undoables.size()>0){
            //get the most recent undoable action.
            Vector thisUndoable = (Vector)undoables.remove(undoables.size()-1);
            String action = (String)thisUndoable.remove(thisUndoable.size()-1);

            //get its variables and do the action.
            if(action=="create_line"){
                //kill the line
                BounceLine l = (BounceLine)thisUndoable.remove(thisUndoable.size()-1);

                if(validBounceLine(l)!=0){
                    lines.remove((Object)l);
                    l = null;
                }
            }
            else if(action=="move_line"){
                //move the line back.
                BounceLine l = (BounceLine)(thisUndoable.remove(thisUndoable.size()-1));

                if(validBounceLine(l)!=0){
                    int y = ((Integer)thisUndoable.remove(thisUndoable.size()-1)).intValue();
                    int x = ((Integer)thisUndoable.remove(thisUndoable.size()-1)).intValue();
                    int which = ((Integer)thisUndoable.remove(thisUndoable.size()-1)).intValue();

                    if(which==0){
                        l.set1(x,y);
                    }
                    else {
                        l.set2(x,y);
                    }
                }
            }
            else if(action=="delete_line"){
                int y2 = ((Integer)(thisUndoable.remove(thisUndoable.size()-1))).intValue();
                int x2 = ((Integer)(thisUndoable.remove(thisUndoable.size()-1))).intValue();
                int y1 = ((Integer)(thisUndoable.remove(thisUndoable.size()-1))).intValue();
                int x1 = ((Integer)(thisUndoable.remove(thisUndoable.size()-1))).intValue();
                BounceLine l = new BounceLine(x1,y1,x2,y2);
                lines.add((Object)l);
            }
            else {
                println("Undoable action unknown: "+action);
            }
            thisUndoable = null;
        }
        undo_busy = 0;
    }
}

class Ball {
    float oldX;
    float oldY;
    float x;
    float y;
    float forceX;
    float forceY;
    int channel;
    float jitter;
    char volume;
    long [] lastBounceTimes;
    long bounceTimeDelta;
    long tooMuchBouncingThreshold;

    Ball(){
        initMem();
    }

    void initMem(){
        oldX = x = 0;
        oldY = y = 0;
        forceX = 0;
        forceY = 0;
        channel = 0;
        volume = 0;
        lastBounceTimes = new long[16];
        jitter = 0;
        bounceTimeDelta = 10000;
        tooMuchBouncingThreshold = 300;
    }

    Ball(float _x,float _y, int _channel){
        initMem();
        oldX = x = _x;
        oldY = y = _y;
        channel = _channel;
    }

    Ball(float x_,float y_,float oldX_,float oldY_,float forceX_,float forceY_,float jitter){
        initMem();
        x = x_;
        y = y_;
        oldX = oldX_;
        oldY = oldY_;
        forceX = forceX_;
        forceY = forceY_;
    }

    float getOldX(){
        return oldX;
    }

    float getOldY(){
        return oldY;
    }

    float getX(){
        return x;
    }

    float getY(){
        return y;
    }

    void setPos(float _x,float _y){
        x = _x;
        y = _y;
    }

    void stepPhysics(){
        //apply the forces
        oldX = x;
        oldY = y;
        x+= forceX;
        y+= forceY;
        forceX *= getFriction();
        forceY *= getFriction();
        if(jitter>0)jitter-=0.1;
    }

    void applyForce(float applyX,float applyY){
        forceX += applyX;
        forceY += applyY;
    }

    void reflectInDirection(float reflectAngle){
        //convert to polar
        float radius = getForceRadius();//pythagorean to find distance
        float theta = atan2(forceY,forceX);//atan2 to find theta
        theta += reflectAngle; //then add the direction to it
        //convert it back to rect
        forceX = radius * cos(theta);
        forceY = radius * sin(theta);
    }

    float getForceRadius(){
        return sqrt(forceX*forceX+forceY*forceY);//pythag to find dist
    }

    void bounce(){
        //volume = 255.0;
        for(int i=15;i>0;i--){
            //shift the queue
            lastBounceTimes[i] = lastBounceTimes[i-1];
        }

        lastBounceTimes[0] = millis();//then add the new value
        //now check for unusual behavior
        bounceTimeDelta = lastBounceTimes[0] - lastBounceTimes[15];

        if (bounceTimeDelta<tooMuchBouncingThreshold){
            //softeners for the balls
            forceX = 0;//make it still
            forceY = 0;//if it misbehaved.
        }
        else {
            if(getForceRadius() >= 0.5 && getForceRadius() <= 10.0){
                // Map to microtonal MIDI values
                float MIDI = map(getForceRadius(), 0.5, 10.0, 42.0, 127.0);
                // pan = map(self.x, 0, width, -1, 1)
                // Add the global MIDI offset and play
                playSound(MIDI + getMIDIRange());
            }
            jitter = getForceRadius();
        }
    }

    void amnesia(){
        oldX = x;
        oldY = y;
    }

    void rollBackOnePos(){
        x = oldX;
        y = oldY;
    }

    float getJitter(){
        return jitter;
    }

    float getForceX(){
        return forceX;
    }

    float getForceY(){
        return forceY;
    }
}

class BounceLine {
    float x1;
    float y1;
    float x2;
    float y2;

    BounceLine(){
        initMem();
    }

    void initMem(){
        x1 = 0;
        y1 = 0;
        x2 = 0;
        y2 = 0;
    }

    BounceLine(float _x1, float _y1, float _x2, float _y2){
        initMem();
        //this makes sure that x1 is always the smallest of the pair.
        x1 = _x2;
        y1 = _y2;
        x2 = _x1;
        y2 = _y1;
        fixDirection();
    }

    float getX1(){
        return x1;
    }

    float getY1(){
        return y1;
    }

    float getX2(){
        return x2;
    }

    float getY2(){
        return y2;
    }

    void set1(float x,float y){
        x1 = x;
        y1 = y;
    }

    void set2(float x,float y){
        x2 = x;
        y2 = y;
    }

    int whichSideY(float x,float y){
        //get the slope - M in y=mx+b
        float m = (y2-y1)/(x2-x1);
        float b = y1 - m*x1;
        int fallen_outside=0;
        //now find out if it's hitting the line seg, and not the entire ray.

        if(x>x1||x<x2){
            //if fallen outside
            return 3;
        }
        else{
            return (x*m+b)>y?1:0;// here is whether or not it's above.
        }
    }

    int fixDirection(){
        //this makes sure that x1 is always the smallest of the pair.
        //swap everyone
        int swapReport=0;

        if(x1 < x2){
            float t = x1;
            x1=x2;
            x2=t;
            t = y1;
            y1=y2;
            y2=t;
            swapReport = 1;
        }
        else {
            swapReport = 0;
        }

        //also fix verticality.
        if(x1==x2){
            x1+=0.1;
        }

        return swapReport;
    }
}
