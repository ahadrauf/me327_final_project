clear; clc;

%% Set up webcam
cam = webcam(1, 'Resolution', '352x288');  % cam.AvailableResolutions
intrinsics = cameraIntrinsics([263.5568 269.5951], [179.0278 147.3135], [288 352], 'RadialDistortion', [0.1392 -0.1443]);

%% AR Tag Files
dataFolder = fullfile(tempdir, 'apriltag-imgs', filesep);
tagFamily = 'tag36h11';
INCH_TO_METERS = 0.0254;
tagSize = 2.875*INCH_TO_METERS;

%% Define dimensions and helper variables
% Global parameters
easiness_factor = 1.5;
global swap ring_pts_orig handle_pts_orig

% Camera Parameters
INCH_TO_METERS = 0.0254;
% camera_params = [958.9126, 956.1364, 957.4814, 557.8223]  % from matlab calibration, 1920x1080
% camera_params = [443.8266, 443.4999, 320.3827, 247.3580]  % from matlab calibration, 640x480
% camera_params = [233.4269, 232.5352, 214.9525, 123.1879]  % from matlab calibration, 424x240
camera_params = [263.5568, 269.5951, 179.0278, 147.3135];  % from matlab calibration, 352x288
tag_size = 3*INCH_TO_METERS;
swap = [0 0 1; -1 0 0; 0 -1 0];

% Dimensions
thickness = 0.02*2;  % thickness of wand
ring_r_inner = 0.075/2*easiness_factor;  % inner radius of the ring (m)
ring_r_outer = 0.045*easiness_factor;  % outer radius of the ring (m)
handle_length = 0.130;  % handle length
handle_width = 0.03;  % handle width

N_ring = 15;
ring_r_avg = (ring_r_outer + ring_r_inner)/2;
ring_pts_orig = zeros(N_ring, 3);
ring_pts_orig(:,1) = ring_r_avg*cos(linspace(0, 2*pi, N_ring));
ring_pts_orig(:,2) = ring_r_avg*sin(linspace(0, 2*pi, N_ring));
handle_pts_orig = [ring_r_inner, 0, 0; ring_r_outer + handle_length, 0, 0];
ring_pts_x = ring_pts_orig(:, 1);
ring_pts_y = ring_pts_orig(:, 2);
ring_pts_z = ring_pts_orig(:, 3);
handle_pts_x = handle_pts_orig(:, 1);
handle_pts_y = handle_pts_orig(:, 2);
handle_pts_z = handle_pts_orig(:, 3);

N_curve = 100;
curve = generate_curve(0.25, 1.5, N_curve);
curve_midpoints = (curve(2:end, :) + curve(1:end-1, :))/2;

%% Plotting
% plt = plot3(ring_pts_x, ring_pts_y, ring_pts_z, 'LineWidth', 3);
% hold on;
% plot3(handle_pts_x, handle_pts_y, handle_pts_z, 'LineWidth', 3);
% plot3(curve(:,1), curve(:,2), curve(:,3), 'LineWidth', 3);
fig = figure(1);
fig.Position = [10 25 1500 1000];
plts = plot3(ring_pts_x, ring_pts_y, ring_pts_z, "b-", ...
    handle_pts_x, handle_pts_y, handle_pts_z, "b-", ...
    curve(:,1), curve(:,2), curve(:,3), "k-");
xlabel("X");
ylabel("Y");
zlabel("Z");
xlim([0, 2]);
ylim([-0.3, 0.3]);
zlim([-0.3, 0.3]);
view([30, 45]);  % [az, el]
plts(1).XDataSource = "ring_pts_x";
plts(1).YDataSource = "ring_pts_y";
plts(1).ZDataSource = "ring_pts_z";
plts(1).LineWidth = 3;
plts(2).XDataSource = "handle_pts_x";
plts(2).YDataSource = "handle_pts_y";
plts(2).ZDataSource = "handle_pts_z";
plts(2).LineWidth = 3;
plts(3).LineWidth = 3;
% view([95, 5])  % [az, el] (view2)

%% Main Loop
tic;
for i=1:1000
    frame = snapshot(cam);
    frame = undistortImage(frame,intrinsics,"OutputView","same");
    [id, loc, pose] = readAprilTag(frame, tagFamily, intrinsics, tagSize);
    
    if (~isempty(pose))
        [ring_pts, handle_pts] = draw_wand(pose.Translation', pose.Rotation);
        ring_pts_x = ring_pts(:, 1);
        ring_pts_y = ring_pts(:, 2);
        ring_pts_z = ring_pts(:, 3);
        handle_pts_x = handle_pts(:, 1);
        handle_pts_y = handle_pts(:, 2);
        handle_pts_z = handle_pts(:, 3);
        refreshdata
        drawnow
    end
%     worldPoints = [0 0 0; tagSize/2 0 0; 0 tagSize/2 0; 0 0 tagSize/2];
%     for j = 1:length(pose)
%         % Get image coordinates for axes.
%         imagePoints = worldToImage(intrinsics,pose(j).Rotation, ...
%                       pose(j).Translation,worldPoints);
% 
%         % Draw colored axes.
%         frame = insertShape(frame,"Line",[imagePoints(1,:) imagePoints(2,:); ...
%             imagePoints(1,:) imagePoints(3,:); imagePoints(1,:) imagePoints(4,:)], ...
%             "Color",["red","green","blue"],"LineWidth",7);
% 
% %         frame = insertText(frame,loc(1,:,j),id(j),"BoxOpacity",1,"FontSize",25);
%     end
%     imshow(frame);
end
toc;

clear('cam');
disp("Done!");

%% Data functions
function [curve] = generate_curve(xmin, xmax, Nspline)
    curve = zeros(Nspline, 3);
    x_range = linspace(xmin, xmax, Nspline);
    z = @(x) 0.05*(sin(4*x) + cos(7*x));
    for i=1:length(x_range)
        curve(i,:) = [x_range(i), 0, z(x_range(i))];
    end
end

function [ring_pts, handle_pts] = draw_wand(pos, R)
    global swap ring_pts_orig handle_pts_orig
    ring_pts = transpose(swap*R*ring_pts_orig' + swap*pos);
    handle_pts = transpose(swap*R*handle_pts_orig' + swap*pos);
end