from datasets import load_dataset
import json



ds = load_dataset("heliosbrahma/mental_health_chatbot_dataset")


output_file = "mental_health.jsonl"


def process_conversation(text):

    human, assistant = text.split('<ASSISTANT>:')
    human = human.replace('<HUMAN>:', '').strip()
    assistant = assistant.strip()
    return {
        "human": human,
        "assistant": assistant
    }


with open(output_file, "w", encoding="utf-8") as f:
    for example in ds['train']:  
        processed = process_conversation(example['text'])  
        json_line = json.dumps(processed, ensure_ascii=False) 
        f.write(json_line + "\n")  

print(f"Dataset saved to {output_file}")