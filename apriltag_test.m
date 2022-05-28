clear; clc;

%% Set up webcam
cam = webcam(1, 'Resolution', '352x288');  % cam.AvailableResolutions
intrinsics = cameraIntrinsics([263.5568 269.5951], [179.0278 147.3135], [288 352], 'RadialDistortion', [0.1392 -0.1443]);

%% AR Tag Files
dataFolder = fullfile(tempdir, 'apriltag-imgs', filesep);
tagFamily = 'tag36h11';
INCH_TO_METERS = 0.0254;
tagSize = 2.875*INCH_TO_METERS;

%% Main Loop
tic;
for i=1:1000
    frame = snapshot(cam);
    frame = undistortImage(frame,intrinsics,"OutputView","same");
    [id, loc, pose] = readAprilTag(frame, tagFamily, intrinsics, tagSize);
    
    worldPoints = [0 0 0; tagSize/2 0 0; 0 tagSize/2 0; 0 0 tagSize/2];
    
    for j = 1:length(pose)
        % Get image coordinates for axes.
        imagePoints = worldToImage(intrinsics,pose(j).Rotation, ...
                      pose(j).Translation,worldPoints);

        % Draw colored axes.
        frame = insertShape(frame,"Line",[imagePoints(1,:) imagePoints(2,:); ...
            imagePoints(1,:) imagePoints(3,:); imagePoints(1,:) imagePoints(4,:)], ...
            "Color",["red","green","blue"],"LineWidth",7);

%         frame = insertText(frame,loc(1,:,j),id(j),"BoxOpacity",1,"FontSize",25);
    end
    imshow(frame);
end
toc;

clear('cam');