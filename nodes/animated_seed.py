import re
import random

class AnimatedSeed:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "keyframes": ("STRING", {"multiline": True}),
                "current_frame": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "mode": (["randomize", "increment"],),
                "base_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "generate_seed"
    CATEGORY = "utils"

    def generate_seed(self, keyframes, current_frame, mode, base_seed):
        # Parse keyframes
        frame_seed_pairs = re.findall(r'(\d+):(\d+)', keyframes)
        frame_seed_pairs = [(int(frame), int(seed)) for frame, seed in frame_seed_pairs]
        frame_seed_pairs.sort(key=lambda x: x[0])

        # Find the appropriate seed based on current frame
        current_seed = base_seed
        for frame, seed in frame_seed_pairs:
            if current_frame >= frame:
                current_seed = seed
            else:
                break

        # Apply mode
        if mode == "randomize":
            random.seed(current_seed + current_frame)
            final_seed = random.randint(0, 0xffffffffffffffff)
        elif mode == "increment":
            final_seed = (current_seed + current_frame) % 0xffffffffffffffff
        else:
            final_seed = current_seed

        return (final_seed,)

NODE_CLASS_MAPPINGS = {
    "AnimatedSeed": AnimatedSeed
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AnimatedSeed": "Animated Seed"
}
