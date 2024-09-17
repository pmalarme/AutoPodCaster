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
echo STATUS_ENDPOINT=${STATUS_ENDPOINT} >> .env
```

## Run the video indexer

```bash
python video_indexer.py
```