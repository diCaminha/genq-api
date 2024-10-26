from dataclasses import dataclass, asdict
from typing import List, Dict

from dtos.item import Item
from dtos.question import Question


@dataclass
class Exam:
    title: str
    questions: List[Question]

    @classmethod
    def from_json(cls, data: Dict):
        questions = [
            Question(
                text=q['text'],
                items=[Item(**item) for item in q['items']]
            ) for q in data['questions']
        ]
        return cls(title=data['title'], questions=questions)

    def to_dict(self):
        return asdict(self)
