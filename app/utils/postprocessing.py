import numpy as np

def nms_numpy(box_xyxy, scores, iou_threshold=0.5):
    x1 = box_xyxy[:, 0]
    y1 = box_xyxy[:, 1]
    x2 = box_xyxy[:, 2]
    y2 = box_xyxy[:, 3]
    
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h

        iou = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]
    return keep

def remove_padding(box, pad_x, pad_y):
    x1 = box[:, 0] - pad_x[0]
    y1 = box[:, 1] - pad_y[0]
    x2 = box[:, 2] - pad_x[0]
    y2 = box[:, 3] - pad_y[0]
    return np.stack((x1, y1, x2, y2), axis=1)

def scale_up(scale, box):
    x1 = box[:, 0] / scale
    y1 = box[:, 1] / scale
    x2 = box[:, 2] / scale
    y2 = box[:, 3] / scale
    return np.stack((x1, y1, x2, y2), axis=1)

def postprocess(arr, metadata):
    arr = arr.squeeze()
    arr = arr.transpose()
    
    scores = arr[:, 4:]
    max_scores = scores.max(axis=1)

    keep = max_scores > 0.25
    boxes = arr[keep]
    scores = max_scores[keep]
    
    x1, y1 = boxes[:, 0] - (boxes[:, 2]/2), boxes[:, 1] - (boxes[:, 3]/2)
    x2, y2 = boxes[:, 0] + (boxes[:, 2]/2), boxes[:, 1] + (boxes[:, 3]/2)
    box_xyxy = np.stack((x1, y1, x2, y2), axis=1)

    result = nms_numpy(box_xyxy, scores, iou_threshold=0.5)
    box_xyxy_kept = np.stack([x1[result], y1[result], x2[result], y2[result]], axis=1)
    score, cls = scores[result], boxes[result, 4:].argmax(axis=1)

    box_xyxy = remove_padding(box_xyxy_kept, metadata["pad_x"], metadata["pad_y"])
    box_xyxy = scale_up(metadata["scale"], box_xyxy)

    return score, box_xyxy, cls