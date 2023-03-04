import cv2
import imutils
from imutils.video import FPS

FRAME_TITLE = "Review analyzed video"
COLOR_LEYE_BB = (0, 255, 0)
COLOR_REYE_BB = (255, 0, 0)
COLOR_LEYE_ROI = (0, 127, 127)
COLOR_REYE_ROI = (127, 0, 127)


class Regulator(object):
    """
    This class analyze vidoe and export frame by frame result to folder
    """

    def __init__(self) -> None:
        # self.analyzer = analyzer
        # self.mutator = mutator
        pass

    @staticmethod
    def _setROI_(img, leyeROI, reyeROI, delay):
        """
        set the ROI of eyes tracked 
        """
        # pause on not tracked frame or key's' pressed
        key = cv2.waitKey(delay) & 0xFF
        #show up existing left or right eye ROIs
        frame = img.copy()
        if (leyeROI):
            (x, y, w, h) = [int(v) for v in leyeROI]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                            COLOR_LEYE_ROI, 2)          
        if (reyeROI):
            (x, y, w, h) = [int(v) for v in reyeROI]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                            COLOR_REYE_ROI, 2)
        cv2.imshow(FRAME_TITLE, frame)

        if key == ord("l"):
            # draw on the new frame
            frame = img.copy()
            # select the bounding box of left eye
            leyeROI = cv2.selectROI(FRAME_TITLE, frame, fromCenter=False,
                                    showCrosshair=True)
            (x, y, w, h) = [int(v) for v in leyeROI]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          COLOR_LEYE_ROI, 2)
            # show existing bounding box of right eye
            if (reyeROI):
                (x, y, w, h) = [int(v) for v in reyeROI]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                                COLOR_REYE_ROI, 2)
            cv2.imshow(FRAME_TITLE, frame)
            return Regulator._setROI_(img, leyeROI, reyeROI, 0)
        if key == ord("r"):
            # draw on the new frame
            frame = img.copy()
            # select the bounding box of left eye
            if (leyeROI):
                (x, y, w, h) = [int(v) for v in leyeROI]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                                COLOR_LEYE_ROI, 2)
            # select existing bounding box of right eye        
            reyeROI = cv2.selectROI(FRAME_TITLE, frame, fromCenter=False,
                                    showCrosshair=True)
            (x, y, w, h) = [int(v) for v in reyeROI]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          COLOR_REYE_ROI, 2)
            cv2.imshow(FRAME_TITLE, frame)
            return Regulator._setROI_(img, leyeROI, reyeROI, 0)

        elif key == ord("n"):
            # continue to next frame
            # FIXME: check for ROI

            return leyeROI, reyeROI, "n"
        # elif key == ord("p"):
        #     # continue to previous frame
        #     return leftEyeBB, rightEyeBB, "p"
        elif key == ord("t"):
            # tracking eye from this frame on
            # FIXME: check for ROI
            return leyeROI, reyeROI, 't'
        else:
            # FIXME: proper prompt for avaialbe key
            return leyeROI, reyeROI, None

    def review(self, analyzer, mutator):
        # TODO: enhance: retrieve full report for review
        frameNo = 0
        stickKey = None
        leyeROI = None
        reyeROI = None
        leftEyeBB = None
        rightEyeBB = None
        grabed, frame, report = analyzer.retrieve(frameNo)
        print("review frame({}) grabed=({})".format(frameNo, grabed))
        (H, W) = frame.shape[:2]
        print("review on frame of size ({}*{})".format(H, W))
        fps = FPS().start()

        while grabed:
            if(report):
                (frameNo, leftEyeBB, rightEyeBB, confid) = report
                if confid:
                    # print(leftEyeBB)
                    (x, y, w, h) = [int(v) for v in leftEyeBB]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                COLOR_LEYE_BB, 2)
                    # print(rightEyeBB)
                    (x, y, w, h) = [int(v) for v in rightEyeBB]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                COLOR_REYE_BB, 2)
                    # update the FPS counter
                    fps.update()
                    fps.stop()
                    # initialize the set of information we'll be displaying on
                    # the frame
                    info = [
                        ("eyes identified", "Yes" if confid else "No"),
                        ("FPS", "{:.2f}".format(fps.fps())),
                    ]
                    # loop over the info tuples and draw them on our frame
                    for (i, (k, v)) in enumerate(info):
                        text = "{}: {}".format(k, v)
                        cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    # TODO: mutate on review
                    # TODO: show muated frame in parrallel with original one
                else:
                    print("not tracked or detected in frame({})".format(frameNo))
                    stickKey = "n"
            else:
                print("no report found in frame({})".format(frameNo))
                stickKey = "n"

            if (stickKey):
                # stick left and right ROIs together with stickKey
                (leyeROI, reyeROI, stickKey) = Regulator._setROI_(
                    frame, leyeROI, reyeROI, 0)
                if (leyeROI):
                    leftEyeBB = leyeROI
                if (reyeROI):
                    rightEyeBB = reyeROI
                analyzer.archive((frameNo, leftEyeBB, rightEyeBB, True))
                if (stickKey == 't'):
                    # TODO: restart tracky Eye from current frame on
                    analyzer.trackEye(frameNo)
                    stickKey = None
            else:
                (leyeROI, reyeROI, stickKey) = Regulator._setROI_(
                    frame, None, None, 1)
                if(stickKey):
                    if (leyeROI):
                        leftEyeBB = leyeROI
                    if (reyeROI):
                        rightEyeBB = reyeROI
                    analyzer.archive((frameNo,leftEyeBB,rightEyeBB, True))
            frameNo += 1
            grabed, frame, report = analyzer.retrieve(frameNo)

        cv2.destroyAllWindows()

        # TODO: appove before mutate
        # ok, videoPath = mutator.mutate(analyzer)
