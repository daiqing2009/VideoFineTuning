import cv2
import sys
from moviepy.editor import VideoFileClip

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
 
fileToProcess = "Kevin.mp4"
fileToSave = "KevinBlur.mp4"
secondsToSkip = 0
 
if __name__ == '__main__' :
    # first we cut the seconds off of the video
    if secondsToSkip > 0:
        clip = VideoFileClip(fileToProcess).subclip(secondsToSkip)
        clip.write_videofile(fileToSave, codec="mpeg4")
        fileToProcess=fileToSave
 
    # the trackers included in OpenCV version 4.5.1
    # tracker_types = ['MIL','KCF', 'GOTURN', 'CSRT']
    # tracker_type = tracker_types[3]
    # if int(minor_ver) < 3:
    #     tracker = cv2.Tracker_create(tracker_type)
    # else:
    #     if tracker_type == 'MIL':
    #         tracker = cv2.TrackerMIL_create()
    #     if tracker_type == 'KCF':
    #         tracker = cv2.TrackerKCF_create()
    #     if tracker_type == 'GOTURN':
    #         # not working try to remove opencv-contrib-python
    #         tracker = cv2.TrackerGOTURN_create()
    #     if tracker_type == "CSRT":
    #         tracker = cv2.TrackerCSRT_create()
    # replace the tracker with gaze tracking
    gaze = GazeTracking()

    # Read video
    # video = cv2.VideoCapture(fileToProcess)
    video = cv2.VideoCapture(0)

    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()
 
    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print('Cannot read video file')
        sys.exit()
     
    video.release()
 
    # Define an initial bounding box if you know it
#    bbox = (488*2, 266*2, 629*2, 730*2)
 
    # Uncomment the line below to select a different bounding box
    # bbox = cv2.selectROI('Select Area', frame, False)
    # cv2.destroyAllWindows()
 
    # Initialize tracker with first frame and bounding box
    # ok = tracker.init(frame, bbox)


    def blur(image):
        frame = image.copy()
        ok, bbox = tracker.update(frame)
        if ok:
            blured = cv2.blur(frame,(int(frame.shape[0]*.05),int(frame.shape[0]*.05)))
            bluredroi = blured[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])]          
            frame[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])] = bluredroi
            # in case you want a rectangle around the object
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
        else:
            print("Error")
            sys.exit()
        return frame
 
    clip = VideoFileClip(fileToProcess)
    clip_blurred = clip.fl_image(blur)
    clip_blurred.write_videofile(fileToSave) 