# UI

## Run

1. Run the fastAPI first 
cd src\indexer
(if needed) ..\..\.venv\Scripts\Activate.ps1
fastapi dev indexer.py --port 8081

2. Run react (second terminal)
cd ui
(if needed) npm install
npm run dev


## Test
LoRA (Low-Rank Adaptation of Large Language Models) is a popular and lightweight training technique that significantly reduces the number of trainable parameters. It works by inserting a smaller number of new weights into the model and only these are trained. 
This makes training with LoRA much faster, memory-efficient, and produces smaller model weights (a few hundred MBs), which are easier to store and share. LoRA can also be combined with other training techniques like DreamBooth to speedup training.
https://arxiv.org/pdf/2106.09685
LoRA reduces the number of trainable parameters by learning pairs of rank-decompostion matrices while freezing the original weights. This vastly reduces the storage requirement for large language models adapted to specific tasks and enables efficient task-switching during deployment all without introducing inference latency. LoRA also outperforms several other adaptation methods including adapter, prefix-tuning, and fine-tuning.
