import config

class Tracker:

    def __init__(self):

        print("Tracker initialized successfully.")


    def extract_objects(self, results):

        boxes = results[0].boxes

        person_data = []
        bag_data = []

        if boxes.id is None:

            return person_data, bag_data

        ids = boxes.id.int().tolist()
        classes = boxes.cls.int().tolist()

        confidences = boxes.conf.tolist()

        for box, track_id, class_id, confidence in zip(boxes.xyxy, ids, classes, confidences):

            x1, y1, x2, y2 = map(int, box)

            class_name = results[0].names[class_id]
            
            if class_name == "person":

                cx = (x1 + x2) // 2
                cy = (y2)

                width = x2 - x1
                height = y2 - y1

                person_data.append({

                     "id": track_id,

                     "center": (cx, cy),

                     "bbox" : (x1, y1, x2, y2),
                     
                     "width": width,

                     "height": height,

                     "area": width * height,

                     "aspect_ratio": width / height if height > 0 else 0,

                     "confidence": float(confidence)

                     

                })

            elif class_name in ["backpack","handbag","suitcase"]:

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                bag_data.append({
                    "id": track_id,

                    "center": (cx, cy),

                    "bbox" : (x1, y1, x2, y2),

                    "type" : class_name
                })
        return person_data, bag_data