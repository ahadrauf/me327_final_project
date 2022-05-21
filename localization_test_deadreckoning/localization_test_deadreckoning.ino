// Basic demo for accelerometer & gyro readings from Adafruit
// LSM6DSOX sensor
// Calibration results (gyro):  Zero rate offset: (-0.0012217, 0.0006109, -0.0091630) rad/s noise: (0.002, 0.001, 0.001)
// Calibration results (accelerometer):  Zero rate offset: (-0.0669990, -0.0125623, 9.9607219) rad/s noise: (0.036, 0.036, 0.030)
#include <Adafruit_LSM6DSOX.h>

// For SPI mode, we need a CS pin
#define LSM_CS 10
// For software-SPI mode we need SCK/MOSI/MISO pins
#define LSM_SCK 13
#define LSM_MISO 12
#define LSM_MOSI 11

Adafruit_LSM6DSOX sox;

// For position tracking
float x, y, z;
float dx, dy, dz;
float ddx, ddy, ddz;
float theta_x, theta_y, theta_z;
float dtheta_x, dtheta_y, dtheta_z;
float ddtheta_x, ddtheta_y, ddtheta_z;
float alpha = 0.9;  // what proportion of new value to trust
long lastTime = 0;
float minAccel = 0.1;
float minGyro = 0.05;

int delayTime = 1;
float dt = delayTime/1000.0;

// Zero rate offset
float ddx0 = -0.1106681;  // -0.0669990;  // -0.0730;
float ddy0 = -0.2913262;  // -0.0125623;  // 0.0383;
float ddz0 = 9.9720878;  // 9.9607219;  // 9.9452;  // - 9.79936;
float ddtheta_x0 = -0.0012217;
float ddtheta_y0 = 0.0006109;
float ddtheta_z0 = -0.0091630;

// Debugging
int print_every_hz = 10;
int print_every = (int)(1000.0/delayTime/print_every_hz);
int loop_count = 0;
bool plot = true;


