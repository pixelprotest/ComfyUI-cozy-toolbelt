import numpy as np
import torch
import torch.nn.functional as F

class CubemapToSpherical:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "cubemap_front": ("IMAGE",),
                "cubemap_back": ("IMAGE",),
                "cubemap_left": ("IMAGE",),
                "cubemap_right": ("IMAGE",),
                "cubemap_top": ("IMAGE",),
                "cubemap_bottom": ("IMAGE",),
                "output_width": ("INT", {"default": 1024, "min": 64, "max": 8192}),
                "output_height": ("INT", {"default": 512, "min": 32, "max": 4096}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "convert"
    CATEGORY = "image/processing"

    def convert(self, cubemap_front, cubemap_back, cubemap_left, cubemap_right, cubemap_top, cubemap_bottom, output_width, output_height):
        # Combine cubemap faces into a single tensor
        cubemap = torch.stack([
            cubemap_back[0], cubemap_bottom[0], cubemap_front[0],
            cubemap_left[0], cubemap_right[0], cubemap_top[0]
        ], dim=0)

        # Ensure the cubemap is in the format [faces, channels, height, width]
        cubemap = cubemap.permute(0, 3, 1, 2)

        # Generate spherical coordinates
        u = torch.linspace(-1, 1, output_width, device=cubemap.device)
        v = torch.linspace(-1, 1, output_height, device=cubemap.device)
        v, u = torch.meshgrid(v, u, indexing='ij')

        # Convert to spherical angles
        theta = u * np.pi
        phi = v * np.pi / 2

        # Convert spherical to Cartesian coordinates
        x = torch.cos(phi) * torch.cos(theta)
        y = torch.sin(phi)
        z = torch.cos(phi) * torch.sin(theta)

        # Prepare output tensor
        output = torch.zeros(output_height, output_width, 3, device=cubemap.device)

        # Find colors for each pixel
        abs_x, abs_y, abs_z = torch.abs(x), torch.abs(y), torch.abs(z)
        
        # Face selection logic
        is_x_face = (abs_x >= abs_y) & (abs_x >= abs_z)
        is_y_face = (abs_y > abs_x) & (abs_y >= abs_z)
        is_z_face = (abs_z > abs_x) & (abs_z > abs_y)

        # X faces (left and right)
        self.sample_face(output, cubemap, x, y, z, is_x_face & (x < 0), 3, flip_z=True)  # Left
        self.sample_face(output, cubemap, x, y, z, is_x_face & (x >= 0), 4)  # Right

        # Y faces (top and bottom)
        self.sample_face(output, cubemap, x, y, z, is_y_face & (y < 0), 5, flip_z=True)  # Top
        self.sample_face(output, cubemap, x, y, z, is_y_face & (y >= 0), 1)  # Bottom

        # Z faces (front and back)
        self.sample_face(output, cubemap, x, y, z, is_z_face & (z < 0), 2)  # Front
        self.sample_face(output, cubemap, x, y, z, is_z_face & (z >= 0), 0, flip_x=True)  # Back

        # Normalize to 0-1 range
        output = (output - output.min()) / (output.max() - output.min())

        # Add batch dimension and ensure float32 dtype
        output = output.unsqueeze(0).to(torch.float32)

        return (output,)

    def sample_face(self, output, cubemap, x, y, z, mask, face_idx, flip_x=False, flip_z=False):
        w, h = cubemap.shape[2], cubemap.shape[3]
        
        if face_idx in [3, 4]:  # Left or Right face
            uu = z / torch.abs(x)
            vv = y / torch.abs(x)
        elif face_idx in [1, 5]:  # Bottom or Top face
            uu = x / torch.abs(y)
            vv = z / torch.abs(y)
        else:  # Front or Back face
            uu = x / torch.abs(z)
            vv = y / torch.abs(z)

        if flip_x:
            uu = -uu
        if flip_z:
            uu = -uu

        # Scale to image coordinates
        xx = ((uu + 1) * w / 2).long().clamp(0, w - 1)
        yy = ((vv + 1) * h / 2).long().clamp(0, h - 1)

        # Sample colors
        sampled_colors = cubemap[face_idx, :, yy[mask], xx[mask]]
        output[mask] = sampled_colors.permute(1, 0)

NODE_CLASS_MAPPINGS = {
    "CubemapToSpherical": CubemapToSpherical
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CubemapToSpherical": "Cubemap to Spherical Map"
}
