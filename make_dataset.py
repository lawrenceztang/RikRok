from google.cloud import storage
import requests
import subprocess
import cv2

storage_client = storage.Client()

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

def get_crop(width, height):
    new_width = aspect_ratio[0] / aspect_ratio[1] * height
    new_height = height
    new_x = (width - new_width) / 2
    new_y = 0
    return new_width, new_height, new_x, new_y

key = "AIzaSyDYhQYpJy_JLoeeTMoMHbpZNkeE5c7TXpI"


i = 1
token = ""
query = "img"
download_path = "vid0.mp4"
format_path = "vid1.mp4"
aspect_ratio = (9, 16)
upload_path = "rikrok-24942.appspot.com"
channel_set = set()

while True:
    link = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&order=title&q={query}&safeSearch=moderate&type=video&videoCaption=none&videoDefinition=standard&videoDimension=2d&videoDuration=short&videoEmbeddable=true&videoLicense=creativeCommon&videoSyndicated=any&maxResults=50&pageToken={token}&key={key}"
    contents = requests.get(link).json()
    token = contents['nextPageToken']
    for video in contents['items']:
        id = video['id']['videoId']
        
        channel = video['snippet']['channelId']
        if channel in channel_set:
            continue
        channel_set.add(channel)

        video_url = f"https://www.youtube.com/watch?v={id}"
        subprocess.run(["yt-dlp", video_url, "-o", download_path, "-f", "mp4"])

        vid = cv2.VideoCapture(download_path)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        w, h, x, y = get_crop(width, height)

        subprocess.run(["ffmpeg", "-y", "-i", download_path, "-filter:v", f"crop={w}:{h}:{x}:{y}", format_path, "-movflags", "faststart"])
        subprocess.run(["rm", download_path])
        try:
            upload_blob(upload_path, format_path, f"Videos/{i}.mp4")
        except:
            print('Error uploading video')
            pass
        i += 1
        print(i)