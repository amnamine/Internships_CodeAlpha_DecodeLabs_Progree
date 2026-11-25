"""
TASK 4: Object Detection and Tracking
--------------------------------------
- Reads a video file (not real-time/webcam) using OpenCV.
- Uses the pretrained YOLO26n model (yolo26n.pt) for object detection.
- Processes each frame to detect objects and draw bounding boxes.
- Applies object tracking (ByteTrack, a SORT-family algorithm) to assign
  persistent tracking IDs to each detected object across frames.
- Draws labels + tracking IDs on every frame and saves the result as a
  new annotated video file.

Requirements:
    pip install ultralytics opencv-python

Usage:
    python object_detection_tracking.py --input input_video.mp4 --output output_video.mp4
"""

import argparse
import time

import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="YOLO26n Object Detection + Tracking on a video file")
    parser.add_argument("--input", type=str, default="video.mp4",
                         help="Path to the input video file")
    parser.add_argument("--output", type=str, default="output_video.mp4",
                         help="Path to save the annotated output video")
    parser.add_argument("--model", type=str, default="yolo26n.pt",
                         help="Path/name of the pretrained YOLO model weights")
    parser.add_argument("--conf", type=float, default=0.4,
                         help="Confidence threshold for detections")
    parser.add_argument("--tracker", type=str, default="bytetrack.yaml",
                         help="Tracker config: bytetrack.yaml (SORT-family) or botsort.yaml")
    parser.add_argument("--show", action="store_true",
                         help="Display the video while processing (optional)")
    return parser.parse_args()


def get_color(track_id: int):
    """Generate a consistent BGR color for a given tracking ID."""
    rng = (37 * int(track_id)) % 255
    return (int((rng * 5) % 255), int((rng * 11) % 255), int((rng * 17) % 255))


def main():
    args = parse_args()

    # ---------------------------------------------------------------
    # 1. Load the pretrained YOLO26n model
    # ---------------------------------------------------------------
    print(f"[INFO] Loading model: {args.model}")
    model = YOLO(args.model)

    # ---------------------------------------------------------------
    # 2. Open the input video file (NOT a webcam — offline processing)
    # ---------------------------------------------------------------
    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise IOError(f"Could not open video file: {args.input}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[INFO] Input video: {args.input} ({width}x{height} @ {fps:.1f} FPS, {total_frames} frames)")

    # ---------------------------------------------------------------
    # 3. Set up the video writer for the annotated output
    # ---------------------------------------------------------------
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height))

    frame_idx = 0
    start_time = time.time()

    # ---------------------------------------------------------------
    # 4. Process each frame: detect + track + draw
    # ---------------------------------------------------------------
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # end of video

        frame_idx += 1

        # Run detection + tracking on this single frame.
        # persist=True keeps track identities consistent across frames.
        results = model.track(
            frame,
            persist=True,
            conf=args.conf,
            tracker=args.tracker,
            verbose=False,
        )

        result = results[0]
        boxes = result.boxes

        if boxes is not None and boxes.id is not None:
            xyxy = boxes.xyxy.cpu().numpy()
            track_ids = boxes.id.cpu().numpy().astype(int)
            confs = boxes.conf.cpu().numpy()
            classes = boxes.cls.cpu().numpy().astype(int)
            class_names = result.names

            for box, track_id, conf, cls_id in zip(xyxy, track_ids, confs, classes):
                x1, y1, x2, y2 = map(int, box)
                label_name = class_names.get(cls_id, str(cls_id))
                color = get_color(track_id)

                # Bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # Label + tracking ID
                label = f"ID {track_id} | {label_name} {conf:.2f}"
                (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame, (x1, y1 - text_h - 8), (x1 + text_w + 4, y1), color, -1)
                cv2.putText(frame, label, (x1 + 2, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Overlay frame counter / progress info
        cv2.putText(frame, f"Frame {frame_idx}/{total_frames}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

        writer.write(frame)

        if args.show:
            cv2.imshow("YOLO26 Detection + Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if frame_idx % 30 == 0 or frame_idx == total_frames:
            print(f"[INFO] Processed frame {frame_idx}/{total_frames}")

    # ---------------------------------------------------------------
    # 5. Clean up
    # ---------------------------------------------------------------
    elapsed = time.time() - start_time
    cap.release()
    writer.release()
    if args.show:
        cv2.destroyAllWindows()

    print(f"[DONE] Processed {frame_idx} frames in {elapsed:.1f}s "
          f"({frame_idx / elapsed:.1f} FPS average)")
    print(f"[DONE] Annotated video saved to: {args.output}")


if __name__ == "__main__":
    main()