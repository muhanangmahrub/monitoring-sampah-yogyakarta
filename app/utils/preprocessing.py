import base64
import io
import numpy as np
from PIL import Image

def preprocess(frame):
    raw_bytes = base64.b64decode(frame)
    stream_str = io.BytesIO(raw_bytes)
    decoded_image = Image.open(stream_str).convert("RGB")
    resized_image = decoded_image.resize((640, 640))
    img_array = np.asarray(resized_image)
    normalized_img = (img_array / 255.0).astype("float32")
    batched = np.transpose(normalized_img, (2, 0, 1))
    batched = np.expand_dims(batched, axis=0)
    return batched

