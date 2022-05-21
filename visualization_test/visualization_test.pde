import processing.serial.*;
import java.io.Serializable.*;
import java.util.*;
import java.lang.Math;
//import libomv.types.Vector3;

PShape can;
float angle;
PShader colorShader;

boolean frameMoved = false;

void setup() {
  size(640, 360, P3D);
  surface.setLocation(100, 100);  // Documentation https://processing.org/reference/setLocation_.html
  can = createCan(100, 200, 32);
}

void draw() {  
  background(0);
  lights();
  float fov = PI/3.0;
  float cameraZ = (height/2.0) / tan(fov/2.0);
  perspective(fov, float(width)/float(height), cameraZ/2.0, cameraZ*2.0);

  translate(width/2, height/2);
  rotateY(angle);
  rotateX(.7);
  lights();
  shape(can);

  angle += 0.01;
  println(angle);
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
//Vector3 hermiteInterpolation(float t, Vector3 p0, Vector3 p1, Vector3 m0, Vector3 m1) {
//  float t2 = t*t;
//  float t3 = t*t*t;
//  float h00 = 2*t3 - 3*t2 + 1;
//  float h10 = t3 - 2*t2 + t;
//  float h01 = -2*t3 + 3*t2;
//  float h11 = t3 - t2;
//  return h00*p0 + h10*m0 + h01*p1 + h11*m1;
//}
