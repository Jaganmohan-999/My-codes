import argparse
import csv
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np
from ultralytics import YOLO


# ================= USER CONFIG =================
VIDEO_PATH = r"D:\RS_Videos\paramount\record_20260415_134453.mp4"
OUTPUT_PATH = r"D:\RS_Videos\paramount\output_mobile_alert.mp4"
DETECTOR_MODEL_PATH = "yolo11s.pt"
POSE_MODEL_PATH = "yolo11s-pose.pt"
PERSON_CLASS_ID = 0
PHONE_CLASS_ID = 67
PERSON_CONF = 0.35
PHONE_CONF = 0.20
POSE_CONF = 0.35
KEYPOINT_CONF = 0.35
IMGSZ = 960
DEVICE = None
CLEAR_PHONE_CONF = 0.35
# ==============================================


PERSON_KP = {
    "left_ear": 3,
    "right_ear": 4,
    "left_shoulder": 5,
    "right_shoulder": 6,
    "left_elbow": 7,
    "right_elbow": 8,
    "left_wrist": 9,
    "right_wrist": 10,
    "left_hip": 11,
    "right_hip": 12,
}


@dataclass
class Detection:
    box: Tuple[float, float, float, float]
    conf: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect mobile usage in a video using YOLO detection + YOLO pose."
    )
    parser.add_argument("--video", default=VIDEO_PATH, help="Path to the input video.")
    parser.add_argument(
        "--output",
        default=OUTPUT_PATH,
        help="Path to the output annotated video. Defaults next to the input video.",
    )
    parser.add_argument(
        "--detector-model",
        default=DETECTOR_MODEL_PATH,
        help="YOLO detection model path/name. Must detect person and phone classes.",
    )
    parser.add_argument(
        "--pose-model",
        default=POSE_MODEL_PATH,
        help="YOLO pose model path/name.",
    )
    parser.add_argument(
        "--person-class",
        type=int,
        default=PERSON_CLASS_ID,
        help="Class id for person in the detection model.",
    )
    parser.add_argument(
        "--phone-class",
        type=int,
        default=PHONE_CLASS_ID,
        help="Class id for cell phone/mobile in the detection model.",
    )
    parser.add_argument(
        "--person-conf",
        type=float,
        default=PERSON_CONF,
        help="Confidence threshold for person detections.",
    )
    parser.add_argument(
        "--phone-conf",
        type=float,
        default=PHONE_CONF,
        help="Confidence threshold for phone detections.",
    )
    parser.add_argument(
        "--pose-conf",
        type=float,
        default=POSE_CONF,
        help="Confidence threshold for pose detections.",
    )
    parser.add_argument(
        "--keypoint-conf",
        type=float,
        default=KEYPOINT_CONF,
        help="Minimum confidence for a pose keypoint to be used.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=IMGSZ,
        help="Inference image size for both models.",
    )
    parser.add_argument(
        "--device",
        default=DEVICE,
        help="Inference device such as cpu, 0, 0,1. Defaults to Ultralytics auto selection.",
    )
    return parser.parse_args()


def ensure_output_path(video_path: str, output_path: Optional[str]) -> str:
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        return output_path

    src_dir = os.path.dirname(video_path) or "."
    src_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(src_dir, f"{src_name}_mobile_alert.mp4")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    return output_path


def bbox_iou(box_a: Sequence[float], box_b: Sequence[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    if inter_area <= 0:
        return 0.0

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter_area
    return inter_area / denom if denom > 0 else 0.0


def point_distance(point_a: Sequence[float], point_b: Sequence[float]) -> float:
    return float(math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1]))


def joint_angle(
    point_a: Optional[Tuple[float, float]],
    point_b: Optional[Tuple[float, float]],
    point_c: Optional[Tuple[float, float]],
) -> Optional[float]:
    if point_a is None or point_b is None or point_c is None:
        return None

    ba = np.array([point_a[0] - point_b[0], point_a[1] - point_b[1]], dtype=float)
    bc = np.array([point_c[0] - point_b[0], point_c[1] - point_b[1]], dtype=float)
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    if norm_ba == 0 or norm_bc == 0:
        return None

    cosine = float(np.dot(ba, bc) / (norm_ba * norm_bc))
    cosine = max(-1.0, min(1.0, cosine))
    return float(np.degrees(np.arccos(cosine)))


