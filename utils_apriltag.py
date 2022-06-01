import numpy as np
import pupil_apriltags

INCH_TO_METERS = 0.0254


def create_apriltag_detector(nthreads=2) -> pupil_apriltags.Detector:
    apriltag_detector = pupil_apriltags.Detector(families="tag36h11", nthreads=nthreads, quad_decimate=1.0,
                                                 quad_sigma=0.0, refine_edges=1, decode_sharpening=0.5,
                                                 debug=0)
    return apriltag_detector


def detect_apriltag(img: np.ndarray, apriltag_detector: pupil_apriltags.Detector, estimate_tag_pose=True,
                    camera_intrinsics=None, tag_size=None):
    """
    Detect location of apriltag in image and
    :param img: Image to detect apriltag in
    :param apriltag_detector: Apriltag detector (created via create_ar_detector())
    :param estimate_tag_pose: True if you want the return tags array to include pose information. Requires camera
        intrinsics and tag_size to also be specified
    :param camera_intrinsics: Camera intrinsics [cx, cy, fx, fy] (calibrate via https://www.mathworks.com/help/vision/ug/camera-calibration-using-apriltag-markers.html)
    :param tag_size: Size of the tag, in whatever units you want from the translation (e.g. meters)
    :return:
    """
    tags = apriltag_detector.detect(img, estimate_tag_pose=estimate_tag_pose, camera_params=camera_intrinsics,
                                    tag_size=tag_size)
    return tags
