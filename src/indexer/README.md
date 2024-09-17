# Indexer

The indexer is a tool to create a indexer job based on the inputs.

## Install requirements

```bash
pip install -r requirements.txt
```

## Deploy the infrastructure

```bash
. ../infra/deploy.sh
```

## Create the environment variables file

```bash
echo SERVICEBUS_CONNECTION_STRING=${SERVICEBUS_CONNECTION_STRING} > .env
echo STORAGE_CONNECTION_STRING=${STORAGE_CONNECTION_STRING} >> .env
```

## Run the indexer

```bash
fastapi dev indexer.py --port 8081
```

# Output Service Bus
Queue: note, website and video
```json
{
  "request_id": "0b310ec5-e055-4d36-b2d6-9bf7db1ee83f",
  "input": "The text input (either plain text, url or youtube link)"
}
```

Queue: pdf and word
```json
{
  "request_id": "b317ea3b-4e7d-4856-91a2-5913c0f998e5",
  "file_name": "example.pdf",
  "file_container": "uploads",
  "file_location": "https://stautopodcaster682818.blob.core.windows.net/uploads/example.pdf"
}
```