from utils.logger import log
import config

class FeatureDatabase:

    def __init__(self):

        # Stable ID -> Person Information
        self.database = {}

        # Maximum number of features stored per person
        self.max_features = config.MAX_FEATURES

        log("Feature Database initialized successfully.")

    # --------------------------------------------------
    # Register New Stable Person
    # --------------------------------------------------

    def add_person(
            self,
            stable_id,
            feature,
            track_id,
            frame_number
    ):

        self.database[stable_id] = {

            # Feature Gallery
            "features": [feature],

            "track_id": track_id,

            "last_seen": frame_number,

            "feature_count": 1
        }

        log(
            f"Database : Added Stable ID {stable_id}"
        )

    # --------------------------------------------------
    # Update Existing Person
    # --------------------------------------------------

    def update_person(
        self,
        stable_id,
        feature,
        track_id,
        frame_number
    ):

        if stable_id not in self.database:
             return

        person = self.database[stable_id]

        # Add feature to gallery
        person["features"].append(feature)

        # Keep only latest features
        if len(person["features"]) > self.max_features:

            person["features"].pop(0)

        person["track_id"] = track_id
        person["last_seen"] = frame_number
        person["feature_count"] += 1

        # Log only every 5 gallery updates
        if person["feature_count"] % 5 == 0:

            log(
                f"Stable {stable_id} | "
                f"Gallery Size = {len(person['features'])}"
            )
    # --------------------------------------------------
    # Get One Person
    # --------------------------------------------------

    def get_person(
            self,
            stable_id
    ):

        return self.database.get(stable_id)

    # --------------------------------------------------
    # Get Complete Database
    # --------------------------------------------------

    def get_all_people(self):

        return self.database