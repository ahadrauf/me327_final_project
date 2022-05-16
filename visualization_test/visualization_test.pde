PShape can;
float angle;
PShader colorShader;

boolean frameMoved = false;

void setup() {
  size(640, 360, P3D);
  surface.setLocation(100, 100);
  can = createCan(100, 200, 32);
}

void draw() {  
  background(0);
  lights();

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

  textureMode(NORMAL);
  PShape sh = createShape();

  sh.beginShape(QUAD_STRIP);

  sh.noStroke();
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
