import os
import random
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


model= LiteLlm(
  model= "gpt-4o-mini",
  api_key= os.getenv("OPENAI_KEY")
)

def get_dad_joke():
  """
  Get a random dad joke.
  """
  jokes= [
    "Why did the chicken cross the road? To get to the other side!",
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "Why did the bicycle fall over? Because it was two-tired!",
  ]
  return random.choice(jokes)


root_agent= Agent(
  name= "litellm_agent",
  model= model,
  description= "Dad Joke Agent",
  instruction= """
  You are a helpful assistant that can tell dad jokes.
  Only use the tool 'get_dad_joke' to tell dad jokes.
  """,
  tools= [ get_dad_joke ],

)