def is_talking_pose(
    wrist: Optional[Tuple[float, float]],
    elbow: Optional[Tuple[float, float]],
    ear: Optional[Tuple[float, float]],
    shoulder: Optional[Tuple[float, float]],
    elbow_angle: Optional[float],
    diag: float,
    height: float,
) -> Tuple[bool, float]:
    if wrist is None or elbow is None or ear is None or shoulder is None or elbow_angle is None:
        return False, 0.0

    wrist_ear_dist = point_distance(wrist, ear)
    elbow_ear_dist = point_distance(elbow, ear)
    wrist_near_ear = wrist_ear_dist < diag * 0.18
    elbow_near_face = elbow_ear_dist < diag * 0.28
    wrist_above_shoulder = wrist[1] <= shoulder[1] + height * 0.10
    elbow_bent = 25 <= elbow_angle <= 145

    if not (wrist_near_ear and elbow_near_face and wrist_above_shoulder and elbow_bent):
        return False, 0.0

    wrist_score = max(0.0, 1.0 - (wrist_ear_dist / (diag * 0.18)))
    elbow_score = max(0.0, 1.0 - (elbow_ear_dist / (diag * 0.28)))
    angle_score = max(0.0, 1.0 - (abs(elbow_angle - 85.0) / 60.0))
    score = 0.45 * wrist_score + 0.25 * elbow_score + 0.30 * angle_score
    return True, min(score, 0.99)


def is_hand_hold_pose(
    wrist: Optional[Tuple[float, float]],
    elbow: Optional[Tuple[float, float]],
    shoulder: Optional[Tuple[float, float]],
    hip: Optional[Tuple[float, float]],
    elbow_angle: Optional[float],
    diag: float,
    width: float,
) -> Tuple[bool, float]:
    if wrist is None or elbow is None or shoulder is None or hip is None or elbow_angle is None:
        return False, 0.0

    between_shoulder_hip = shoulder[1] - width * 0.05 <= wrist[1] <= hip[1] + width * 0.05
    wrist_inside_body_band = abs(wrist[0] - shoulder[0]) < width * 0.35
    elbow_bent = 30 <= elbow_angle <= 165
    wrist_elbow_dist = point_distance(wrist, elbow)
    forearm_visible = wrist_elbow_dist < diag * 0.30

    if not (between_shoulder_hip and wrist_inside_body_band and elbow_bent and forearm_visible):
        return False, 0.0

    height_span = max(1.0, hip[1] - shoulder[1])
    vertical_mid = shoulder[1] + 0.55 * height_span
    vertical_score = max(0.0, 1.0 - (abs(wrist[1] - vertical_mid) / max(1.0, height_span * 0.6)))
    angle_score = max(0.0, 1.0 - (abs(elbow_angle - 95.0) / 70.0))
    center_score = max(0.0, 1.0 - (abs(wrist[0] - shoulder[0]) / max(1.0, width * 0.35)))
    score = 0.35 * vertical_score + 0.35 * angle_score + 0.30 * center_score
    return True, min(score, 0.99)


def point_in_box(point: Sequence[float], box: Sequence[float], margin: float = 0.0) -> bool:
    x1, y1, x2, y2 = box
    return (x1 - margin) <= point[0] <= (x2 + margin) and (y1 - margin) <= point[1] <= (y2 + margin)


def clip_box(box: Sequence[float], width: int, height: int) -> Tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return (
        max(0, min(width - 1, int(x1))),
        max(0, min(height - 1, int(y1))),
        max(0, min(width - 1, int(x2))),
        max(0, min(height - 1, int(y2))),
    )


