import numpy as np
from PIL import Image
import glob
import os

image_paths = glob.glob("C:\\Users\\iniga\\Datasets\\Custom\\BPCS Stego\\*.png")
for i, path in enumerate(image_paths):
    img = Image.open(path).convert("L")  # grayscale
    arr = np.array(img, dtype=np.uint8)
    arr = arr / 255.0
    nameSplit = os.path.splitext(os.path.basename(path))[0]
    print(f"{int(i * 10000 / len(image_paths))/100}%, {nameSplit}")
    nameSplitTwo = nameSplit.split("_")
    name = f"{nameSplitTwo[0]}_{int(nameSplitTwo[1]) + 1}"
    np.save(f"C:\\Users\\iniga\\Datasets\\Custom\\NPY\\BPCS Stego\\{name}.npy", arr)