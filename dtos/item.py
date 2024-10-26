from dataclasses import dataclass


@dataclass
class Item:
    item: str
    text: str
    correct: bool
