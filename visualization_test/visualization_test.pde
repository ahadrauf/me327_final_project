import processing.serial.*;
import java.io.Serializable.*;
import java.util.*;
//import libomv.types.Vector3;


import java.awt.*;

PShape ring;
PShape handle;
float angle;
PShader colorShader;
Vector3 spline;

boolean frameMoved = false;

void setup() {
  size(640, 360, P3D);
  int xpos = 100;
  int ypos = 100;
  surface.setLocation(xpos, ypos);  // Documentation https://processing.org/reference/setLocation_.html
  int canX = 75;
  int canY = 25;
  int cannum = 100;
  ring = createCan(canX, canY, cannum);
  handle = createCan(canY, 200, cannum);
  
  Vector3 p0 = new Vector3(1.0,2.0,3.0);
  Vector3 p1 = new Vector3(4.0,8.0,12.0);
  Vector3 m0 = new Vector3(2.0,2.0,2.0);
  Vector3 m1 = new Vector3(8.0,8.0,8.0);
  spline = hermiteInterpolation(0.5, p0, p1, m0, m1);
  
  //drawSpline(Graphics, 5, 10, 50, 100, 70, -20);
  
}

void draw() {  
  background(0);
  lights();
  translate(width/2, height/2);
  rotateZ(1.5708);
  //rotateY(angle);
  //rotateX(.7);
  lights();
  shape(ring);
  
  translate(width/100, height/8);
  rotateZ(1.5708);
  shape(handle);
  

  //angle += 0.01;
  //println(angle);
}

//-------------------------------------------------------------------------

PShape createCan(float r, float h, int detail) {
  // Taken from https://forum.processing.org/two/discussion/26800/how-to-create-a-3d-cylinder-using-pshape-and-vertex-x-y-z
  textureMode(NORMAL);
  PShape sh = createShape();

  sh.beginShape(QUAD_STRIP);

  //sh.noStroke();
  sh.fill(255, 0, 0); 
  for (int i = 0; i <= detail; i++) {
    float angle = TWO_PI / detail;
    float x = sin(i * angle);
    float z = cos(i * angle);
    float u = float(i) / detail;
    sh.normal(x, 0, z);
    sh.vertex(x * r, -h/2, z * r, u, 0);
    sh.vertex(x * r, +h/2, z * r, u, 1);
  }
  sh.endShape();
  return sh;
}


/*
Cubic hermite interpolation
:param t: Time [0, 1]
:param p0: Initial position (t = 0)
:param p1: Final position (t = 1)
:param m0: Initial tangent (t = 0)
:param m1: Final tangent (t = 1)
https://en.wikipedia.org/wiki/Cubic_Hermite_spline
*/

Vector3 hermiteInterpolation(float t, Vector3 p0, Vector3 p1, Vector3 m0, Vector3 m1) {
  float t2 = t*t;
  float t3 = t*t*t;
  float h00 = 2*t3 - 3*t2 + 1;
  float h10 = t3 - 2*t2 + t;
  float h01 = -2*t3 + 3*t2;
  float h11 = t3 - t2;
  Vector3 h00p0 = Vector3.Multiply(p0, h00);
  Vector3 h10m0 = Vector3.Multiply(m0, h10);
  Vector3 h01p1 = Vector3.Multiply(p1, h01);
  Vector3 h11m1 = Vector3.Multiply(m1, h11);
  Vector3 first = Vector3.Add(h00p0, h10m0);
  Vector3 second = Vector3.Add(h01p1, h11m1);
  println(Vector3.Add(first,second));
  return Vector3.Add(first,second);
}


/*private static final int SPLINE_THRESH = 3;

void drawSpline(Graphics graphics, int x1, int y1, int x2, int y2, int x3, int y3) {
    int xa, ya, xb, yb, xc, yc, xp, yp;

    xa = (x1 + x2) / 2;/*from w  w w  . j  a  v  a2s.  com
    ya = (y1 + y2) / 2;
    xc = (x2 + x3) / 2;
    yc = (y2 + y3) / 2;
    xb = (xa + xc) / 2;
    yb = (ya + yc) / 2;

    xp = (x1 + xb) / 2;
    yp = (y1 + yb) / 2;
    if (Math.abs(xa - xp) + Math.abs(ya - yp) > SPLINE_THRESH)
        drawSpline(graphics, x1, y1, xa, ya, xb, yb);
    else
        graphics.drawLine(x1, y1, xb, yb);

    xp = (x3 + xb) / 2;
    yp = (y3 + yb) / 2;
    if (Math.abs(xc - xp) + Math.abs(yc - yp) > SPLINE_THRESH)
        drawSpline(graphics, xb, yb, xc, yc, x3, y3);
    else
        graphics.drawLine(xb, yb, x3, y3);
} */