void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  if (!sox.begin_I2C()) {
    // if (!sox.begin_SPI(LSM_CS)) {
    // if (!sox.begin_SPI(LSM_CS, LSM_SCK, LSM_MISO, LSM_MOSI)) { 
    // Serial.println("Failed to find LSM6DSOX chip");
    while (1) {
      delay(10);
    }
  }

  if (!plot) {
    Serial.println("LSM6DSOX Found!");
  
    // sox.setAccelRange(LSM6DS_ACCEL_RANGE_2_G);
    Serial.print("Accelerometer range set to: ");
    switch (sox.getAccelRange()) {
    case LSM6DS_ACCEL_RANGE_2_G:
      Serial.println("+-2G");
      break;
    case LSM6DS_ACCEL_RANGE_4_G:
      Serial.println("+-4G");
      break;
    case LSM6DS_ACCEL_RANGE_8_G:
      Serial.println("+-8G");
      break;
    case LSM6DS_ACCEL_RANGE_16_G:
      Serial.println("+-16G");
      break;
    }
  
    // sox.setGyroRange(LSM6DS_GYRO_RANGE_250_DPS );
    Serial.print("Gyro range set to: ");
    switch (sox.getGyroRange()) {
    case LSM6DS_GYRO_RANGE_125_DPS:
      Serial.println("125 degrees/s");
      break;
    case LSM6DS_GYRO_RANGE_250_DPS:
      Serial.println("250 degrees/s");
      break;
    case LSM6DS_GYRO_RANGE_500_DPS:
      Serial.println("500 degrees/s");
      break;
    case LSM6DS_GYRO_RANGE_1000_DPS:
      Serial.println("1000 degrees/s");
      break;
    case LSM6DS_GYRO_RANGE_2000_DPS:
      Serial.println("2000 degrees/s");
      break;
    case ISM330DHCX_GYRO_RANGE_4000_DPS:
      break; // unsupported range for the DSOX
    }
  
    // sox.setAccelDataRate(LSM6DS_RATE_12_5_HZ);
    Serial.print("Accelerometer data rate set to: ");
    switch (sox.getAccelDataRate()) {
    case LSM6DS_RATE_SHUTDOWN:
      Serial.println("0 Hz");
      break;
    case LSM6DS_RATE_12_5_HZ:
      Serial.println("12.5 Hz");
      break;
    case LSM6DS_RATE_26_HZ:
      Serial.println("26 Hz");
      break;
    case LSM6DS_RATE_52_HZ:
      Serial.println("52 Hz");
      break;
    case LSM6DS_RATE_104_HZ:
      Serial.println("104 Hz");
      break;
    case LSM6DS_RATE_208_HZ:
      Serial.println("208 Hz");
      break;
    case LSM6DS_RATE_416_HZ:
      Serial.println("416 Hz");
      break;
    case LSM6DS_RATE_833_HZ:
      Serial.println("833 Hz");
      break;
    case LSM6DS_RATE_1_66K_HZ:
      Serial.println("1.66 KHz");
      break;
    case LSM6DS_RATE_3_33K_HZ:
      Serial.println("3.33 KHz");
      break;
    case LSM6DS_RATE_6_66K_HZ:
      Serial.println("6.66 KHz");
      break;
    }
  
    // sox.setGyroDataRate(LSM6DS_RATE_12_5_HZ);
    Serial.print("Gyro data rate set to: ");
    switch (sox.getGyroDataRate()) {
    case LSM6DS_RATE_SHUTDOWN:
      Serial.println("0 Hz");
      break;
    case LSM6DS_RATE_12_5_HZ:
      Serial.println("12.5 Hz");
      break;
    case LSM6DS_RATE_26_HZ:
      Serial.println("26 Hz");
      break;
    case LSM6DS_RATE_52_HZ:
      Serial.println("52 Hz");
      break;
    case LSM6DS_RATE_104_HZ:
      Serial.println("104 Hz");
      break;
    case LSM6DS_RATE_208_HZ:
      Serial.println("208 Hz");
      break;
    case LSM6DS_RATE_416_HZ:
      Serial.println("416 Hz");
      break;
    case LSM6DS_RATE_833_HZ:
      Serial.println("833 Hz");
      break;
    case LSM6DS_RATE_1_66K_HZ:
      Serial.println("1.66 KHz");
      break;
    case LSM6DS_RATE_3_33K_HZ:
      Serial.println("3.33 KHz");
      break;
    case LSM6DS_RATE_6_66K_HZ:
      Serial.println("6.66 KHz");
      break;
    }

    Serial.print(F("Fetching samples in 3..."));
    delay(1000);
    Serial.print("2...");
    delay(1000);
    Serial.print("1...");
    delay(1000);
    Serial.println("NOW!");
  } else {
    Serial.println("x y z");
  }

  x = y = z = 0.0;
  dx = dy = dz = 0.0;
  theta_x = theta_y = theta_z = 0;
  dtheta_x = dtheta_y = dtheta_z = 0;
  lastTime = millis();
}

