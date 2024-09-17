from dotenv import load_dotenv
from pytubefix import YouTube
from moviepy.editor import VideoFileClip
from azure.servicebus.aio import ServiceBusClient
from openai import AzureOpenAI
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import LanceDB
from azure.cosmos import CosmosClient

import os
import asyncio
import json
import whisper
import tiktoken
import lancedb
import uuid
import requests

# Load the environment variables
load_dotenv()

servicebus_connection_string = os.getenv("SERVICEBUS_CONNECTION_STRING")
cosmosdb_connection_string = os.getenv("COSMOSDB_CONNECTION_STRING")
status_endpoint = os.getenv("STATUS_ENDPOINT")


class Input:
    id: str
    title: str
    date: str
    last_updated: str
    author: str
    description: str
    source: str
    type: str
    thumbnail_url: str
    topics: list
    entities: list
    content: str

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "last_updated": self.last_updated,
            "author": self.author,
            "description": self.description,
            "source": self.source,
            "type": self.type,
            "thumbnail_url": self.thumbnail_url,
            "topics": self.topics,
            "entities": self.entities,
            "content": self.content
        }


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
                    update_status(video_input['request_id'], "Indexing")
                    input = index_video(video_url)
                    update_status(video_input['request_id'], "Indexed")
                    save_to_cosmosdb(input)
                    update_status(video_input['request_id'], "Saved")
                    await receiver.complete_message(message)


def save_to_cosmosdb(input: Input):
    client = CosmosClient.from_connection_string(cosmosdb_connection_string)
    database_name = "autopodcaster"
    database = client.get_database_client(database_name)
    container_name = "inputs"
    container = database.get_container_client(container_name)
    container.create_item(body=input.to_dict())


def update_status(request_id: str, status: str):
    status = {"status": status}
    requests.post(
        f"{status_endpoint}/status/{request_id}", json=status)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def index_video(video_url: str):
    youtube_video = YouTube(video_url)

    title = youtube_video.title
    description = youtube_video.description
    url = youtube_video.watch_url
    thumbnail_url = youtube_video.thumbnail_url

    input = Input()
    input.id = str(uuid.uuid4())
    input.title = title
    input.date = youtube_video.publish_date.isoformat()
    input.last_updated = youtube_video.publish_date.isoformat()
    input.author = youtube_video.author
    input.description = description
    input.source = url
    input.type = 'video'
    input.thumbnail_url = thumbnail_url
    input.topics = []
    input.entities = []

    temporary_video_filename = youtube_video.streams \
        .filter(progressive=True, file_extension='mp4') \
        .order_by('resolution').desc() \
        .first() \
        .download(output_path='outputs')

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

    # Create the prompt to improve each transcript chunk using the title and the description of the video (technologies, people names, etc.)
    prompt_template = """Given title and description of a video, can you check its transcript and correct it. Give back only the corrected transcript.

    Title: {title}
    Description:
    {description}

    Transcript:
    {transcript}
    """

    # Create the gpt-4o model client
    azure_openai_client = AzureOpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
        azure_endpoint=os.environ['OPENAI_AZURE_ENDPOINT'],
        api_version=os.environ['OPENAI_API_VERSION']
    )

    encoding_name = 'gpt-4o'

    # Split the text in chunks of maximum 500 tokens with '.' as separator without using langchain
    sentences = result['text'].split('.')
    chunks = []
    chunk = ''
    chunk_number = 1
    for sentence in sentences:
        if num_tokens_from_string(chunk + sentence, encoding_name) > 500:
            prompt = prompt_template.format(
                title=title, description=description, transcript=chunk)
            corrected_chunk = azure_openai_client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                top_p=1,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            ).choices[0].message.content
            chunks.append(corrected_chunk)
            chunk = sentence + '. '
            chunk_number += 1
        else:
            chunk += sentence + '. '

    # Write the last chunk
    prompt = prompt_template.format(
        title=title, description=description, transcript=chunk)
    corrected_chunk = azure_openai_client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        top_p=1,
        messages=[
            {"role": "user", "content": prompt},
        ],
    ).choices[0].message.content
    chunks.append(corrected_chunk)

    # Create the full corrected transcript and add white-lines between the chunks but not for the last chunk
    full_corrected_transcript = ''

    for i, chunk in enumerate(chunks):
        full_corrected_transcript += chunk
        if i < len(chunks) - 1:
            full_corrected_transcript += '\n\n'

    input.content = full_corrected_transcript

    # Write the full corrected transcript
    full_corrected_transcript_file_name = temporary_video_filename.split('.')[
        0] + '_corrected.txt'

    with open(get_file(full_corrected_transcript_file_name), "w") as f:
        f.write(full_corrected_transcript)

    # Create langchain document
    document = Document(
        page_content=full_corrected_transcript,
        metadata={
            "title": title,
            "source": url,
            "description": description,
            "thumbnail_url": thumbnail_url,
            "page": 0,
            "type": "video"
        }
    )

    documents = [document]  # List of documents to be processed

    # Split the document in chunks of maximum 1000 characters with 200 characters overlap using langchain
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)

    # Define the embeddings model
    azure_openai_embeddings = AzureOpenAIEmbeddings(
        api_key=os.environ['OPENAI_API_KEY'],
        azure_endpoint=os.environ['OPENAI_AZURE_ENDPOINT'],
        api_version=os.environ['OPENAI_API_VERSION'],
        azure_deployment=os.environ['OPENAI_AZURE_DEPLOYMENT_EMBEDDINGS']
    )

    # Create the vector store
    db = lancedb.connect("/tmp/lancedb")

    vectorstore = LanceDB.from_documents(
        documents=splits,
        embedding=azure_openai_embeddings
    )

    retriever = vectorstore.as_retriever()

    return input


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
