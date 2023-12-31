# Make calls to language models.
import replicate
import openai
import anthropic
import dotenv
import asyncio
import os
import shelve
import functools
from tenacity import retry, stop_after_attempt
_env_dir = os.path.expanduser('~/.env')if \
    os.path.isfile(os.path.expanduser('~/.env')) else None
dotenv.load_dotenv(_env_dir)
_cache_file = "model_cache"

_live_requests = {}


def log(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        global _live_requests
        _live_requests[func.__name__] = _live_requests.get(
            func.__name__, 0) + 1
        print(_live_requests)
        result = await func(*args, **kwargs)
        _live_requests[func.__name__] -= 1
        print(_live_requests)
        return result
    return wrapper


def limit_concurrency(max_concurrent_tasks):
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)
        return wrapper
    return decorator


@limit_concurrency(10)
@retry(stop=stop_after_attempt(3))
@log
async def replicate_request(input, model='mistral'):
    model_urls = {
        'mistral-7b': 'mistralai/mistral-7b-instruct-v0.1:83b6a56e7c828e667f21fd596c338fd4f0039b46bcfa18d973e8e70e455fda70'
    }
    output = await replicate.async_run(
        model_urls[model],
        input={"prompt": input},
    )
    result = ''.join(output)
    return result


@limit_concurrency(10)
@retry(stop=stop_after_attempt(3))
@log
async def openai_request(input, model="gpt-3.5-turbo"):
    completion = await openai.ChatCompletion.acreate(
        model=model,
        messages=[
            {"role": "user", "content": input},
        ]
    )
    result = completion.choices[0].message.content
    return result


@limit_concurrency(2)
@retry(stop=stop_after_attempt(3))
@log
async def anthropic_request(input, model="claude-2"):
    client = anthropic.AsyncAnthropic()
    completion = await client.completions.create(
        model=model,
        max_tokens_to_sample=50,
        prompt=f"{anthropic.HUMAN_PROMPT} {input}{anthropic.AI_PROMPT}",
    )

    return completion.completion


async def complete(inputs, models=None, use_cache=False):
    if models is None:
        models = ["openai/gpt-3.5-turbo"]  # Default model if none specified

    # Ensure inputs is a list, even if a single string is provided
    if not isinstance(inputs, list):
        inputs = [inputs]
    try:
        cache = shelve.open(_cache_file) if use_cache else None

        tasks = []
        for input in inputs:
            for model in models:
                cache_key = f"{model}:{input}"
                if use_cache and cache_key in cache:
                    # append a task that returns the cached value
                    tasks.append(asyncio.create_task(
                        asyncio.sleep(0, cache[cache_key])))
                    continue

                provider, model_name = model.split('/', 1)

                if provider == 'replicate':
                    task = replicate_request(input, model=model_name)
                elif provider == 'openai':
                    task = openai_request(input, model=model_name)
                elif provider == 'anthropic':
                    task = anthropic_request(input, model=model_name)
                else:
                    raise ValueError(f"Unknown provider: {provider}")

                tasks.append(task)

        responses = await asyncio.gather(*tasks)
        # Group responses by original input order, so that we have
        # [{"prompt": "What is 2+2?", "responses": {"model1": "4", "model2": "5"}}]
        ordered_responses = []
        for i, input in enumerate(inputs):
            ordered_responses.append({
                "prompt": input,
                "responses": {}
            })
            for j, model in enumerate(models):
                ordered_responses[i]["responses"][model] = responses[i *
                                                                     len(models) + j]
                if use_cache:
                    cache[f"{model}:{input}"] = responses[i*len(models) + j]
    finally:
        if use_cache:
            cache.close()
    return ordered_responses


def test():
    import json
    test_prompts = ["what model are you?",
                    "what is 2+2?", "what is the 9th digit of pi?"]
    models = [
        'openai/gpt-3.5-turbo',
        'replicate/mistral-7b',
        'anthropic/claude-2'
    ]
    # Call the complete function with the test prompts
    responses = asyncio.run(
        complete(test_prompts, models=models, use_cache=False))

    # Print the responses
    print(json.dumps(responses, indent=4))


if __name__ == "__main__":
    test()
