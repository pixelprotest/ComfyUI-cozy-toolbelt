import numpy as np
import torch

class SphericalToCubemapV2:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "spherical_image": ("IMAGE",),
                "output_size": ("INT", {"default": 1024, "min": 64, "max": 8192}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("front", "back", "left", "right", "top", "bottom")
    FUNCTION = "convert"
    CATEGORY = "image/processing"

    def convert(self, spherical_image, output_size):
        # Ensure the spherical image is in the format [batch, channels, height, width]
        spherical = spherical_image.permute(0, 3, 1, 2)

        # Generate cubemap coordinates
        x, y = torch.meshgrid(torch.linspace(-1, 1, output_size, device=spherical.device),
                              torch.linspace(-1, 1, output_size, device=spherical.device),
                              indexing='ij')

        # Create cubemap faces
        cubemap_faces = []
        for i, (x_face, y_face, z_face) in enumerate([
            (-y, -torch.ones_like(x), -x),  # Front
            (-y, torch.ones_like(x), x),    # Back
            (-torch.ones_like(x), -y, -x),  # Left
            (torch.ones_like(x), y, -x),  # Right
            (y, -x, torch.ones_like(x)),  # Top
            (y, x, -torch.ones_like(x)),  # Bottom 
        ]):
            # Convert to spherical coordinates
            r = torch.sqrt(x_face**2 + y_face**2 + z_face**2)
            theta = torch.atan2(y_face, x_face)
            phi = torch.acos(z_face / r)

            # Map to spherical image coordinates
            u = (theta + np.pi) / (2 * np.pi)
            v = phi / np.pi

            # Sample from spherical image
            u = (u * spherical.shape[3]).long().clamp(0, spherical.shape[3] - 1)
            v = (v * spherical.shape[2]).long().clamp(0, spherical.shape[2] - 1)

            face = spherical[:, :, v, u]
            cubemap_faces.append(face)

        # Convert to the desired output format [batch, height, width, channels]
        cubemap_faces = [face.permute(0, 2, 3, 1) for face in cubemap_faces]

        # Flip the Front face horizontally
        cubemap_faces[0] = torch.flip(cubemap_faces[0], dims=[2])
        
        # Rotate the Back face 180 degrees counter-clockwise and flip horizontally
        cubemap_faces[1] = torch.rot90(cubemap_faces[1], k=2, dims=[1, 2])
        cubemap_faces[1] = torch.flip(cubemap_faces[1], dims=[2])

        return tuple(cubemap_faces)

NODE_CLASS_MAPPINGS = {
    "SphericalToCubemapV2": SphericalToCubemapV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SphericalToCubemapV2": "Spherical to Cubemap V2"
}