def get_detection_results(
    frame: np.ndarray,
    detector_model: YOLO,
    pose_model: YOLO,
    args: argparse.Namespace,
) -> Tuple[List[Detection], List[Detection], List[Dict[str, object]]]:
    det_result = detector_model.predict(
        source=frame,
        conf=min(args.person_conf, args.phone_conf),
        imgsz=args.imgsz,
        device=args.device,
        verbose=False,
    )[0]
    pose_result = pose_model.predict(
        source=frame,
        conf=args.pose_conf,
        imgsz=args.imgsz,
        device=args.device,
        verbose=False,
    )[0]

    persons: List[Detection] = []
    phones: List[Detection] = []

    if det_result.boxes is not None:
        boxes = det_result.boxes.xyxy.cpu().numpy()
        confs = det_result.boxes.conf.cpu().numpy()
        clss = det_result.boxes.cls.cpu().numpy().astype(int)

        for box, conf, cls_id in zip(boxes, confs, clss):
            detection = Detection(tuple(float(v) for v in box.tolist()), float(conf))
            if cls_id == args.person_class and conf >= args.person_conf:
                persons.append(detection)
            elif cls_id == args.phone_class and conf >= args.phone_conf:
                phones.append(detection)

    poses: List[Dict[str, object]] = []
    if pose_result.boxes is not None and pose_result.keypoints is not None:
        pose_boxes = pose_result.boxes.xyxy.cpu().numpy()
        pose_confs = pose_result.boxes.conf.cpu().numpy()
        keypoints = pose_result.keypoints.data.cpu().numpy()

        for pose_box, pose_conf, pose_kps in zip(pose_boxes, pose_confs, keypoints):
            if pose_conf < args.pose_conf:
                continue
            poses.append(
                {
                    "box": tuple(float(v) for v in pose_box.tolist()),
                    "conf": float(pose_conf),
                    "keypoints": pose_kps,
                }
            )

    return persons, phones, poses


def get_keypoint(
    keypoints: np.ndarray, idx: int, min_conf: float
) -> Optional[Tuple[float, float]]:
    if keypoints.shape[0] <= idx:
        return None
    x, y, conf = keypoints[idx]
    if conf < min_conf:
        return None
    return float(x), float(y)


def average_point(points: Sequence[Optional[Tuple[float, float]]]) -> Optional[Tuple[float, float]]:
    valid_points = [pt for pt in points if pt is not None]
    if not valid_points:
        return None
    xs = [pt[0] for pt in valid_points]
    ys = [pt[1] for pt in valid_points]
    return float(sum(xs) / len(xs)), float(sum(ys) / len(ys))


def match_pose_to_person(
    person_box: Sequence[float], poses: Sequence[Dict[str, object]]
) -> Optional[Dict[str, object]]:
    best_pose = None
    best_iou = 0.0
    for pose in poses:
        iou = bbox_iou(person_box, pose["box"])  # type: ignore[index]
        if iou > best_iou:
            best_iou = iou
            best_pose = pose
    return best_pose if best_iou >= 0.15 else None


def get_relevant_phones(
    person_box: Sequence[float], phones: Sequence[Detection]
) -> List[Detection]:
    x1, y1, x2, y2 = person_box
    width = x2 - x1
    height = y2 - y1
    margin = max(width, height) * 0.08
    relevant = []

    for phone in phones:
        px1, py1, px2, py2 = phone.box
        center = ((px1 + px2) * 0.5, (py1 + py2) * 0.5)
        if point_in_box(center, person_box, margin=margin) or bbox_iou(person_box, phone.box) > 0.0:
            relevant.append(phone)

    return relevant


