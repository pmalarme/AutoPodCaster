# Output API

The output API generates output (blog, podcast, presentation) based on a subject id using the subject space API.

## Install requirements

```bash
pip install -r requirements.txt
```

Install fast api standard library

```bash
pip install fastapi[standard]==0.112.0
```

## Deploy the infrastructure

```bash
. ../../infra/deploy.sh
```

## Create the environment variables file

```bash
echo SERVICEBUS_CONNECTION_STRING=${SERVICEBUS_CONNECTION_STRING} > .env
echo SUBJECT_SPACE_API_URL=${SUBJECT_SPACE_API_URL} >> .env
```

## Run the output API

```bash
fastapi dev output.py --port 8083
```

# Output Service Bus
Queue: blog, podcast, presentation
```json
{
  "request_id": "0b310ec5-e055-4d36-b2d6-9bf7db1ee83f",
  "subject_id": "d8b1b3b0-4b7b-4b7b-8b7b-8b7b8b7b8b7b",
  "subject_json": {
    "uuid": "d8b1b3b0-4b7b-4b7b-8b7b-8b7b8b7b8b7b",
    "subject": "LoRa fine-tuning",
    "date": "2021-02-06",
    "last_update": "2021-02-06",
    "inputs": ["d8b1b3b0-4b7b-4b7b-8b7b-8b7b8b7b8b7b"],
    "vectorDbName": "vectorDbName"
  },
  "output_type": "blog"
}
```
