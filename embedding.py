import boto3
import json
import math

# Create clients
s3_client = boto3.client(
    service_name='s3',
    region_name='ap-south-1'
)

bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='ap-south-1'
)

BUCKET_NAME = "hari-bedrock-documents-2026"
CLAUDE_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"

# Step 1 - Load all documents from S3
def get_all_documents():
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    documents = []
    for obj in response['Contents']:
        file_name = obj['Key']
        file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_name)
        content = file_obj["Body"].read().decode("utf-8")
        documents.append(content)
    print(f"Total documents loaded: {len(documents)}")
    return documents

# Step 2 - Convert one text to embedding
def get_embedding(text):
    response = bedrock_client.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text}),
        contentType="application/json",
        accept="application/json"
    )
    result = json.loads(response['body'].read())
    return result['embedding']

# Step 3 - Build index (content + embedding together)
def build_index(documents):
    index = []
    for doc in documents:
        emb = get_embedding(doc)
        index.append({
            "content": doc,
            "embedding": emb
        })
    print(f"Index built: {len(index)} documents")
    return index

# Step 4 and 5 - Find most relevant document
def find_relevant_document(question, index):
    question_embedding = get_embedding(question)
    
    best_match = None
    best_score = -1
    
    for doc in index:
        score = cosine_similarity(question_embedding, doc["embedding"])
        if score > best_score:
            best_score = score
            best_match = doc
    
    print(f"Best score: {best_score:.4f}")
    return best_match

# Cosine similarity - compare two embeddings
def cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0
    return dot_product / (magnitude_a * magnitude_b)

# Step 6 - Send to Claude and get answer
def answer_question(question, index):
    relevant_doc = find_relevant_document(question, index)
    
    prompt = f"""Answer the question based on this document only.

DOCUMENT:
{relevant_doc['content']}

QUESTION: {question}"""
    
    response = bedrock_client.invoke_model(
        modelId=CLAUDE_MODEL,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }),
        contentType="application/json",
        accept="application/json"
    )
    
    result = json.loads(response['body'].read())
    return result['content'][0]['text']

# Main - Run everything
documents = get_all_documents()
index = build_index(documents)

question = "What is Machine learning?"
print(f"\nQuestion: {question}")
answer = answer_question(question, index)
print(f"Answer: {answer}")