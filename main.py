import multiprocessing
from concurrent import futures
import cv2
import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as plt
import config
import natsort
import functools
import random
from plot_labels import plot_label, plot_and_save
from image_to_video import to_video
from tidy_imglbl import cleanup


# for parsing single file
def parse_detection(file):  # -> [[class, centerx, centery, width, height],...]
    detections = []
    with open(file, "r") as f:
        for line in f:
            line = line.replace("\n", "") # there is a \n char in the end of each line
            info_list = line.split(" ")
            detections.append(info_list)
    return detections


def extract_feature(image, nfeature, box, bg = False):
    global resolution_x
    global resolution_y
    class_type, centerx, centery, width, height = box
    # get top_left coords
    height = round(float(height) * resolution_y)
    width = round(float(width) * resolution_x)
    # print(round(float(centerx)*resolution_x))
    top_left_x = round(float(centerx)*resolution_x) - width // 2
    top_left_y = round(float(centery)*resolution_y) - height // 2
    
    if not bg: # for objects in the 1st photo
        # print(top_left_x,top_left_y,width,height)
        # I want to expand range of coords a little to increase matching, but if the object is in corner, the coords may be lower than 0 or higher than resolution which causes error
        if top_left_y-1 >= 0 and top_left_y+height+5 <= resolution_y and top_left_x-1 >= 0 and top_left_x+width+5 <= resolution_x:
            roi = image[top_left_y-1:top_left_y+height+5,top_left_x-1:top_left_x+width+5] # the constants added or deducted are for testing purposes
        else:
            roi = image[top_left_y:top_left_y+height,top_left_x:top_left_x+width]
    else: # for the 2nd photo
        top_left_x = top_left_x - config.x_offset_for_detection if ((top_left_x - config.x_offset_for_detection) >= 0) else 0
        top_left_y = top_left_y - config.y_offset_for_detection if ((top_left_y - config.y_offset_for_detection) >= 0) else 0
        width = width + config.width_offset if top_left_x+width+config.width_offset <= resolution_x else resolution_x-top_left_x
        height = height + config.height_offset if top_left_y+height+config.height_offset <= resolution_y else resolution_y-top_left_y
        # print(top_left_x, top_left_y, width, height)
        roi = image[top_left_y:top_left_y+height,top_left_x:top_left_x+width]
        class_type = None
    # feature extraction
    # print(top_left_x, top_left_y, width, height)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB.create(nfeatures = nfeature, scaleFactor=1.2, nlevels=8, edgeThreshold=31, firstLevel=0, WTA_K=2, scoreType=cv2.ORB_HARRIS_SCORE, patchSize=21, fastThreshold=20)
    kp, des = orb.detectAndCompute(gray, None)
    return top_left_x,top_left_y, kp, des, class_type


def match_features(des1, des2, ratio_threshold=config.ratio_threshold, min_matches=config.min_matches): # return matching
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.knnMatch(des1, des2, k=2)  # Find the two best matches for each descriptor
    # for i,j in matches:
    #     print(i.distance, j.distance)
    good_matches = []
    for m, n in matches:
        if m.distance < ratio_threshold * n.distance:
            good_matches.append(m) # [m] when want to see the photos by plt 
    if len(good_matches) < min_matches:
        # print("Object not found in this photo")
        # sys.stdout.flush() 
        return None 
    return good_matches


def get_coords(kp2, good_matches, width, height, x, y):
        global resolution_x
        global resolution_y

        x_cord = []
        y_cord = []

        # For each match...
        for mat in good_matches:

            # Get the matching keypoints for each of the images
            # img1_idx = mat.queryIdx
            img2_idx = mat.trainIdx

            # x - columns
            # y - rows
            # Get the coordinates
            # (x1, y1) = kp[img1_idx].pt
            (x2, y2) = kp2[img2_idx].pt

            # Append to each list
            x_cord.append(x2)
            y_cord.append(y2)

        minx, maxx = min(x_cord), max(x_cord)
        miny, maxy = min(y_cord), max(y_cord)
        w = maxx - minx
        h = maxy - miny
        centerx = minx + w / 2
        centery = miny + h / 2

        # IMPLEMENT REJECT OVERSIZED COORDS --------------------
        if (w / resolution_x > config.max_size_acceptable * width) or (h /resolution_y > config.max_size_acceptable * height): # FILLER CHECK
            print("TOO BIG")
            sys.stdout.flush() 
            return None
        # print(centerx, centery, w, h)
        return ((centerx+x) / resolution_x, (centery+y) / resolution_y, w / resolution_x, h / resolution_y)


