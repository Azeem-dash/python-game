import math

import mediapipe as mp
import numpy as np


class HandGestureRecognizer:
    """Class for recognizing hand gestures using MediaPipe."""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.gestures = {
            "open_palm": self._is_open_palm,
            "closed_fist": self._is_closed_fist,
            "pointing": self._is_pointing,
            "victory": self._is_victory,
            "thumbs_up": self._is_thumbs_up,
        }

    def recognize_gesture(self, hand_landmarks):
        """Recognize the gesture from hand landmarks.

        Args:
            hand_landmarks: MediaPipe hand landmarks

        Returns:
            str: The recognized gesture name or None if no gesture is recognized
        """
        if not hand_landmarks:
            return None

        for gesture_name, gesture_func in self.gestures.items():
            if gesture_func(hand_landmarks):
                return gesture_name

        return "unknown"

    def get_hand_position(self, hand_landmarks, img_width, img_height):
        """Get the position of the hand.

        Args:
            hand_landmarks: MediaPipe hand landmarks
            img_width: Width of the image
            img_height: Height of the image

        Returns:
            tuple: (x, y) position of the hand's palm
        """
        if not hand_landmarks:
            return None

        # Use the wrist as the hand position
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        x = int(wrist.x * img_width)
        y = int(wrist.y * img_height)

        return (x, y)

    def get_finger_positions(self, hand_landmarks, img_width, img_height):
        """Get the positions of fingertips.

        Args:
            hand_landmarks: MediaPipe hand landmarks
            img_width: Width of the image
            img_height: Height of the image

        Returns:
            dict: Dictionary with the positions of each fingertip
        """
        if not hand_landmarks:
            return None

        fingertips = {
            "thumb": self.mp_hands.HandLandmark.THUMB_TIP,
            "index": self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            "middle": self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            "ring": self.mp_hands.HandLandmark.RING_FINGER_TIP,
            "pinky": self.mp_hands.HandLandmark.PINKY_TIP,
        }

        positions = {}
        for finger_name, landmark_id in fingertips.items():
            landmark = hand_landmarks.landmark[landmark_id]
            positions[finger_name] = (
                int(landmark.x * img_width),
                int(landmark.y * img_height),
            )

        return positions

    def calculate_velocity(self, current_pos, previous_pos, delta_time):
        """Calculate velocity vector from position change.

        Args:
            current_pos: Current position (x, y)
            previous_pos: Previous position (x, y)
            delta_time: Time difference in seconds

        Returns:
            tuple: (vx, vy) velocity components
        """
        if not current_pos or not previous_pos or delta_time == 0:
            return (0, 0)

        vx = (current_pos[0] - previous_pos[0]) / delta_time
        vy = (current_pos[1] - previous_pos[1]) / delta_time

        return (vx, vy)

    def _is_open_palm(self, hand_landmarks):
        """Check if the hand gesture is an open palm."""
        fingers_up = self._count_fingers_up(hand_landmarks)
        return fingers_up >= 4

    def _is_closed_fist(self, hand_landmarks):
        """Check if the hand gesture is a closed fist."""
        fingers_up = self._count_fingers_up(hand_landmarks)
        return fingers_up <= 1  # Only thumb might be up

    def _is_pointing(self, hand_landmarks):
        """Check if the hand gesture is pointing (only index finger up)."""
        # Get fingertip y positions relative to the pip (middle knuckle)
        thumb_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.THUMB_TIP,
            self.mp_hands.HandLandmark.THUMB_IP,
        )
        index_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
        )
        middle_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        )
        ring_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
        )
        pinky_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.PINKY_TIP,
            self.mp_hands.HandLandmark.PINKY_PIP,
        )

        # Only index finger is up, others are down
        return index_up and not middle_up and not ring_up and not pinky_up

    def _is_victory(self, hand_landmarks):
        """Check if the hand gesture is a victory sign (index and middle fingers up)."""
        index_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
        )
        middle_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        )
        ring_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
        )
        pinky_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.PINKY_TIP,
            self.mp_hands.HandLandmark.PINKY_PIP,
        )

        # Index and middle fingers are up, others are down
        return index_up and middle_up and not ring_up and not pinky_up

    def _is_thumbs_up(self, hand_landmarks):
        """Check if the hand gesture is a thumbs up."""
        # Thumb is up, other fingers are curled
        thumb_up = self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.THUMB_TIP,
            self.mp_hands.HandLandmark.THUMB_IP,
            is_thumb=True,
        )
        fingers_up = self._count_fingers_up(hand_landmarks)

        # Only thumb is up
        return thumb_up and fingers_up == 1

    def _is_finger_up(self, hand_landmarks, fingertip_id, pip_id, is_thumb=False):
        """Check if a finger is extended (pointing up).

        Args:
            hand_landmarks: MediaPipe hand landmarks
            fingertip_id: MediaPipe landmark ID for fingertip
            pip_id: MediaPipe landmark ID for the PIP joint (middle knuckle)
            is_thumb: Whether the finger is a thumb (special case)

        Returns:
            bool: True if the finger is extended/up
        """
        fingertip = hand_landmarks.landmark[fingertip_id]
        pip = hand_landmarks.landmark[pip_id]

        if is_thumb:
            # For thumb, we use x instead of y and check if it's to the side
            # This depends on hand orientation, so it's not perfect
            wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            return fingertip.x < wrist.x
        else:
            # For other fingers, if fingertip is higher (smaller y) than PIP, finger is up
            return fingertip.y < pip.y

    def _count_fingers_up(self, hand_landmarks):
        """Count the number of extended fingers.

        Args:
            hand_landmarks: MediaPipe hand landmarks

        Returns:
            int: Number of extended fingers
        """
        count = 0

        # Check thumb
        if self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.THUMB_TIP,
            self.mp_hands.HandLandmark.THUMB_IP,
            is_thumb=True,
        ):
            count += 1

        # Check index finger
        if self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
        ):
            count += 1

        # Check middle finger
        if self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        ):
            count += 1

        # Check ring finger
        if self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
        ):
            count += 1

        # Check pinky finger
        if self._is_finger_up(
            hand_landmarks,
            self.mp_hands.HandLandmark.PINKY_TIP,
            self.mp_hands.HandLandmark.PINKY_PIP,
        ):
            count += 1

        return count
