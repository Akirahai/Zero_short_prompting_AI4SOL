import os
from dotenv import load_dotenv
from typing import Any, Dict, Iterable, List, Optional
from openai import OpenAI
from groq import Groq
# CHECK: Read OpenAI API key from an environment variable
# Load the environment variables from .env file

o = os.path.dirname(os.path.abspath(__file__))

os.chdir(o)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    
    raise ValueError("No OpenAI API key found in environment variables", os.getcwd())
    
# Init
DEFAULT_MODEL = 'gpt-3.5-turbo'
DEFAULT_MAX_TOKENS = 1200
DEFAULT_TEMPERATURE = 0.00000001
DEFAULT_TOP_P = 1.0
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0
DEFAULT_N_PAST_MESSAGES = 10
DEFAULT_SEED = None

GROQ_API_KEY = os.getenv('GROQ_API_KEY')


client_Groq = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
client_OpenAI = OpenAI(api_key = OPENAI_API_KEY)

def get_completion_Groq(
    messages: List[Dict[str, str]],
    model="llama3-8b-8192",
    max_tokens: Optional[int] = DEFAULT_MAX_TOKENS,
    temperature: Optional[float] = DEFAULT_TEMPERATURE,
    top_p: Optional[float] = DEFAULT_TOP_P,
    frequency_penalty: Optional[float] = DEFAULT_FREQUENCY_PENALTY,
    presence_penalty: Optional[float] = DEFAULT_PRESENCE_PENALTY,
    seed: Optional[int] = DEFAULT_SEED,
):  
    if model == "gpt-3.5-turbo":
        response = client_OpenAI.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,  # type: ignore
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            stream=False,
        )
        reply_content = response.choices[0].message.content
        if reply_content:
            return response

        raise ValueError("No reply content from API response!")
    
    else:
        
        response = client_Groq.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=600,
        top_p=top_p,
        stream=False,
    )

    reply_content = response.choices[0].message.content
    
    if reply_content:
        return response
    
    
    raise ValueError("No reply content from API response!")

# def get_completion_Groq(messages: List[Dict[str, str]], 
#                         model="llama3-8b-8192",
#                         temperature: Optional[float] = DEFAULT_TEMPERATURE,
#                         top_p: Optional[float] = DEFAULT_TOP_P,
#                     ):
#     response = client.chat.completions.create(
#         messages=messages,
#         model=model,
#         temperature=temperature,
#         max_tokens=600,
#         top_p=top_p,
#         stream=False,
#     )

#     reply_content = response.choices[0].message.content
    
#     if reply_content:
#         return response
    
    
#     raise ValueError("No reply content from API response!")