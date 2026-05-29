# AWS Bedrock AI Agent

## Project Structure
├── main.py              → FastAPI REST API
├── chatbot.py           → Streaming chatbot
├── document_processor.py→ S3 document processor
├── embedding.py         → Vector embeddings + RAG
├── Dockerfile           → Docker configuration
├── setup.sh             → EC2 setup script
└── requirements.txt     → Python dependencies

## Setup Instructions

### Local Development
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Docker Local
```bash
docker build -t bedrock-app .
docker run -p 8000:8000 bedrock-app
```

### EC2 Deployment
```bash
# 1. SSH into EC2
ssh -i bedrock-key.pem ec2-user@your-ec2-ip

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Pull from ECR
aws ecr get-login-password --region ap-south-1 | \
docker login --username AWS \
--password-stdin 186388117366.dkr.ecr.ap-south-1.amazonaws.com

# 4. Run container
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=xxx \
  -e AWS_SECRET_ACCESS_KEY=xxx \
  -e AWS_DEFAULT_REGION=ap-south-1 \
  186388117366.dkr.ecr.ap-south-1.amazonaws.com/bedrock-app:latest
```

## Architecture