/**
 * 3D Vector class with X, Y and Z coordinates.
 * 
 * <para>The class incapsulates X, Y and Z coordinates of a 3D vector and
 * provides some operations with it.</para>
 */
public static class Vector3 {
    /**
     * X coordinate of the vector.
     */
    public float x;
    /**
     * Y coordinate of the vector.
     */
    public float y;
    /**
     * Z coordinate of the vector.
     */
    public float z;
    /**
     * Initialize a new instance of the Vector3 class.
     */
    public Vector3() {}

    /**
     * Initialize a new instance of the Vector3 class.
     * @param x X coordinate of the vector.
     * @param y Y coordinate of the vector.
     * @param z Z coordinate of the vector.
     */
    public Vector3(float x, float y, float z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }
    
    /**
     * Initialize a new instance of the Vector3 class.
     * @param value Value, which is set to all 3 coordinates of the vector.
     */
    public Vector3(float value){
        x = y = z = value;
    }
    
    /**
     * Get maximum value of the vector.
     * @return Returns maximum value of all 3 vector's coordinates.
     */
    public float getMax(){
        return ( x > y ) ? ( ( x > z ) ? x : z ) : ( ( y > z ) ? y : z );
    }
    
    /**
     * Get minimum value of the vector.
     * @return Returns minimum value of all 3 vector's coordinates.
     */
    public float getMin(){
        return ( x < y ) ? ( ( x < z ) ? x : z ) : ( ( y < z ) ? y : z );
    }
    
    /**
     * Get index of the coordinate with maximum value.
     * @return Index of the coordinate with maximum value.
     */
    public int getMaxIndex(){
        return ( x >= y ) ? ( ( x >= z ) ? 0 : 2 ) : ( ( y >= z ) ? 1 : 2 );
    }
    
    /**
     * Get index of the coordinate with minimum value.
     * @return Index of the coordinate with minimum value.
     */
    public int getMinIndex(){
        return ( x <= y ) ? ( ( x <= z ) ? 0 : 2 ) : ( ( y <= z ) ? 1 : 2 );
    }
    
    /**
     * Returns vector's normalization.
     * @return Euclidean normalization of the vector, which is a square root of the sum.
     */
    public float Norm(){
        return (float) Math.sqrt( x * x + y * y + z * z );
    }
    
    /**
     * Returns square of the vector's norm.
     * @return Square of the vector's norm.
     */
    public float Square(){
        return x * x + y * y+ z * z;
    }
    
    /**
     * Returns array representation of the vector.
     * @return Array with 3 values containing X/Y/Z coordinates.
     */
    public float[] toArray(){
        return new float[] {x,y,z};
    }
    
    /**
     * Adds corresponding coordinates of two vectors.
     * @param vector1 First vector to use for dot product calculation.
     * @param vector2 Second vector to use for dot product calculation.
     * @return Returns a vector which coordinates are equal to sum of corresponding coordinates of the two specified vectors.
     */
    public static Vector3 Add(Vector3 vector1, Vector3 vector2){
        return new Vector3( vector1.x + vector2.x, vector1.y + vector2.y, vector1.z + vector2.z );
    }
    
    /**
     * Adds a value to all coordinates of the specified vector.
     * @param vector Vector to add the specified value to.
     * @param value Value to add to all coordinates of the vector.
     * @return Returns new vector with all coordinates increased by the specified value.
     */
    public static  Vector3 Add(Vector3 vector, float value){
        return new Vector3( vector.x + value, vector.y + value, vector.z + value );
    }
    
    /**
     * Subtracts corresponding coordinates of two vectors.
     * @param vector1 First vector to use for dot product calculation.
     * @param vector2 Second vector to use for dot product calculation.
     * @return Returns a vector which coordinates are equal to difference of corresponding coordinates of the two specified vectors.
     */
    public Vector3 Subtract(Vector3 vector1, Vector3 vector2){
        return new Vector3( vector1.x - vector2.x, vector1.y - vector2.y, vector1.z - vector2.z );
    }
    
    /**
     * Subtracts a value from all coordinates of the specified vector.
     * @param vector Vector to subtract the specified value from.
     * @param value Value to subtract from all coordinates of the vector.
     * @return Returns new vector with all coordinates decreased by the specified value.
     */
    public Vector3 Subtract(Vector3 vector, float value){
        return new Vector3( vector.x - value, vector.y - value, vector.z - value );
    }
    
