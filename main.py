import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

from dtos.exam import Exam
from utils.exam_util import format_exam_from_llm

load_dotenv()
api_key = os.getenv('API_KEY')
client = OpenAI(api_key=api_key)

app = Flask(__name__)

# Route to serve the frontend
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/exams/generate", methods=["POST"])
def create_exam():
    req_data = request.get_json()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a specialist on creating exams about specific topics."
            },
            {
                "role": "user",
                "content": f"""
                Analyze the course available at the following link: {req_data["url_course"]}. 
                Based on the course content, generate a questionnaire in JSON format 
                containing {req_data["number_questions"]} questions of difficulty {req_data["level"]}. The JSON should have the 
                following structure: 
                {{
                    "title": "<title of the exam>",
                    "questions": [
                        {{
                            "text": "<the question text>",
                            "items": [
                                {{ "item": "A", "text": "<item description>", "correct": <true or false> }},
                                {{ "item": "B", "text": "<item description>", "correct": <true or false> }},
                                {{ "item": "C", "text": "<item description>", "correct": <true or false> }},
                                {{ "item": "D", "text": "<item description>", "correct": <true or false> }}
                            ]
                        }}
                    ]
                }}
                Return ONLY this JSON format with {req_data["number_questions"]} questions."""
            }
        ]
    )

    response_content = format_exam_from_llm(completion.choices[0].message.content)

    try:
        response_dict = json.loads(response_content.strip())
        exam = Exam.from_json(response_dict)
        return jsonify(exam.to_dict())

    except json.JSONDecodeError as e:
        return jsonify({"error": "Invalid data format by LLM", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()
