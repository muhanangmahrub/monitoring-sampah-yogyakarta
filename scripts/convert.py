from xml.dom import minidom
import os
import glob

lut = {}
lut["clean"] = 0
lut["dirty"] = 1
path_in = "clean-dirty-garbage-containers/annotations"
path_out = "dataset/labels"

def convert_coordinates(size, box):
    dw = 1.0/size[0]
    dh = 1.0/size[1]
    x = (box[0]+box[1])/2.0
    y = (box[2]+box[3])/2.0
    w = box[1]-box[0]
    h = box[3]-box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


def convert_xml2yolo(lut):
    for fname in glob.glob(f"{path_in}/**/*.xml", recursive=True):
        xmldoc = minidom.parse(fname)
        if "train" in fname:
            path_out_train = os.path.join(path_out, "train")
            os.makedirs(path_out_train, exist_ok=True)
            fname_out = os.path.join(path_out_train, os.path.basename(fname[:-4]+".txt"))
        elif "test" in fname:
            path_out_val = os.path.join(path_out, "val")
            os.makedirs(path_out_val, exist_ok=True)
            fname_out = os.path.join(path_out_val, os.path.basename(fname[:-4]+".txt"))

        with open(fname_out, "w") as f:
            itemlist = xmldoc.getElementsByTagName("object")
            size = xmldoc.getElementsByTagName("size")[0]
            width = int((size.getElementsByTagName("width")[0]).firstChild.data)
            height = int((size.getElementsByTagName("height")[0]).firstChild.data)
            classid = (xmldoc.getElementsByTagName("folder")[0]).firstChild.data
            if classid in lut:
                label_str = str(lut[classid])
            else:
                label_str = "-1"
                print("warning: label '%s' not in look-up table" % classid)

            for item in itemlist:
                xmin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmin')[0]).firstChild.data
                ymin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymin')[0]).firstChild.data
                xmax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmax')[0]).firstChild.data
                ymax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymax')[0]).firstChild.data
                b = (float(xmin), float(xmax), float(ymin), float(ymax))
                bb = convert_coordinates((width, height), b)

                f.write(label_str + " " + " ".join([("%.6f" % a) for a in bb]) + "\n")

        print("wrote %s" % fname_out)

def main():
    convert_xml2yolo(lut)

if __name__ == "__main__":
    main()