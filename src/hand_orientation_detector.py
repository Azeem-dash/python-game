import math

import cv2
import numpy as np


class HandOrientationDetector:
    """A detector optimized for detecting hand orientation using OpenCV."""

    def __init__(self):
        # Parameters for skin detection
        self.lower_skin = np.array([0, 48, 80], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        # Previous hand orientations for smoothing
        self.prev_orientations = []
        self.max_orientations = 5

        # Current calculated orientation angle in degrees (0-360)
        self.current_angle = 0

        # Current direction based on angle
        self.current_direction = "unknown"

    def process_frame(self, frame, face_mask=None):
        """Process a frame to detect hand orientation.

        Args:
            frame: OpenCV frame (BGR format)
            face_mask: Optional mask to exclude face areas (255=include, 0=exclude)

        Returns:
            tuple: (hand_center, contour, direction_vector, processed_frame)
        """
        # Create a copy for visualization
        processed_frame = frame.copy()

        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a binary mask of skin color
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)

        # If a face mask is provided, use it to exclude face areas
        if face_mask is not None:
            mask = cv2.bitwise_and(mask, face_mask)

        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        # Add the mask in a small corner for debugging
        if face_mask is not None:
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
            return None, None, None, processed_frame

        # Find the largest contour (presumably the hand)
        max_contour = max(contours, key=cv2.contourArea)

        # If contour is too small, ignore it
        if cv2.contourArea(max_contour) < 3000:
            return None, None, None, processed_frame

        # Draw the contour on the visualization frame
        cv2.drawContours(processed_frame, [max_contour], -1, (0, 255, 0), 2)

        # Calculate hand center
        M = cv2.moments(max_contour)
        if M["m00"] == 0:
            return None, None, None, processed_frame

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        hand_center = (cx, cy)

        # Draw hand center
        cv2.circle(processed_frame, hand_center, 5, (0, 0, 255), -1)

        # Calculate hand orientation
        direction_vector = self.calculate_orientation(
            max_contour, hand_center, processed_frame
        )

        # Add angle information to the frame
        self.add_angle_info(processed_frame)

        return hand_center, max_contour, direction_vector, processed_frame

    def calculate_orientation(self, contour, center, frame):
        """Calculate the orientation of the hand contour.

        Args:
            contour: The hand contour
            center: The center point of the hand
            frame: The visualization frame

        Returns:
            tuple: Direction vector (x, y) normalized
        """
        try:
            # Find the rotated bounding rectangle
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.array(box, dtype=np.int32)

            # Draw the rotated bounding box
            cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)

            # Get the angle of the rectangle
            angle = rect[2]

            # Adjust angle based on rectangle dimensions
            if rect[1][0] < rect[1][1]:  # Width < Height
                angle += 90

            # Convert to range 0-360 for easier interpretation
            if angle < 0:
                angle += 360

            # Smooth the angle with previous readings
            self.prev_orientations.append(angle)
            if len(self.prev_orientations) > self.max_orientations:
                self.prev_orientations.pop(0)

            # Calculate average angle
            avg_angle = sum(self.prev_orientations) / len(self.prev_orientations)
            self.current_angle = avg_angle

            # Convert angle to radians
            angle_rad = math.radians(avg_angle)

            # Calculate direction vector
            direction = (math.cos(angle_rad), math.sin(angle_rad))

            # Draw direction line
            line_length = 100
            end_point = (
                int(center[0] + direction[0] * line_length),
                int(center[1] + direction[1] * line_length),
            )
            cv2.line(frame, center, end_point, (255, 0, 255), 2)

            # Determine direction name
            self.update_direction()

            return direction

        except Exception as e:
            print(f"Error calculating hand orientation: {e}")
            return None

    def update_direction(self):
        """Update the direction name based on current angle."""
        angle = self.current_angle

        if angle > 315 or angle < 45:
            self.current_direction = "RIGHT"
        elif 45 <= angle < 135:
            self.current_direction = "DOWN"
        elif 135 <= angle < 225:
            self.current_direction = "LEFT"
        else:  # 225 <= angle < 315
            self.current_direction = "UP"

    def add_angle_info(self, frame):
        """Add angle and direction information to the frame."""
        # Add angle text
        cv2.putText(
            frame,
            f"Angle: {self.current_angle:.1f}°",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Add direction text
        cv2.putText(
            frame,
            f"Direction: {self.current_direction}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

    def get_direction(self):
        """Get the current direction name.

        Returns:
            str: Direction name (UP, DOWN, LEFT, RIGHT, or unknown)
        """
        return self.current_direction
