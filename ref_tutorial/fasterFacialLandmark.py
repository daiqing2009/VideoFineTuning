# import the necessary packages
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import cv2
import os
from moviepy.editor import VideoFileClip

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-p", "--shape-predictor", required=True,
# 	help="path to facial landmark predictor")
# args = vars(ap.parse_args())
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
currentDir = os.path.dirname(__file__)

# initialize dlib's face detector (HOG-based) and then create the
# facial landmark predictor
print("[INFO] loading facial landmark predictor...")
 
detector = dlib.get_frontal_face_detector()
# model_path = os.path.join(currentDir, 'models/shape_predictor_68_face_landmarks_GTX.dat')
model_path = os.path.join(currentDir, 'models/shape_predictor_5_face_landmarks.dat')
predictor = dlib.shape_predictor(model_path)
# initialize the video stream and sleep for a bit, allowing the
# camera sensor to warm up
# print("[INFO] camera sensor warming up...")
# vs = VideoStream(src=1).start()
# vs = VideoStream(usePiCamera=True).start() # Raspberry Pi
# time.sleep(2.0)

fileToProcess = os.path.join(currentDir, '../video/DemoEye1.mp4')
fileToSave = os.path.join(currentDir, '../video_edited/DemoEye1.mp4')

clip = VideoFileClip(fileToProcess)

missFrameCount = 0

# loop over the frames from the video stream
def markFace(image):
	# grab the frame from the threaded video stream, resize it to
	# have a maximum width of 400 pixels, and convert it to
	# grayscale
	frame = image.copy()
	# frame = imutils.resize(frame, width=400)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
	# detect faces in the grayscale frame
	global missFrameCount
	rects = detector(gray, 0)
	# check to see if a face was detected, and if so, draw the total
	# number of faces on the frame
	if len(rects) > 0:
		text = "{} face(s) found".format(len(rects))
		cv2.putText(frame, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (0, 0, 255), 2)
	else:
		missFrameCount = missFrameCount +1

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
		print(shape)
		shape = face_utils.shape_to_np(shape)
		
		# loop over the (x, y)-coordinates for the facial landmarks
		# and draw each of them
		for (i, (x, y)) in enumerate(shape):
			cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
			cv2.putText(frame, str(i + 1), (x - 10, y - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	return frame

clip_blurred = clip.fl_image(markFace)
clip_blurred.write_videofile(fileToSave) 
