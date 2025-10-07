"""Defines motion sequences for robot arm movements."""

import math
from typing import Dict

# commands are not interpolated between keyframes
COMMANDS = [
    "xvel",
    "yvel",
    "yawrate",
]
# positions are interpolated between keyframes for smoother motions
POSITIONS = [
    "base_height",
    "base_roll",
    "base_pitch",
    "rshoulderpitch",
    "rshoulderroll",
    "rshoulderyaw",
    "relbowpitch",
    "rwristroll",
    "lshoulderpitch",
    "lshoulderroll",
    "lshoulderyaw",
    "lelbowpitch",
    "lwristroll",
]


class Motion:
    """Represents a sequence of arm motions with keyframes and interpolation."""

    def __init__(self, keyframes: Dict[float, Dict[str, float]], dt: float) -> None:
        """Initialize a motion sequence.

        Args:
            keyframes: Dictionary mapping time to command/position values
            dt: Time step for interpolation
        """
        self.keyframes = dict(sorted(keyframes.items()))
        self.times = sorted(keyframes.keys())
        self.total_duration = self.times[-1]
        self.dt = dt
        self.current_time = 0.0

    def get_next_motion_frame(self) -> Dict[str, float] | None:
        """Get the next motion frame.

        Returns:
            Dictionary of all values,
            or None if sequence is complete
        """
        if self.current_time > self.total_duration:
            return None

        # Find surrounding keyframes
        next_idx = 0
        while next_idx < len(self.times) and self.times[next_idx] < self.current_time:
            next_idx += 1

        # Get interpolated positions and commands
        if next_idx == 0:
            frame = self.keyframes[self.times[0]]
        elif next_idx >= len(self.times):
            frame = self.keyframes[self.times[-1]]
        else:
            # Interpolate between keyframes
            prev_time = self.times[next_idx - 1]
            next_time = self.times[next_idx]
            prev_frame = self.keyframes[prev_time]
            next_frame = self.keyframes[next_time]

            alpha = (self.current_time - prev_time) / (next_time - prev_time)

            frame = {}
            # Interpolate positions
            for joint in POSITIONS:
                prev_pos = prev_frame.get(joint, 0.0)
                next_pos = next_frame.get(joint, 0.0)
                frame[joint] = prev_pos + alpha * (next_pos - prev_pos)

            # Use the previous keyframe's commands (no interpolation)
            for cmd in COMMANDS:
                frame[cmd] = prev_frame.get(cmd, 0.0)

        # Build output with all values
        all_values = {
            **{cmd: frame.get(cmd, 0.0) for cmd in COMMANDS},
            **{joint: frame.get(joint, 0.0) for joint in POSITIONS},
        }

        self.current_time += self.dt
        return all_values

    def reset(self) -> None:
        """Reset the motion sequence to start."""
        self.current_time = 0.0


def create_test_motion(joint_name: str, dt: float = 0.01) -> Motion:
    """Creates a test motion for a joint: 0° -> -90° -> 90° -> 0°.

    Args:
        joint_name: Name of the joint to test
        dt: Time step between frames
    """
    keyframes = {
        0.0: {joint_name: math.radians(0.0)},
        1.0: {joint_name: math.radians(-90.0)},
        2.0: {joint_name: math.radians(90.0)},
        3.0: {joint_name: math.radians(0.0)},
    }
    return Motion(keyframes, dt=dt)


def create_wave(dt: float = 0.01) -> Motion:
    """Creates a waving motion sequence."""
    keyframes = {
        0.0: {},
        0.5: {
            "rshoulderroll": math.radians(-45.0),
            "relbowpitch": math.radians(90.0),
        },
        1.0: {
            "rshoulderroll": math.radians(-45.0),
            "rshoulderyaw": math.radians(45.0),
            "relbowpitch": math.radians(90.0),
        },
        1.5: {
            "rshoulderroll": math.radians(-45.0),
            "rshoulderyaw": math.radians(-45.0),
            "relbowpitch": math.radians(90.0),
        },
        2.0: {
            "rshoulderroll": math.radians(-10.0),
            "relbowpitch": math.radians(90.0),
        },
        2.5: {},
    }
    return Motion(keyframes, dt=dt)


