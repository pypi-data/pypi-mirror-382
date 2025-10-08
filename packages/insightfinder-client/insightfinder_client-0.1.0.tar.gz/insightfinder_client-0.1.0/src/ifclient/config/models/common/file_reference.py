from pydantic import BaseModel 
from typing import List

class FileReference(BaseModel):
    files: List[str]

