import os
from openai import OpenAI
from google import genai
from google.genai import types
import anthropic
from mistralai import Mistral
import concurrent.futures

ITERATIONS = 1000
MAX_WORKERS = 5
BASE_OUTPUT_DIR = "./responses"
SCALES = [
    "psycho-short",
    "psycho-long",
    "political-scale"
]

def send_gpt_query(prompt, model):
    client = OpenAI(api_key= os.getenv("OPENAI_API_KEY"))
    if model == "o4-mini" or model == "o3-mini":
        response = client.chat.completions.create(        
                model=model,
                messages=[{"role": "user", "content": prompt}],
                reasoning_effort="low",
            )
    else:   
        response = client.chat.completions.create(        
            model=model,
            messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_deepseek_query(prompt, model):    
    client = OpenAI(api_key= os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")
    response = client.chat.completions.create(
        model=model,
        messages=[            
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content

def send_grok_query(prompt, model):    
    client = OpenAI(api_key= os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
    if model == "grok-3-mini":
        response = client.chat.completions.create(        
                model=model,
                messages=[{"role": "user", "content": prompt}],
                reasoning_effort="low",
            )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=[            
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
    return response.choices[0].message.content

def send_gemini_query(prompt, model_id):
    client = genai.Client()
    if model_id == "gemini-2.5-flash-preview-05-20":
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
    else:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
    return response.text

def send_anthropic_query(prompt, model):
    client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))    
    response = client.messages.create(
        model=model,        
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        thinking={"type":"disabled"},
    )
    
    return response.content[0].text

def send_mistral_query(prompt, model):
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Configuration
MODEL_HANDLERS = [    
    {"handler":send_gemini_query, "models": [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash"
    ]},
    {"handler":send_deepseek_query, "models": [
        "deepseek-reasoner",
        "deepseek-chat"
    ]},
    {"handler":send_gpt_query, "models": [
        "gpt-4.1-nano",
        "gpt-4.1-mini",
        "gpt-4.1",
        "o4-mini"
    ]},
    {"handler":send_gemini_query, "models": [
        "gemini-2.5-pro-preview-03-25",
        # "gemini-2.5-flash-preview-05-20"
    ]},
    {"handler":send_grok_query, "models": [
        "grok-3-mini"
    ]},
    {"handler":send_anthropic_query, "models": [
        "claude-sonnet-4-20250514"
    ]},
    {"handler":send_mistral_query, "models": [
        "mistral-medium-2505",        
        "mistral-small-2503"
    ]
    }

]

# Ensure the output directory exists
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)


for scale_name in SCALES:

    scale_file_path = os.path.join("./scales", f"{scale_name}.txt")
    with open(scale_file_path, "r", encoding="utf-8") as file:
        scale = file.read()

    # Use the scale as the prompt    
    print(f"Using prompt from {scale_name}...")

    # Create a directory for each scale
    scale_dir = os.path.join(BASE_OUTPUT_DIR, scale_name)
    os.makedirs(scale_dir, exist_ok=True)


    # Iterate over each model handler
    for model_handler in MODEL_HANDLERS:
        handler = model_handler["handler"]
        models = model_handler["models"]

        # Iterate over each model
        for model in models:
            print(f"Using model {model}...")
            # Create a directory for each model
            model_dir = os.path.join(scale_dir, model)
            os.makedirs(model_dir, exist_ok=True)

            # Update the output directory to the new model directory
            output_dir = model_dir

            def send_and_save(i):
                file_name = f"{output_dir}/{scale_name}_{model}_response_{i}.txt"
                if os.path.exists(file_name):
                    print(f"File {file_name} already exists. Skipping...")
                    return
                print(f"Sending query {i}...")
                response = handler(scale, model)
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(response)
                print(f"Response {i} saved to {file_name}")

            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [
                    executor.submit(send_and_save, i)
                    for i in range(1, ITERATIONS + 1)
                ]
                # Optionally, wait for all to complete and handle exceptions
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as exc:
                        print(f"Generated an exception: {exc}")

            print("All queries completed.")