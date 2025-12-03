import ollama
result = ollama.chat(model="llama3.1", messages=[{"role": "user", "content": "hi"}])
print(result["message"]["content"])
