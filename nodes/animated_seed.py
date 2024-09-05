import re
import random

class AnimatedSeed:
    OUTPUT_SEED = None

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

    @classmethod
    def get_new_seed(cls, mode, current_seed):
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
            AnimatedSeed.OUTPUT_SEED = base_seed

        if current_frame in frame_numbers:
            new_seed = self.get_new_seed(mode, AnimatedSeed.OUTPUT_SEED)
            AnimatedSeed.OUTPUT_SEED = new_seed
            return (new_seed,)

        return (AnimatedSeed.OUTPUT_SEED, )

    @classmethod
    def IS_CHANGED(cls, keyframes, current_frame, mode, base_seed):
        return float("nan")


NODE_CLASS_MAPPINGS = {
    "AnimatedSeed": AnimatedSeed
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AnimatedSeed": "Animated Seed"
}
