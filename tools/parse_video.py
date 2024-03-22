# Developed by Anton Melnychuk          March 1st 2024
# For ASTR 330 Class                    Yale University

import os
import cv2
import platform
import subprocess

CURRENT_DIR = os.path.dirname(__file__)


def combine_images_to_video(folder_path, video_filename):
    image_filenames = sorted([os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith('.png')])
    
    if not image_filenames:
        print("No images found in the folder.")
        return

    sample_image = cv2.imread(image_filenames[0])
    height, width, _ = sample_image.shape

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    video_writer = cv2.VideoWriter(video_filename, fourcc, 10, (width, height))

    for image_filename in image_filenames:
        image = cv2.imread(image_filename)
        video_writer.write(image)

    video_writer.release()
    print(f"Proccess completed! Video saved as {video_filename}")

    # Open the video file using default player
    if platform.system() == 'Windows':
        os.startfile(video_filename)
    elif platform.system() == 'Darwin':  # ahndle macOS
        subprocess.Popen(['open', video_filename])
    else:  # Linux and other Unix-like systems
        subprocess.Popen(['xdg-open', video_filename])
