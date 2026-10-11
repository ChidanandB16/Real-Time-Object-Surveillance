# ==============================
# Model Paths
# ==============================

YOLO_MODEL = "models/yolov8s.pt"
TRACKER_CONFIG = "tracker/my_bytetrack.yaml"

# ==============================
# Video Paths
# ==============================

INPUT_VIDEO = "data/videos/sample.mp4"
OUTPUT_VIDEO = "data/outputs/output.mp4"

# ==============================
# Detection Parameters
# ==============================

CONFIDENCE_THRESHOLD = 0.3
IOU_THRESHOLD = 0.5

# ==============================
# Abandoned Object Parameters
# ==============================

ABANDON_DISTANCE = 120 # pixels

ABANDON_FRAMES = 90 # 5 sec @ 30FPS



# ==============================
# ReID Parameters
# ==============================

# Wait before running ReID on a new ByteTrack ID
REID_DELAY_FRAMES = 8

# Update feature gallery every N frames
FEATURE_UPDATE_INTERVAL = 10

# OSNet similarity threshold
REID_SIMILARITY_THRESHOLD = 0.70

# Minimum person size before running ReID
MIN_BBOX_HEIGHT = 100
MIN_BBOX_WIDTH = 40
MIN_BBOX_AREA = 4000
MIN_ASPECT_RATIO = 0.25
MAX_ASPECT_RATIO = 1.0

# Maximum features stored per person
MAX_FEATURES = 20

# Number of frames used for ReID voting
REID_VOTING_FRAMES = 5
