import config
from utils.logger import log


class RiskScore:

    def __init__(self):
        log("Risk Score Module initialized successfully.")

    def calculate_risk(
            self,
            bag,
            owner,
            abandonment_state,
            frame_number
    ):
        # ----------------------------
        # Distance Score
        # ----------------------------
        distance = abandonment_state["distance"]
        distance_score = self.calculate_distance_risk(distance)

        # ----------------------------
        # Time Score
        # ----------------------------
        elapsed_frames = abandonment_state.get("elapsed_frames", 0)
        time_score = self.calculate_time_risk(elapsed_frames)

        # ----------------------------
        # Visibility Score
        # ----------------------------
        owner_visible = owner is not None
        visibility_score = self.calculate_visibility_risk(owner_visible)

        # ----------------------------
        # Stationary Score
        # ----------------------------
        bag_stationary = abandonment_state.get("bag_stationary", False)
        stationary_score = self.calculate_stationary_risk(bag_stationary)

        # ----------------------------
        # Total Risk
        # ----------------------------
        total_score = (
            distance_score +
            time_score +
            visibility_score +
            stationary_score
        )

        # ----------------------------
        # Risk Level
        # ----------------------------
        if total_score <= 30:
            level = "SAFE"
        elif total_score <= 60:
            level = "SUSPICIOUS"
        elif total_score <= 80:
            level = "HIGH RISK"
        else:
            level = "ABANDONED"

        log("========== RISK SCORE ==========")
        log(f"Distance Score   : {distance_score}")
        log(f"Time Score       : {time_score}")
        log(f"Visibility Score : {visibility_score}")
        log(f"Stationary Score : {stationary_score}")
        log(f"TOTAL            : {total_score}")
        log(f"LEVEL            : {level}")
        log("================================")

        return {
            "score": total_score,
            "level": level,
            "distance_score": distance_score,
            "time_score": time_score,
            "visibility_score": visibility_score,
            "stationary_score": stationary_score
        }

    # Distance Risk
    def calculate_distance_risk(self, distance):
        if distance <= 100:
            return 0
        elif distance <= 200:
            return 10
        elif distance <= 300:
            return 20
        else:
            return 30

    # Time Risk
    def calculate_time_risk(self, elapsed_frames):
        if elapsed_frames <= 30:
            return 0
        elif elapsed_frames <= 60:
            return 10
        elif elapsed_frames <= 120:
            return 20
        else:
            return 30

    # Visibility Risk
    def calculate_visibility_risk(self, owner_visible):
        if owner_visible:
            return 0
        return 20

    # Stationary Bag Risk
    def calculate_stationary_risk(self, bag_stationary):
        if bag_stationary:
            return 20
        return 0