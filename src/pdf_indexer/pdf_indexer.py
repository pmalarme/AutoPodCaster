import os
import json
import uuid
import requests
import asyncio
from dotenv import load_dotenv
from azure.servicebus.aio import ServiceBusClient
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_community.document_loaders import PyPDFLoader
import tiktoken

load_dotenv()

servicebus_connection_string = os.getenv("SERVICEBUS_CONNECTION_STRING")
cosmosdb_connection_string = os.getenv("COSMOSDB_CONNECTION_STRING")
status_endpoint = os.getenv("STATUS_ENDPOINT")
blob_service_client = BlobServiceClient.from_connection_string(
    os.getenv("STORAGE_CONNECTION_STRING"))
container_name = "uploads"


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
            receiver = servicebus_client.get_queue_receiver('pdf')
            async with receiver:
                received_messages = await receiver.receive_messages(
                    max_message_count=1, max_wait_time=5)
                for message in received_messages:
                    pdf_input = json.loads(str(message))
                    file_location = pdf_input['input']
                    update_status(pdf_input['request_id'], "Indexing")
                    input = index_pdf(file_location)
                    update_status(pdf_input['request_id'], "Indexed")
                    save_to_cosmosdb(input)
                    update_status(pdf_input['request_id'], "Saved")
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


def index_pdf(file_location: str):
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=file_location)
    download_file_path = file_location
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    loader = PyPDFLoader(download_file_path)
    documents = loader.load()

    title = documents[0].metadata.get('title', 'Unknown Title')
    description = documents[0].metadata.get('description', '')
    url = file_location

    input = Input()
    input.id = str(uuid.uuid4())
    input.title = title
    input.date = ''
    input.last_updated = ''
    input.author = ''
    input.description = description
    input.source = url
    input.type = 'pdf'
    input.thumbnail_url = ''
    input.topics = []
    input.entities = []

    for document in documents:
        document.metadata['title'] = title
        document.metadata['source'] = url
        document.metadata['description'] = description
        document.metadata['thumbnail_url'] = ''
        document.metadata['type'] = 'pdf'

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)

    azure_openai_embeddings = AzureOpenAIEmbeddings(
        api_key=os.environ['OPENAI_API_KEY'],
        azure_endpoint=os.environ['OPENAI_AZURE_ENDPOINT'],
        api_version=os.environ['OPENAI_API_VERSION'],
        azure_deployment=os.environ['OPENAI_AZURE_DEPLOYMENT_EMBEDDINGS']
    )

    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_ADMIN_KEY"),
        index_name=index_name,
        embedding_function=azure_openai_embeddings.embed_query,
    )
    vector_store.add_documents(documents=splits)

    input.content = '\n\n'.join([doc.page_content for doc in documents])

    os.remove(download_file_path)

    return input


while (True):
    asyncio.run(main())
    asyncio.sleep(5)
