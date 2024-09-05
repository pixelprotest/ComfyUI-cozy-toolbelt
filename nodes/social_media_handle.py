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
    LOGO_URLS = {
        "x.com": "https://about.x.com/content/dam/about-twitter/x/large-x-logo.png",
        "github": "https://github.githubassets.com/favicons/favicon.png",
        "instagram": "https://www.instagram.com/static/images/ico/favicon.ico/36b3ee2d91ed.ico",
        }

    def burn_handle(self, image, handle, platform, position, font_size):
        print(f"-- image.shape start: {image.shape}")
        # Convert tensor image to numpy array
        img_np = image.squeeze().cpu().numpy()
        
        # Ensure the image is in the correct format (HWC)
        if img_np.shape[2] != 3:
            img_np = np.transpose(img_np, (1, 2, 0))
        
        # Convert to PIL Image
        img_pil = Image.fromarray((img_np * 255).astype(np.uint8))

        # Download and prepare logo
        logo_url = self.LOGO_URLS.get(platform)
        if logo_url:
            response = requests.get(logo_url)
            logo = Image.open(requests.get(logo_url, stream=True).raw)
        else:
            logo = None

        # Prepare text
        font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", "DejaVuSans-Bold.ttf")
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(img_pil)
        text_bbox = draw.textbbox((0, 0), handle, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Resize logo to match text height
        if logo:
            aspect_ratio = logo.width / logo.height
            new_logo_height = int(text_height * 0.5)  # Make logo slightly smaller than text
            new_logo_width = int(new_logo_height * aspect_ratio)
            logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

        # Calculate total width (logo + text)
        total_width = (logo.width + 5 + text_width) if logo else text_width

        # Calculate position
        img_width, img_height = img_pil.size
        position_map = {
            "top_left": (10, 10),
            "top_right": (img_width - total_width - 10, 10),
            "bottom_left": (10, img_height - text_height - 10),
            "bottom_right": (img_width - total_width - 10, img_height - text_height - 10)
        }
        pos = position_map.get(position, (10, 10))

        # Paste logo if available
        if logo:
            logo_y_offset = int((text_height - logo.height) / 2)  # Center logo vertically with text
            logo_pos = (pos[0], pos[1] + logo_y_offset)
            img_pil.paste(logo, logo_pos, logo if logo.mode == 'RGBA' else None)
            text_pos = (pos[0] + logo.width + 5, pos[1])
        else:
            text_pos = pos

        # Draw text on image
        draw.text(text_pos, handle, font=font, fill=(255, 255, 255))

        # Convert back to tensor
        img_np = np.array(img_pil)
        img_tensor = torch.from_numpy(img_np).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
        
        # Ensure the image is in float32 format
        img_tensor = img_tensor.to(torch.float32)
        
        # Clamp values to the range [0, 1]
        img_tensor = torch.clamp(img_tensor, 0, 1)
        print(f"-- image.shape end: {img_tensor.shape}")

        return (img_tensor,)

NODE_CLASS_MAPPINGS = {
    "BurnSocialMediaHandle": BurnSocialMediaHandle
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BurnSocialMediaHandle": "Burn Social Media Handle"
}
