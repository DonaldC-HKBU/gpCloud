#import configparser
import os
import requests
import logging
from urllib.parse import urlparse
logging.basicConfig(level=logging.INFO)
#from dotenv import load_dotenv 
#load_dotenv('token.env')

class HKBU_ChatGPT():
    def submit(self,message):
        conversation = [{"role": "user","content": message}]
        url = "https://genai.hkbu.edu.hk/general/rest/deployments/gpt-4-o-mini/chat/completions?api-version=2024-05-01-preview"
        try:
            chatgpt_token = os.environ['GPT_ACCESS_TOKEN']
            #used for docker below
            #chatgpt_token = os.getenv('GPT_ACCESS_TOKEN')
            logging.info("CHATGPT_TOKEN: %s", chatgpt_token)  # Log the token
        except KeyError:
            logging.error("CHATGPT_TOKEN environment variable not set.")

        #headers = { 'Content-Type': 'application/json','api-key':os.getenv('GPT_ACCESS_TOKEN') }
        headers = { 'Content-Type': 'application/json','api-key': os.environ['GPT_ACCESS_TOKEN'] }
        payload = { 'messages': conversation }

        # Validate the URL
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            logging.error("Invalid URL: %s", url)
            return "Error: The connection string (URL) is invalid."
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raises an error for bad responses
            data = response.json()
                # Ensure you are processing the JSON response correctly           
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                return "Error: Unexpected response structure."
        except requests.exceptions.RequestException as e:
            logging.exception("Request failed: ")
            return "Sorry, there was an error communicating with the ChatGPT service."
        except (KeyError, IndexError) as e:
            logging.exception("Error processing response: ")
            return "Sorry, the response format was unexpected."  

if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()
    
    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response) 