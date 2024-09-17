from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage

import os
import uuid
import json


class InputBody(BaseModel):
    input: str


class StatusBody(BaseModel):
    status: str


load_dotenv()

servicebus_connection_string = os.getenv("SERVICEBUS_CONNECTION_STRING")

status_cache = {}
app = FastAPI()


@app.post("/index")
async def index(inputBody: InputBody):
    input = inputBody.input
    # Generate a uuid for the request
    request_id = str(uuid.uuid4())
    status_cache[request_id] = "Creating"

    message = {
        "request_id": request_id,
        "input": input
    }

    queue = 'note'
    # If it is a URL
    if input.startswith("http"):
        # If it is a YouTube URL
        if "youtube.com" in input:
            queue = 'video'
        else:
            queue = 'website'

    # Send the message to the Service Bus
    with ServiceBusClient.from_connection_string(servicebus_connection_string) as client:
        with client.get_queue_sender(queue) as sender:
            # Encode the service bus message dict as JSON string
            message_json = json.dumps(message)
            servicebus_message = ServiceBusMessage(message_json)
            sender.send_messages(servicebus_message)
            # Update the status
            status_cache[request_id] = "Queued"

    return {"request_id": request_id}


@app.get("/status/{request_id}")
async def status(request_id: str):
    # If request_id is not found, return HTTP 404
    if request_id not in status_cache:
        raise HTTPException(status_code=404, detail="Request ID not found")
    return {"status": status_cache.get(request_id)}


@app.post("/status/{request_id}")
async def update_status(request_id: str, statusBody: StatusBody):
    status_cache[request_id] = statusBody.status
    return {"status": status_cache[request_id]}
