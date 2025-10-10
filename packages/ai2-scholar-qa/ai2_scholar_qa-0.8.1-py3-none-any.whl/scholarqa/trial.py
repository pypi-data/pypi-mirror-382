from pydantic import BaseModel

from llms.constants import GPT_5_CHAT, GPT_4_1

OPENAI_API_KEY = "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"

import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


class TaskResult(BaseModel):
    """The outcome of running a Task to completion"""
    name: str
    id: str
    roll_no: int
    class_: str


from litellm import completion

res = completion(messages=[{"role": "user", "content": "Create a random student record"}], model=GPT_4_1,
                 response_format=TaskResult)
print(res)
