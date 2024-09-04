import os
import requests
from PIL import Image, ImageDraw, ImageFont
import torch
import numpy as np

class BurnSocialMediaHandle:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "handle": ("STRING", {"default": ""}),
                "platform": (["x.com", "github", "instagram"],),
                "position": (["top_left", "top_right", "bottom_left", "bottom_right"],),
                "font_size": ("INT", {"default": 24, "min": 8, "max": 72}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "burn_handle"
    CATEGORY = "image/postprocessing"

    def burn_handle(self, image, handle, platform, position, font_size):
        # Convert tensor image to PIL Image
        img_np = image.squeeze().permute(1, 2, 0).cpu().numpy()
        img_pil = Image.fromarray((img_np * 255).astype(np.uint8))

        # Load platform logo
        logo_path = os.path.join(os.path.dirname(__file__), f"{platform.replace('.', '_')}_logo.png")
        if not os.path.exists(logo_path):
            # Download logo if not exists
            url = f"https://raw.githubusercontent.com/pixelprotest/ComfyUI-cozy-toolbelt/main/assets/{platform.replace('.', '_')}_logo.png"
            response = requests.get(url)
            if response.status_code == 200:
                with open(logo_path, 'wb') as f:
                    f.write(response.content)
            else:
                raise Exception(f"Failed to download logo for {platform}")

        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((font_size, font_size), Image.LANCZOS)

        # Prepare text
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        text = f"/{handle}"
        text_width, text_height = font.getsize(text)

        # Create a new image for handle
        handle_img = Image.new('RGBA', (logo.width + text_width + 10, max(logo.height, text_height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(handle_img)

        # Paste logo and draw text
        handle_img.paste(logo, (0, (handle_img.height - logo.height) // 2), logo)
        draw.text((logo.width + 5, (handle_img.height - text_height) // 2), text, font=font, fill=(255, 255, 255, 255))

        # Calculate position
        if position == "top_left":
            pos = (10, 10)
        elif position == "top_right":
            pos = (img_pil.width - handle_img.width - 10, 10)
        elif position == "bottom_left":
            pos = (10, img_pil.height - handle_img.height - 10)
        else:  # bottom_right
            pos = (img_pil.width - handle_img.width - 10, img_pil.height - handle_img.height - 10)

        # Paste handle image onto original image
        img_pil.paste(handle_img, pos, handle_img)

        # Convert back to tensor
        img_tensor = torch.from_numpy(np.array(img_pil).astype(np.float32) / 255.0).unsqueeze(0).permute(0, 3, 1, 2)

        return (img_tensor,)

NODE_CLASS_MAPPINGS = {
    "BurnSocialMediaHandle": BurnSocialMediaHandle
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BurnSocialMediaHandle": "Burn Social Media Handle"
}
