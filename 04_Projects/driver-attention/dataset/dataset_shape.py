from PIL import Image
import numpy as np

path = r"04_Projects\driver-attention\drivergaze360_subset\dataset\train\C001\001\001-1\saliency\000001.jpg"

with Image.open(path) as img:
    print("Image size (W, H):", img.size)
    print("Image mode:", img.mode)

    arr = np.asarray(img)
    print("Array shape:", arr.shape)
    print("Data type:", arr.dtype)
    print("Min / max:", arr.min(), arr.max())