    /**
     * Multiplies corresponding coordinates of two vectors.
     * @param vector1 The first vector to multiply.
     * @param vector2 The second vector to multiply.
     * @return Returns a vector which coordinates are equal to multiplication of corresponding coordinates of the two specified vectors.
     */
    public Vector3 Multiply(Vector3 vector1, Vector3 vector2){
        return new Vector3( vector1.x * vector2.x, vector1.y * vector2.y, vector1.z * vector2.z );
    }
    
    /**
     * Multiplies coordinates of the specified vector by the specified factor.
     * @param vector Vector to multiply coordinates of.
     * @param factor Factor to multiple coordinates of the specified vector by.
     * @return Returns new vector with all coordinates multiplied by the specified factor.
     */
    public static Vector3 Multiply(Vector3 vector, float factor){
        return new Vector3( vector.x * factor, vector.y * factor, vector.z * factor );
    }
    
    /**
     * Divides corresponding coordinates of two vectors.
     * @param vector1 The first vector to divide.
     * @param vector2 The second vector to divide.
     * @return Returns a vector which coordinates are equal to coordinates of the first vector divided by corresponding coordinates of the second vector.
     */
    public Vector3 Divide(Vector3 vector1, Vector3 vector2){
        return new Vector3( vector1.x / vector2.x, vector1.y / vector2.y, vector1.z / vector2.z );
    }
    
    /**
     * Divides coordinates of the specified vector by the specified factor.
     * @param vector Vector to divide coordinates of.
     * @param factor Factor to divide coordinates of the specified vector by.
     * @return Returns new vector with all coordinates divided by the specified factor.
     */
    public Vector3 Divide(Vector3 vector, float factor){
        return new Vector3( vector.x / factor, vector.y / factor, vector.z / factor );
    }
    
    /**
     * Normalizes the vector by dividing it’s all coordinates with the vector's norm.
     * @return Returns the value of vectors’ norm before normalization.
     */
    public float Normalize( ){
        float norm = (float) Math.sqrt( x * x + y * y + z * z );
        float invNorm = 1.0f / norm;

        x *= invNorm;
        y *= invNorm;
        z *= invNorm;

        return norm;
    }
    
    /**
     * Inverse the vector.
     * @return Returns a vector with all coordinates equal to 1.0 divided by the value of corresponding coordinate
     * in this vector (or equal to 0.0 if this vector has corresponding coordinate also set to 0.0).
     */
    public Vector3 Inverse( ){
        return new Vector3(
            ( x == 0 ) ? 0 : 1.0f / z,
            ( y == 0 ) ? 0 : 1.0f / y,
            ( z == 0 ) ? 0 : 1.0f / z );
    }
    
    /**
     * Calculate absolute values of the vector.
     * @return Returns a vector with all coordinates equal to absolute values of this vector's coordinates.
     */
    public Vector3 Abs(){
        return new Vector3( Math.abs( x ), Math.abs( y ), Math.abs( z ) );
    }
    
    /**
     * Calculates cross product of two vectors.
     * @param vector1 First vector to use for cross product calculation.
     * @param vector2 Second vector to use for cross product calculation.
     * @return Returns cross product of the two specified vectors.
     */
    public Vector3 Cross( Vector3 vector1, Vector3 vector2 ){
        return new Vector3(
            vector1.y * vector2.z - vector1.z * vector2.y,
            vector1.z * vector2.x - vector1.x * vector2.z,
            vector1.x * vector2.y - vector1.y * vector2.x );
    }
    
    /**
     * Calculates dot product of two vectors.
     * @param vector1 First vector to use for dot product calculation.
     * @param vector2 Second vector to use for dot product calculation.
     * @return Returns dot product of the two specified vectors.
     */
    public float Dot( Vector3 vector1, Vector3 vector2 ){
        return vector1.x * vector2.x + vector1.y * vector2.y + vector1.z * vector2.z;
    }
    
    /**
     * Converts the vector to a 4D vector.
     * 
     * <para>The method returns a 4D vector which has X, Y and Z coordinates equal to the
     * coordinates of this 3D vector and Vector.W coordinate set to 1.0.
     * 
     * @return Returns 4D vector which is an extension of the 3D vector.
     */
   
    
    @Override
    public boolean equals(Object obj){
        if (obj.getClass().isAssignableFrom(Vector3.class)) {
            Vector3 v = (Vector3)obj;
            if ((this.x == v.x) && (this.y == v.y) && (this.z == v.z)) {
                return true;
            }
        }
        return false;
    }
    
    
}

