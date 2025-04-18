import asyncio
import inspect

from app.definitions import EVALUATION_DATA_SET
from app.openai_llm import OpenAiLlm
from app.smol_rag import SmolRag
from app.utilities import get_json

rag = SmolRag()
llm = OpenAiLlm()


async def evaluate_accuracy(query, response, source):
    prompt = inspect.cleandoc(f"""
        Does the <response> accurately answer the <query> in relation to the <source>?
        
        Response parameters:
        You must answer with either "yes" or "no"
        There must be no other content in your response
        
        <query>
        {query}
        </query>
        
        <response>
        {response}
        </response>
        
        <source>
        {source}
        </source>
    """)

    tasks = [
        rag.rate_limited_get_completion(prompt, use_cache=False)
        for _ in range(3)
    ]
    results = await asyncio.gather(*tasks)

    responses = [
        1 if result == "yes" else 0
        for result in results
        if result in ("yes", "no")
    ]

    for result in results:
        if result not in ("yes", "no"):
            print("failed to respond with yes or no")

    return 1 if sum(responses) / len(responses) > 0.5 else 0


if __name__ == '__main__':
    async def main():

        data_set = get_json(EVALUATION_DATA_SET)

        query_tasks = [rag.mix_query(row["query"]) for row in data_set]
        responses = await asyncio.gather(*query_tasks)

        accuracy_tasks = [
            evaluate_accuracy(row["query"], response, row["pull_quote"])
            for row, response in zip(data_set, responses)
        ]
        results = await asyncio.gather(*accuracy_tasks)

        score = sum(results) / len(results)
        print(score)


    asyncio.run(main())
