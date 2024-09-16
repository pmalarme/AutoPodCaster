from fastapi import FastAPI
from dotenv import load_dotenv
from pytubefix import YouTube

# Load the environment variables
load_dotenv()

# Create the FastAPI app
app = FastAPI()


@app.post("/video_indexer/youtube")
async def youtube_indexer(video_url: str):
    """Index a YouTube video in the vector store.

    Args:
        video_url (str): The URL of the YouTube video to index.
    """
    youtube_video = YouTube(video_url)

    title = youtube_video.title
    url = youtube_video.url
    description = youtube_video.description
    thumbnail_url = youtube_video.thumbnail_url

    temporary_video_filename = youtube_video.streams \
        .filter(progressive=True, file_extension='mp4') \
        .order_by('resolution').desc() \
        .first() \
        .download(output_path='outputs')