def evaluate_mobile_usage(
    person: Detection,
    pose: Optional[Dict[str, object]],
    phones: Sequence[Detection],
    keypoint_conf: float,
) -> Tuple[bool, float, str]:
    x1, y1, x2, y2 = person.box
    width = max(1.0, x2 - x1)
    height = max(1.0, y2 - y1)
    diag = math.hypot(width, height)
    relevant_phones = get_relevant_phones(person.box, phones)

    phone_near_hand_score = 0.0
    phone_in_person_score = 0.0
    calling_pose_score = 0.0
    holding_pose_score = 0.0
    reasons: List[str] = []

    if relevant_phones:
        phone_in_person_score = max(phone.conf for phone in relevant_phones)

    if pose is not None:
        keypoints = pose["keypoints"]  # type: ignore[index]

        left_wrist = get_keypoint(keypoints, PERSON_KP["left_wrist"], keypoint_conf)
        right_wrist = get_keypoint(keypoints, PERSON_KP["right_wrist"], keypoint_conf)
        left_elbow = get_keypoint(keypoints, PERSON_KP["left_elbow"], keypoint_conf)
        right_elbow = get_keypoint(keypoints, PERSON_KP["right_elbow"], keypoint_conf)
        left_ear = get_keypoint(keypoints, PERSON_KP["left_ear"], keypoint_conf)
        right_ear = get_keypoint(keypoints, PERSON_KP["right_ear"], keypoint_conf)
        left_shoulder = get_keypoint(keypoints, PERSON_KP["left_shoulder"], keypoint_conf)
        right_shoulder = get_keypoint(keypoints, PERSON_KP["right_shoulder"], keypoint_conf)
        left_hip = get_keypoint(keypoints, PERSON_KP["left_hip"], keypoint_conf)
        right_hip = get_keypoint(keypoints, PERSON_KP["right_hip"], keypoint_conf)
        left_elbow_angle = joint_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = joint_angle(right_shoulder, right_elbow, right_wrist)

        left_talking, left_talking_score = is_talking_pose(
            left_wrist, left_elbow, left_ear, left_shoulder, left_elbow_angle, diag, height
        )
        right_talking, right_talking_score = is_talking_pose(
            right_wrist, right_elbow, right_ear, right_shoulder, right_elbow_angle, diag, height
        )
        calling_pose_score = max(
            calling_pose_score,
            left_talking_score if left_talking else 0.0,
            right_talking_score if right_talking else 0.0,
        )

        left_hold, left_hold_score = is_hand_hold_pose(
            left_wrist, left_elbow, left_shoulder, left_hip, left_elbow_angle, diag, width
        )
        right_hold, right_hold_score = is_hand_hold_pose(
            right_wrist, right_elbow, right_shoulder, right_hip, right_elbow_angle, diag, width
        )
        holding_pose_score = max(
            holding_pose_score,
            left_hold_score if left_hold else 0.0,
            right_hold_score if right_hold else 0.0,
        )

        if relevant_phones:
            for phone in relevant_phones:
                px1, py1, px2, py2 = phone.box
                phone_center = ((px1 + px2) * 0.5, (py1 + py2) * 0.5)
                dists = []
                for point in (left_wrist, right_wrist, left_ear, right_ear):
                    if point is not None:
                        dists.append(point_distance(phone_center, point))
                if dists:
                    min_dist = min(dists)
                    normalized = max(0.0, 1.0 - (min_dist / (diag * 0.22)))
                    phone_near_hand_score = max(phone_near_hand_score, normalized * phone.conf)

                if left_elbow and left_wrist:
                    if point_distance(phone_center, left_wrist) < diag * 0.18 or point_distance(phone_center, left_elbow) < diag * 0.16:
                        phone_near_hand_score = max(phone_near_hand_score, 0.7 * phone.conf)
                if right_elbow and right_wrist:
                    if point_distance(phone_center, right_wrist) < diag * 0.18 or point_distance(phone_center, right_elbow) < diag * 0.16:
                        phone_near_hand_score = max(phone_near_hand_score, 0.7 * phone.conf)

                if left_hold and left_wrist is not None and point_distance(phone_center, left_wrist) < diag * 0.18:
                    holding_pose_score = max(holding_pose_score, max(left_hold_score, 0.75 * phone.conf))
                if right_hold and right_wrist is not None and point_distance(phone_center, right_wrist) < diag * 0.18:
                    holding_pose_score = max(holding_pose_score, max(right_hold_score, 0.75 * phone.conf))

    clear_phone_visible = phone_in_person_score >= CLEAR_PHONE_CONF
    talking_pose_match = calling_pose_score >= 0.42
    holding_pose_match = holding_pose_score >= 0.45 or (holding_pose_score >= 0.30 and phone_near_hand_score >= 0.30)

    if talking_pose_match:
        reasons.append("talking-on-phone")
    elif holding_pose_match:
        reasons.append("phone-in-hand")
    elif clear_phone_visible:
        reasons.append("phone-visible")

    alert_score = max(
        phone_in_person_score,
        calling_pose_score * (0.55 + 0.45 * max(phone_in_person_score, phone_near_hand_score)),
        holding_pose_score * (0.60 + 0.40 * max(phone_in_person_score, phone_near_hand_score)),
    )
    alert = clear_phone_visible or talking_pose_match or holding_pose_match

    reason_text = ", ".join(reasons) if reasons else "no-alert"
    return alert, min(alert_score, 0.99), reason_text


