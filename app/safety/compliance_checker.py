"""
Warehouse Safety Compliance Checker
====================================
Implements Australian Work Health & Safety (WHS) protocols
aligned with Safe Work Australia — Model WHS Framework.

Detectable rules (vision-based):
  §9  PPE Management         — hardhat, hi-vis vest, gloves, boots
  §4  Manual Handling        — safe lifting posture, no twisting, no overhead lift
  §2  Working at Heights     — proximity to unprotected edges
  §6  Plant & Equipment      — pedestrian near forklift/pallet jack
  §3  Lifting & Rigging      — person under suspended load

Rules NOT detectable by vision alone (require sensor/API input):
  §5  Heat Stress, §7 Electrical, §8 Confined Space,
  §10 Incident Reporting, §11 Consultation, §12 SWMS
"""
import math
from pathlib import Path


class ComplianceChecker:
    """Checks detection results against Australian WHS safety rules."""

    # ---- WHS §9: PPE Proximity Thresholds (pixels) ----
    HARDHAT_DISTANCE = 180      # Max px from person head to hardhat
    VEST_DISTANCE = 150         # Max px from person torso to hi-vis vest
    GLOVE_DISTANCE = 80         # Max px from person hands to gloves
    BOOT_DISTANCE = 100         # Max px from person feet to safety boots

    # ---- WHS §4: Manual Handling Posture Thresholds ----
    MAX_SAFE_LIFT_ANGLE = 30.0      # Spine angle from vertical (degrees)
    MAX_RISKY_LIFT_ANGLE = 60.0     # >60° = dangerous
    MAX_TWIST_ANGLE = 25.0          # Shoulder-hip twist while lifting
    OVERHEAD_LIFT_SHOULDER_RATIO = 0.85  # Hands above shoulder = overhead

    # ---- WHS §4: Box proximity for lifting context ----
    BOX_PROXIMITY = 250         # Person-to-box distance to trigger lift check

    # ---- WHS §6: Plant/Equipment exclusion zone ----
    FORKLIFT_EXCLUSION_ZONE = 200   # Min px between pedestrian and forklift
    FORKLIFT_FRONT_CONE = 300       # Danger zone in front of forklift

    # ---- WHS §2: Edge proximity ----
    EDGE_MARGIN = 80            # Pixels from frame border = potential edge

    # ---- WHS §3: Load overhead (person under box) ----
    LOAD_OVERHEAD_OVERLAP = 0.3      # 30% of box above person = under load

    def __init__(self, rules_config=None):
        self.rules = rules_config or {}

        # WHS §9: PPE toggles
        self._check_hardhat  = self.rules.get('require_hardhat', True)
        self._check_vest     = self.rules.get('require_vest', True)
        self._check_gloves   = self.rules.get('require_gloves', False)
        self._check_boots    = self.rules.get('require_boots', False)

        # WHS §4: Manual handling toggles
        self._check_lifting  = self.rules.get('check_lifting', True)
        self._check_twisting = self.rules.get('check_twisting', True)
        self._check_overhead = self.rules.get('check_overhead_lift', True)

        # WHS §6: Plant safety
        self._check_forklift_zone = self.rules.get('check_forklift_zone', True)

        # WHS §2: Edge safety
        self._check_edge = self.rules.get('check_edge_proximity', False)

        # WHS §3: Suspended load
        self._check_suspended_load = self.rules.get('check_suspended_load', True)

    # =================================================================
    #  MAIN CHECK — runs once per frame
    # =================================================================

    def check_frame(self, detections, frame_shape=None, pose_keypoints=None):
        """
        Check all WHS compliance rules for one frame.

        Args:
            detections: list of dicts from ObjectDetector.predict()
                        each has: class_name, bbox [x1,y1,x2,y2], confidence
            frame_shape: tuple (height, width) for edge checks
            pose_keypoints: optional per-person pose data for §4 checks

        Returns:
            list of violation dicts (type, severity, whs_section, message, ...)
        """
        violations = []

        # --- Classify detections ---
        persons   = [d for d in detections if d['class_name'] == 'person']
        hardhats  = [d for d in detections if d['class_name'] in ('hardhat', 'helmet')]
        vests     = [d for d in detections if d['class_name'] in (
                       'safety vest', 'vest', 'high-visibility vest')]
        gloves    = [d for d in detections if d['class_name'] in ('glove', 'safety glove')]
        boots     = [d for d in detections if d['class_name'] in ('boot', 'safety boot', 'steel-toe boot')]
        boxes     = [d for d in detections if d['class_name'] in (
                       'box', 'cardboard box', 'package', 'crate', 'pallet')]
        forklifts = [d for d in detections if d['class_name'] in ('forklift', 'pallet jack', 'pallet truck')]
        loads     = [d for d in detections if d['class_name'] in (
                       'suspended load', 'hanging load', 'crane load')]

        for person in persons:
            pc = self._bbox_center(person['bbox'])
            pid = f"person@{int(pc[0])},{int(pc[1])}"

            # ================================================
            #  WHS §9: PPE MANAGEMENT
            # ================================================

            # 9.1 Hardhat / helmet
            if self._check_hardhat:
                if not self._is_near(pc, hardhats, self.HARDHAT_DISTANCE):
                    violations.append(self._violation(
                        'NO_HARDHAT', 'HIGH', '9',
                        'WHS §9: Person without hardhat/helmet detected. '
                        'PPE must be suitable and worn at all times in designated zones.',
                        pid, person['bbox']))

            # 9.2 Hi-vis vest
            if self._check_vest:
                if not self._is_near(pc, vests, self.VEST_DISTANCE):
                    violations.append(self._violation(
                        'NO_VEST', 'MEDIUM', '9',
                        'WHS §9: Person without hi-vis safety vest. '
                        'High-visibility clothing required in warehouse operational areas.',
                        pid, person['bbox']))

            # 9.3 Gloves
            if self._check_gloves:
                if not self._is_near(pc, gloves, self.GLOVE_DISTANCE):
                    violations.append(self._violation(
                        'NO_GLOVES', 'LOW', '9',
                        'WHS §9: Person without safety gloves detected when handling materials.',
                        pid, person['bbox']))

            # 9.4 Safety boots
            if self._check_boots:
                if not self._is_near(pc, boots, self.BOOT_DISTANCE):
                    violations.append(self._violation(
                        'NO_BOOTS', 'MEDIUM', '9',
                        'WHS §9: Person without steel-toe/safety boots in warehouse zone.',
                        pid, person['bbox']))

            # ================================================
            #  WHS §4: MANUAL HANDLING & HAZARDOUS TASKS
            # ================================================
            near_box = self._is_near(pc, boxes, self.BOX_PROXIMITY)

            if near_box or self._check_lifting:
                # 4.1 Unsafe lifting posture (bending at waist)
                if self._check_lifting:
                    lift_v = self._check_lifting_posture(person, boxes, pose_keypoints, pid)
                    if lift_v:
                        violations.append(lift_v)

                # 4.2 Twisting while lifting
                if self._check_twisting and near_box and pose_keypoints:
                    twist_v = self._check_twisting_posture(person, pose_keypoints, pid)
                    if twist_v:
                        violations.append(twist_v)

                # 4.3 Overhead reach with load
                if self._check_overhead and near_box and pose_keypoints:
                    oh_v = self._check_overhead_lift(person, pose_keypoints, pid)
                    if oh_v:
                        violations.append(oh_v)

            # ================================================
            #  WHS §6: PLANT & EQUIPMENT — Forklift exclusion
            # ================================================
            if self._check_forklift_zone:
                # 6.1 Pedestrian too close to forklift
                for fl in forklifts:
                    flc = self._bbox_center(fl['bbox'])
                    dist = self._distance(pc, flc)
                    if dist < self.FORKLIFT_EXCLUSION_ZONE:
                        # Check if person is in front (travel path danger)
                        in_front = self._is_in_front(person['bbox'], fl['bbox'])
                        if in_front and dist < self.FORKLIFT_FRONT_CONE:
                            violations.append(self._violation(
                                'FORKLIFT_PATH', 'CRITICAL', '6',
                                'WHS §6: Person in forklift travel path — '
                                'immediate exclusion zone breach. Maintain 3m clearance.',
                                pid, person['bbox']))
                        else:
                            violations.append(self._violation(
                                'FORKLIFT_PROXIMITY', 'HIGH', '6',
                                'WHS §6: Person within forklift exclusion zone. '
                                'Maintain safe distance from operating plant.',
                                pid, person['bbox']))

                # 6.2 Multiple pedestrians near equipment (congestion risk)
                if len(forklifts) > 0 and len(persons) > 2:
                    # Already flagged individually above
                    pass

            # ================================================
            #  WHS §2: WORKING AT HEIGHTS / EDGE PROXIMITY
            # ================================================
            if self._check_edge and frame_shape:
                h, w = frame_shape
                # Person bbox near any frame edge (proxy for unprotected edge)
                bx = person['bbox']
                near_left   = bx[0] < self.EDGE_MARGIN
                near_right  = bx[2] > w - self.EDGE_MARGIN
                near_top    = bx[1] < self.EDGE_MARGIN
                near_bottom = bx[3] > h - self.EDGE_MARGIN
                if near_left or near_right or near_top or near_bottom:
                    violations.append(self._violation(
                        'EDGE_PROXIMITY', 'HIGH', '2',
                        'WHS §2: Person near unprotected edge. '
                        'Fall prevention (guardrails/scaffolds) must be in place.',
                        pid, person['bbox']))

            # ================================================
            #  WHS §3: LIFTING & RIGGING — Suspended loads
            # ================================================
            if self._check_suspended_load:
                for load in loads:
                    if self._person_under_load(person['bbox'], load['bbox']):
                        violations.append(self._violation(
                            'UNDER_LOAD', 'CRITICAL', '3',
                            'WHS §3: Person standing under suspended/hanging load. '
                            'No persons permitted under loads at any time.',
                            pid, person['bbox']))
                        break  # one is enough

        return violations

    # =================================================================
    #  WHS §4 posture sub-checks
    # =================================================================

    def _check_lifting_posture(self, person, boxes, pose_keypoints, pid):
        """Check if person is lifting with unsafe spine angle (§4.1)."""
        pc = self._bbox_center(person['bbox'])
        near_box = self._is_near(pc, boxes, self.BOX_PROXIMITY)
        if not near_box:
            return None

        kp = pose_keypoints[0] if pose_keypoints else None

        # --- Without pose: bbox aspect ratio proxy ---
        if kp is None:
            w = person['bbox'][2] - person['bbox'][0]
            h = person['bbox'][3] - person['bbox'][1]
            aspect = h / max(w, 1)
            if aspect < 1.3:
                return self._violation(
                    'UNSAFE_LIFTING', 'HIGH', '4',
                    'WHS §4: Unsafe lifting posture — bending at waist instead of using legs. '
                    'Use mechanical aids or squat-lift technique.',
                    pid, person['bbox'])
            return None

        # --- With pose keypoints: spine angle ---
        try:
            shoulder_y = (kp[5][1] + kp[6][1]) / 2
            hip_y = (kp[11][1] + kp[12][1]) / 2
            shoulder_x = (kp[5][0] + kp[6][0]) / 2
            hip_x = (kp[11][0] + kp[12][0]) / 2

            dx = hip_x - shoulder_x
            dy = hip_y - shoulder_y
            angle = abs(math.degrees(math.atan2(dx, abs(dy))))

            if angle > self.MAX_RISKY_LIFT_ANGLE:
                return self._violation(
                    'UNSAFE_LIFTING_CRITICAL', 'CRITICAL', '4',
                    f'WHS §4: Dangerous lifting posture ({angle:.0f}°). '
                    'Risk of serious back injury. Use mechanical aids or team lift.',
                    pid, person['bbox'], angle=angle)
            elif angle > self.MAX_SAFE_LIFT_ANGLE:
                return self._violation(
                    'RISKY_LIFTING', 'MEDIUM', '4',
                    f'WHS §4: Risky lifting posture ({angle:.0f}°). '
                    'Bend knees, keep back straight, hold load close.',
                    pid, person['bbox'], angle=angle)
        except (IndexError, KeyError):
            pass
        return None

    def _check_twisting_posture(self, person, pose_keypoints, pid):
        """Check for trunk twisting while lifting (§4.2)."""
        try:
            kp = pose_keypoints[0]
            # Shoulder midpoint vs hip midpoint horizontal offset
            sh_x = (kp[5][0] + kp[6][0]) / 2
            sh_y = (kp[5][1] + kp[6][1]) / 2
            hip_x = (kp[11][0] + kp[12][0]) / 2
            hip_y = (kp[11][1] + kp[12][1]) / 2

            # Angle between shoulder line and hip line
            shoulder_angle = math.degrees(math.atan2(
                kp[5][1] - kp[6][1], kp[5][0] - kp[6][0]))
            hip_angle = math.degrees(math.atan2(
                kp[11][1] - kp[12][1], kp[11][0] - kp[12][0]))
            twist = abs(shoulder_angle - hip_angle)
            # Normalize to 0-180
            if twist > 180:
                twist = 360 - twist
            if twist > 90:
                twist = 180 - twist

            if twist > self.MAX_TWIST_ANGLE:
                return self._violation(
                    'TWISTING_LIFT', 'HIGH', '4',
                    f'WHS §4: Trunk twisting detected while handling load ({twist:.0f}°). '
                    'Move feet to face the load — do not twist the spine.',
                    pid, person['bbox'])
        except (IndexError, KeyError):
            pass
        return None

    def _check_overhead_lift(self, person, pose_keypoints, pid):
        """Check for overhead reaching with load (§4.3)."""
        try:
            kp = pose_keypoints[0]
            shoulder_y = (kp[5][1] + kp[6][1]) / 2
            wrist_y = (kp[9][1] + kp[10][1]) / 2
            # Wrists above shoulders = overhead
            if wrist_y < shoulder_y * self.OVERHEAD_LIFT_SHOULDER_RATIO:
                return self._violation(
                    'OVERHEAD_LIFT', 'MEDIUM', '4',
                    'WHS §4: Overhead reaching with load detected. '
                    'Use platform steps or mechanical lift assist — avoid overhead handling.',
                    pid, person['bbox'])
        except (IndexError, KeyError):
            pass
        return None

    # =================================================================
    #  Spatial helpers
    # =================================================================

    @staticmethod
    def _is_near(person_center, targets, max_dist):
        """True if any target bbox center is within max_dist of person_center."""
        for t in targets:
            tc = ComplianceChecker._bbox_center(t['bbox'])
            if ComplianceChecker._distance(person_center, tc) < max_dist:
                return True
        return False

    @staticmethod
    def _is_in_front(person_bbox, vehicle_bbox):
        """Check if person is roughly in front of a vehicle (based on bbox overlap)."""
        px, py, px2, py2 = person_bbox
        vx, vy, vx2, vy2 = vehicle_bbox
        # Person bbox overlaps or is directly ahead of vehicle in x-range
        person_cx = (px + px2) / 2
        if vx <= person_cx <= vx2:
            return True
        return False

    @staticmethod
    def _person_under_load(person_bbox, load_bbox):
        """True if >30% of the load bbox is positioned above the person bbox."""
        px1, py1, px2, py2 = person_bbox
        lx1, ly1, lx2, ly2 = load_bbox
        # Load must overlap person horizontally and be above them vertically
        overlap_x = max(0, min(px2, lx2) - max(px1, lx1))
        overlap_ratio = overlap_x / max((px2 - px1), 1)
        load_above = ly2 < py2 and ly1 < py1  # load is higher than person
        return load_above and overlap_ratio > ComplianceChecker.LOAD_OVERHEAD_OVERLAP

    @staticmethod
    def _violation(vtype, severity, whs_section, message, person_id, bbox, **extra):
        """Build a standardized violation dict."""
        v = {
            'type': vtype,
            'severity': severity,
            'whs_section': whs_section,
            'message': message,
            'person': person_id,
            'person_bbox': bbox,
        }
        v.update(extra)
        return v

    # =================================================================
    #  Geometry helpers
    # =================================================================

    @staticmethod
    def _bbox_center(bbox):
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

    @staticmethod
    def _distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
