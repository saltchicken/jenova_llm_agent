import ollama

def query_ollama(model, prompt, system_message=None, verbose=False, host="localhost", port=11434):
    ollama.api_host = f"http://{host}:{port}"
    messages = [{"role": "user", "content": prompt}]
    if system_message:
        messages.insert(0,{"role": "system", "content": system_message})

    result = ollama.chat(
        model=model,  # Replace with the model you're using
        messages=messages
    )
    response = result['message']['content']
    if verbose: pretty_print_prompt(prompt, system_message, response)
    return response

def pretty_print_prompt(prompt, system_message, response):
    print("-------SYSTEM MESSAGE--------")
    print(system_message)
    print("----------PROMPT---------")
    print(prompt)
    print("----------RESPONSE---------")
    print(response)
    print("\n\n")
    print(f"Estimated tokens: {estimate_token_length(system_message) + estimate_token_length(prompt)}")

def estimate_token_length(text: str) -> int:
    """Estimate the number of tokens in a string."""
    avg_chars_per_token = 4
    return max(1, len(text) // avg_chars_per_token)
