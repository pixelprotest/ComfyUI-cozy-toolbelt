import os
import subprocess
import tempfile
import requests
from PIL import Image
import torch
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Telegram bot token and chat ID from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class CombineAndSendToTelegram:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "fps": ("INT", {"default": 10, "min": 1, "max": 60}),
            },
            "optional": {
                "bot_token": ("STRING", {"default": ""}),
                "chat_id": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    FUNCTION = "process_and_send"
    CATEGORY = "image/postprocessing"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(s, images, fps, bot_token, chat_id):
        return float("NaN")  # Always process

    def process_and_send(self, images, fps, bot_token="", chat_id=""):
        print("HELLO processing and sending now")
        ## if bot_token or chat_id is not set, 
        ## use the default values from the .env file
        if bot_token == "":
            bot_token = TELEGRAM_BOT_TOKEN
        if chat_id == "":
            chat_id = TELEGRAM_CHAT_ID

        # Convert tensor images to PIL images and save as temporary files
        temp_dir = tempfile.mkdtemp()
        image_files = []
        for i, img_tensor in enumerate(images):
            img_np = img_tensor.cpu().numpy()
            img_pil = Image.fromarray((img_np * 255).astype(np.uint8))
            file_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            img_pil.save(file_path)
            image_files.append(file_path)

        print(f"bot_token: {bot_token}")
        print(f"chat_id: {chat_id}")

        # Combine images into a video using ffmpeg
        output_file = os.path.join(temp_dir, "output.mp4")
        ffmpeg_cmd = [
            "ffmpeg",
            "-framerate", str(fps),
            "-i", os.path.join(temp_dir, "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_file
        ]
        subprocess.run(ffmpeg_cmd, check=True)

        # Send video to Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
        with open(output_file, "rb") as video_file:
            files = {"video": video_file}
            data = {"chat_id": chat_id}
            response = requests.post(url, files=files, data=data)

        # Clean up temporary files
        for file in image_files:
            os.remove(file)

        if response.status_code == 200:
            print("Video sent successfully to Telegram!")
        else:
            print(f"Failed to send video. Status code: {response.status_code}")
            print(f"Response: {response.text}")

        return (output_file,)

    @classmethod
    def IS_CHANGED(s, images, fps, bot_token, chat_id):
        return float("NaN")

    @classmethod
    def VALIDATE_INPUTS(s, images, fps, bot_token="", chat_id=""):
        if not isinstance(images, torch.Tensor):
            return "Invalid image input"
        if not isinstance(fps, int) or fps < 1 or fps > 60:
            return "FPS must be an integer between 1 and 60"
        if bot_token and not isinstance(bot_token, str):
            return "Bot token must be a string"
        if chat_id and not isinstance(chat_id, str):
            return "Chat ID must be a string"
        return True
NODE_CLASS_MAPPINGS = {
    "CombineAndSendToTelegram": CombineAndSendToTelegram
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CombineAndSendToTelegram": "Combine and Send to Telegram"
}
