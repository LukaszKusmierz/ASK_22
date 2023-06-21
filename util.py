import datetime
import os
import uuid
from pathlib import Path


def convert_timestamp_to_date(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime("%Y-%m-%d %H:%M:%S")


def save_image_dm(image_file):
    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    image_path = 'static/uploads/' + unique_filename
    image_file.save(image_path)
    return image_path


def get_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def delete_image_files(image_paths):
    [Path(image_path).unlink() for image_path in image_paths if image_path and
     Path(image_path).is_file() and Path(image_path).exists()]
