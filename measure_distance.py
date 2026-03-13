import cv2
import math

# Load image
image = cv2.imread(r"D:\Usecases\silver_ornaments_customer_unattended_1773383062639.jpg")
clone = image.copy()

points = []

def click_event(event, x, y, flags, param):
    global points, image
    
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

        # Draw point
        cv2.circle(image, (x, y), 5, (0,0,255), -1)

        # If two points selected
        if len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]

            # Draw line
            cv2.line(image, (x1,y1), (x2,y2), (255,0,0), 2)

            # Calculate distance
            distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)

            # Show distance
            cv2.putText(image, f"Dist: {int(distance)} px",
                        (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0,255,0), 2)

            print("Distance:", distance, "pixels")

            points = []

        cv2.imshow("Image", image)

cv2.imshow("Image", image)
cv2.setMouseCallback("Image", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()