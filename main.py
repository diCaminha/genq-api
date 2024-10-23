import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify

load_dotenv()
api_key = os.getenv('API_KEY')
client = OpenAI(api_key=api_key)

app = Flask(__name__)

@app.route("/exams/generate", methods=["POST"])
def create_exam():
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a specialist on creating exams about specific topics."
            },
            {
                "role": "user",
                "content": """
                        Look at the content of the course of 
                        this url link: https://www.alura.com.br/curso-online-spring-boot-3-desenvolva-api-rest-java.
                        Then, generate an exam with 10 questions about the topics related to this course.
                        The output should be in JSON format following this structure:
                        {
                              "title": <string>,
                              "questions": [
                                {
                                  "id": <string>,
                                  "text": <string>,
                                  "items": [
                                    {
                                      "item": A,
                                      "text": <string>,
                                      "correct": true
                                    },
                                   {
                                      "item": B,
                                      "text": <string>,
                                      "correct": false
                                    },
                                    {
                                      "item": C,
                                      "text": <string>,
                                      "correct": false
                                    },
                                    {
                                      "item": D,
                                      "text": <string>,
                                      "correct": false
                                    }
                                  ]
                                }
                              ]
                        }
                        Dont write nothing beyond a json with this format. The response should be only a json.
                        """
            }
        ]
    )

    # Extract the content from the response properly
    response_content = completion.choices[0].message.content
    return jsonify(response_content)

if __name__ == "__main__":
    app.run()