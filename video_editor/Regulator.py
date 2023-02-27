import cv2
import imutils
from imutils.video import FPS

class Regulator(object):
    """
    This class analyze vidoe and export frame by frame result to folder
    """
    
    def __init__(self) -> None:
        # self.analyzer = analyzer
        # self.mutator = mutator
        pass

    def review(self,analyzer, mutator):
        #TODO: enhance: retrieve full report for review 
        frameNo = 0
        #FIXME: always return false in retrieve
        success, frame, report = analyzer.retrieve(frameNo)
        print(frame)
        (H, W) = frame.shape[:2]
        (frameNo, leftEyeBB, rightEyeBB, confid ) = report
        fps = FPS().start()

        while success:
            (frameNo, leftEyeBB, rightEyeBB, confid ) = report
            if confid:
                (x, y, w, h) = [int(v) for v in leftEyeBB]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                            (0, 255, 0), 2)
                (x, y, w, h) = [int(v) for v in rightEyeBB]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                            (0, 255, 0), 2)
                # update the FPS counter
                fps.update()
                fps.stop()
                # initialize the set of information we'll be displaying on
                # the frame
                info = [
                    ("Success", "Yes" if success else "No"),
                    ("FPS", "{:.2f}".format(fps.fps())),
                ]
                # loop over the info tuples and draw them on our frame
                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                #TODO: mutate on review
                #TODO: show muated frame in parrallel with original one
            else:
                # pause on error frame and rectify it than continue tracking
                while True:
                    key = cv2.waitKey(0) & 0xFF
                    if key == ord("l"):
                        # select the bounding box of the object we want to track (make
                        # sure you press ENTER or SPACE after selecting the ROI)
                        leftEyeBB = cv2.selectROI("leftEyeBB", frame, fromCenter=False,
                                            showCrosshair=True)
                    if key == ord("r"):
                        # select the bounding box of the object we want to track (make
                        # sure you press ENTER or SPACE after selecting the ROI)
                        rightEyeBB = cv2.selectROI("rightEyeBB", frame, fromCenter=False,
                                            showCrosshair=True)
                 
                    # if the `q` key was pressed, break from the loop
                    elif key == ord("q"):
                        break
                (x, y, w, h) = [int(v) for v in leftEyeBB]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                            (0, 255, 0), 2)  
                (x, y, w, h) = [int(v) for v in rightEyeBB]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                            (0, 255, 0), 2)                       
                analyzer.archive((frameNo,leftEyeBB,rightEyeBB, True))      
                analyzer.trackEye(frameNo)
            # show the output frame
            cv2.imshow("Frame", frame)
            frame += 1
            success, frame, report = analyzer.retrieve(frameNo)

        cv2.destroyAllWindows()
        
        # TODO: appove before mutate
        # ok, videoPath = mutator.mutate(analyzer)
        