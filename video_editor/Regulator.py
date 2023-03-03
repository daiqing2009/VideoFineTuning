import cv2
import imutils
from imutils.video import FPS

FRAME_TITLE = "Review analyzed video"
COLOR_LEYE_BB = (0, 255, 0)
COLOR_REYE_BB = (255, 0, 0)
COLOR_LEYE_ROI = (0, 255, 127)
COLOR_REYE_ROI = (255, 0, 127)


class Regulator(object):
    """
    This class analyze vidoe and export frame by frame result to folder
    """

    def __init__(self) -> None:
        # self.analyzer = analyzer
        # self.mutator = mutator
        pass

    @staticmethod
    def _reviewROI_(img, leyeROI, reyeROI, delay):
        # pause on not tracked frame or key's' pressed
        key = cv2.waitKey(delay) & 0xFF
        #FIXME: show up existing left or right eye ROIs
        cv2.imshow(FRAME_TITLE, img)
        if key == ord("l"):
            # draw on the new frame
            frame = img.copy()
            # select the bounding box of left eye
            leyeROI = cv2.selectROI(FRAME_TITLE, frame, fromCenter=False,
                                    showCrosshair=True)
            (x, y, w, h) = [int(v) for v in leyeROI]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          COLOR_LEYE_ROI, 2)
            if (reyeROI):
                (x, y, w, h) = [int(v) for v in reyeROI]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              COLOR_REYE_ROI, 2)
            cv2.imshow(FRAME_TITLE, frame)
            return Regulator._reviewROI_(img, leyeROI, reyeROI, 0)
        if key == ord("r"):
            # draw on the new frame
            frame = img.copy()
            # select the bounding box of left eye
            reyeROI = cv2.selectROI(FRAME_TITLE, frame, fromCenter=False,
                                    showCrosshair=True)
            if (leyeROI):
                (x, y, w, h) = [int(v) for v in leyeROI]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              COLOR_LEYE_ROI, 2)
            (x, y, w, h) = [int(v) for v in reyeROI]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          COLOR_REYE_ROI, 2)
            cv2.imshow(FRAME_TITLE, frame)
            return Regulator._reviewROI_(img, leyeROI, reyeROI, 0)

        elif key == ord("n"):
            # continue to next frame
            # FIXME: check for ROI

            return leyeROI, reyeROI, "n"
        # elif key == ord("p"):
        #     # continue to previous frame
        #     return leftEyeBB, rightEyeBB, "p"
        elif key == ord("g"):
            # continue to play mode
            # FIXME: check for ROI
            return leyeROI, reyeROI, 'g'
        else:
            # FIXME: proper prompt if error key pressed
            return leyeROI, reyeROI, 'g'
            # return Regulator._reviewROI_(img, leyeROI, reyeROI, 0)

    def review(self, analyzer, mutator):
        # TODO: enhance: retrieve full report for review
        frameNo = 0
        stickKey = None
        grabed, frame, report = analyzer.retrieve(frameNo)
        print("review frame({}) grabed=({})".format(frameNo, grabed))
        (H, W) = frame.shape[:2]
        print("review on frame of size ({}*{})".format(H, W))
        fps = FPS().start()

        while grabed:
            (frameNo, leftEyeBB, rightEyeBB, confid) = report
            if confid:
                # print(leftEyeBB)
                (x, y, w, h) = [int(v) for v in leftEyeBB]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              COLOR_LEYE_BB, 2)
                # print(rightEyeBB)
                (x, y, w, h) = [int(v) for v in rightEyeBB]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (255, 0, 0), 2)
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
                print("not tracked or detected")
                stickKey = "n"

            # show the output frame
            # cv2.imshow(FRAME_TITLE, frame)
            if (stickKey):
                #FIXME: stick left and right ROIs together with stickKey
                (leyeROI, reyeROI, stickKey) = Regulator._reviewROI_(
                    frame, None, None, 0)
                if (leyeROI):
                    lefEyeBB = leyeROI
                if (reyeROI):
                    rightEyeBB = reyeROI
                analyzer.archive((frameNo, lefEyeBB, rightEyeBB, True))
                if (stickKey == 'c'):
                    # TODO: restart tracky Eye from current frame on
                    # analyzer.trackEye(frameNo)
                    stickKey = None
            else:
                (leyeROI, reyeROI, stickKey) = Regulator._reviewROI_(
                    frame, None, None, 1)
                if (leyeROI):
                    lefEyeBB = leyeROI
                if (reyeROI):
                    rightEyeBB = reyeROI
                analyzer.archive((frameNo,leftEyeBB,rightEyeBB, True))
            frameNo += 1
            grabed, frame, report = analyzer.retrieve(frameNo)

        cv2.destroyAllWindows()

        # TODO: appove before mutate
        # ok, videoPath = mutator.mutate(analyzer)
