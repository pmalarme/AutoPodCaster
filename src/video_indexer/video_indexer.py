from dotenv import load_dotenv
from pytubefix import YouTube
from moviepy.editor import VideoFileClip
from azure.servicebus.aio import ServiceBusClient

import os
import asyncio
import json
import whisper

# Load the environment variables
load_dotenv()

servicebus_connection_string = os.getenv("SERVICEBUS_CONNECTION_STRING")
improve_transcript_prompt_template = """Given title and description of a video, can you check its transcript and correct it. Give back only the corrected transcript.

Title: {title}
Description:
{description}

Transcript:
{transcript}
"""


async def main():
    """Index a YouTube video in the vector store.

    Args:
        video_url (str): The URL of the YouTube video to index.
    """
    async with ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_string) as servicebus_client:
        async with servicebus_client:
            receiver = servicebus_client.get_queue_receiver('video')
            async with receiver:
                received_messages = await receiver.receive_messages(
                    max_message_count=1, max_wait_time=5)
                for message in received_messages:
                    video_input = json.loads(str(message))
                    video_url = video_input['input']
                    print(f"Indexing video: {video_url}")
                    index_video(video_url)
                    print(f"Video indexed: {video_url}")
                    await receiver.complete_message(message)


def index_video(video_url: str):
    youtube_video = YouTube(video_url)

    title = youtube_video.title
    url = youtube_video.watch_url
    description = youtube_video.description
    thumbnail_url = youtube_video.thumbnail_url

    temporary_video_filename = youtube_video.streams \
        .filter(progressive=True, file_extension='mp4') \
        .order_by('resolution').desc() \
        .first() \
        .download(output_path='outputs')

    # Create the information file
    escaped_description = description.replace('\n', '\\n').replace('"', '\\"')
    info_file_name = temporary_video_filename.split('.')[0] + '_info.json'
    with open(get_file(info_file_name), 'w') as f:
        f.write(f'{{"title": "{title}", "url": "{url}", "description": "{escaped_description}", "thumbnail_url": "{thumbnail_url}"}}')

    # Create the file name for the audio file
    audioFileName = temporary_video_filename.split('.')[0] + '.wav'

    # Create the audio
    video = VideoFileClip(temporary_video_filename)
    audio = video.audio
    audio.write_audiofile(get_file(audioFileName))

    # Cleanup: delete the video file
    video.close()
    os.remove(get_file(temporary_video_filename))

    # Create the transcript using Whisper
    model = whisper.load_model('base')
    result = model.transcribe(get_file(audioFileName))

    # Cleanup: delete the audio file
    os.remove(get_file(audioFileName))

    # Save the transcript
    transcriptFileName = temporary_video_filename.split('.')[0] + '.txt'

    with open(get_file(transcriptFileName), "w") as f:
        f.write(result["text"])


def get_file(file_name: str):
    """Get file path

    Args:
        file_name (str): File name

    Returns:
        File path
    """
    output_folder = 'outputs'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return os.path.join(output_folder, file_name)


while (True):
    asyncio.run(main())
    asyncio.sleep(5)
