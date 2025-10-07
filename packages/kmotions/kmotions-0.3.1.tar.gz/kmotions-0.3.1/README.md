# kmotions

Keyframe-based motion sequences for KBOT robot arms.

## Usage

```python
from kmotions.motions import MOTIONS

motion = MOTIONS["wave"](dt=0.01)
while (frame := motion.get_next_motion_frame()) is not None:
    # Send frame to robot
    pass
```


