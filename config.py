import os


with open("home/rebox/config.txt", "r") as f:
    data = [i.replace("\n","") for i in f.readlines()]
    resolution_x = int(data[0])
    resolution_y = int(data[1])
    video_fps = int(data[2])
    no_photo_match = int(data[3])
    nfeature_obj = int(data[4])
    nfeature_detect_zone = int(data[5])
    x_offset_for_detection = int(data[6])
    y_offset_for_detection = int(data[7])
    width_offset = int(data[8])
    height_offset = int(data[9])
    min_x_offset_same_cls = float(data[10])    
    min_y_offset_same_cls = float(data[11])
    ratio_threshold = float(data[12])
    min_matches = int(data[13])
    max_size_acceptable = float(data[14])
    project_folder = data[15]
    name = data[16] 

# paths for rebox.py
projects_folder = "/home/rebox/projects/"
project_folder = os.path.join(projects_folder, project_folder)

# paths for plot_label.py
pl_save_dir = "/home/rebox/boxed/"

# #---------CONFIGURATION---------#

# # how many photos matched from 1 photo
# no_photo_match
# # this is for the detection zone in the 2nd image, the 2 values determine how much away from the object is relevant for detection
# x_offset_for_detection  # ?? unit away from obj top left x
# y_offset_for_detection  # ?? unit away from obj top left y
# width_offset # How wide the detect zone is
# height_offset # How tall the detect zone is

# # determine how close can boxes of same class be
# min_x_offset_same_cls # ?? unit away from the closest box of same class
# min_y_offset_same_cls # ?? unit away from the closest box of same class

# # for detection confidence and threshold
# ratio_threshold # the higher, the more lenient the matching is
# min_matches # higher values will allow boxes with lower confidence
# max_size_acceptable # the maximum size that a new box can replace an existing box, i.e. x times larger than original,
# # set higher if boxes diminish fast or object is sometimes big and sometimes small

# # for matching computation, may need higher values only for ambiguous objects

# # THIS PART BOTTLENECKS THE PROGRAM THE MOST, SETTING EITHER VALUE ABOVE 300000 WILL CRASH 
# nfeature_obj
# nfeature_detect_zone

# #---------CONFIGURATION---------#