def create_salute(dt: float = 0.01) -> Motion:
    """Creates a saluting motion sequence."""
    keyframes = {
        0.0: {},
        0.6: {
            "rshoulderroll": math.radians(-90.0),
            "relbowpitch": math.radians(0.0),
        },
        1.1: {
            "rshoulderroll": math.radians(-90.0),
            "relbowpitch": math.radians(85.0),
        },
        2.1: {
            "rshoulderroll": math.radians(-90.0),
            "relbowpitch": math.radians(85.0),
        },
        2.6: {
            "rshoulderroll": math.radians(-10.0),
            "relbowpitch": math.radians(0.0),
        },
        3.0: {},
    }
    return Motion(keyframes, dt=dt)


def create_pickup(dt: float = 0.01) -> Motion:
    """Creates a pickup motion sequence."""
    keyframes = {
        0.0: {},
        0.3: {
            "rshoulderpitch": 0.0,
            "rshoulderroll": math.radians(10.0),
            "relbowpitch": 0.0,
            "rwristroll": 0.0,
            "lshoulderpitch": 0.0,
            "lshoulderroll": math.radians(-10.0),
            "lelbowpitch": 0.0,
            "lwristroll": 0.0,
        },
        0.8: {
            "rshoulderpitch": math.radians(-45.0),
            "rshoulderroll": math.radians(20.0),
            "relbowpitch": math.radians(-10.0),
            "rwristroll": 0.0,
            "lshoulderpitch": math.radians(45.0),
            "lshoulderroll": math.radians(-20.0),
            "lelbowpitch": math.radians(10.0),
            "lwristroll": 0.0,
            "base_pitch": math.radians(15.0),
        },
        1.3: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(20.0),
            "relbowpitch": math.radians(-45.0),
            "rwristroll": math.radians(20.0),
            "lshoulderpitch": math.radians(90.0),
            "lshoulderroll": math.radians(-20.0),
            "lelbowpitch": math.radians(45.0),
            "lwristroll": math.radians(-20.0),
            "base_height": -0.2,
            "base_pitch": math.radians(30.0),
        },
        1.6: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(20.0),
            "relbowpitch": math.radians(-90.0),
            "rwristroll": math.radians(30.0),
            "lshoulderpitch": math.radians(90.0),
            "lshoulderroll": math.radians(-20.0),
            "lelbowpitch": math.radians(90.0),
            "lwristroll": math.radians(-30.0),
            "base_height": -0.2,
            "base_pitch": math.radians(30.0),
        },
        2.1: {
            "rshoulderpitch": math.radians(-45.0),
            "rshoulderroll": math.radians(20.0),
            "relbowpitch": math.radians(-90.0),
            "rwristroll": math.radians(30.0),
            "lshoulderpitch": math.radians(45.0),
            "lshoulderroll": math.radians(-20.0),
            "lelbowpitch": math.radians(90.0),
            "lwristroll": math.radians(-30.0),
            "base_pitch": math.radians(15.0),
        },
        2.6: {
            "rshoulderpitch": 0.0,
            "rshoulderroll": math.radians(10.0),
            "relbowpitch": 0.0,
            "rwristroll": 0.0,
            "lshoulderpitch": 0.0,
            "lshoulderroll": math.radians(-10.0),
            "lelbowpitch": 0.0,
            "lwristroll": 0.0,
        },
        3.0: {},
    }
    return Motion(keyframes, dt=dt)


