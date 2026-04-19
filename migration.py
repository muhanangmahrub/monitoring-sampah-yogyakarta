import glob
import shutil
import os

def check_extension():
    extensions = set()
    for fname in glob.glob("clean-dirty-garbage-containers/**", recursive=True):
        ext = os.path.splitext(fname)[1]
        extensions.add(ext)
    print("extensions found: %s" % extensions)

def main():
    src_dir = ["clean-dirty-garbage-containers/train", "clean-dirty-garbage-containers/test"]
    for src in src_dir:
        list_dir = os.listdir(src)
        if "train" in src:
            dst = "dataset/images/train"
        elif "test" in src:
            dst = "dataset/images/val"
        os.makedirs(dst, exist_ok=True)

        for dir in list_dir:
            src_path = os.path.join(src, dir)
            for fname in os.listdir(src_path):
                src_file = os.path.join(src_path, fname)
                dst_file = os.path.join(dst, fname)
                shutil.copy(src_file, dst_file)
                print("copied %s to %s" % (src_file, dst_file))


if __name__ == "__main__":
    check_extension()
    main()