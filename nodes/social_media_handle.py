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
                "username": ("STRING", {"default": ""}),
                "platform": (["x.com", "github", "instagram"],),
                "position": (["top_left", "top_right", "bottom_left", "bottom_right"],),
                "font_size": ("INT", {"default": 24, "min": 8, "max": 72}),
                "size_mult": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 2.0}),
                "add_logo": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "burn_handle"
    CATEGORY = "image/postprocessing"
    LOGO_URLS = {
        "x.com": "https://about.x.com/content/dam/about-twitter/x/large-x-logo.png",
        "github": "https://github.githubassets.com/favicons/favicon.png",
        "instagram": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Instagram_logo.png/600px-Instagram_logo.png",
        }

    def burn_handle(self, image, username, platform, position, font_size, size_mult, add_logo):
        print(f"-- image.shape start: {image.shape}")
        img_pil = self.tensor_to_pil(image)
        ## ----------------------------------------------------------------

        img_pil = self.burn_handle_on_image(img_pil, username, platform, position, font_size, size_mult, add_logo)

        ## ----------------------------------------------------------------
        img_tensor = self.pil_to_tensor(img_pil)
        print(f"-- image.shape end: {img_tensor.shape}")

        return (img_tensor,)

    def burn_handle_on_image(self, img_pil, username, platform, position, font_size, size_mult, add_logo):
        logo = self.download_logo(platform, add_logo)

        ## initialize the draw object
        draw_obj = ImageDraw.Draw(img_pil)

        ## prepare the font
        font_obj = self.get_font(font_size)

        ## get the height and width of the final text
        text_height, text_width = self.prepare_text(draw_obj, username, font_obj)

        ## resize the logo to match the text height
        logo = self.resize_logo_to_match_text(logo, text_height, size_mult=size_mult)

        ## calculate the width of the burnin
        burnin_width = (logo.width + 5 + text_width) if logo else text_width

        ## now grab the position of the logo
        burnin_pos = self.calculate_logo_position(img_pil, position, text_height, burnin_width)

        ## paste in the logo in front of the burn in text
        text_pos = self.paste_logo(img_pil, logo, burnin_pos, text_height)

        ## draw the text
        draw_obj.text(text_pos, username, font=font_obj, fill=(255, 255, 255))

        return img_pil
        
    
    def paste_logo(self, img_pil, logo, burnin_pos, text_height):
        if not logo: ## if there is no logo, we just return the straight burnin position
            return burnin_pos

        # logo_y_offset = int((text_height - logo.height) / 2)  # Center logo vertically with text
        logo_y_offset = int(logo.height / 4)
        logo_pos = (burnin_pos[0], burnin_pos[1] + logo_y_offset)
        img_pil.paste(logo, logo_pos, logo if logo.mode == 'RGBA' else None)
        text_pos = (burnin_pos[0] + logo.width + 5, burnin_pos[1])
        return text_pos
    
    def prepare_text(self, draw_obj, username, font):
        ## now we can get the bbox, width and height of the text
        text_bbox = draw_obj.textbbox((0, 0), username, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        return text_height, text_width
    
    def get_font(self, font_size):
        font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", "DejaVuSans-Bold.ttf")
        font = ImageFont.truetype(font_path, font_size)
        return font

    def calculate_logo_position(self, image, position_name, text_height, total_width):
        """ receives a PIL image and returns the position of the logo """
        img_width, img_height = image.size
        offset = 30
        position_map = {
            "top_left": (offset, offset),
            "top_right": (img_width - total_width - offset, offset),
            "bottom_left": (offset, img_height - text_height - offset),
            "bottom_right": (img_width - total_width - offset, img_height - text_height - offset)
        }
        pos = position_map.get(position_name, (10, 10))

        return pos

    def resize_logo_to_match_text(self, logo, text_height, size_mult=1.0):
        if not logo:
            return 

        ## get the aspect ratio of the logo
        aspect_ratio = logo.width / logo.height
        new_logo_height = int(text_height * size_mult)  # Make logo slightly smaller than text
        new_logo_width = int(new_logo_height * aspect_ratio)
        logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

        return logo
    
    def download_logo(self, platform, add_logo):
        logo = None
        if not add_logo:
            return logo

        url = self.LOGO_URLS.get(platform)
        if url:
            response = requests.get(url, stream=True).raw 
            logo = Image.open(response)
        return logo

    def tensor_to_pil(self, image):
        # Convert tensor image to numpy array
        img_np = image.squeeze().cpu().numpy()
        
        # Ensure the image is in the correct format (HWC)
        if img_np.shape[2] != 3:
            img_np = np.transpose(img_np, (1, 2, 0))
        
        # Convert to PIL Image
        img_pil = Image.fromarray((img_np * 255).astype(np.uint8))

        return img_pil

    def pil_to_tensor(self, image):
        # Convert back to tensor
        img_np = np.array(image)
        img_tensor = torch.from_numpy(img_np).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
        
        # Ensure the image is in float32 format
        img_tensor = img_tensor.to(torch.float32)
        
        # Clamp values to the range [0, 1]
        img_tensor = torch.clamp(img_tensor, 0, 1)

        return img_tensor
    
NODE_CLASS_MAPPINGS = {
    "BurnSocialMediaHandle": BurnSocialMediaHandle
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BurnSocialMediaHandle": "Burn Social Media Handle"
}