def create_wild_walk(dt: float = 0.01) -> Motion:
    """Creates a wild walking motion with extreme arm movements."""
    keyframes = {
        0.0: {
            "rshoulderpitch": 0.0,
            "rshoulderroll": 0.0,
            "rshoulderyaw": 0.0,
            "relbowpitch": 0.0,
            "lshoulderpitch": 0.0,
            "lshoulderroll": 0.0,
            "lshoulderyaw": 0.0,
            "lelbowpitch": 0.0,
        },
        1.0: {
            "rshoulderpitch": math.radians(-135.0),
            "rshoulderroll": math.radians(-90.0),
            "rshoulderyaw": math.radians(90.0),
            "relbowpitch": math.radians(120.0),
            "lshoulderpitch": math.radians(135.0),
            "lshoulderroll": math.radians(90.0),
            "lshoulderyaw": math.radians(-90.0),
            "lelbowpitch": math.radians(-120.0),
            "xvel": 0.5,
            "yvel": 0.0,
            "yawrate": 1.0,
        },
        2.0: {
            "rshoulderpitch": math.radians(90.0),
            "rshoulderroll": math.radians(45.0),
            "rshoulderyaw": math.radians(-90.0),
            "relbowpitch": math.radians(-90.0),
            "lshoulderpitch": math.radians(-90.0),
            "lshoulderroll": math.radians(-45.0),
            "lshoulderyaw": math.radians(90.0),
            "lelbowpitch": math.radians(90.0),
            "xvel": 0.0,
            "yvel": 0.5,
            "yawrate": -1.0,
        },
        3.0: {
            "rshoulderpitch": math.radians(-180.0),
            "rshoulderroll": math.radians(-120.0),
            "rshoulderyaw": math.radians(180.0),
            "relbowpitch": math.radians(145.0),
            "lshoulderpitch": math.radians(180.0),
            "lshoulderroll": math.radians(120.0),
            "lshoulderyaw": math.radians(-180.0),
            "lelbowpitch": math.radians(-145.0),
            "xvel": 0.5,
            "yvel": -0.5,
            "yawrate": 2.0,
        },
        4.0: {},
    }
    return Motion(keyframes, dt=dt)


def create_zombie_walk(dt: float = 0.01) -> Motion:
    """Creates a classic zombie shambling motion with stiff arms."""
    keyframes = {
        0.0: {},
        0.5: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(20.0),
            "rshoulderyaw": math.radians(90.0),
            "relbowpitch": math.radians(-90.0),
            "lshoulderpitch": math.radians(90.0),
            "lshoulderroll": math.radians(-20.0),
            "lshoulderyaw": math.radians(-90.0),
            "lelbowpitch": math.radians(90.0),
            "base_pitch": math.radians(15.0),
            "xvel": 0.2,
        },
        3.5: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(20.0),
            "rshoulderyaw": math.radians(90.0),
            "relbowpitch": math.radians(-90.0),
            "lshoulderpitch": math.radians(90.0),
            "lshoulderroll": math.radians(-20.0),
            "lshoulderyaw": math.radians(-90.0),
            "lelbowpitch": math.radians(90.0),
            "base_pitch": math.radians(15.0),
            "xvel": 0.2,
        },
        4.0: {},
    }
    return Motion(keyframes, dt=dt)


