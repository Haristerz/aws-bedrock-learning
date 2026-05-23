import boto3

# Create Bedrock client
client = boto3.client(
    service_name='bedrock-runtime',
    region_name='ap-south-1'
)

# Ask Claude a question
response = client.converse(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    messages=[
        {
            'role': 'user',
            'content': [
                {'text': 'I am learning AWS and AI Agents. Give me a motivational message in 2 lines.'}
            ]
        }
    ]
)

# Print Claude's answer
answer = response['output']['message']['content'][0]['text']
print("Claude says:")
print(answer)