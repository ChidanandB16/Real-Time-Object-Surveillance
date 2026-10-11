from utils.logger import log
import config
import torch.nn.functional as F


class FeatureMatcher:

    def __init__(self):

        self.similarity_threshold = config.REID_SIMILARITY_THRESHOLD

        log("Feature Matcher initialized successfully.")

    # --------------------------------------------------
    # Find Best Matching Stable Person
    # --------------------------------------------------

    def find_best_match(

            self,

            feature,

            database,

            frame_number

    ):

        best_similarity = -1
        best_stable_id = None

        log("")
        log("========== FEATURE MATCH ==========")

        if len(database) == 0:

            log("Database is empty.")
            log("==================================")
            log("")

            return None, -1

        # --------------------------------------------------
        # Compare against every Stable Person
        # --------------------------------------------------

        for stable_id, person_info in database.items():

            current_track = person_info["track_id"]
            last_seen = person_info["last_seen"]
            gallery_size = len(person_info["features"])

            # Ignore identities not seen recently
            if frame_number - last_seen > 300:

                continue

            feature_gallery = person_info["features"]

            person_best_similarity = -1

            for stored_feature in feature_gallery:

                similarity = F.cosine_similarity(

                    feature,

                    stored_feature

                ).item()

                if similarity > person_best_similarity:

                    person_best_similarity = similarity

            log(
                f"Stable {stable_id:3d} | "
                f"Track {current_track:3d} | "
                f"LastSeen {last_seen:5d} | "
                f"Gallery {gallery_size:2d} | "
                f"Best Similarity {person_best_similarity:.3f}"
            )

            if person_best_similarity > best_similarity:

                best_similarity = person_best_similarity
                best_stable_id = stable_id

        log("----------------------------------")
        log(f"Best Stable ID : {best_stable_id}")
        log(f"Best Similarity: {best_similarity:.3f}")
        log(f"Threshold      : {self.similarity_threshold:.3f}")

        if best_similarity >= self.similarity_threshold:

            log("MATCH FOUND")
            log("==================================")
            log("")

            return best_stable_id, best_similarity

        log("NO MATCH FOUND")
        log("==================================")
        log("")

        return None, best_similarity