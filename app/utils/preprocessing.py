import base64
import io
import cv2
import numpy as np
from PIL import Image

def scale_down(orig_w, orig_h):
    scale_x = 640 / orig_w
    scale_y = 640 / orig_h
    scale = min(scale_x, scale_y)
    new_w, new_h = int(orig_w * scale), int(orig_h * scale)
    return scale, new_w, new_h

def add_padding(img, new_w, new_h):
    img_array = np.asarray(img)
    total_pad = 640 - new_w if new_h > new_w else 640 - new_h
    pad_before = int(total_pad / 2)
    pad_after = 640 - new_w - pad_before if new_h > new_w else 640 - new_h - pad_before
    if new_w > new_h:
        img_array = cv2.copyMakeBorder(img_array, top=pad_before, bottom=pad_after, left=0, right=0, borderType=cv2.BORDER_DEFAULT, value=(114, 114, 114))
        pad_x = [0, 0]
        pad_y = [pad_before, pad_after]
    else:
        img_array = cv2.copyMakeBorder(img_array, top=0, bottom=0, left=pad_before, right=pad_after, borderType=cv2.BORDER_DEFAULT, value=(114, 114, 114))
        pad_x = [pad_before, pad_after]
        pad_y = [0, 0]
    return img_array, pad_x, pad_y

def preprocess(frame):
    raw_bytes = base64.b64decode(frame)
    stream_str = io.BytesIO(raw_bytes)
    img = Image.open(stream_str).convert("RGB")
    orig_w, orig_h = img.size
    scale, new_w, new_h = scale_down(orig_w=orig_w, orig_h=orig_h)
    img = img.resize(size=(new_w, new_h)) 
    img_array, pad_x, pad_y = add_padding(img, new_w=new_w, new_h=new_h)
    img_array = (img_array / 255.0).astype("float32")
    img_batch = np.transpose(img_array, (2, 0, 1))
    img_batch = np.expand_dims(img_batch, axis=0)
    return {
        "batch": img_batch,
        "metadata": {
            "orig_h": orig_h,
            "orig_w": orig_w,
            "scale": scale,
            "pad_x": pad_x,
            "pad_y": pad_y
        }
    }

