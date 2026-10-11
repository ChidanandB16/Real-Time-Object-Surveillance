import torch
import cv2
import numpy as np
from torchvision import transforms
from PIL import Image
from reid.models.osnet import osnet_x1_0


class OSNetReID:

    def __init__(self):

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(f"Device : {self.device}")

        self.model = None

        print("OSNet ReID initialized successfully.")

        self.transform = transforms.Compose([

            transforms.ToPILImage(),

            transforms.Resize((256, 128)),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )

        ])

    def load_model(self):

        print("Loading OSNet...")

        self.model = osnet_x1_0(
            pretrained=True
        )

        self.model.to(self.device)

        self.model.eval()

        print("OSNet Loaded Successfully.")

    def extract_features(
        self,
        frame,
        bbox
    ):

        x1, y1, x2, y2 = bbox

        # Crop person from frame
        person_crop = frame[y1:y2, x1:x2]

        # Empty crop protection
        if person_crop.size == 0:

           return None

        # BGR -> RGB
        person_crop = cv2.cvtColor(
            person_crop,
            cv2.COLOR_BGR2RGB
        )

        # Apply preprocessing
        person_tensor = self.transform(
            person_crop
        )

        # Add batch dimension
        person_tensor = person_tensor.unsqueeze(0)

        # Move to CPU / GPU
        person_tensor = person_tensor.to(self.device)

        # Extract features
        with torch.no_grad():

            features = self.model(person_tensor)

        return features