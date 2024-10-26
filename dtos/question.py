from dataclasses import dataclass
from typing import List
import json

from dtos.item import Item


@dataclass
class Question:
    text: str
    items: List[Item]