from utils.logger import log


class StableIdentity:

    def __init__(self):

        # ByteTrack ID -> Stable ID
        self.track_to_stable = {}

        # Stable ID Generator
        self.next_stable_id = 1

        log("Stable Identity initialized successfully.")

    # ----------------------------------
    # Check if Track ID is already known
    # ----------------------------------

    def has_track(
            self,
            track_id
    ):

        return track_id in self.track_to_stable

    # ----------------------------------
    # Get Stable ID
    # ----------------------------------

    def get_stable_id(
            self,
            track_id
    ):

        return self.track_to_stable.get(track_id)

    # ----------------------------------
    # Assign Existing Stable ID
    # ----------------------------------

    def assign_track(
            self,
            track_id,
            stable_id
    ):

        self.track_to_stable[track_id] = stable_id

        log(
            f"Track {track_id} assigned to Stable {stable_id}"
        )

    # ----------------------------------
    # Create New Stable ID
    # ----------------------------------

    def create_new_identity(
            self,
            track_id
    ):

        stable_id = self.next_stable_id

        self.next_stable_id += 1

        self.track_to_stable[track_id] = stable_id

        log(
            f"Created Stable ID {stable_id} for Track {track_id}"
        )

        return stable_id

    # ----------------------------------
    # Get Complete Mapping
    # ----------------------------------

    def get_all_tracks(self):

        return self.track_to_stable