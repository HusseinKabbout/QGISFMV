# -*- coding: utf-8 -*-
import traceback

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QCoreApplication
from QGIS_FMV.utils.QgsUtils import QgsUtils as qgsu

try:
    import cv2
except Exception as e:
    qgsu.showUserAndLogMessage(QCoreApplication.translate(
        "VideoProcessor", "Error: Missing OpenCV packages"))

try:
    from pydevd import *
except ImportError:
    None


class ExtractFramesProcessor(QObject):
    ''' Extract All Video Frames in a specific folder '''
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str, Exception, basestring)
    progress = pyqtSignal(float)

    @pyqtSlot(str, str)
    def ExtractFrames(self, directory, fileName):
        try:
            vidcap = cv2.VideoCapture(fileName)
            length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            count = 0
            while True:
                _, image = vidcap.read()
                cv2.imwrite(directory + "\\frame_%d.jpg" %
                            count, image)  # save frame as JPEG file
                self.progress.emit(count * 100 / length)
                count += 1
            vidcap.release()
            cv2.destroyAllWindows()
            self.progress.emit(100)
            self.finished.emit("ExtractFramesProcessor",
                               "Capture All Frames Finished!")
        except Exception as e:
            self.error.emit("ExtractFramesProcessor",
                            e, traceback.format_exc())
            return
