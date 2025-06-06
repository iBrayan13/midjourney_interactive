from typing_extensions import List

from pydantic import BaseModel

class ImgPrompt(BaseModel):
    prompt_num: int
    prompt: str

class ImagesPrompts(BaseModel):
    directory: str
    img_prompts: List[ImgPrompt]