import os
import moviepy.video.io.ImageSequenceClip
import config
import natsort


def to_video(img_folder, video_name, fps):
    image_folder= img_folder
    fps=fps


    destination_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),f"videos/{video_name}.mp4")

    image_files = natsort.os_sorted([os.path.join(image_folder,img)
                for img in os.listdir(image_folder)
                if img.endswith(".jpg")])

    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(destination_dir)


if __name__ == "__main__":
    to_video("/home/rebox/boxed/construction_400img3", "construction", 15)
  