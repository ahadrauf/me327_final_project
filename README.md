# Directional Vibration Cues for 3D Virtual Tracking
## ME 327 Final Project, Spring 2022

Our project will investigate how directional vibration feedback can affect tracking performance in a virtual environment. The system is based on the Buzzwire children’s toy, the physical version of which involves traversing a wire using a loop and wand that closes a circuit and makes a sound when the loop touches the wire. We plan to build a virtual version of this setup, where users hold a tracked wand and attempt to traverse a virtual “wire” modeling using a parametric spline curve. Although traditional Buzzwire games only use a single vibration feedback when the loop and wire collide, we hypothesize that ramping the vibration amplitude as the loop approaches the wire can help users re-center the loop more reliably than when just relying on visual information. We also propose creating a spatial gradient in the vibration around the user’s wrist to investigate whether directional information can further improve this reliability. We envision this can be a fun and engaging demonstration on how haptic cues can improve user performance in dynamic and physically dexterous situations.

## Installation
This code was built using Python 3.7, and requires the following packages:
 * NumPy
 * Matplotlib
 * OpenCV
 * imutils (tentative)
 * pupil-apriltags (https://pypi.org/project/pupil-apriltags/)

You'll also need to generate AprilTags, which is in general kinda difficult. Thanks to 
https://github.com/AprilRobotics/apriltag-imgs for generating a wide swath of popular AprilTags!
