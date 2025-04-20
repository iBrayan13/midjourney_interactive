from typing import Optional

from pydantic import BaseModel

from src.models.prompts import ImagesPrompts

class InteractiveInput(BaseModel):
    prompts_data: ImagesPrompts
    encrypted_cookies: Optional[str] = None
    key: Optional[str] = None