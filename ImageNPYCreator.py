import numpy as np
from PIL import Image
import glob

image_paths = glob.glob("C:\\Users\\iniga\\Datasets\\Custom\\Stego\\*.png")
for i, path in enumerate(image_paths):
    print(f"{int(i * 10000 / len(image_paths))/100}%")
    img = Image.open(path).convert("L")  # grayscale
    arr = np.array(img, dtype=np.uint8)
    arr = arr & 1
    nameSplit = path.lstrip(r"C:\Users\iniga\Datasets\Custom\NPY/Stego").rstrip(".png")
    #print(nameSplit)
    name = f"{nameSplit}_0"
    np.save(f"C:\\Users\\iniga\\Datasets\\Custom\\NPY\\Stego\\{name}.npy", arr)