from fastapi import FastAPI
from pydantic import BaseModel
import boto3

app=FastAPI(
    title="Hari's AI Agent API",
    description="AWS Bedrock powered AI API",
    version="1.0.0"
)

client = boto3.client(
    service_name='bedrock-runtime',
    region_name='ap-south-1'
)

# Store conversation history
conversation_history = []

# Define request structure
class ChatRequest(BaseModel):
    message: str

# Define response structure
class ChatResponse(BaseModel):
    answer: str
    total_messages: int

@app.get('/')
def health_check():
    return {
        "status": "running",
        "project": "AWS Bedrock agent",
        "model": "Claude 3 Haiku"
    }

@app.post('/chat',response_model=ChatResponse)
def chat(request: ChatRequest):

    # Add user message to history
    conversation_history.append({
        'role': 'user',
        'content': [{'text': request.message}]
    })

    # Call Claude via Bedrock
    response = client.converse(
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
                - Connect concepts to Bedrock 
                  and AI Agents always
                - Give practical hands-on advice
                - Keep answers concise and clear'''
            }
        ],
        messages=conversation_history
    )

        # Get answer
    answer = response['output']['message']['content'][0]['text']
    
    # Add to history
    conversation_history.append({
        'role': 'assistant',
        'content': [{'text': answer}]
    })
    
    return ChatResponse(
        answer=answer,
        total_messages=len(conversation_history)
    )
# Clear conversation
@app.delete("/clear")
def clear_conversation():
    conversation_history.clear()
    return {"status": "conversation cleared"}
