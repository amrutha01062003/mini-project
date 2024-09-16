import cv2
import easyocr

def initialize_camera():
    # Open a connection to the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    return cap

def arrange_text(result):
    lines = []
    current_line = []
    current_y = None
    threshold = 30  # Vertical threshold for grouping text into the same line

    for (bbox, text, prob) in sorted(result, key=lambda r: (r[0][0][1], r[0][0][0])):
        top_left, _, bottom_right, _ = bbox
        x_min, y_min = top_left
        x_max, y_max = bottom_right

        if current_y is None:
            current_y = y_min

        if abs(y_min - current_y) < threshold:
            current_line.append((text, x_min))
        else:
            # Sort current line based on the x_min position
            current_line = sorted(current_line, key=lambda x: x[1])
            lines.append(" ".join([text for text, _ in current_line]))
            current_line = [(text, x_min)]
            current_y = y_min

    if current_line:
        current_line = sorted(current_line, key=lambda x: x[1])
        lines.append(" ".join([text for text, _ in current_line]))

    return "\n".join(lines)

def capture_and_recognize_text(cap):
    # Initialize the EasyOCR reader
    reader = easyocr.Reader(['en'])

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image")
                break

            # Convert the frame to grayscale (as EasyOCR works better on grayscale images)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Use EasyOCR to detect text
            result = reader.readtext(gray)

            # Arrange detected text properly
            arranged_text = arrange_text(result)

            # Print detected text to the terminal
            print("\nDetected text:\n")
            print(arranged_text)

            # Save the detected text to a file
            save_to_file(arranged_text)
            print("Text saved to file. Exiting.")
            break

            # Check for 'q' key press to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting on user request.")
                break

    except cv2.error as e:
        print(f"OpenCV error: {e}")

    finally:
        # When everything is done, release the capture
        cap.release()
        cv2.destroyAllWindows()

def save_to_file(text):
    with open("detected_text.txt", "w") as file:
        file.write(text)

def main():
    cap = initialize_camera()
    if cap is None:
        return

    print("Press 'q' to quit the camera feed...")

    try:
        capture_and_recognize_text(cap)
    finally:
        # When everything is done, release the capture
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
