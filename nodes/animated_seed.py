import re
import random

class AnimatedSeed:
    def __init__(self):
        self.stored_seed = None

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
    OUTPUT_NODE = True

    def get_new_seed(self, mode, current_seed):
        if mode == "randomize":
            new_seed = random.randint(0, 0xffffffffffffffff)
        elif mode == "increment":
            new_seed = current_seed + 1
        else:
            new_seed = current_seed
        return new_seed

    def generate_seed(self, keyframes, current_frame, mode, base_seed):
        frame_numbers = [int(frame.strip()) for frame in keyframes.split(',')]

        if self.stored_seed is None:
            self.stored_seed = base_seed

        if current_frame in frame_numbers:
            new_seed = self.get_new_seed(mode, self.stored_seed)
            self.stored_seed = new_seed
            return (new_seed,)

        return (self.stored_seed,)
NODE_CLASS_MAPPINGS = {
    "AnimatedSeed": AnimatedSeed
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AnimatedSeed": "Animated Seed"
}
