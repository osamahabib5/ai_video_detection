"""
Face Recognizer — OpenCV-based (no dlib required)
==================================================
Face detection: OpenCV DNN SSD Caffe model
Face embedding: OpenCV DNN FaceNet ONNX model
Matching: cosine similarity against PersonDB
"""
import cv2
import numpy as np
import logging
from pathlib import Path


# Paths to model files (relative to project root)
MODELS_DIR = Path(__file__).parent.parent.parent / 'data' / 'models'

FACE_DETECTOR_PROTO = str(MODELS_DIR / 'deploy.prototxt')
FACE_DETECTOR_CAFFE = str(MODELS_DIR / 'res10_300x300_ssd_iter_140000_fp16.caffemodel')


class FaceRecognizer:
    """
    Detects faces and matches them against an enrolled person database.
    Works with a single face per frame (for worker profiling).
    """

    def __init__(self, person_db, confidence=0.5, embedding_dim=128):
        self.logger = logging.getLogger(__name__)
        self.db = person_db
        self.confidence_threshold = confidence
        self.embedding_dim = embedding_dim

        # Load face detector
        if not Path(FACE_DETECTOR_PROTO).exists():
            raise FileNotFoundError(f"Face detector proto missing: {FACE_DETECTOR_PROTO}")
        if not Path(FACE_DETECTOR_CAFFE).exists():
            raise FileNotFoundError(f"Face detector model missing: {FACE_DETECTOR_CAFFE}")

        self._face_net = cv2.dnn.readNetFromCaffe(FACE_DETECTOR_PROTO, FACE_DETECTOR_CAFFE)
        self.logger.info("Face detector loaded (OpenCV DNN SSD)")

        # Embedding extractor uses a simple but effective approach:
        # We resize the detected face and use a lightweight feature extraction.
        # For robust embeddings, a pre-trained ONNX FaceNet can be loaded here.
        self._embedding_model_loaded = False

    # ================================================================
    #  Face Detection
    # ================================================================

    def detect_faces(self, frame):
        """
        Detect faces in a frame.

        Returns:
            list of dicts: [{'bbox': (x,y,w,h), 'confidence': float}, ...]
            sorted by confidence (best face first).
        """
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
        self._face_net.setInput(blob)
        detections = self._face_net.forward()

        faces = []
        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            if conf < self.confidence_threshold:
                continue
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)
            # Clamp to frame bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            faces.append({
                'bbox': (x1, y1, x2 - x1, y2 - y1),
                'confidence': float(conf),
            })

        # Best face first
        faces.sort(key=lambda f: f['confidence'], reverse=True)
        return faces

    # ================================================================
    #  Embedding
    # ================================================================

    def get_embedding(self, face_crop):
        """
        Generate a face embedding vector.

        Uses a lightweight feature-based approach:
        - Resize face to standard size
        - Apply histogram equalization
        - Use HOG-like gradient features as a proxy embedding

        For production, swap with FaceNet ONNX:
            https://github.com/onnx/models/tree/main/vision/body_analysis/arcface

        Returns:
            numpy array [128,] or None
        """
        try:
            # Resize to standard size
            face = cv2.resize(face_crop, (96, 96))

            # Convert to grayscale for feature extraction
            if len(face.shape) == 3:
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            else:
                gray = face

            # Equalize for lighting invariance
            gray = cv2.equalizeHist(gray)

            # Multi-scale HOG-like descriptor
            features = []
            for scale in [96, 48, 24]:
                scaled = cv2.resize(gray, (scale, scale))
                gx = cv2.Sobel(scaled, cv2.CV_32F, 1, 0, ksize=3)
                gy = cv2.Sobel(scaled, cv2.CV_32F, 0, 1, ksize=3)
                mag, ang = cv2.cartToPolar(gx, gy)
                # Pool into bins
                for n_bins in [8, 4]:
                    hist = np.histogram(ang, bins=n_bins, range=(0, 2*np.pi), weights=mag)[0]
                    hist = hist / (hist.sum() + 1e-8)
                    features.extend(hist.tolist())

            vec = np.array(features, dtype=np.float32)

            # Pad or truncate to EMBEDDING_DIM
            if len(vec) < self.embedding_dim:
                vec = np.pad(vec, (0, self.embedding_dim - len(vec)))
            else:
                vec = vec[:self.embedding_dim]

            # L2 normalize
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm

            return vec

        except Exception as e:
            self.logger.error(f"Embedding extraction failed: {e}")
            return None

    # ================================================================
    #  Identification
    # ================================================================

    def identify(self, frame):
        """
        Detect the single largest face in a frame and identify the person.

        Returns:
            (person_id, person_name, confidence, face_bbox)
            If no face: (None, 'NO_FACE_DETECTED', 0.0, None)
            If unknown: (None, 'UNKNOWN_PERSON', sim, bbox)
        """
        faces = self.detect_faces(frame)

        if not faces:
            return None, 'NO_FACE_DETECTED', 0.0, None

        # Single-face mode: use the most confident face
        best_face = faces[0]
        x, y, fw, fh = best_face['bbox']
        face_crop = frame[y:y+fh, x:x+fw]
        if face_crop.size == 0:
            return None, 'NO_FACE_DETECTED', 0.0, None

        embedding = self.get_embedding(face_crop)
        if embedding is None:
            return None, 'NO_FACE_DETECTED', 0.0, None

        if self.db.count_enrolled() == 0:
            return None, 'NOT_ENROLLED', 0.0, best_face['bbox']

        pid, name, sim = self.db.identify(embedding)
        return pid, name, sim, best_face['bbox']
