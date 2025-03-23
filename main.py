import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

from dtos.exam import Exam
from utils.exam_util import format_exam_from_llm

from web_loader import CourseWebLoader
from web_scrap import extract_text_with_requests

load_dotenv()
api_key = os.getenv('API_KEY')
client = OpenAI(api_key=api_key)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/exams/generate", methods=["POST"])
def create_exam():
    req_data = request.get_json()
    
    url = req_data["url_course"]
    
    content = extract_text_with_requests(url)
    print(f"content: {content}")
    
    get_topics_completions = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a specialist on retrieve the topics content of a web scrapped content of a course on web."
            },
            {
                "role": "user",
                "content": f"""
                    Extract from the url's course content the topics addressed and covered by the course.
                    Course Content: {content}
                    Expected Result:
                        1. topic_one_here
                            1.1 possible subtopic here
                            1.2 possible subtopic here
                        2. topic_two_here
                            2.1 possible subtopic here
                            2.2 possible subtopic here
                        3. topic_three_here
                            3.1 possible subtopic here
                            3.2 possible subtopic here
                    
                    Observation: dont have a limit for number of topics. creates as much as you find in the course content.
                    If you cant find any topic covered by the course content, return: None
                """
            }
        ]
    )
    
    topics = get_topics_completions.choices[0].message.content
    print(f"topics here {topics}")
    
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
                Course Content: {topics}
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
