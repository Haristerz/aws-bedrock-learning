import boto3
import psycopg2
import json
from dotenv import load_dotenv
import os

load_dotenv()

BUCKET_NAME = "hari-bedrock-documents-2026"
CLAUDE_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"

# Bedrock client
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='ap-south-1'
)

# S3 client
s3_client = boto3.client(
    service_name='s3',
    region_name='ap-south-1'
)

# RDS connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT'),
    sslmode='verify-full',
    sslrootcert='./global-bundle.pem'
)

print("All connections established!")

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

# Step 2 - Chunk documents
def chunk_documents(documents, chunk_size=500):
    chunks = []
    for doc in documents:
        for i in range(0, len(doc), chunk_size):
            chunk = doc[i:i+chunk_size]
            chunks.append(chunk)
    print(f"Total chunks created: {len(chunks)}")
    return chunks

# Step 3 - Get embedding for one text
def get_embedding(text):
    response = bedrock_client.invoke_model(
        modelId=EMBEDDING_MODEL,
        body=json.dumps({"inputText": text}),
        contentType="application/json",
        accept="application/json"
    )
    result = json.loads(response['body'].read())
    return result['embedding']

# Step 4 - Build index
def build_index(chunks):
    index = []
    for chunk in chunks:
        emb = get_embedding(chunk)
        index.append({
            "content": chunk,
            "embedding": emb
        })
    print(f"Index built: {len(index)} chunks")
    return index

# Step 5 - Store in RDS
def store_in_rds(index):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents;")
    print("Cleared existing data!")
    for item in index:
        cursor.execute(
            "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
            (item['content'], item['embedding'])
        )
    conn.commit()
    cursor.close()
    print(f"Stored {len(index)} chunks in RDS!")

# Step 6 - Find relevant chunk using pgvector
def find_relevant_chunk(question):
    question_embedding = get_embedding(question)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT content
        FROM documents
        ORDER BY embedding <-> %s::vector
        LIMIT 1
        """,
        (question_embedding,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result[0]

# Step 7 - Answer question using Claude
def answer_question(question):
    relevant_chunk = find_relevant_chunk(question)
    print(f"\nRelevant chunk found:\n{relevant_chunk}\n")

    prompt = f"""Answer the question based on this context only.

CONTEXT:
{relevant_chunk}

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
chunks = chunk_documents(documents)
index = build_index(chunks)
store_in_rds(index)

# Test
question = "What is machine learning?"
answer = answer_question(question)
print(f"\nQuestion: {question}")
print(f"Answer: {answer}")