import cv2


class Drawing:

    def __init__(self):
        print("Drawing module initialized successfully.")

    def draw_detections(
        self,
        frame,
        person_data,
        bag_data
    ):

        # -----------------------------
        # Draw Persons
        # -----------------------------
        for person in person_data:

            x1, y1, x2, y2 = person["bbox"]

            track_id = person["id"]
            stable_id = person.get("stable_id", "?")

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                6
            )

            cv2.putText(
                frame,
                f"T:{track_id} | S:{stable_id}",
                (x1, y1 - 15),
                cv2.FONT_HERSHEY_DUPLEX,
                1.3,
                (255, 0, 0),
                4,
                cv2.LINE_AA
            )

        # -----------------------------
        # Draw Bags
        # -----------------------------
        for bag in bag_data:

            x1, y1, x2, y2 = bag["bbox"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                6
            )

            cv2.putText(
                frame,
                bag["type"],
                (x1, y1 - 15),
                cv2.FONT_HERSHEY_DUPLEX,
                1.2,
                (0, 255, 0),
                4,
                cv2.LINE_AA
            )

        return frame

    def draw_centers(
            self,
            frame,
            person_data,
            bag_data
    ):

        # Person Centers
        for person in person_data:

            cx, cy = person["center"]

            cv2.circle(
                frame,
                (cx, cy),
                8,
                (0, 0, 255),
                -1
            )

        # Bag Centers
        for bag in bag_data:

            cx, cy = bag["center"]

            cv2.circle(
                frame,
                (cx, cy),
                8,
                (0, 255, 255),
                -1
            )

        return frame

    def draw_owner_lines(
            self,
            frame,
            person_data,
            bag_data,
            ownership,
            abandoned_bags,
            risk_results
    ):

        for bag in bag_data:

            bag_id = bag["id"]

            risk_score = 0
            risk_level = "SAFE"

            if bag_id in risk_results:
                risk_score = risk_results[bag_id]["score"]
                risk_level = risk_results[bag_id]["level"]

            is_abandoned = False

            if (
                bag_id in abandoned_bags
                and abandoned_bags[bag_id]["abandoned"]
            ):
                is_abandoned = True

            bag_center = bag["center"]
            bag_x1, bag_y1, bag_x2, bag_y2 = bag["bbox"]

            if bag_id not in ownership:
                continue

            owner_track_id = ownership[bag_id]["owner_track_id"]

            # -----------------------------
            # Decide Colors
            # -----------------------------
            if is_abandoned:
                box_color = (0, 0, 255)
                line_color = (0, 0, 255)
            else:
                box_color = (0, 255, 0)
                line_color = (255, 0, 255)

            text_x = bag_x1
            text_y = bag_y1 - 20

            # -----------------------------
            # ALWAYS Draw Bag Box
            # -----------------------------
            cv2.rectangle(
                frame,
                (bag_x1, bag_y1),
                (bag_x2, bag_y2),
                box_color,
                6
            )

            # -----------------------------
            # ALWAYS Draw Risk Score
            # -----------------------------
            cv2.putText(
                frame,
                f"Risk: {risk_score}",
                (text_x, text_y),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                line_color,
                3,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                risk_level,
                (text_x, text_y - 35),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                line_color,
                3,
                cv2.LINE_AA
            )

            # -----------------------------
            # ALWAYS Draw Abandoned Text
            # -----------------------------
            if is_abandoned:

                cv2.putText(
                    frame,
                    "ABANDONED OBJECT",
                    (bag_x1, bag_y1 - 70),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1.4,
                    (0, 0, 255),
                    4,
                    cv2.LINE_AA
                )

            # -----------------------------
            # Draw Owner Line ONLY if owner is visible
            # -----------------------------
            for person in person_data:

                if person["id"] != owner_track_id:
                    continue

                x1, y1, x2, y2 = person["bbox"]

                bag_type = bag["type"]

                if bag_type == "suitcase":
                    person_center = (
                        (x1 + x2) // 2,
                        y2
                    )

                elif bag_type == "backpack":
                    person_center = (
                        (x1 + x2) // 2,
                        (y1 + y2) // 2
                    )

                elif bag_type == "handbag":
                    person_center = (
                        (x1 + x2) // 2,
                        y1 + (y2 - y1) // 3
                    )

                else:
                    person_center = person["center"]

                cv2.line(
                    frame,
                    person_center,
                    bag_center,
                    line_color,
                    6
                )

                break

        return frame