
import os  
import base64
from openai import AzureOpenAI  

endpoint = os.getenv("ENDPOINT_URL", "***")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "***")  

# Initialize Azure OpenAI client with key-based authentication    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-05-01-preview",  
)
    
    
# IMAGE_PATH = "YOUR_IMAGE_PATH"
# encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

#Prepare the chat prompt 
chat_prompt = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": "You are an AI assistant."
            }
        ]
    }
] 

    
# Include speech result if speech is enabled  
messages = [
        {"role": "user", "content": "What is the difference between OS update & OS upgrade?"}
    ]  
    
# Generate the completion  
completion = client.chat.completions.create(  
    model=deployment,  
    messages=messages,  
    max_tokens=800,  
    temperature=0.7,  
    top_p=0.95,  
    frequency_penalty=0,  
    presence_penalty=0,  
    stop=None,  
    stream=False
)

# Print the response
completion_text = completion.choices[0].message.content
print(completion_text)