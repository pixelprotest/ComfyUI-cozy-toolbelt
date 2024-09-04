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
    _seed = 0

    def get_new_seed(self, mode):
        if mode=="randomize":
            new_seed = random.randint(0, 0xffffffffffffffff)
            self._seed = new_seed
        elif mode=="increment":
            new_seed = self._seed + 1
            self._seed = new_seed
        
        return self._seed

    def generate_seed(self, keyframes, current_frame, mode, base_seed):
        frame_numbers = [int(frame.strip()) for frame in keyframes.split(',')]

        if current_frame in frame_numbers:
            new_seed = self.get_new_seed(mode)
            return (new_seed, )

        return (self._seed, )


NODE_CLASS_MAPPINGS = {
    "AnimatedSeed": AnimatedSeed
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AnimatedSeed": "Animated Seed"
}
