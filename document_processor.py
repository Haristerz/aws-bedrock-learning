import boto3

# Create clients
s3_client = boto3.client(
    service_name='s3',
    region_name='ap-south-1'
)

bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='ap-south-1'
)

def read_document_from_s3(bucket_name, file_name):
    """Read document content from S3"""
    
    print(f"Reading {file_name} from S3...")
    
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=file_name
    )
    
    content = response['Body'].read().decode('utf-8')
    
    print(f"Document loaded — {len(content)} characters")
    
    return content

def summarize_document(document_content, question):
    """Send document to Claude and get answer"""
    
    print(f"\nAsking Claude: {question}")
    print("-" * 40)
    
    # Build prompt with document
    prompt = f"""Here is a document:

{document_content}

Based on this document, answer this question:
{question}

Give a clear and concise answer."""

    response = bedrock_client.converse(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        messages=[
            {
                'role': 'user',
                'content': [{'text': prompt}]
            }
        ]
    )
    
    answer = response['output']['message']['content'][0]['text']
    return answer

def main():
    # Configuration
    BUCKET_NAME = 'hari-bedrock-documents-2026'
    FILE_NAME = 'test_document.txt'
    
    # Step 1: Read document from S3
    document = read_document_from_s3(BUCKET_NAME, FILE_NAME)
    
    # Step 2: Ask multiple questions about the document
    questions = [
        "What is AWS Bedrock?",
        "What is RAG and why is it important?",
        "What can AI Agents do with tools?"
    ]
    
    for question in questions:
        answer = summarize_document(document, question)
        print(f"\nAnswer: {answer}")
        print("=" * 40)

if __name__ == "__main__":
    main()