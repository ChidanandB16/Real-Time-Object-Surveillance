import math

class OwnerAssignment:

    def __init__(self):

        self.ownership = {}

        self.previous_person_centers = {}

        self.previous_bag_centers = {}

        self.owner_change_counter = {}
        
        print("Owner Assignment initialized successfully.")

    # actual ownership algorithm.

    def calculate_distance_score(
            self,
            distance
    ):
        
        MAX_DISTANCE = 300
  
        score = max(

            0,

            100 * (1 - distance / MAX_DISTANCE)

        )

        return round(score, 2)
    
    
    def calculate_overlap_score(
            self,
            person_bbox,
            bag_bbox
    ):
        
        px1, py1, px2, py2 = person_bbox

        bx1, by1, bx2, by2 = bag_bbox

        # Intersection

        x_left = max(px1, bx1)
        y_top = max(py1, by1)

        x_right = min(px2, bx2)
        y_bottom = min(py2, by2)

        if x_right <= x_left or y_bottom <= y_top:

            return 0.0
        
        intersection = (

            x_right - x_left

        ) * (

            y_bottom - y_top

        )

        bag_area = (

            bx2 - bx1

        ) * (

            by2 - by1

        )

        if bag_area == 0:

            return 0.0
        
        score = (

            intersection / bag_area

        ) * 100

        return round(score, 2)
    
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
    
    # adding motion score

    def calculate_motion_score(
            
            self,

            person,

            bag
    ):
        
        person_id = person["id"]

        bag_id = bag["id"]

        current_person = self.get_person_reference_point(

            person,

            bag
        )

        current_bag = bag["center"]

        if(

            person_id not in self.previous_person_centers

            or

            bag_id not in self.previous_bag_centers
        ):
            
            self .previous_person_centers[person_id] = current_person

            self.previous_bag_centers[bag_id] = current_bag

            return 0
        
        previous_person = self.previous_person_centers[person_id]

        previous_bag = self.previous_bag_centers[bag_id]

        person_motion = math.dist(

            current_person,

            previous_person

        )

        bag_motion = math.dist(

            current_bag,

            previous_bag
        )

        difference = abs(

            person_motion - bag_motion

        )

        score = max(

            0,

            100 - difference * 10

        )

        self.previous_person_centers[person_id] = current_person

        self.previous_bag_centers[bag_id] = current_bag

        return round(score,2)
    
    


    def assign_owner(self, person_data, bag_data):

        for bag in bag_data:

            bag_id = bag["id"]

            bag_center = bag["center"]


            best_score = -1

            owner_track_id = None

            owner_stable_id = None

            best_distance_score = 0

            best_overlap_score = 0

            best_motion_score = 0

            print("\nPersons Available")

            for p in person_data:

                print(
                    p["id"],
                    p.get("stable_id")
                )

            for person in person_data:

                if person["stable_id"] is None:

                    continue

                person_center = self.get_person_reference_point(

                    person,

                    bag
                )

                distance = math.dist(
                    bag_center,
                    person_center
                )

                MAX_OWNER_DISTANCE = 350

                if distance > MAX_OWNER_DISTANCE:

                    continue

                # NEW: Calculate overlap for this person and this bag

                overlap_score = self.calculate_overlap_score(

                    person["bbox"],

                    bag["bbox"]

                )

                motion_score = self.calculate_motion_score(

                    person,

                    bag
                )

                print(
                    f"Bag {bag['id']} | " 
                    f"Person {person['id']} | "
                    f"Overlap = {overlap_score:.2f}"
                )

                distance_score = self.calculate_distance_score(

                    distance

                )

                # Combined score
                total_score = (

                    0.55 * distance_score

                    +

                    0.25 * overlap_score

                    +

                    0.20 * motion_score


                )
                

                if total_score > best_score:

                    best_score = total_score

                    owner_track_id = person["id"]

                    owner_stable_id = person["stable_id"]

                    best_distance_score = distance_score

                    best_overlap_score = overlap_score

                    best_motion_score = motion_score

            # Assign only after checking every person

            MIN_OWNER_SCORE = 25

            OWNER_SWITCH_MARGIN = 15

            OWNER_SWITCH_FRAMES = 5
            

            if (
                
                owner_stable_id is not None

                and

                best_score >= MIN_OWNER_SCORE

            ):

                # FIRST TIME ASSIGNING OWNER

                if bag_id not in self.ownership:

                    self.owner_change_counter[bag_id] = 0

                    self.ownership[bag_id] = {

                        "owner_track_id": owner_track_id,

                        "owner_stable_id": owner_stable_id,

                        "confidence": round(best_score, 2),

                        "distance_score": best_distance_score,

                        "overlap_score": best_overlap_score,

                        "motion_score": best_motion_score,

                        "interaction_score": 0

                    }

                    print(

                        f"Bag {bag_id} -> "

                        f"Stable {owner_stable_id} "

                        f"(Initial Owner)"

                    )

                else:

                    current_owner = self.ownership[bag_id]["owner_stable_id"]

                    current_score = self.ownership[bag_id]["confidence"]

                    # SAME OWNER

                    if owner_stable_id == current_owner:

                        self.owner_change_counter[bag_id] = 0

                        self.ownership[bag_id]["confidence"] = round(best_score, 2)

                    # DIFFERENT OWNER

                    elif best_score > current_score + OWNER_SWITCH_MARGIN:

                        self.owner_change_counter[bag_id] += 1

                        print(

                            f"Bag {bag_id} "

                            f"Pending Owner "

                            f"{owner_stable_id} "

                            f"({self.owner_change_counter[bag_id]}/"

                            f"{OWNER_SWITCH_FRAMES})"

                        )

                        if self.owner_change_counter[bag_id] >= OWNER_SWITCH_FRAMES:

                            self.owner_change_counter[bag_id] = 0

                            self.ownership[bag_id] = {

                                "owner_track_id": owner_track_id,

                                "owner_stable_id": owner_stable_id,

                                "confidence": round(best_score, 2),

                                "distance_score": best_distance_score,

                                "overlap_score": best_overlap_score,

                                "motion_score": best_motion_score,

                                "interaction_score": 0

                            }

                            print(

                                f"Bag {bag_id} "

                                f"Owner Changed -> "

                                f"Stable {owner_stable_id}"

                            )

                    else:

                        self.owner_change_counter[bag_id] = 0

        return self.ownership