def valid_write_coords(file, class_type, coords): # check valid + write coords to txt
    global resolution_x
    global resolution_y
    with open(file, "r") as f:
        # naive check whether the coords are near or in txt already
        # print("opened file")
        bigger = False
        can_append = True
        data = f.readlines()
        for line_index in range(len(data)):
            # IMPLEMENT COORDS CHECKING -----------------
            line = data[line_index].replace("\n", "") # there is a \n char in the end of each line
            # print(line)
            obj_class, centerx, centery, width, height = line.split(" ") # [class, centerx, centery, width, height]
            # print(obj_class)
            if class_type == obj_class:
                # width and height validity checked in get_coords(), now check whether centerx and centery is in box already
                # coords = (centerx, centery, width, height)
                
                # IF CENTER IN A BOX ALREADY
                
                if ((float(centerx) - (float(width)/2)-(config.min_x_offset_same_cls/resolution_x)) <= coords[0] <= (float(centerx) + (float(width) / 2)+config.min_x_offset_same_cls/resolution_x)) and ((float(centery) - (float(height)/2)-config.min_y_offset_same_cls/resolution_y) <= coords[1] <= (float(centery) + (float(height) / 2)+config.min_y_offset_same_cls/resolution_y)):  
                    
                    if (coords[2] >= float(width)) and (coords[3] >= float(height)): # ALWAYS TAKE THE ONE WITH LARGER WIDTH AND HEIGHT TO PREVENT BOX SHRINKING
                        # print("BIGGER IS FOUND")
                        if len(centerx) >= 11 or len(centery) >= 11 or len(width) >= 11 or len(height) >= 11:
                            bigger = True
                            data[line_index] = f"{class_type} {coords[0]} {coords[1]} {coords[2]} {coords[3]}\n"
                            print(data[line_index])
                            sys.stdout.flush() 
                        else:
                            can_append = False
                    else:
                        print(f"boxed already, photo {file}")
                        sys.stdout.flush() 
                        return 

    if bigger:
        with open(file, "w") as f:
            f.writelines(data)
            print(f"bigger is found and is not original label, photo {file}")
            sys.stdout.flush() 
    else:
        if can_append:
            data.append(f"{class_type} {coords[0]} {coords[1]} {coords[2]} {coords[3]}\n")
            with open(file, "w") as f:
                f.writelines(data)
                print(f"appending class {class_type} to {file}")
                sys.stdout.flush() 


def match_and_store(obj, first, second, label_path):
   
    width = float(obj[3])
    height = float(obj[4])
    # print(width, height)
    x1,y1, kp, des, class_type= extract_feature(first,config.nfeature_obj,obj)
    x2,y2, kp2, des2, dummy = extract_feature(second,config.nfeature_detect_zone,obj, True)

    # print(class_type)
    good = match_features(des,des2)
    if good is not None:
        coords = get_coords(kp2, good, width, height,x2,y2)
        if coords is not None:
            valid_write_coords(label_path, class_type, coords)


def match_and_store_multiprocessing(partial_func, objects):
    with multiprocessing.Pool(3) as pool:
            pool.map(partial_func, objects)


def copy_directory_with_sequence(source_dir, base_dest_dir):

    destination_dir = os.path.join(base_dest_dir,config.name)
    if os.path.exists(destination_dir):
        shutil.rmtree(destination_dir)
        
    shutil.copytree(source_dir, destination_dir)
    print(f"Successfully copied from {source_dir} to {destination_dir}")
    sys.stdout.flush() 
            

    return destination_dir


if __name__ == "__main__":
    print("STARTING")
    sys.stdout.flush() 

    class_color = {}
    label = []
    color_list = []
    # initialize img and lbl folders
    img_folder = os.path.join(config.project_folder,"images")
    label_folder = os.path.join(config.project_folder,"labels")

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

    # move the images away from the img_folder if there is no corresponding txt in the label_folder
    cleanup(config.project_folder)

    # make a copy of the label folder and do the relabelling there
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"relabelled")
    # print(dir_path)
    dest_dir = copy_directory_with_sequence(f"{os.path.join(os.getcwd(),label_folder)}",dir_path)
    print(dest_dir)
    sys.stdout.flush() 
    images = natsort.os_sorted(os.listdir(img_folder)) # need to sort to ensure the oldest image get treated first
    print(len(images))
    sys.stdout.flush() 

    # get the resolution of the images of the project folder
    resolution_x = cv2.imread(os.path.join(img_folder,images[0])).shape[1]
    resolution_y = cv2.imread(os.path.join(img_folder,images[0])).shape[0]

    boxed_path = os.path.join("/home/rebox/boxed",config.name)
    if os.path.exists(boxed_path):
        shutil.rmtree(boxed_path)
    os.mkdir(boxed_path)
        

    # algorithm in action
    for i in range(len(images)):
        image_read = []
        # label_detect = []
        func_list = []

        image1_path = os.path.join(img_folder, images[i])
        label1_path = os.path.join(dest_dir,images[i].replace(images[i][-3:],"txt"))
        image1 = cv2.imread(image1_path)
        image1_detection = parse_detection(label1_path)

        for j in range(1,config.no_photo_match+1):
            try:
                image_read.append(images[i+j])
                image_path = os.path.join(img_folder, images[i+j])
                label_path = os.path.join(dest_dir,images[i+j].replace(images[i][-3:],"txt"))

                image = cv2.imread(image_path)
               

                partial_func = functools.partial(match_and_store,first=image1, second=cv2.imread(image_path), label_path=label_path)
                func_list.append(partial_func)
            except IndexError:
                continue

        if image_read:

            for image in image_read:
                print(image)
                sys.stdout.flush() 

            processes = []
            for func in func_list:
                p = multiprocessing.Process(target=match_and_store_multiprocessing,args=(func,image1_detection))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()
        
        # BOX 1 IMAGE
        class_color, color_list = plot_and_save(boxed_path, image1_path, label1_path, class_color, label, color_list)

        
    
    # box image
    # boxed_path = plot_label(dest_dir)

    # make video
    to_video(boxed_path, config.name, config.video_fps)

    print("ENDED")
