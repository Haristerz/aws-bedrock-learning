import boto3

# Create Bedrock client
client = boto3.client(
    service_name='bedrock-runtime',
    region_name='ap-south-1'
)

# This stores conversation history
conversation_history = []

def chat(user_message):
    # Add user message to history
    conversation_history.append({
        'role': 'user',
        'content': [{'text': user_message}]
    })
    
    # Call Claude with full history
    response = client.converse_stream(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        system=[
          {
            'text': '''You are an expert AWS and 
            AI Engineer mentor for Hari.
            
            About Hari:
            - Systems Engineer at TCS
            - 6.4 years experience
            - Working on BT Group AI Agents 
            project using AWS Bedrock
            - Learning AWS and Agentic AI
            - Goal: Australia PR and 
            international career
            
            Your job:
            - Explain AWS concepts simply
            - Always connect concepts to 
            Bedrock and AI Agents
            - Give practical hands-on advice
            - Be encouraging but honest
            - Keep answers concise and clear'''
          }
        ],
        messages=conversation_history
    )
    
    # Stream response word by word
    print("\nClaude: ", end="", flush=True)
    
    full_response = ""
    
    for event in response['stream']:
        if 'contentBlockDelta' in event:
            text = event['contentBlockDelta']['delta']['text']
            print(text, end="", flush=True)
            full_response += text
    
    print("\n")
    
    # Add Claude response to history
    conversation_history.append({
        'role': 'assistant',
        'content': [{'text': full_response}]
    })

# Main chat loop
print("=== AWS Bedrock AI Chatbot ===")
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() in ['quit', 'bye', 'exit', 'stop']:
        print("Goodbye!")
        break
        
    if user_input.strip() == "":
        continue
        
    chat(user_input)