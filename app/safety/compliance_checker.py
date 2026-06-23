"""
Warehouse Safety Compliance Checker
====================================
Checks PPE compliance (hardhat, vest) and posture (safe lifting)
against configurable rules and generates violations.
"""
from pathlib import Path


class ComplianceChecker:
    """Checks detection results against safety rules."""

    # ---- Proximity thresholds (in pixels) ----
    HARDHAT_MAX_DISTANCE = 150   # Max px between person head and nearest hardhat
    VEST_MAX_DISTANCE = 120      # Max px between person torso and nearest vest
    BOX_MAX_DISTANCE = 200       # Max px between person and a box (for lifting check)

    # ---- Posture thresholds ----
    # For lifting: angle between spine (shoulder→hip) and vertical.
    # < 30° = safe, 30-60° = risky, > 60° = dangerous
    MAX_SAFE_LIFT_ANGLE = 30.0   # degrees from vertical
    MAX_RISKY_LIFT_ANGLE = 60.0  # degrees from vertical

    def __init__(self, rules_config=None):
        self.rules = rules_config or {}
        self._hardhat_required = self.rules.get('require_hardhat', True)
        self._vest_required = self.rules.get('require_vest', True)
        self._check_lifting = self.rules.get('check_lifting', True)

    def check_frame(self, detections, pose_keypoints=None):
        """
        Check all compliance rules for one frame.

        Args:
            detections: list of dicts from ObjectDetector.predict()
                        each has: class_name, bbox [x1,y1,x2,y2], confidence, ...
            pose_keypoints: optional list of pose keypoints per person
                            (reserved for future YOLOv8-pose integration)

        Returns:
            list of violation dicts
        """
        violations = []

        # Separate detections by class
        persons = [d for d in detections if d['class_name'] == 'person']
        hardhats = [d for d in detections if d['class_name'] in ('hardhat', 'helmet')]
        vests = [d for d in detections if d['class_name'] in ('safety vest', 'vest', 'high-visibility vest', 'jacket')]
        boxes = [d for d in detections if d['class_name'] in ('box', 'cardboard box', 'package')]

        for person in persons:
            p_center = self._bbox_center(person['bbox'])
            person_id = f"person@{int(p_center[0])},{int(p_center[1])}"

            # --- PPE: Hardhat check ---
            if self._hardhat_required:
                has_helmet = any(
                    self._distance(p_center, self._bbox_center(h['bbox'])) < self.HARDHAT_MAX_DISTANCE
                    for h in hardhats
                )
                if not has_helmet:
                    violations.append({
                        'type': 'NO_HARDHAT',
                        'severity': 'HIGH',
                        'person': person_id,
                        'message': 'Person without hardhat/helmet detected',
                        'person_bbox': person['bbox'],
                    })

            # --- PPE: Vest check ---
            if self._vest_required:
                has_vest = any(
                    self._distance(p_center, self._bbox_center(v['bbox'])) < self.VEST_MAX_DISTANCE
                    for v in vests
                )
                if not has_vest:
                    violations.append({
                        'type': 'NO_VEST',
                        'severity': 'MEDIUM',
                        'person': person_id,
                        'message': 'Person without safety vest/jacket detected',
                        'person_bbox': person['bbox'],
                    })

            # --- Lifting posture check (requires pose keypoints) ---
            if self._check_lifting and pose_keypoints is not None:
                lifting_violation = self._check_lifting_posture(person, boxes, pose_keypoints)
                if lifting_violation:
                    violations.append(lifting_violation)

        return violations

    def _check_lifting_posture(self, person, boxes, pose_keypoints):
        """Check if person is lifting with unsafe posture.
           Requires pose keypoints: [nose, L-eye, R-eye, L-ear, R-ear,
           L-shoulder(5), R-shoulder(6), L-elbow(7), R-elbow(8),
           L-wrist(9), R-wrist(10), L-hip(11), R-hip(12),
           L-knee(13), R-knee(14), L-ankle(15), R-ankle(16)]"""
        # Find if person is near a box (likely lifting)
        p_center = self._bbox_center(person['bbox'])
        near_box = any(
            self._distance(p_center, self._bbox_center(b['bbox'])) < self.BOX_MAX_DISTANCE
            for b in boxes
        )
        if not near_box:
            return None  # Not lifting — no posture check needed

        # Find this person's keypoints (simplified — in practice, match by proximity)
        kp = pose_keypoints[0] if pose_keypoints else None
        if kp is None:
            # Without real pose data, use bbox aspect ratio as rough proxy
            w = person['bbox'][2] - person['bbox'][0]
            h = person['bbox'][3] - person['bbox'][1]
            aspect = h / max(w, 1)
            if aspect < 1.3:  # Bending over = wider than tall
                return {
                    'type': 'UNSAFE_LIFTING',
                    'severity': 'HIGH',
                    'person': f"person@{int(p_center[0])},{int(p_center[1])}",
                    'message': 'Unsafe lifting posture detected (bending at waist)',
                    'person_bbox': person['bbox'],
                }
            return None

        # Real pose-based check
        try:
            # Shoulders (indices 5,6) and hips (11,12)
            shoulder_y = (kp[5][1] + kp[6][1]) / 2
            hip_y = (kp[11][1] + kp[12][1]) / 2
            shoulder_x = (kp[5][0] + kp[6][0]) / 2
            hip_x = (kp[11][0] + kp[12][0]) / 2

            # Angle of the spine from vertical
            import math
            dx = hip_x - shoulder_x
            dy = hip_y - shoulder_y  # positive = hips below shoulders (normal)
            angle = abs(math.degrees(math.atan2(dx, abs(dy))))

            if angle > self.MAX_RISKY_LIFT_ANGLE:
                return {
                    'type': 'UNSAFE_LIFTING',
                    'severity': 'CRITICAL',
                    'person': f"person@{int(p_center[0])},{int(p_center[1])}",
                    'message': f'Dangerous lifting posture ({angle:.0f}° from vertical)',
                    'angle': angle,
                    'person_bbox': person['bbox'],
                }
            elif angle > self.MAX_SAFE_LIFT_ANGLE:
                return {
                    'type': 'RISKY_LIFTING',
                    'severity': 'MEDIUM',
                    'person': f"person@{int(p_center[0])},{int(p_center[1])}",
                    'message': f'Risky lifting posture ({angle:.0f}° from vertical)',
                    'angle': angle,
                    'person_bbox': person['bbox'],
                }
        except (IndexError, KeyError):
            pass

        return None

    # ---- Helpers ----
    @staticmethod
    def _bbox_center(bbox):
        """Return (cx, cy) center of a bbox [x1, y1, x2, y2]."""
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

    @staticmethod
    def _distance(p1, p2):
        """Euclidean distance between two points."""
        import math
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