def create_pirouette(dt: float = 0.01) -> Motion:
    """Creates a graceful spinning pirouette motion."""
    keyframes = {
        0.0: {},
        0.5: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(-90.0),
            "rshoulderyaw": 0.0,
            "relbowpitch": math.radians(30.0),
            "rwristroll": math.radians(-20.0),
            "lshoulderpitch": math.radians(-90.0),
            "lshoulderroll": math.radians(90.0),
            "lshoulderyaw": 0.0,
            "lelbowpitch": math.radians(-30.0),
            "lwristroll": math.radians(20.0),
            "base_height": 0.0,
            "xvel": 0.0,
            "yvel": 0.0,
            "yawrate": 0.0,
        },
        # Preparation - rise and begin
        1.5: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(-120.0),
            "rshoulderyaw": math.radians(45.0),
            "relbowpitch": math.radians(45.0),
            "rwristroll": math.radians(-30.0),
            "lshoulderpitch": math.radians(-90.0),
            "lshoulderroll": math.radians(120.0),
            "lshoulderyaw": math.radians(-45.0),
            "lelbowpitch": math.radians(-45.0),
            "lwristroll": math.radians(30.0),
            "base_height": 0.15,
            "xvel": 0.0,
            "yvel": 0.0,
            "yawrate": 0.5,
        },
        # First rotation
        3.5: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(-120.0),
            "rshoulderyaw": math.radians(45.0),
            "relbowpitch": math.radians(45.0),
            "rwristroll": math.radians(-30.0),
            "lshoulderpitch": math.radians(-90.0),
            "lshoulderroll": math.radians(120.0),
            "lshoulderyaw": math.radians(-45.0),
            "lelbowpitch": math.radians(-45.0),
            "lwristroll": math.radians(30.0),
            "base_height": 0.15,
            "xvel": 0.0,
            "yvel": 0.0,
            "yawrate": 1.0,
        },
        # Second rotation - slightly faster
        5.5: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(-120.0),
            "rshoulderyaw": math.radians(45.0),
            "relbowpitch": math.radians(45.0),
            "rwristroll": math.radians(-30.0),
            "lshoulderpitch": math.radians(-90.0),
            "lshoulderroll": math.radians(120.0),
            "lshoulderyaw": math.radians(-45.0),
            "lelbowpitch": math.radians(-45.0),
            "lwristroll": math.radians(30.0),
            "base_height": 0.15,
            "xvel": 0.0,
            "yvel": 0.0,
            "yawrate": 1.2,
        },
        # Start slowing down
        7.0: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(-120.0),
            "rshoulderyaw": math.radians(45.0),
            "relbowpitch": math.radians(45.0),
            "rwristroll": math.radians(-30.0),
            "lshoulderpitch": math.radians(-90.0),
            "lshoulderroll": math.radians(120.0),
            "lshoulderyaw": math.radians(-45.0),
            "lelbowpitch": math.radians(-45.0),
            "lwristroll": math.radians(30.0),
            "base_height": 0.15,
            "xvel": 0.0,
            "yvel": 0.0,
            "yawrate": 0.5,
        },
        # Final pose
        8.0: {
            "rshoulderpitch": math.radians(-90.0),
            "rshoulderroll": math.radians(-90.0),
            "rshoulderyaw": 0.0,
            "relbowpitch": math.radians(30.0),
            "rwristroll": math.radians(-20.0),
            "lshoulderpitch": math.radians(-90.0),
            "lshoulderroll": math.radians(90.0),
            "lshoulderyaw": 0.0,
            "lelbowpitch": math.radians(-30.0),
            "lwristroll": math.radians(20.0),
            "base_height": 0.0,
            "xvel": 0.0,
            "yvel": 0.0,
            "yawrate": 0.0,
        },
        8.5: {},
    }
    return Motion(keyframes, dt=dt)


