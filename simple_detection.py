import math

import cv2
import numpy as np


class SimpleHandDetector:
    """A simplified hand detector using basic OpenCV functions instead of MediaPipe."""

    def __init__(self):
        # Parameters for skin detection - wider range for better detection
        self.lower_skin = np.array(
            [0, 30, 60], dtype=np.uint8
        )  # More permissive lower bound
        self.upper_skin = np.array(
            [30, 255, 255], dtype=np.uint8
        )  # Higher upper hue bound

        # Previous hand positions for smoothing
        self.prev_positions = []
        self.max_positions = 5

        # Current gesture
        self.current_gesture = "unknown"

        # Background subtraction
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=200, varThreshold=25, detectShadows=False
        )
        self.has_bg_model = False
        self.frames_to_learn = 30
        self.frame_count = 0

        # Adaptive parameters for better tracking
        self.min_contour_area = 3000  # Minimum area for hand contour

    def process_frame(self, frame, face_mask=None):
        """Process a frame to detect a hand and its center.

        Args:
            frame: OpenCV frame (BGR format)
            face_mask: Optional mask to exclude face areas (255=include, 0=exclude)

        Returns:
            tuple: (hand_center, contour, processed_frame)
        """
        # Create a visualization frame
        processed_frame = frame.copy()

        # Apply background subtraction if we have a model
        if self.frame_count < self.frames_to_learn:
            # Learning phase - just apply the model but don't use it yet
            self.bg_subtractor.apply(frame)
            self.frame_count += 1

            if self.frame_count == self.frames_to_learn:
                self.has_bg_model = True
                # Add text to show background model is ready
                cv2.putText(
                    processed_frame,
                    "Background model ready! Hand detection improved",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

        # Apply actual background subtraction if model is ready
        motion_mask = None
        if self.has_bg_model:
            # Get foreground mask
            motion_mask = self.bg_subtractor.apply(frame)
            # Clean up the mask
            motion_mask = cv2.morphologyEx(
                motion_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)
            )
            motion_mask = cv2.morphologyEx(
                motion_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)
            )
            # Only consider pixels with value 255 (confident foreground)
            motion_mask = cv2.threshold(motion_mask, 200, 255, cv2.THRESH_BINARY)[1]

        # Convert to HSV color space for skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a binary mask of skin color
        skin_mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)

        # Combine skin detection with motion detection if available
        if motion_mask is not None:
            mask = cv2.bitwise_and(skin_mask, motion_mask)
        else:
            mask = skin_mask

        # If a face mask is provided, use it to exclude face areas
        if face_mask is not None:
            # Apply face mask to exclude face areas from skin detection
            mask = cv2.bitwise_and(mask, face_mask)

        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(
            mask, kernel, iterations=3
        )  # More dilation to connect hand parts
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        # Final thresholding to get binary mask
        mask = cv2.threshold(mask, 60, 255, cv2.THRESH_BINARY)[1]

        # Add the mask in a small corner for debugging
        h, w = frame.shape[:2]
        mask_small = cv2.resize(mask, (w // 4, h // 4))
        # Add small mask in the bottom right corner
        processed_frame[h - h // 4 : h, w - w // 4 : w] = cv2.cvtColor(
            mask_small, cv2.COLOR_GRAY2BGR
        )

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # If no contours found
        if not contours:
            return None, None, processed_frame

        # Find the largest contour (presumably the hand)
        valid_contours = [
            c for c in contours if cv2.contourArea(c) > self.min_contour_area
        ]
        if not valid_contours:
            return None, None, processed_frame

        max_contour = max(valid_contours, key=cv2.contourArea)

        # Draw the contour on the visualization frame
        cv2.drawContours(processed_frame, [max_contour], -1, (0, 255, 0), 2)

        # Find the center of the hand
        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            hand_center = (cx, cy)

            # Apply smoothing
            self.prev_positions.append(hand_center)
            if len(self.prev_positions) > self.max_positions:
                self.prev_positions.pop(0)

            # Calculate the average position for smoothing
            avg_x = sum(pos[0] for pos in self.prev_positions) // len(
                self.prev_positions
            )
            avg_y = sum(pos[1] for pos in self.prev_positions) // len(
                self.prev_positions
            )
            smooth_center = (avg_x, avg_y)

            # Draw the hand center
            cv2.circle(processed_frame, smooth_center, 5, (0, 0, 255), -1)

            # Get the current gesture
            self.detect_gesture(max_contour)

            # Draw the gesture text
            cv2.putText(
                processed_frame,
                self.current_gesture,
                (cx, cy - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2,
            )

            return smooth_center, max_contour, processed_frame

        return None, None, processed_frame

    def detect_gesture(self, contour):
        """Detect a simple hand gesture based on contour properties.

        Args:
            contour: Hand contour from OpenCV
        """
        # Calculate contour area and perimeter
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        # Convex hull and defects for finger detection
        hull = cv2.convexHull(contour, returnPoints=False)

        # If hull is empty, return unknown gesture
        if len(hull) < 3:
            self.current_gesture = "unknown"
            return

        try:
            defects = cv2.convexityDefects(contour, hull)
        except:
            self.current_gesture = "unknown"
            return

        # If no defects found, return closed fist gesture
        if defects is None:
            self.current_gesture = "closed_fist"
            return

        # Count fingers using convexity defects
        finger_count = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])
            far = tuple(contour[f][0])

            # Calculate angle between start, far, and end points
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

            try:
                angle = math.acos((b**2 + c**2 - a**2) / (2 * b * c))
            except:
                continue

            # If angle is less than 90 degrees, it's likely a finger gap
            if angle <= math.pi / 2:
                finger_count += 1

        # Determine gesture based on finger count
        if finger_count == 0:
            self.current_gesture = "closed_fist"
        elif finger_count == 1:
            self.current_gesture = "pointing"
        elif finger_count == 2:
            self.current_gesture = "victory"
        elif finger_count >= 4:
            self.current_gesture = "open_palm"
        else:
            # For 3 fingers, check contour shape to distinguish from thumbs up
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area

            if solidity > 0.9:
                self.current_gesture = "thumbs_up"
            else:
                self.current_gesture = "unknown"

    def get_hand_position(self, center, frame_width, frame_height):
        """Get hand position normalized to the frame size.

        Args:
            center: Center point of the hand (x, y)
            frame_width: Width of the frame
            frame_height: Height of the frame

        Returns:
            tuple: Normalized hand position (x, y)
        """
        if center is None:
            return None

        return center

    def get_gesture(self):
        """Get the current detected gesture.

        Returns:
            str: Gesture name
        """
        return self.current_gesture
