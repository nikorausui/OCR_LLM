import ollama
prompt="""
Output the results of the analysis of the browser screenshot under the following conditions.
Condition 1: Read all text information.
Condition 2: Output text and information readable from the image other than text.
"""
res = ollama.chat(
    model="llava-phi3",
    messages=[{
        'role': 'user',
        'content': prompt,
        'images': ['./c.png']
    }]
)

print(res['message']['content'])