def create_backflip(dt: float = 0.01) -> Motion:
    """Creates an attempted backflip motion using base height, pitch and counter-rotating arms."""
    keyframes = {
        # Start neutral
        0.0: {},
        # Start standing
        0.2: {
            "rshoulderpitch": 0.0,  # Arms neutral
            "lshoulderpitch": 0.0,
            "base_height": 0.0,
            "base_pitch": 0.0,
        },
        # Mid squat, arms starting to rise
        0.6: {
            "rshoulderpitch": math.radians(-45.0),  # Arms raising
            "lshoulderpitch": math.radians(45.0),
            "base_height": -0.15,
            "base_pitch": 0.0,
        },
        # Deep squat, arms forward
        1.0: {
            "rshoulderpitch": math.radians(-90.0),  # Arms forward
            "lshoulderpitch": math.radians(90.0),
            "base_height": -0.3,
            "base_pitch": 0.0,
        },
        1.4: {
            "rshoulderpitch": math.radians(-90.0),  # Arms forward
            "lshoulderpitch": math.radians(90.0),
            "base_height": -0.3,
            "base_pitch": 0.0,
            "xvel": 0.0,
            "yvel": 0.0,
            "yawrate": 0.0,
        },
        # Arms swing back hard as jump starts
        1.41: {
            "rshoulderpitch": math.radians(90.0),  # Arms back
            "lshoulderpitch": math.radians(-90.0),
            "base_height": 0.4,
            "base_pitch": math.radians(-50.0),
        },
        # Peak of jump, arms coming forward to drive flip
        1.6: {
            "rshoulderpitch": math.radians(135.0),  # Arms driving forward and down
            "lshoulderpitch": math.radians(-135.0),
            "base_height": 0.4,
            "base_pitch": math.radians(-180.0),
        },
        # Complete rotation, arms up to spot landing
        1.8: {
            "rshoulderpitch": math.radians(90.0),  # Arms up
            "lshoulderpitch": math.radians(-90.0),
            "base_height": 0.2,
            "base_pitch": math.radians(-340.0),
        },
        # Landing squat, arms forward for balance
        2.0: {
            "rshoulderpitch": math.radians(-45.0),  # Arms forward for balance
            "lshoulderpitch": math.radians(45.0),
            "base_height": -0.3,
            "base_pitch": math.radians(-360.0),
        },
        2.5: {},
    }
    return Motion(keyframes, dt=dt)


