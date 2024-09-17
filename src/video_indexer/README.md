# Video Indexer

This video indexer get messages from the service bus and process the video to extract the information.

## Install requirements

```bash
sudo apt-get install ffmpeg # For Whisper
pip install -r requirements.txt
```

## Deploy the infrastructure

If not already done, deploy the infrastructure:

```bash
. ../infra/deploy.sh
```

## Create the environment variables file

```bash
echo SERVICEBUS_CONNECTION_STRING=${SERVICEBUS_CONNECTION_STRING} > .env
echo COSMOSDB_CONNECTION_STRING=${COSMOSDB_CONNECTION_STRING} >> .env
echo STATUS_ENDPOINT=http://localhost:8081 >> .env
echo AI_SEARCH_ENDPOINT=${AI_SEARCH_ENDPOINT} >> .env
echo AZURE_SEARCH_ADMIN_KEY=${AZURE_SEARCH_ADMIN_KEY} >> .env
```

Add the following to the `.env` file:

```bash
OPENAI_API_KEY=<API_KEY>
OPENAI_AZURE_ENDPOINT=<ENDPOINT>
OPENAI_AZURE_DEPLOYMENT=gpt-4o
OPENAI_API_VERSION=2024-02-15-preview
```

Replace `<API_KEY>` and `<ENDPOINT>` with the actual values.

## Run the video indexer

```bash
python video_indexer.py
```