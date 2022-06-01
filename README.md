# Directional Vibration Cues for 3D Virtual Tracking
## ME 327 Final Project, Spring 2022

Our project investigated how directional vibration feedback can affect tracking performance in a virtual environment. The system is based on the Buzzwire children’s toy, the physical version of which involves threading a loop through a wire, which makes a sound when the loop touches the wire. We built a virtual version of this setup, where users hold a tracked wand and attempt to traverse a virtual “wire.” Although traditional Buzzwire games only use a single vibration feedback when the loop and wire collide, we also added directional haptic cues in a wristband to explore whether directional information can improve positional tracking or even allow non-sighted users to navigate 3D virtual environments. We first explore the dynamics of directional haptic feedback, showing that (N=3) users can distinguish broad directional cues when vibration motors embedded in the wristband are activated. We then had users play the Buzzwire game under three conditions: with both a visual and directional haptic interface, with only directional haptic cues, and with visual and non-directional haptic cues. We found that users were significantly more steady when following the wire given both visual cues and directional haptic feedback, traversing less than half the distance in freespace compared to either of the alternative modes. Moreover, users were able to traverse the wire with their eyes closed and given only directional cues with only a 15% performance cut compared to when given both visual and haptic cues, in terms of the mean deviation from the center of the wire, highlighting the promise of this feedback approach to future work towards more immersive and accessible virtual environments.

A more detailed description of the project can be found at http://charm.stanford.edu/ME327/Group13.

## Installation
This code was built using Python 3.7, and requires the following packages:
 * NumPy
 * Matplotlib
 * OpenCV
 * imutils (tentative)
 * pupil-apriltags (https://pypi.org/project/pupil-apriltags/)

You'll also need to generate AprilTags, which is in general kinda difficult. Thanks to 
https://github.com/AprilRobotics/apriltag-imgs for generating a wide swath of popular AprilTags!

Finally, you'll need to estimate your [camera intrinsic parameters](https://en.wikipedia.org/wiki/Camera_resectioning) 
in order to obtain decent measurements for position and rotation. The easiest script I found online to do this was 
[this one in Matlab](https://www.mathworks.com/help/vision/ug/camera-calibration-using-apriltag-markers.html), which
requires the Computer Vision toolbox and which can be opened via the command
``openExample('vision/CalibrateCameraUsingAprilTagBasedPatternExample')``

## Bill of Materials
Other than miscellaneous electrical wiring, and heat shrink, the below table contains all of the essential
materials used to build this device. The CAD files for the wand can be found as well as the DXF files used to laser cut
the AR tag's white background circle and black tab can be found in the `CAD\` folder.

| Item         | Price/Each     | Qty | Vendor |
|--------------|-----------|------------|---|
| Arduino Micro | $23.44      | 1        | [Amazon](https://smile.amazon.com/dp/B00AFY2S56) |
| 10-pin Screw Terminal      | $3.35  | 1       |[Adafruit](https://www.adafruit.com/product/2142)|
| Jameco 2189476 Coin Cell Vibration Motors | $0.75 | 4 | [Jameco](https://www.jameco.com/z/C1034B850F-Jameco-Reliapro-9000-RPM-Vibrating-Shaftless-Motor_2189476.html)
| 10-ft USB Micro B Cable | $3.33 | 1 | [Amazon](https://smile.amazon.com/dp/B09P364JW6)
| M4 Screws and Nuts | N/A | 4 | N/A |
| Cardstock (for AR tag background) | N/A | 1 | N/A |
| Ballistic nylon (for AR tag) | N/A | 1 | N/A |