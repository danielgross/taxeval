import asyncio
import json
import re
import llm


def parse_input(input_str):
    lines = input_str.strip().split("\n")
    parsed_data = []
    for line in lines:
        if not line.strip():
            continue

        parts = line.split(';')
        parts = [p.strip().strip('"') for p in parts]
        entry = {
            "category": parts[0],
            "description": parts[1],
            "options": parts[2:6],
            "correct_answer": int(parts[6]),
            "reference": parts[7],
            "tag": parts[8]
        }
        parsed_data.append(entry)

    return parsed_data


async def main():
    with open("far.txt", "r") as f:
        input_str = f.read()

    parsed_data = parse_input(input_str)
    tasks = []
    library = {}
    for question in parsed_data:
        prompt = "Below is a multipart question:\n" + question["description"]
        for i, option in enumerate(question["options"]):
            prompt += f"\n{i+1}. {option}"
        prompt += "\n\nAnswer the question by entering the number of the correct option. Response with a single number and nothing else."
        tasks.append(prompt)
        library[prompt] = question

    responses = await llm.complete(tasks, models=[
        'replicate/mistral-7b',
        'openai/gpt-3.5-turbo-1106',
        'openai/gpt-4-1106-preview',
        'anthropic/claude-2'
    ], use_cache=True)
    # Process responses
    output = []
    for r in responses:
        output.append({
            "prompt": r["prompt"],
            "full": r["responses"],
            "simplified": {model: re.search(r'\d', r["responses"][model][:100]).group() for model in r["responses"]},
            "source_question": library[r["prompt"]]
        })

    with open("output.json", "w") as f:
        print(json.dumps(output, indent=4))
        f.write(json.dumps(output, indent=4))
# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
