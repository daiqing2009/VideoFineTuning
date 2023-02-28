import os
import pickle
import cv2
import dlib
import imutils
from imutils import face_utils


class Analyzer(object):

    """
    This class analyze vidoe and export frame by frame result to folder
    """
    def __init__(self, video_path, resizedWidth=400):
        cwd = os.path.abspath(os.path.dirname(__file__))

        if (os.path.exists(video_path) and os.path.isfile(video_path)):
            self.reportName = os.path.basename(video_path)
            self.reportFile = os.path.abspath(os.path.join(cwd, "data/{}.pkl".format(self.reportName)))
            if (os.path.exists(self.reportFile)):
                fileR = open(self.reportFile, "rb")
                self.reports = pickle.load(fileR)
                print("report {} with length({}) loaded".format(self.reportName,len(self.reports)))
            else:
                self.reports = []
                print("empty reports initialized")
        else:
            raise ValueError(
                "{} doesn't exist or is Not a file".format(video_path))

        self._cap = cv2.VideoCapture(video_path)
        self._fno = 0
        self.resizeWidth = resizedWidth
        # list of reports
        total = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # _trackers to track both eyes
        self.leftEyeTracker = cv2.TrackerCSRT_create()
        self.rightEyeTracker = cv2.TrackerCSRT_create()

        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        model_path = os.path.abspath(os.path.join(
            cwd, "trained_models/shape_predictor_68_face_landmarks_GTX.dat"))
        self._predictor = dlib.shape_predictor(model_path)
        # TODO:  detection via CNN if in enhanced mode

    def __del__(self):
        # dump analyzed report to file 
        fileW = open(self.reportFile, "wb")
        pickle.dump(self.reports, fileW)
        self._cap.release()

    def _detectEyes(self, frame):
        # initilize the bounding box of both eyes
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self._face_detector(gray, 0)
        if(len(rects)>0):
            rect = rects[0]  # Assume only one face
            shape = self._predictor(gray, rect)
            coords = face_utils.shape_to_np(shape)
            leftEyeBB = cv2.boundingRect(coords[42:48,])
            rightEyeBB = cv2.boundingRect(coords[36:42,])
            return True, leftEyeBB, rightEyeBB
        else:
            return False, None, None
        
    def trackEye(self, frameNo=0, stopOnTracked = False):
        """
        track eye from certain frame
        """
        grabed, frame, report = self.retrieve(frameNo)
        if report:
            (frameNo, leftEyeBB, rightEyeBB, confid) = report
            print("init trackers with frame({}) grabed({}) with tracked({}) result Bounding Box".format(frameNo, grabed, confid))
        else:
            #TODO: treat detection failure
            (detected, leftEyeBB, rightEyeBB) = self._detectEyes(frame)
            print("init trackers with frame({}) grabed({}) with detected({}) result Bounding Box".format(frameNo, grabed, detected))

        self.leftEyeTracker.init(frame, leftEyeBB)
        self.rightEyeTracker.init(frame, rightEyeBB)

        while grabed:
            # TODO: calculate confidence level more complex way
            if report:
                (frameNo, leftEyeBB, rightEyeBB, confid) = report
                if(stopOnTracked and confid):
                    break
            else:
                confid = True
                # grab the bounding box coordinates of the object
                (tracked, leftEyeBB) = self.leftEyeTracker.update(frame)
                confid = tracked and confid
                leftEyeBB = leftEyeBB
                # check to see if the tracking was a success
                # if success:
                #     (x, y, w, h) = [int(v) for v in leftEyeBB]
                #     report.leftEyeBB = (x, y, w, h)

                (tracked, rightEyeBB) = self.rightEyeTracker.update(frame)
                confid = tracked and confid
                rightEyeBB = rightEyeBB
                # if success:
                #     (x, y, w, h) = [int(v) for v in rightEyeBB]
                #     report.rightEyeBB = (x, y, w, h)
                if(not confid):
                    (detected, leftEyeBB, rightEyeBB) = self._detectEyes(frame)
                    confid = detected and confid
                self.archive((frameNo, leftEyeBB, rightEyeBB, confid))

            frameNo += 1
            grabed, frame, report = self.retrieve(frameNo)

    def retrieve(self, frameNo=0):
        """
        return the frame as well as the report of certain frame
        """
        grabed = True
        frame = None
        report = None
        if (frameNo < self._fno):
            # support rewind case
            print("retrieve rewinded: current frameNo={} and request frameNo={}".format(self._fno,frameNo))
            #TODO: rewind to nearest cached frame/thumbnail
            self._fno = 0
            
        # skip to frame to track without decoding
        while frameNo >= self._fno and grabed:
            self._fno += 1
            grabed = self._cap.grab()
            # print("Frame{} grabed for request for frame{}".format(
            #     self._fno, frameNo))
        if (grabed):
            retrieved, img = self._cap.retrieve()
            print("Frame({}) retrieved={}".format(self._fno,retrieved))
            frame = imutils.resize(img, self.resizeWidth)
            self.frame = frame
        # retrive the report
        if (len(self.reports) > frameNo):
            report = self.reports[frameNo]

        return grabed, frame, report

    def archive(self, report):
        """
        set the report rectified by report
        """
        (frameNo, initLeftEyeBB, initRightEyeBB, confid) = report
        len_report = len(self.reports)
        # length check if reports already processed certain frame
        if (frameNo == len_report):
            self.reports.append(report)
        elif (frameNo < len_report):
            self.reports[frameNo] = report
        else:
            print("error archive")