void loop() {
  //  /* Get a new normalized sensor event */
  sensors_event_t accel; // accel.acceleration.x (.y, .z) (m/s^2)
  sensors_event_t gyro;  // gyro.gyro.x (.y, .z) (rad/s)
  sensors_event_t temp;  // temp.temperature (deg. C)
  sox.getEvent(&accel, &gyro, &temp);

  // Zero rate offset + filtering
  float currTime = millis();
  dt = (currTime - lastTime)/1000.0;
//  ddx = (accel.acceleration.x - ddx0)*alpha + ddx*(1 - alpha);
//  ddy = (accel.acceleration.y - ddy0)*alpha + ddy*(1 - alpha);
//  ddz = (accel.acceleration.z - ddz0)*alpha + ddz*(1 - alpha);
//  ddtheta_x = (gyro.gyro.x - ddtheta_x0)*alpha + ddtheta_x*(1 - alpha);
//  ddtheta_y = (gyro.gyro.y - ddtheta_y0)*alpha + ddtheta_y*(1 - alpha);
//  ddtheta_z = (gyro.gyro.z - ddtheta_z0)*alpha + ddtheta_z*(1 - alpha);
  ddx = filterAcceleration(accel.acceleration.x, ddx, ddx0, minAccel);
  ddy = filterAcceleration(accel.acceleration.y, ddy, ddy0, minAccel);
  ddz = filterAcceleration(accel.acceleration.z, ddz, ddz0, minAccel);
  ddtheta_x = filterAcceleration(gyro.gyro.x, ddtheta_x, ddtheta_x0, minGyro);
  ddtheta_y = filterAcceleration(gyro.gyro.y, ddtheta_y, ddtheta_y0, minGyro);
  ddtheta_z = filterAcceleration(gyro.gyro.z, ddtheta_z, ddtheta_z0, minGyro);
  

  x += dx*dt + 0.5*ddx*dt*dt;
  y += dy*dt + 0.5*ddy*dt*dt;
  z += dz*dt + 0.5*ddz*dt*dt;
  theta_x += dtheta_x*dt + 0.5*ddtheta_x*dt*dt;
  theta_y += dtheta_y*dt + 0.5*ddtheta_y*dt*dt;
  theta_z += dtheta_z*dt + 0.5*ddtheta_z*dt*dt;
  
//  dx += ddx*dt;
//  dy += ddy*dt;
//  dz += ddz*dt;
//  dtheta_x += ddtheta_x*dt;
//  dtheta_y += ddtheta_y*dt;
//  dtheta_z += ddtheta_z*dt;
  dx = updateVelocity(dx, ddx, minAccel);
  dy = updateVelocity(dy, ddy, minAccel);
  dz = updateVelocity(dz, ddz, minAccel);
  dtheta_x = updateVelocity(dtheta_x, ddtheta_x, minGyro);
  dtheta_y = updateVelocity(dtheta_y, ddtheta_y, minGyro);
  dtheta_z = updateVelocity(dtheta_z, ddtheta_z, minGyro);
  // Print statements
  if (loop_count == print_every) {
//    Serial.print("dt: ");
//    Serial.println(dt);
//    
//    Serial.print("\t\tx: ");
//    Serial.print(x, 5);
//    Serial.print(" \t dx: ");
//    Serial.print(dx, 5);
//    Serial.print(" \t ddx: ");
//    Serial.println(ddx, 5);
//  
//    Serial.print("\t\ty: ");
//    Serial.print(y, 5);
//    Serial.print(" \t dy: ");
//    Serial.print(dy, 5);
//    Serial.print(" \t ddy: ");
//    Serial.println(ddy, 5);
//  
//    Serial.print("\t\tz: ");
//    Serial.print(z, 5);
//    Serial.print(" \t dz: ");
//    Serial.print(dz, 5);
//    Serial.print(" \t ddz: ");
//    Serial.println(ddz, 5);
//  
//    Serial.print("\t\ttheta_x: ");
//    Serial.print(theta_x, 5);
//    Serial.print(" \t dtheta_x: ");
//    Serial.print(dtheta_x, 5);
//    Serial.print(" \t ddx: ");
//    Serial.println(ddtheta_x, 5);
//  
//    Serial.print("\t\ttheta_y: ");
//    Serial.print(theta_y, 5);
//    Serial.print(" \t dtheta_y: ");
//    Serial.print(dtheta_y, 5);
//    Serial.print(" \t ddy: ");
//    Serial.println(ddtheta_y, 5);
//  
//    Serial.print("\t\ttheta_z: ");
//    Serial.print(theta_z, 5);
//    Serial.print(" \t dtheta_z: ");
//    Serial.print(dtheta_z, 5);
//    Serial.print(" \t ddtheta_z: ");
//    Serial.println(ddtheta_z, 5);

    Serial.print(x*1000);
    Serial.print(",");
    Serial.print(y*1000);
    Serial.print(",");
    Serial.println(z*1000);
  //  Serial.print(",");
  //  Serial.println(dt*1000);
  
//    Serial.print(theta_x);
//    Serial.print(",");
//    Serial.print(theta_y);
//    Serial.print(",");
//    Serial.println(theta_z);
    loop_count = 0;
  }
  
  lastTime = currTime;
  loop_count += 1;
  delay(delayTime);
}

float filterAcceleration(float currAccel, float prevAccel, float zero_offset, float minValue) {
  float filt = (currAccel - zero_offset)*alpha + prevAccel*(1 - alpha);
  if (abs(filt) >= minValue) {
    return filt;
  } else {
    return 0.0;
  }
}

float updateVelocity(float currVelocity, float currAccel, float minAccel) {
  if (abs(currAccel) > minAccel) {
    return currVelocity + currAccel*dt;
  } else {
    return 0.0;
  }
}
