import numpy as np
import torch

class CubemapToSphericalV2:
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
                "edge_width": ("FLOAT", {"default": 5.0, "min": 0.1, "max": 20.0, "step": 0.1}),
                "mask_blur": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 100.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "convert"
    CATEGORY = "image/processing"

    def convert(self, cubemap_front, cubemap_back, cubemap_left, cubemap_right, cubemap_top, cubemap_bottom, output_width, output_height, edge_width, mask_blur):
        # Convert edge_width from percentage to decimal
        edge_width = edge_width / 100.0

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

        # Prepare output tensor and edge mask
        output = torch.zeros(output_height, output_width, 3, device=cubemap.device)
        edge_mask = torch.zeros(output_height, output_width, dtype=torch.float32, device=cubemap.device)

        # Find colors for each pixel
        abs_x, abs_y, abs_z = torch.abs(x), torch.abs(y), torch.abs(z)

        # Face selection logic
        is_x_face = (abs_x >= abs_y) & (abs_x >= abs_z)
        is_y_face = (abs_y > abs_x) & (abs_y >= abs_z)
        is_z_face = (abs_z > abs_x) & (abs_z > abs_y)

        # X faces (left and right)
        self.sample_face(output, edge_mask, cubemap, x, y, z, is_x_face & (x < 0), 3, edge_width, flip_x=True)  # Left
        self.sample_face(output, edge_mask, cubemap, x, y, z, is_x_face & (x >= 0), 4, edge_width)  # Right

        # Y faces (top and bottom)
        self.sample_face(output, edge_mask, cubemap, x, y, z, is_y_face & (y < 0), 5, edge_width, flip_y=True)  # Top
        self.sample_face(output, edge_mask, cubemap, x, y, z, is_y_face & (y >= 0), 1, edge_width)  # Bottom

        # Z faces (front and back)
        self.sample_face(output, edge_mask, cubemap, x, y, z, is_z_face & (z < 0), 2, edge_width)  # Front
        self.sample_face(output, edge_mask, cubemap, x, y, z, is_z_face & (z >= 0), 0, edge_width, flip_x=True)  # Back

        # Normalize to 0-1 range
        output = (output - output.min()) / (output.max() - output.min())

        # Apply Gaussian blur to the edge mask
        kernel_size = max(3, int(mask_blur * 4)) | 1  # Ensure odd kernel size
        blurred_edge_mask = self.custom_gaussian_blur(edge_mask, kernel_size=kernel_size, sigma=mask_blur)

        # Combine sharp and blurred masks
        combined_mask = torch.maximum(edge_mask, blurred_edge_mask)

        # Add batch dimension and ensure float32 dtype
        output = output.unsqueeze(0).to(torch.float32)
        mask_output = combined_mask.unsqueeze(0).unsqueeze(0).to(torch.float32)

        return (output, mask_output)

    def sample_face(self, output, edge_mask, cubemap, x, y, z, mask, face_idx, edge_width, flip_x=False, flip_y=False):
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
        if flip_y:
            vv = -vv

        # Scale to image coordinates
        xx = ((uu + 1) * w / 2)
        yy = ((vv + 1) * h / 2)

        # Detect edges
        is_edge = (xx < edge_width * w) | (xx > w - edge_width * w) | (yy < edge_width * h) | (yy > h - edge_width * h)
        edge_mask[mask] = torch.maximum(edge_mask[mask], is_edge[mask].float())

        # Clamp coordinates for sampling
        xx = xx.long().clamp(0, w - 1)
        yy = yy.long().clamp(0, h - 1)

        # Sample colors
        sampled_colors = cubemap[face_idx, :, yy[mask], xx[mask]]
        output[mask] = sampled_colors.permute(1, 0)

    def custom_gaussian_blur(self, img, kernel_size, sigma):
        # Generate Gaussian kernel
        x = torch.arange(-(kernel_size // 2), kernel_size // 2 + 1, dtype=torch.float32, device=img.device)
        kernel = torch.exp(-x**2 / (2 * sigma**2))
        kernel = kernel / kernel.sum()

        # Reshape kernel for 2D convolution
        kernel_x = kernel.view(1, 1, kernel_size, 1)
        kernel_y = kernel.view(1, 1, 1, kernel_size)

        # Pad the image
        pad_size = kernel_size // 2
        padded_img = torch.nn.functional.pad(img.unsqueeze(0).unsqueeze(0), (pad_size, pad_size, pad_size, pad_size), mode='reflect')

        # Apply separable Gaussian blur
        blurred = torch.nn.functional.conv2d(padded_img, kernel_x, padding=0)
        blurred = torch.nn.functional.conv2d(blurred, kernel_y, padding=0)

        return blurred.squeeze(0).squeeze(0)

NODE_CLASS_MAPPINGS = {
    "CubemapToSphericalV2": CubemapToSphericalV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CubemapToSphericalV2": "Cubemap to Spherical V2 (with Mask)"
}
