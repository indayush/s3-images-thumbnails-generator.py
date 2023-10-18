import os
import boto3
from PIL import Image

BOOLEAN_UPLOAD_THUMBNAIL = True
BOOLEAN_PRESERVE_ORIGINAL_ON_LOCAL = False
BOOLEAN_PRESERVE_THUMBNAIL_ON_LOCAL = False
BOOLEAN_ENABLE_LOGGING = True


# Replace these with your S3 credentials and bucket name
S3_BUCKET_NAME = 'bucket_name'

# Define the source and destination folder in S3
source_folder = 'path/to/images/'
destination_folder = 'location/for/s3/thumbnails'
thumbnail_file_prefix = 'thumbnail_'

# Create an S3 client
aws_config_rofile_name = 'aws_profile_name_on_local'
boto3.setup_default_session(profile_name=aws_config_rofile_name)
s3 = boto3.client('s3')


# List all files in the source folder
response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=source_folder)

# Creating Folders to Download Images & generate it's thumbnail
current_directory = os.getcwd()
images_directory = os.path.join(current_directory, r'images/')
if not os.path.exists(images_directory):
   os.makedirs(images_directory)


for obj in response.get('Contents', []):
    # Check if the object is a file (not a folder)

    print("----------------------------------------------------------------------------------")
    if obj['Key'] != source_folder:
        # Create a unique name for the thumbnail
        filename = obj['Key'].split("/")[len(obj['Key'].split("/")) - 1]

        if BOOLEAN_ENABLE_LOGGING:
            print(f"Image on S3 path = {obj['Key']}")

        # Download the image from S3
        s3.download_file(S3_BUCKET_NAME, obj['Key'], images_directory + filename)
        if BOOLEAN_ENABLE_LOGGING:
            print(f"HD File Download Location = {images_directory + filename}")

        # Create a thumbnail
        with Image.open(images_directory + filename) as img:
            img.thumbnail((300, 300))  # Adjust the size as needed
            img.save(images_directory + thumbnail_file_prefix + filename, format='JPEG')

            if BOOLEAN_ENABLE_LOGGING:
                print(f"Thumbnail File Download Location = {images_directory + thumbnail_file_prefix + filename}")


        thumbnail_key = destination_folder + thumbnail_file_prefix + filename

        # Upload the thumbnail to S3
        if BOOLEAN_UPLOAD_THUMBNAIL:
            s3.upload_file(images_directory + thumbnail_file_prefix + filename, S3_BUCKET_NAME, thumbnail_key)
            if BOOLEAN_ENABLE_LOGGING:
                print(f"Thumbnail File Upload Location = {thumbnail_key}")

        # Clean up temporary files
        try:
            if not BOOLEAN_PRESERVE_ORIGINAL_ON_LOCAL:
                os.remove(images_directory + filename)

            if not BOOLEAN_PRESERVE_THUMBNAIL_ON_LOCAL:
                os.remove(images_directory + thumbnail_file_prefix + filename)

        except Exception as e:
            print(e)