def create_boxing(dt: float = 0.01) -> Motion:
    """Creates a boxing motion sequence."""
    keyframes = {
        # Start neutral
        0.0: {},
        # Raise guard - walk forward
        0.2: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),  # Forward and up
            "rshoulderroll": math.radians(15.0),  # Slightly inward
            "rshoulderyaw": math.radians(30.0),  # Rotate in
            "relbowpitch": math.radians(30.0),  # Bent up
            # Left arm
            "lshoulderpitch": math.radians(55.0),  # Forward and up
            "lshoulderroll": math.radians(-15.0),  # Slightly inward
            "lshoulderyaw": math.radians(-30.0),  # Rotate in
            "lelbowpitch": math.radians(-30.0),  # Bent up
            "base_pitch": math.radians(10.0),
            "xvel": 0.2,
        },
        # Hold guard
        1.8: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Left punch land
        1.81: {
            # Right arm stays in guard
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm prepares punch
            "lshoulderpitch": math.radians(100.0),  # extend
            "lshoulderroll": math.radians(-15.0),  # Keep tight to body
            "lshoulderyaw": math.radians(-30.0),  # Natural rotation
            "lelbowpitch": math.radians(85.0),  # straight
            "base_pitch": math.radians(10.0),
        },
        # Left punch hold
        2.0: {
            # Right arm stays in guard
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(100.0),  # extend
            "lshoulderroll": math.radians(-15.0),  # Keep tight to body
            "lshoulderyaw": math.radians(-30.0),  # Natural rotation
            "lelbowpitch": math.radians(85.0),  # straight
            "base_pitch": math.radians(10.0),
        },
        # Return to guard
        2.2: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Hold guard briefly
        2.5: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Right punch land
        2.51: {
            # Right arm extends
            "rshoulderpitch": math.radians(-100.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(-85.0),
            # Left arm stays in guard
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Right punch hold
        2.7: {
            # Right arm extended
            "rshoulderpitch": math.radians(-100.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(-85.0),
            # Left arm stays in guard
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Return to guard and start sideways movement
        2.9: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
            "yvel": 0.3,  # Start moving sideways
            "yawrate": -0.8,  # Start rotating
        },
        # stop movement, hold guard
        4.6: {
            # Maintain guard position during movement
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Right punch land
        4.61: {
            # Right arm extends
            "rshoulderpitch": math.radians(-100.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(-85.0),
            # Left arm stays in guard
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # hold right punch
        4.8: {
            # Right arm extended
            "rshoulderpitch": math.radians(-100.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(-85.0),
            # Left arm stays in guard
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # back to guard
        5.0: {
            # Right arm guard
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # left punch land
        5.01: {
            # Right arm guard
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm extends
            "lshoulderpitch": math.radians(100.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(85.0),
            "base_pitch": math.radians(10.0),
        },
        # left punch hold
        5.2: {
            # Right arm guard
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm extends
            "lshoulderpitch": math.radians(100.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(85.0),
            "base_pitch": math.radians(10.0),
        },
        # Final return to guard
        5.4: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # empty keyframe interpolate back to start
        5.6: {},
    }
    return Motion(keyframes, dt=dt)


def create_boxing_guard_hold(dt: float = 0.01) -> Motion:
    """Raise guard and hold without walking."""
    keyframes = {
        # Start neutral
        0.0: {},
        # Raise guard
        0.2: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),  # Forward and up
            "rshoulderroll": math.radians(15.0),  # Slightly inward
            "rshoulderyaw": math.radians(30.0),  # Rotate in
            "relbowpitch": math.radians(30.0),  # Bent up
            # Left arm
            "lshoulderpitch": math.radians(55.0),  # Forward and up
            "lshoulderroll": math.radians(-15.0),  # Slightly inward
            "lshoulderyaw": math.radians(-30.0),  # Rotate in
            "lelbowpitch": math.radians(-30.0),  # Bent up
            "base_pitch": math.radians(10.0),
        },
        # Hold guard for a few seconds
        3.0: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        3.5: {},
    }
    return Motion(keyframes, dt=dt)


def create_boxing_left_punch(dt: float = 0.01) -> Motion:
    """Raise guard, throw left punch, return to guard. No walking."""
    keyframes = {
        # Start neutral
        0.0: {},
        # Raise guard
        0.2: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Hold guard briefly
        0.5: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Left punch land
        0.51: {
            # Right arm stays in guard
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm extends
            "lshoulderpitch": math.radians(100.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(85.0),
            "base_pitch": math.radians(10.0),
        },
        # Left punch hold
        0.7: {
            # Right arm stays in guard
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm extended
            "lshoulderpitch": math.radians(100.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(85.0),
            "base_pitch": math.radians(10.0),
        },
        # Return to guard
        0.9: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Hold guard long
        3.0: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        3.2: {},
    }
    return Motion(keyframes, dt=dt)


def create_boxing_right_punch(dt: float = 0.01) -> Motion:
    """Raise guard, throw right punch, return to guard. No walking."""
    keyframes = {
        # Start neutral
        0.0: {},
        # Raise guard
        0.2: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Hold guard briefly
        0.5: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Right punch land
        0.51: {
            # Right arm extends
            "rshoulderpitch": math.radians(-100.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(-85.0),
            # Left arm stays in guard
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Right punch hold
        0.7: {
            # Right arm extended
            "rshoulderpitch": math.radians(-100.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(-85.0),
            # Left arm stays in guard
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Return to guard
        0.9: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        # Hold guard long
        3.0: {
            # Right arm
            "rshoulderpitch": math.radians(-55.0),
            "rshoulderroll": math.radians(15.0),
            "rshoulderyaw": math.radians(30.0),
            "relbowpitch": math.radians(30.0),
            # Left arm
            "lshoulderpitch": math.radians(55.0),
            "lshoulderroll": math.radians(-15.0),
            "lshoulderyaw": math.radians(-30.0),
            "lelbowpitch": math.radians(-30.0),
            "base_pitch": math.radians(10.0),
        },
        3.2: {},
    }
    return Motion(keyframes, dt=dt)


def create_cone_motion(dt: float = 0.01) -> Motion:
    """Creates a conical motion by rotating base roll and pitch in a circular pattern."""
    # Parameters for the cone motion
    cone_angle = math.radians(15.0)  # Angle of the cone from vertical
    duration = 5.0  # Total duration of one complete motion
    ramp_duration = 0.5  # Time to ramp up/down

    keyframes: dict[float, dict[str, float]] = {}
    num_keyframes = 16  # Number of points around the circle

    # Add initial keyframes to rampt to starting position
    keyframes[0.0] = {}
    keyframes[ramp_duration] = {
        "base_roll": 0.0,
        "base_pitch": cone_angle,
    }

    # Do the circular motion
    for i in range(num_keyframes + 1):  # +1 to close the circle
        t = ramp_duration + (i / num_keyframes) * (duration - 2 * ramp_duration)
        angle = (i / num_keyframes) * 2 * math.pi

        # Calculate roll and pitch to create circular motion
        roll = cone_angle * math.sin(angle)
        pitch = cone_angle * math.cos(angle)

        keyframes[t] = {
            "base_roll": roll,
            "base_pitch": pitch,
        }

    # Ramp down to 0,0
    keyframes[duration] = {}

    return Motion(keyframes, dt=dt)


def create_come_at_me(dt: float = 0.01) -> Motion:
    """Opens arms into a slightly raised T-pose ("come at me bro"). No walking."""
    keyframes = {
        # Start neutral
        0.0: {},
        # Move to slightly raised T-pose
        0.6: {
            # Right arm (slightly above horizontal)
            "rshoulderpitch": 0.0,
            "rshoulderroll": math.radians(-100.0),
            "rshoulderyaw": 0.0,
            "relbowpitch": math.radians(10.0),
            # Left arm (slightly above horizontal)
            "lshoulderpitch": 0.0,
            "lshoulderroll": math.radians(100.0),
            "lshoulderyaw": 0.0,
            "lelbowpitch": math.radians(-10.0),
            # Neutral base
            "base_pitch": 0.0,
            "base_height": 0.0,
        },
        # Hold the pose
        3.0: {
            "rshoulderpitch": 0.0,
            "rshoulderroll": math.radians(-100.0),
            "rshoulderyaw": 0.0,
            "relbowpitch": math.radians(10.0),
            "lshoulderpitch": 0.0,
            "lshoulderroll": math.radians(100.0),
            "lshoulderyaw": 0.0,
            "lelbowpitch": math.radians(-10.0),
            "base_pitch": 0.0,
            "base_height": 0.0,
        },
        # Empty keyframe to interpolate back to start
        3.2: {},
    }
    return Motion(keyframes, dt=dt)


def create_squats(dt: float = 0.01) -> Motion:
    """Creates a motion sequence of two squats."""
    keyframes = {
        0.0: {},
        0.3: {
            "base_height": 0.0,
        },
        1.3: {
            "base_height": -0.25,
        },
        1.8: {
            "base_height": -0.25,
        },
        2.8: {
            "base_height": 0.0,
        },
        3.3: {
            "base_height": 0.0,
        },
        4.3: {
            "base_height": -0.25,
        },
        4.8: {
            "base_height": -0.25,
        },
        5.8: {},
    }
    return Motion(keyframes, dt=dt)


MOTIONS = {
    "wave": create_wave,
    "salute": create_salute,
    "pickup": create_pickup,
    "wild_walk": create_wild_walk,
    "zombie_walk": create_zombie_walk,
    "squats": create_squats,
    "pirouette": create_pirouette,
    "backflip": create_backflip,
    "boxing": create_boxing,
    "boxing_guard_hold": create_boxing_guard_hold,
    "boxing_left_punch": create_boxing_left_punch,
    "boxing_right_punch": create_boxing_right_punch,
    "come_at_me": create_come_at_me,
    "cone": create_cone_motion,
    # Test motions - automatically generate test functions for each joint
    **{
        f"test_{''.join(word[0].lower() for word in joint_name.split('_')[1:-1])}": lambda dt=0.01,
        joint=joint_name: create_test_motion(joint, dt)
        for joint_name in POSITIONS[3:]
    },
}
