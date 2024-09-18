import os
import json
import uuid
import requests
import asyncio
from dotenv import load_dotenv
from azure.servicebus.aio import ServiceBusClient
from azure.cosmos import CosmosClient
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioDataStream
from openai import AzureOpenAI
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import LanceDB
import whisper
import tiktoken

load_dotenv()

servicebus_connection_string = os.getenv("SERVICEBUS_CONNECTION_STRING")
cosmosdb_connection_string = os.getenv("COSMOSDB_CONNECTION_STRING")
status_endpoint = os.getenv("STATUS_ENDPOINT")
subject_space_api_url = os.getenv("SUBJECT_SPACE_API_URL")

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
    async with ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_string) as servicebus_client:
        async with servicebus_client:
            receiver = servicebus_client.get_queue_receiver('podcast')
            async with receiver:
                received_messages = await receiver.receive_messages(
                    max_message_count=1, max_wait_time=5)
                for message in received_messages:
                    podcast_input = json.loads(str(message))
                    subject_id = podcast_input['subject_id']
                    update_status(podcast_input['request_id'], "Processing")
                    input = process_podcast(subject_id)
                    update_status(podcast_input['request_id'], "Processed")
                    save_to_cosmosdb(input)
                    update_status(podcast_input['request_id'], "Saved")
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

def process_podcast(subject_id: str) -> Input:
    response = requests.get(f"{subject_space_api_url}/subjects/{subject_id}")
    if response.status_code != 200:
        raise Exception("Subject not found")
    subject_json = response.json()

    title = subject_json['subject']
    description = subject_json.get('description', '')
    url = subject_json.get('url', '')
    thumbnail_url = subject_json.get('thumbnail_url', '')

    input = Input()
    input.id = str(uuid.uuid4())
    input.title = title
    input.date = ''
    input.last_updated = ''
    input.author = ''
    input.description = description
    input.source = url
    input.type = 'podcast'
    input.thumbnail_url = thumbnail_url
    input.topics = []
    input.entities = []

    # Generate podcast script and audio
    podcast_script = generate_podcast_script(subject_json)
    podcast_audio = generate_podcast_audio(podcast_script)

    input.content = podcast_script

    return input

def generate_podcast_script(subject_json):
    title = subject_json['subject']
    description = subject_json.get('description', '')

    prompt_template = """Given title and description of a subject, can you create a podcast script. Give back only the script.

    Title: {title}
    Description:
    {description}

    Script:
    """

    azure_openai_client = AzureOpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
        azure_endpoint=os.environ['OPENAI_AZURE_ENDPOINT'],
        api_version=os.environ['OPENAI_API_VERSION']
    )

    prompt = prompt_template.format(title=title, description=description)
    podcast_script_response = azure_openai_client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        top_p=1,
        messages=[
            {"role": "user", "content": prompt},
        ],
    ).choices[0].message.content

    return podcast_script_response

def generate_podcast_audio(podcast_script):
    speech_key = os.environ['AZURE_SPEECH_KEY']
    service_region = os.environ['AZURE_SPEECH_REGION']

    speech_config = SpeechConfig(subscription=speech_key, region=service_region)
    speech_synthesizer = SpeechSynthesizer(speech_config=speech_config)

    ssml_text = f"<speak version='1.0' xmlns='https://www.w3.org/2001/10/synthesis' xml:lang='en-US'>{podcast_script}</speak>"

    result = speech_synthesizer.speak_ssml_async(ssml_text).get()
    stream = AudioDataStream(result)
    podcast_filename = f"podcast_{uuid.uuid4()}.wav"
    stream.save_to_wav_file(podcast_filename)

    return podcast_filename

while (True):
    asyncio.run(main())
    asyncio.sleep(5)
