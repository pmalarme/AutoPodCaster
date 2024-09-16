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
```

## Run the indexer

```bash
fastapi dev indexer.py --port 8081
```