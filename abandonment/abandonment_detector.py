import math

import config

from utils.logger import log


class AbandonmentDetector:

    def __init__(self):
        self.bag_states = {}
        log("Abandonment Detector initialized successfully.")

    def get_person_reference_point(
            self,
            person,
            bag
    ):
        x1, y1, x2, y2 = person["bbox"]

        bag_class = bag["type"]

        # Rolling suitcase
        if bag_class == "suitcase":
            return (
                (x1 + x2) // 2,
                y2
            )

        # Backpack
        elif bag_class == "backpack":
            return (
                (x1 + x2) // 2,
                (y1 + y2) // 2
            )

        # Handbag
        elif bag_class == "handbag":
            return (
                (x1 + x2) // 2,
                y1 + (y2 - y1) // 3
            )

        # Default
        return (
            (x1 + x2) // 2,
            y2
        )

    def detect_abandonment(
            self,
            person_data,
            bag_data,
            ownership,
            frame_number
    ):
        abandoned_bags = {}

        log("")
        log("========== ABANDONMENT DETECTOR ==========")
        log(f"Frame : {frame_number}")

        for bag in bag_data:

            bag_id = bag["id"]

            if bag_id not in ownership:
                continue

            # -----------------------------------
            # Initialize Bag State
            # -----------------------------------
            if bag_id not in self.bag_states:
                self.bag_states[bag_id] = {
                    "first_far_frame": None,
                    "return_counter": 0,
                    "abandoned": False
                }

            state = self.bag_states[bag_id]

            # -----------------------------------
            # Find Owner
            # -----------------------------------
            owner_stable = ownership[bag_id]["owner_stable_id"]

            owner = None

            for person in person_data:
                if person.get("stable_id") == owner_stable:
                    owner = person
                    break

            if owner is None:

                log(f"Bag {bag_id} : Owner not visible")

                state["return_counter"] = 0

                if state["first_far_frame"] is None:
                    state["first_far_frame"] = frame_number
                    log(f"Bag {bag_id} : Timer Started (Owner Missing)")

                elapsed = frame_number - state["first_far_frame"]

                log(f"Bag {bag_id} : Owner Missing for {elapsed} frames")

                if elapsed >= config.ABANDON_FRAMES:

                    if not state["abandoned"]:
                        log("")
                        log("******** ABANDONED OBJECT ********")
                        log(f"Bag ID      : {bag_id}")
                        log(f"Owner Stable: {owner_stable}")
                        log("Reason      : Owner Left Camera")
                        log("*********************************")
                        log("")

                    state["abandoned"] = True

                abandoned_bags[bag_id] = {
                    "abandoned": state["abandoned"],
                    "distance": -1,
                    "elapsed_frames": elapsed,
                    "bag_stationary": False
                }

                continue

            # -----------------------------------
            # Calculate Distance
            # -----------------------------------
            person_reference = self.get_person_reference_point(
                owner,
                bag
            )

            log(
                f"Reference Point = {person_reference}"
            )

            distance = math.dist(
                bag["center"],
                person_reference
            )

            log(
                f"Bag {bag_id} | "
                f"Owner Stable {owner_stable} | "
                f"Distance = {distance:.2f}"
            )

            # ===================================
            # OWNER IS FAR
            # ===================================
            if distance > config.ABANDON_DISTANCE:

                # Owner moved away again
                state["return_counter"] = 0

                if state["first_far_frame"] is None:
                    state["first_far_frame"] = frame_number
                    log(f"Bag {bag_id} : Timer Started")

                elapsed = frame_number - state["first_far_frame"]

                log(f"Bag {bag_id} : Away for {elapsed} frames")

                if elapsed >= config.ABANDON_FRAMES:

                    if not state["abandoned"]:
                        log("")
                        log("******** ABANDONED OBJECT ********")
                        log(f"Bag ID      : {bag_id}")
                        log(f"Owner Stable: {owner_stable}")
                        log(f"Distance    : {distance:.2f}")
                        log("*********************************")
                        log("")

                    state["abandoned"] = True

            # ===================================
            # OWNER IS NEAR
            # ===================================
            else:

                state["return_counter"] += 1

                log(
                    f"Bag {bag_id} : Owner Returned "
                    f"({state['return_counter']}/10)"
                )

                # Reset only after 10 continuous frames
                if state["return_counter"] >= 10:
                    state["first_far_frame"] = None
                    state["return_counter"] = 0
                    state["abandoned"] = False
                    log(f"Bag {bag_id} : Timer Reset")

            elapsed = 0

            if state["first_far_frame"] is not None:
                elapsed = frame_number - state["first_far_frame"]

            abandoned_bags[bag_id] = {
                "abandoned": state["abandoned"],
                "distance": distance,
                "elapsed_frames": elapsed,
                "bag_stationary": False
            }

        log("")
        log("========== ABANDONMENT SUMMARY ==========")

        for bag_id, info in abandoned_bags.items():
            log(
                f"Bag {bag_id} | "
                f"Distance={info['distance']:.2f} | "
                f"Elapsed={info['elapsed_frames']} | "
                f"Abandoned={info['abandoned']}"
            )

        log("=========================================")
        log("")

        return abandoned_bags