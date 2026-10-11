import cv2
import os
import time
import subprocess
from detector.detector import Detector
from tracking.tracker import Tracker
from ownership.owner_assignment import OwnerAssignment
from abandonment.abandonment_detector import AbandonmentDetector
from reid.id_manager import IdentityManager
from risk.risk_score import RiskScore
from utils.drawing import Drawing
from utils.logger import initialize_logger, close_logger


def process_video(video_path):

    initialize_logger()

    detector = Detector(video_path)

    tracker = Tracker()

    owner_assignment = OwnerAssignment()

    abandonment_detector = AbandonmentDetector()

    risk_score = RiskScore()

    identity_manager = IdentityManager()

    drawing = Drawing()

    frame_number = 0

    
    abandoned_bags = set()
    alerted_bags = set()

    max_persons = 0
    max_bags = 0

    latest_alert = "No abandoned object detected."

    width = int(detector.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(detector.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    os.makedirs("output", exist_ok=True)

    fps = detector.cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    video_writer = cv2.VideoWriter(
        "output/output.mp4",
        fourcc,
        fps,
        (width, height)
    )

    cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detection", width, height)
    print(f"Video Resolution : {width} x {height}")
    
    start_time = time.time()

    while True:

        ret, frame = detector.cap.read()

        if not ret:
            break

        frame_number += 1

        results = detector.detect(frame)

        person_data, bag_data = tracker.extract_objects(results)

        # ---------------------------------
        # Process every detected person
        # ---------------------------------

        for person in person_data:

            stable_id = identity_manager.process_person(
                frame,
                person,
                frame_number
            )

            person["stable_id"] = stable_id

        ownership = owner_assignment.assign_owner(
            person_data,
            bag_data
        )

        abandoned = abandonment_detector.detect_abandonment(
            person_data,
            bag_data,
            ownership,
            frame_number
        )

        risk_results = {}

        for bag in bag_data:

            bag_id = bag["id"]

            if bag_id not in abandoned:
                continue

            owner = None

            if bag_id in ownership:

                owner_stable = ownership[bag_id]["owner_stable_id"]

                for person in person_data:
                    if person.get("stable_id") == owner_stable:
                        owner = person
                        break

            risk_results[bag_id] = risk_score.calculate_risk(
                bag,
                owner,
                abandoned[bag_id],
                frame_number
            )

        annotated_frame = drawing.draw_detections(
            frame,
            person_data,
            bag_data
        )

        annotated_frame = drawing.draw_centers(
            annotated_frame,
            person_data,
            bag_data
        )

        annotated_frame = drawing.draw_owner_lines(
            annotated_frame,
            person_data,
            bag_data,
            ownership,
            abandoned,
            risk_results
        )

        # Maximum persons and bags detected
        max_persons = max(max_persons, len(person_data))
        max_bags = max(max_bags, len(bag_data))

        # Store unique abandoned bags
        for bag_id in abandoned.keys():
            abandoned_bags.add(bag_id)

        # Store unique alerted bags
        for bag_id, risk in risk_results.items():

            alerted_bags.add(bag_id)

            latest_alert = (
                f"Frame: {frame_number}\n"
                f"Bag ID: {bag_id}\n"
                f"Risk Score: {risk['score']}\n"
                f"Risk Level: {risk['level']}"
            )

        video_writer.write(annotated_frame)

        cv2.imshow("Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    detector.cap.release()

    cv2.destroyAllWindows()

    video_writer.release()

    close_logger()

    end_time = time.time()

    # ------------------------------------------
    # Convert OpenCV video to browser-compatible MP4
    # ------------------------------------------

    input_video = "output/output.mp4"
    output_video = "output/output_web.mp4"

    ffmpeg_path = r"D:\ffmpeg\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe"

    subprocess.run([
        ffmpeg_path,
        "-y",
        "-i",
        input_video,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        output_video
    ], check=True)

    return {
        "video": output_video,
        "persons": max_persons,
        "bags": max_bags,
        "abandoned": len(abandoned_bags),
        "alerts": len(alerted_bags),
        "fps": round(frame_number / (end_time - start_time), 2),
        "latest_alert": latest_alert
    }