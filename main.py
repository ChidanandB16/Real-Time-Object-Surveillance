import cv2

from detector.detector import Detector
from tracking.tracker import Tracker
from ownership.owner_assignment import OwnerAssignment
from abandonment.abandonment_detector import AbandonmentDetector
from utils.drawing import Drawing
from reid.id_manager import IdentityManager
from risk.risk_score import RiskScore
from utils.logger import log, close_logger


# -------------------------------------------------
# Create Objects
# -------------------------------------------------

detector = Detector()

tracker = Tracker()

owner_assignment = OwnerAssignment()

abandonment_detector = AbandonmentDetector()

risk_score = RiskScore()

identity_manager = IdentityManager()

drawing = Drawing()


# -------------------------------------------------
# Frame Counter
# -------------------------------------------------

frame_number = 0


width = int(detector.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(detector.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

import os

os.makedirs("output", exist_ok = True)

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

        # # Log only IDs that we are debugging
        # if track_id in [23, 28]:

        #     log("-" * 60)
        #     log(f"Frame      : {frame_number}")
        #     log(f"ByteTrack  : {track_id}")
        #     log(f"Stable ID  : {stable_id}")

    ownership = owner_assignment.assign_owner(

        person_data,

        bag_data

    )

    # print("\n========== OWNER ASSIGNMENT ===========")

    # for bag_id, info in ownership.items():

    #     print(f"Bag ID           : {bag_id}")
    #     print(f"Owner ID         : {info['owner_id']}")
    #     print(f"Confidence       : {info['confidence']:.2f}")
    #     print(f"Distance Score   : {info['distance_score']:.2f}")
    #     print(f"Overlap Score    : {info['overlap_score']:.2f}")
    #     print(f"Motion Score     : {info['motion_score']:.2f}")
    #     print(f"Interaction Score: {info['interaction_score']:.2f}")
    #     print("--------------------------------------")

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
        results
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

    video_writer.write(annotated_frame)

    cv2.imshow("Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


detector.cap.release()

cv2.destroyAllWindows()

video_writer.release()

close_logger()