def annotate_frame(
    frame: np.ndarray,
    persons: Sequence[Detection],
    phones: Sequence[Detection],
    poses: Sequence[Dict[str, object]],
    args: argparse.Namespace,
    csv_writer: csv.writer,
    frame_index: int,
    fps: float,
) -> Tuple[np.ndarray, int]:
    annotated = frame.copy()
    alert_count = 0

    for phone in phones:
        px1, py1, px2, py2 = clip_box(phone.box, frame.shape[1], frame.shape[0])
        cv2.rectangle(annotated, (px1, py1), (px2, py2), (0, 255, 255), 2)
        cv2.putText(
            annotated,
            f"phone {phone.conf:.2f}",
            (px1, max(20, py1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

    for idx, person in enumerate(persons, start=1):
        pose = match_pose_to_person(person.box, poses)
        alert, score, reason = evaluate_mobile_usage(person, pose, phones, args.keypoint_conf)
        x1, y1, x2, y2 = clip_box(person.box, frame.shape[1], frame.shape[0])

        color = (0, 0, 255) if alert else (0, 200, 0)
        thickness = 3 if alert else 2
        label = f"mobile usage {score:.2f}" if alert else f"person {person.conf:.2f}"

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)
        cv2.putText(
            annotated,
            label,
            (x1, max(22, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2,
            cv2.LINE_AA,
        )
        if alert:
            cv2.putText(
                annotated,
                reason,
                (x1, min(frame.shape[0] - 10, y2 + 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
                cv2.LINE_AA,
            )
            alert_count += 1

        timestamp_sec = frame_index / fps if fps > 0 else 0.0
        csv_writer.writerow(
            [
                frame_index,
                f"{timestamp_sec:.2f}",
                idx,
                f"{person.conf:.4f}",
                int(alert),
                f"{score:.4f}",
                reason,
                x1,
                y1,
                x2,
                y2,
            ]
        )

    cv2.putText(
        annotated,
        f"alerts: {alert_count}",
        (20, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 0, 255) if alert_count else (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    return annotated, alert_count


def main() -> None:
    args = parse_args()
    if not args.video or args.video == r"D:\path\to\input.mp4":
        raise ValueError("Set VIDEO_PATH at the top of the file or pass --video while running the script.")

    if not args.detector_model:
        raise ValueError(
            "Set DETECTOR_MODEL_PATH at the top of the file or pass --detector-model while running the script."
        )

    if not args.pose_model:
        raise ValueError("Set POSE_MODEL_PATH at the top of the file or pass --pose-model while running the script.")

    output_path = ensure_output_path(args.video, args.output)
    csv_path = os.path.splitext(output_path)[0] + "_alerts.csv"

    detector_model = YOLO(args.detector_model)
    pose_model = YOLO(args.pose_model)

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise FileNotFoundError(f"Unable to open video: {args.video}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
    fps = float(cap.get(cv2.CAP_PROP_FPS)) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Unable to create output video: {output_path}")

    processed_frames = 0
    total_alert_frames = 0

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                "frame_index",
                "timestamp_sec",
                "person_index",
                "person_conf",
                "mobile_alert",
                "alert_score",
                "reason",
                "x1",
                "y1",
                "x2",
                "y2",
            ]
        )

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            persons, phones, poses = get_detection_results(frame, detector_model, pose_model, args)
            annotated_frame, alert_count = annotate_frame(
                frame,
                persons,
                phones,
                poses,
                args,
                csv_writer,
                processed_frames,
                fps,
            )
            writer.write(annotated_frame)

            processed_frames += 1
            if alert_count > 0:
                total_alert_frames += 1

            if processed_frames % 30 == 0:
                if total_frames > 0:
                    print(
                        f"Processed {processed_frames}/{total_frames} frames "
                        f"({processed_frames / total_frames:.1%})"
                    )
                else:
                    print(f"Processed {processed_frames} frames")

    cap.release()
    writer.release()

    print(f"Finished. Output video: {output_path}")
    print(f"Alert log saved to: {csv_path}")
    print(f"Frames with at least one alert: {total_alert_frames}/{processed_frames}")


if __name__ == "__main__":
    main()
