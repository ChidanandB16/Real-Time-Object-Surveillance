from ultralytics import YOLO
import cv2
import config

class Detector:

    def __init__(
            
            self,
                 
            video_path=None
    
    ):

        self.model = YOLO(config.YOLO_MODEL)

        self.video_path = video_path

        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise Exception(f"Error opening video file:{self.video_path}")

    def detect(self, frame):

        results = self.model.track(
            frame,
            persist=True,
            tracker=config.TRACKER_CONFIG,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            imgsz=1280,
            verbose=False 
        )

        # results = self.model(
        #     frame,
        #     conf=config.CONFIDENCE_THRESHOLD,
        #     verbose=False
        # )

        return results