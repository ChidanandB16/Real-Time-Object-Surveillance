from utils.logger import log
import config

from reid.osnet import OSNetReID
from reid.feature_database import FeatureDatabase
from reid.feature_matcher import FeatureMatcher
from reid.stable_identity import StableIdentity


class IdentityManager:

    def __init__(self):

        # -------------------------
        # Initialize Modules
        # -------------------------

        self.osnet = OSNetReID()
        self.osnet.load_model()

        self.database = FeatureDatabase()

        self.matcher = FeatureMatcher()

        self.identity = StableIdentity()

        # -------------------------
        # ReID Parameters
        # -------------------------

        self.feature_update_interval = config.FEATURE_UPDATE_INTERVAL

        self.reid_delay = config.REID_DELAY_FRAMES

        # -------------------------
        # Pending Tracks
        # -------------------------

        self.pending_tracks = {}

        log("Identity Manager initialized successfully.")

    # --------------------------------------------------
    # Process Person
    # --------------------------------------------------

    def process_person(

            self,

            frame,

            person,

            frame_number

    ):

        track_id = person["id"]

        # ==================================================
        # EXISTING TRACK
        # ==================================================

        if self.identity.has_track(track_id):

            stable_id = self.identity.get_stable_id(track_id)

    # ------------------------------------------
            # Update Feature Gallery Periodically
    # ------------------------------------------

            if frame_number % self.feature_update_interval == 0:

                width = person["width"]
                height = person["height"]
                area = person["area"]
                aspect = person["aspect_ratio"]
                confidence = person["confidence"]

                print(
                    f"Track {track_id} | "
                    f"W={width}, H={height}, "
                    f"Area={area}, "
                    f"Conf={confidence:.2f}"
                )

        # Update gallery only if detection quality is good
                if (

                   width >= config.MIN_BBOX_WIDTH

                   and

                   height >= config.MIN_BBOX_HEIGHT

                   and

                   area >= config.MIN_BBOX_AREA

                   and

                   config.MIN_ASPECT_RATIO <= aspect <= config.MAX_ASPECT_RATIO

                   and

                   confidence >= config.CONFIDENCE_THRESHOLD

                ):

                   feature = self.osnet.extract_features(

                       frame,

                       person["bbox"]

                   )

                   if feature is not None:

                        self.database.update_person(

                            stable_id,

                            feature,

                            track_id,

                            frame_number

                        )

                        log(
                            f"Gallery Updated -> Stable {stable_id}"
                        )

                else:

                    log(
                        f"Gallery Update Skipped -> "
                        f"Stable {stable_id} "
                        f"(Poor Detection)"
                    )

            return stable_id

        # ==================================================
        # FIRST TIME THIS TRACK APPEARS
        # ==================================================

        if track_id not in self.pending_tracks:

            self.pending_tracks[track_id] = {

                "first_frame": frame_number

            }

            log(
                f"Pending Track {track_id} created at Frame {frame_number}"
            )

            return None

        # ==================================================
        # WAIT UNTIL TRACK IS STABLE
        # ==================================================

        first_frame = self.pending_tracks[track_id]["first_frame"]

        frames_waited = frame_number - first_frame

        if frames_waited < self.reid_delay:

            return None

        # ==================================================
        # CHECK PERSON VISIBILITY
        # ==================================================

        width = person["width"]

        height = person["height"]

        area = person["area"]

        aspect = person["aspect_ratio"]

        confidence = person["confidence"]

# --------------------------------------------------
        # Detection Quality Check
# --------------------------------------------------

        if (

            width < config.MIN_BBOX_WIDTH

            or

            height < config.MIN_BBOX_HEIGHT

            or

            area < config.MIN_BBOX_AREA

            or

            aspect < config.MIN_ASPECT_RATIO

            or

            aspect > config.MAX_ASPECT_RATIO

            or

            confidence < config.CONFIDENCE_THRESHOLD

        ):

            log("")
            log("Waiting for Better Detection")
            log(f"Track        : {track_id}")
            log(f"Size         : {width} x {height}")
            log(f"Area         : {area}")
            log(f"Aspect Ratio : {aspect:.2f}")
            log(f"Confidence   : {confidence:.2f}")
            log("")

            return None
        # ==================================================
        # READY FOR ReID
        # ==================================================

        del self.pending_tracks[track_id]

        log("")
        log("====================================")
        log(f"Frame            : {frame_number}")
        log(f"Track            : {track_id}")
        log("Running Delayed ReID...")

        feature = self.osnet.extract_features(

            frame,

            person["bbox"]

        )

        if feature is None:

            log("Feature Extraction Failed")
            log("====================================")
            log("")

            return None

        log("Searching Feature Database...")

        stable_id, similarity = self.matcher.find_best_match(

            feature,

            self.database.get_all_people(),

            frame_number

        )

        # ==================================================
        # RECOVER EXISTING PERSON
        # ==================================================

        if stable_id is not None:

            self.identity.assign_track(

                track_id,

                stable_id

            )

            self.database.update_person(

                stable_id,

                feature,

                track_id,

                frame_number

            )

            log("Identity Recovered")
            log(f"Track ID   : {track_id}")
            log(f"Stable ID  : {stable_id}")
            log(f"Similarity : {similarity:.3f}")
            log("====================================")
            log("")

            return stable_id



        # -------------------------------------------------
        # First Person in Database
        # -------------------------------------------------

        if len(self.database.get_all_people()) == 0:

            stable_id = self.identity.create_new_identity(track_id)

            self.database.add_person(
                stable_id,
                feature,
                track_id,
                frame_number
            )

            log("")
            log("Database Empty -> First Stable ID Created")
            log(f"Stable ID : {stable_id}")
            log("")

            return stable_id

        # ==================================================
        # REGISTER NEW PERSON
        # ==================================================

        stable_id = self.identity.create_new_identity(

            track_id

        )

        self.database.add_person(

            stable_id,

            feature,

            track_id,

            frame_number

        )

        log("New Person Registered")
        log(f"Track ID      : {track_id}")
        log(f"Stable ID     : {stable_id}")
        log("====================================")
        log("")

        return stable_id