import cv2

video_path = r"D:\RS_sorting\Phani -\output\inference_output\inferenced_183_82_114_243_cam401_20260227_172503.mp4"  # Change this

cap = cv2.VideoCapture(video_path)

# Counters
tp = 0
fp = 0
fn = 0
correct_classified = 0
wrong_classified = 0

print("\nInstructions:")
print("t -> True Positive (correct detection)")
print("f -> False Positive (wrong detection)")
print("m -> False Negative (missed person)")
print("c -> Correct Classification")
print("w -> Wrong Classification")
print("q -> Quit and calculate results\n")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    display_text = f"TP:{tp} FP:{fp} FN:{fn} CC:{correct_classified} WC:{wrong_classified}"
    cv2.putText(frame, display_text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Inference Video", frame)

    key = cv2.waitKey(25) & 0xFF

    if key == ord('t'):
        tp += 1
    elif key == ord('f'):
        fp += 1
    elif key == ord('m'):
        fn += 1
    elif key == ord('c'):
        correct_classified += 1
    elif key == ord('w'):
        wrong_classified += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Automatically compute total actual persons
total_actual = tp + fn

# Detection metrics
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / total_actual if total_actual > 0 else 0
f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

# Classification accuracy (only on detected persons)
classification_accuracy = correct_classified / tp if tp > 0 else 0

# End-to-end accuracy
system_accuracy = correct_classified / total_actual if total_actual > 0 else 0

print("\n========== RESULTS ==========")
print(f"Total Actual Persons: {total_actual}")
print(f"Detection Precision: {precision*100:.2f}%")
print(f"Detection Recall: {recall*100:.2f}%")
print(f"Detection F1 Score: {f1*100:.2f}%")
print(f"Classification Accuracy (on detected persons): {classification_accuracy*100:.2f}%")
print(f"Overall End-to-End Accuracy: {system_accuracy*100:.2f}%")
print("=============================")