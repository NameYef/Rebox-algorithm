import os 
import cv2
import json
import numpy as np
import random
import sys
import config
import natsort
import random

# from cleanup import clean






# class_color = {'window' : (250, 180, 100),
#                "air_con": (255,215,0),
#                "people": (0, 0, 255),
#                "spalling": (0, 255, 0),
#                "nail": (0, 76, 153),
#                "stain": (240,128,128),
#                "peeling_paint":(100,149,237),
#                "crack":(199,21,133),
#                "rust":(245,222,179),
#                "stain_pipe":(176,196,222),
#                "missing_tiles":(25,25,112),
#                "bulging":(128,128,0)}

margin = 0
# label = ["window","air_con","people","spalling","nail","stain","peeling_paint","crack","rust","stain_pipe","missing_tiles","bulging"]

def plot_and_save(boxed_path, image1_path, label1_path, class_color, label, color_list):
    im = cv2.imread(image1_path)
    with open(label1_path,"r") as f:
        for j in f :
            tmp = j.strip().split(" ")
            # print(tmp)
            try:
                if label:
                    class_name = label[int(tmp[0])]
                else:
                    if tmp[0] not in class_color:
                        while True:
                            random_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                            if random_color not in color_list:
                                color_list.append(random_color)
                                break
                        class_color[tmp[0]] = random_color
                    class_name = tmp[0]
                # print(class_name)
                mid_x = int(float(tmp[1]) * config.resolution_x)
                mid_y = int(float(tmp[2]) * config.resolution_y)

                w = int(float(tmp[3]) * config.resolution_x)
                h = int(float(tmp[4]) * config.resolution_y)

                # pt1 = (mid_x-box_w/2, mid_y-box_h/2)
                # pt1 = (mid_x+box_w/2, mid_y+box_h/2)
                xyxy = int(mid_x - w/2) - margin, int(mid_y - h/2) - margin, int(mid_x + w/2) + margin, int(mid_y + h/2) + margin
                label_text = f'{class_name}'
                plot_one_box(xyxy, im, label=label_text, color=class_color[class_name], line_thickness=1)
            except (IndexError, ValueError):
                break

    file_to_be_saved = os.path.join(boxed_path, image1_path.split("/")[-1])
    cv2.imwrite(file_to_be_saved, im)
    print(f"saving photo {file_to_be_saved}")

    return (class_color, color_list)


def plot_one_box(x, img, color=None, label=None, line_thickness=10):

    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

def plot_label(label_folder):
    class_color = {}
    color_list = []
    label = []
    have_classes = False

    if "classes.txt" in os.listdir(label_folder):
        have_classes = True
        with open(os.path.join(label_folder, "classes.txt"),"r") as f:
            label = [i.replace("\n","") for i in f.readlines()]
            
            for i in label:
                while True:
                    random_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                    if random_color not in color_list:
                        color_list.append(random_color)
                        break
                class_color[i] = random_color

        print(class_color)

    source_dir = label_folder # current dir = cwd
    dir_created = False
    # counter = 0
    # clean(source_dir)
    file_list = natsort.os_sorted(os.listdir(source_dir))
    # for i in file_list:
    #     print(i)
    valid = True
    for i in file_list:
        valid = True
        if i.endswith("classes.txt"): # skip if classes.txt
            print("skipped classes.txt")
            continue
        else:
            img_folder = os.path.join(config.project_folder,"images")
            if i.split(".")[-1] == "txt" :# and  int(i.split("_")[-2]) in target_list:
                label_list = []
                file_name = i.split(".")[0] + ".jpg"
                # print(os.path.join(config.img_folder,file_name))
                im = cv2.imread(os.path.join(img_folder,file_name))
                if im is None:
                    continue
                with open(os.path.join(label_folder,i)) as f:
                    for j in f :
                        tmp = j.strip().split(" ")
                        # print(tmp)
                        try:
                            if have_classes:
                                class_name = label[int(tmp[0])]
                            else:
                                if tmp[0] not in class_color:
                                    while True:
                                        random_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                                        if random_color not in color_list:
                                            color_list.append(random_color)
                                            break
                                    class_color[tmp[0]] = random_color
                                class_name = tmp[0]
                            # print(class_name)
                            mid_x = int(float(tmp[1]) * config.resolution_x)
                            mid_y = int(float(tmp[2]) * config.resolution_y)

                            w = int(float(tmp[3]) * config.resolution_x)
                            h = int(float(tmp[4]) * config.resolution_y)

                            # pt1 = (mid_x-box_w/2, mid_y-box_h/2)
                            # pt1 = (mid_x+box_w/2, mid_y+box_h/2)
                            xyxy = int(mid_x - w/2) - margin, int(mid_y - h/2) - margin, int(mid_x + w/2) + margin, int(mid_y + h/2) + margin
                            label_text = f'{class_name}'
                            plot_one_box(xyxy, im, label=label_text, color=class_color[class_name], line_thickness=1)
                        except (IndexError, ValueError):
                            valid = False
                            break

                    if valid:
                        counter = 1
                        while not dir_created:
                            save_path = os.path.join(config.pl_save_dir,f"{config.project_folder.split('/')[-1]}_{counter}")
                            if not os.path.exists(save_path):
                                try:
                                    print(f"boxed images will be saved at {save_path}")
                                    os.mkdir(save_path)
                                    dir_created = True
                                    break
                                except OSError as e:
                                    print("something went wrong")
                                    break
                            counter += 1
                        file_to_be_saved = os.path.join(save_path, file_name)
                        cv2.imwrite(file_to_be_saved, im)
                        print(f"saving photo {file_to_be_saved}")
    return save_path

if __name__ == "__main__":
    plot_label("/home/rebox/relabelled/0003_images_2")