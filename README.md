## Introduction
A featuring-matching algorithm to enhance object detection in video frames by re-identifying and restoring missing bounding boxes due to model limitations and camera angles

## Components
### main.py
This is the main algorithm. In a series of images generated from a video, several images are compared with an earlier image to see if any object is missing in the images but present in the earlier image, which is done using feature matching. New labels with correct coordinates will be created for every missing object in the image.
### plot_labels.py
This is a helper function to help generate images with bounding boxes for better visualization in the GUI application (image viewer).
### image_to_video.py
This is a helper function to convert the series of images back to a video for better visualization in the GUI application (video player).
### flask_rebox_server.py
This contains flask APIs to bridge the communication between the GUI application and the remote server running the algorithm.
