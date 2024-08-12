import os
import sys
import natsort
import shutil
import config

def cleanup(path):
    img = natsort.os_sorted(os.listdir(os.path.join(path,"images")))
    lbl = natsort.os_sorted(os.listdir(os.path.join(path,"labels")))
    print(len(img),len(lbl))

    
    for i in img:
            txt = i.replace(".jpg",".txt")
            # print(jpg)
            if txt not in lbl:
                # print(txt)
                delete = os.path.join(os.path.join(path,"images"),i)
                print(delete)
                shutil.move(delete,path)
                print(f"moved {delete}")
    print("finished tidying images and labels")


if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python cleanup.py [Dir_path]")

    path = "/home/marco/1/0003_images/"
    clean(path)

            #     print(i)
    # clean(path)