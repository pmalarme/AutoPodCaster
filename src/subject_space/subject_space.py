from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from azure.cosmos import CosmosClient

import logging
import uuid
import datetime

# Load the environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
servicebus_connection_string = os.getenv("SERVICEBUS_CONNECTION_STRING")
cosmosdb_connection_string = os.getenv("COSMOSDB_CONNECTION_STRING")


class InputSubjectSpace(BaseModel):
    subject: str


class SubjectSpace(BaseModel):
    id: str
    subject: str
    date: str
    last_updated: str
    inputs: list


app = FastAPI()

# Disable CORS checking
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/subject")
async def get_subjects():
    """Get all subjects in the subject space.
    """
    client = CosmosClient(cosmosdb_connection_string)
    database = client.get_database_client("autopodcaster")
    container = database.get_container_client("subjects")

    subjects = []
    async for item in container.query_items(
        query="SELECT * FROM subjects",
        enable_cross_partition_query=True
    ):
        subjects.append(item)

    return subjects


@app.get("/subject/{subject_id}")
async def get_subject(subject_id: str):
    """Get a subject in the subject space.
    """
    client = CosmosClient(cosmosdb_connection_string)
    database = client.get_database_client("autopodcaster")
    container = database.get_container_client("subjects")

    subject = await container.read_item(item=subject_id, partition_key=subject_id)
    return subject


@app.post("/subject")
async def create_subject(inputSubjectSpace: InputSubjectSpace):
    """Create a subject in the subject space.
    """
    client = CosmosClient(cosmosdb_connection_string)
    database = client.get_database_client("autopodcaster")
    container = database.get_container_client("subjects")

    now_string = datetime.datetime.now().isoformat()

    subject = SubjectSpace(
        id=str(uuid.uuid4()),
        subject=inputSubjectSpace.subject,
        date=now_string,
        last_updated=now_string,
        inputs=[]
    )

    container.create_item(body=subject.dict())
    return subject


@app.put("/subject/{subject_id}")
async def update_subject(subject_id: str, inputSubjectSpace: InputSubjectSpace):
    """Update a subject in the subject space.
    """
    client = CosmosClient(cosmosdb_connection_string)
    database = client.get_database_client("autopodcaster")
    container = database.get_container_client("subjects")

    subject = await container.read_item(item=subject_id, partition_key=subject_id)
    subject.subject = inputSubjectSpace.subject
    subject.last_updated = datetime.datetime.now().isoformat()

    container.upsert_item(body=subject)
    return subject


@app.delete("/subject/{subject_id}")
async def delete_subject(subject_id: str):
    """Delete a subject in the subject space.
    """
    client = CosmosClient(cosmosdb_connection_string)
    database = client.get_database_client("autopodcaster")
    container = database.get_container_client("subjects")

    await container.delete_item(item=subject_id, partition_key=subject_id)
    return {"message": "Subject deleted"}
