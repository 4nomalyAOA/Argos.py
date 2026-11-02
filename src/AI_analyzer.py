import httpx 
import json
from urllib.parse import urljoin 


AI_INFOS = {
    "CHATGPT": {
        "url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o-mini",
    },
    "CLAUDE": {
        "url": "https://api.anthropic.com/v1/messages",
        "model": "claude-3-5-haiku-20241022",
    },
    "GEMINI": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
        "model": "gemini-1.5-flash",
    },
    "MISTRAL": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-small-latest",
    },
    "DEEPSEEK": {
        "url": "https://api.deepseek.com/chat/completions",
        "model": "deepseek-chat",
    },
    "GROQ": { 
        "url": "https://api.openai.com/v1/chat/completions", 
        "model": "llama-3.1-8b-instant",
    },
    "QWEN": {
        "url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-turbo",
    },
    "GROK": {
        "url": "https://api.x.ai/v1/chat/completions",
        "model": "grok-3-mini",
    },
    "OLLAMA": {
        "url": "http://localhost:11434/v1/chat/completions",
        "model": "llama3:8b",
    }
}

def ask_ai_choice():
    """Invite the user to make his choice between multiple AI models"""
    print("\n[?] Here are all available AI models: ")
    for provider, config in AI_INFOS.items():
        print(f"-{provider} -- {config['model']}") #print all the different providers and the models
    
    provider = ""
    while provider not in AI_INFOS:
        provider = input("\n[?] Enter the model you want to use")
        if provider in AI_INFOS:
            return provider #check if the provider really is in the list   
        else:
            print("\n[-] No valid input entered")    


async def send_ai(data, provider):
    """Sending the request to the AI with the API"""
    async with httpx.AsyncClient() as client:
        API_KEY = input("\n[?] Enter your API key")
        max_tokens = 1024
        
        config = AI_INFOS[provider]
        url = config['url'] 
        model = config['model']
        
        prompt = (
            "You are an OSINT expert and a cybersecurity analyst. " #a prompt so send to an AI
            "The following JSON file is the result of a scraping operation with argos.py. "
            "Highlight the site's structure, potential security vulnerabilities, server configurations, "
            "forms, and key insights. Base you result with the JSON file and internet informations. Provide a clean, structured report in English."
        )
        
        data_str = json.dumps(data, indent=2, ensure_ascii=False)
        full_content = f"{prompt}\nHere is the target you have to analyze\n{data_str}"
        
        if provider.upper() == "CLAUDE": #this is basically the same code for each type of AI but gemini and claude have different requirements
            headers = {
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            payload = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": full_content}]} #the whole content to send to the AI 
            
            try:
                response = await client.post( #sending the data to the AI
                    url = url,
                    json = payload,
                    headers = headers
                )
                
                print("\n[+] Request sent")
                
                content = response.json()["content"][0]["text"] #getting the response as a JSON
                
                return content
                
            except Exception as e:
                print(f"\n[-] Error during sending the request: {e}")
                
        elif provider.upper() == "GEMINI":
            headers = {
                        "Content-Type": "application/json"
                        }
            
            payload = {"contents": [{"parts": [{"text": full_content}]}]}
            
            try:
                response = await client.post(
                url = urljoin(url, f"?key={API_KEY}"), #for gemini, the API is entered in the url
                json = payload,
                headers = headers
                )
                
                print("\n[+] Request sent")
                            
                content = response.json()["candidates"][0]["content"]["parts"][0]["text"] #same, the response
                            
                return content
                            
            except Exception as e:
                print(f"\n[-] Error during sending the request: {e}")
        
        else: #this works for most of others AI, the two above are the exceptions
            headers = { 
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
                        }
                        
            payload = {"model": model, "messages": [{"role": "user", "content": full_content}]}
                        
            try:
                response = await client.post(
                    url = url,
                    json = payload,
                    headers = headers
                )
                            
                print("\n[+] Request sent")
                                        
                content = response.json()["choices"][0]["message"]["content"]
                                        
                return content
                                        
            except Exception as e:
                print(f"\n[-] Error during sending the request: {e}")
               
def content_saver(content):
    """Saving the content the AI made"""
    file_name = input("\n[?] Enter the name of the file you save the AI content in")           
    with open(file_name, 'w', encoding= 'utf-8') as f: 
        f.write(content) #writing the content in a file
    print(f"\n[+] Content successfully saved in: {file_name}")       
    