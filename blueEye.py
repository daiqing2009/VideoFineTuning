"""
Tracking of 
"""

import cv2
from video_editor import GazeTracking
from moviepy.editor import VideoFileClip
import numpy as np
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import dlib

gaze = GazeTracking()
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("models/shape_predictor_5_face_landmarks.dat")

#TODO: read all files in certain folder
fileToProcess = "/Users/qing/demos/movie/GazeTracking/clips/12月21日4.mov"
fileToSave = "/Users/qing/demos/movie/GazeTracking/bluredClips/blured12月21日4.mp4"
# output = cv2.VideoWriter(
#     fileToProcess, cv2.VideoWriter_fourcc(*'MPEG'), cv2.CAP_PROP_FPS, (cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FRAME_WIDTH))

# write to clip
clip = VideoFileClip(fileToProcess)

# initialize prvs
frame = imutils.resize(clip.get_frame(0), width=400)
prvs = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

EYE_WIDTH = 60
EYE_HEIGHT = 30
EYE_WID_OFFSET = EYE_WIDTH/2
EYE_HGT_OFFSET = EYE_HEIGHT/2

last_left_pupil = (0,0)
last_right_pupil = (0,0)
est_left_pupil = (0,0)
est_right_pupil = (0,0)

window1d = np.abs(np.blackman(9))
window2d = np.sqrt(np.outer(window1d,window1d))

windowNorm = window2d/np.sum(window2d)
print(np.sum(windowNorm))

def getEstimatedPos(pupilPos,flow):
    (x, y) = pupilPos
    deltaX = int(flow[y][x][0])
    deltaY = int(flow[y][x][1])
    return (x + deltaX, y + deltaY)

def blur(image):
    frame = image.copy()
    # grab the frame from the threaded video stream, resize it to
	# have a maximum width of 400 pixels, and convert it to
	# grayscale
    frame = imutils.resize(frame, width=400)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # blur the pic
    blured = cv2.blur(frame,(int(frame.shape[0]*.05),int(frame.shape[0]*.05)))

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)
    #locate left and right pupil 
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    #make the estimated index global
    global last_left_pupil, last_right_pupil

    # detect faces in the grayscale frame
    rects = detector(gray, 0)
	# check to see if a face was detected, and if so, draw the total
	# number of faces on the frame
    if len(rects) > 0:
        text = "{} face(s) found".format(len(rects))
        cv2.putText(frame, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (0, 0, 255), 2)

    # loop over the face detections
    for rect in rects:
		# compute the bounding box of the face and draw it on the
		# frame
        (bX, bY, bW, bH) = face_utils.rect_to_bb(rect)
        cv2.rectangle(frame, (bX, bY), (bX + bW, bY + bH),
			(0, 255, 0), 1)
		# determine the facial landmarks for the face region, then
		# convert the facial landmark (x, y)-coordinates to a NumPy
		# array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        # print(shape.shape)
        # print(shape[3:5,])
        # print(np.average(shape[2:4,],axis=0))
        est_left_pupil = np.average(shape[2:4,],axis=0)
        est_right_pupil = np.average(shape[0:2,],axis=0)
 		# loop over the (x, y)-coordinates for the facial landmarks
		# and draw each of them
        # for (i, (x, y)) in enumerate(shape):
        #     cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
        #     cv2.putText(frame, str(i + 1), (x - 10, y - 10),
		# 		cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # global prvs
    # flow = cv2.calcOpticalFlowFarneback(prvs, gray, None, 0.5, 3, 10, 3, 5, 1.1, 0)
    # # flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 20, 3, 7, 1.5, 0)
    # prvs = gray

    # global est_left_pupil,est_right_pupil
    # est_left_pupil = getEstimatedPos(last_left_pupil, flow)
    # est_right_pupil = getEstimatedPos(last_right_pupil, flow)

    # est_right_pupil
    # print(flow)
    # print(np.array(flow).shape)
    if(left_pupil):
        (x, y) = left_pupil
        (est_x, est_y) = est_left_pupil
        xdiff = x - est_x
        ydiff = y - est_y
        if(xdiff>10 or xdiff<-10 or ydiff>10 or ydiff<-10):
            print("xdiffLeft="+str(xdiff)+"&ydiffLeft="+str(ydiff))
    else:
        # (x_left, y_left) = est_left_pupil
        left_pupil = last_left_pupil
    last_left_pupil = left_pupil

    if(right_pupil):
        (x, y) = right_pupil
        (est_x, est_y) = est_right_pupil
        xdiff = x - est_x
        ydiff = y - est_y
        if(xdiff>10 or xdiff<-10 or ydiff>10 or ydiff<-10):
            print("xdiffRigt="+str(xdiff)+"&ydiffright="+str(ydiff))
    else:
        right_pupil = last_right_pupil

    last_right_pupil = right_pupil
    # cv2.circle(frame,left_pupil, EYE_WIDTH, (0,0,255), -1)
    (x,y) = left_pupil
    bbox = [x-EYE_WID_OFFSET,y-EYE_HGT_OFFSET,EYE_WIDTH,EYE_HEIGHT]
    bluredroi = blured[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])]          
    frame[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])] = bluredroi

    (x,y) = right_pupil
    bbox = [x-EYE_WID_OFFSET,y-EYE_HGT_OFFSET,EYE_WIDTH,EYE_HEIGHT]
    bluredroi = blured[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])]          
    frame[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])] = bluredroi

    return frame

clip_blurred = clip.fl_image(blur)
clip_blurred.write_videofile(fileToSave) 

