document.addEventListener("DOMContentLoaded", () => {
  const examForm = document.getElementById("examForm");
  const loadingDiv = document.getElementById("loading");
  const formSection = document.querySelector('.form-section');
  const examSection = document.getElementById("examSection");
  const examInfoPanel = document.getElementById("examInfo");
  const examContainer = document.getElementById("examContainer");
  const submitExamBtn = document.getElementById("submitExam");
  const resetExamBtn = document.getElementById("resetExam");
  const resultDiv = document.getElementById("result");

  let examData = null;
  let formPayload = null; // Store form input data for use in the info panel

  // Ensure the loading overlay is hidden when the page first loads.
  loadingDiv.style.display = "none";

  // Form submit: generate exam via API
  examForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    // Hide any previous exam/results
    examSection.classList.add("hidden");
    resultDiv.classList.add("hidden");
    examContainer.innerHTML = "";
    examInfoPanel.innerHTML = "";
    
    // Show loading overlay
    loadingDiv.style.display = "flex";

    const formData = new FormData(examForm);
    formPayload = {
      url_course: formData.get("url_course"),
      number_questions: formData.get("number_questions"),
      level: formData.get("level"),
    };

    try {
      const response = await fetch("/exams/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formPayload),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || "Error generating exam");
      }

      examData = await response.json();

      // Hide the generation form
      formSection.classList.add("hidden");

      // Populate exam info panel with form details and exam title from backend
      examInfoPanel.innerHTML = `
        <p><strong>Course URL:</strong> <a href="${formPayload.url_course}" target="_blank">${formPayload.url_course}</a></p>
        <p><strong>Exam Title:</strong> ${examData.title}</p>
        <p><strong>Number of Questions:</strong> ${formPayload.number_questions}</p>
        <p><strong>Difficulty Level:</strong> ${formPayload.level}</p>
      `;

      // Render exam questions
      renderExam(examData);
      examSection.classList.remove("hidden");
    } catch (error) {
      alert("Failed to generate exam: " + error.message);
    } finally {
      // Hide loading overlay
      loadingDiv.style.display = "none";
    }
  });

  // Render exam questions
  function renderExam(data) {
    data.questions.forEach((question, qIndex) => {
      const card = document.createElement("div");
      card.classList.add("question-card");

      const questionTitle = document.createElement("h3");
      questionTitle.textContent = `Question ${qIndex + 1}: ${question.text}`;
      card.appendChild(questionTitle);

      // Options container
      question.items.forEach((option) => {
        const optionContainer = document.createElement("div");
        optionContainer.classList.add("option");

        const input = document.createElement("input");
        input.type = "radio";
        input.name = `question-${qIndex}`;
        input.value = option.item; // e.g., "A", "B", etc.

        const label = document.createElement("label");
        label.textContent = `${option.item}: ${option.text}`;
        optionContainer.appendChild(input);
        optionContainer.appendChild(label);

        card.appendChild(optionContainer);
      });

      examContainer.appendChild(card);
    });
  }

  // Evaluate exam answers
  submitExamBtn.addEventListener("click", () => {
    if (!examData) return;

    let score = 0;
    const total = examData.questions.length;

    // Iterate over each question card
    Array.from(examContainer.children).forEach((card, qIndex) => {
      const selected = card.querySelector(`input[name="question-${qIndex}"]:checked`);
      const question = examData.questions[qIndex];
      // Find the correct option (assuming only one is marked correct)
      const correctOption = question.items.find(opt => opt.correct);

      // Remove previous styling if any
      card.classList.remove("correct", "incorrect");

      if (selected) {
        if (selected.value === correctOption.item) {
          score++;
          card.classList.add("correct");
        } else {
          card.classList.add("incorrect");
          // Highlight the correct answer in the card.
          const options = card.querySelectorAll(".option");
          options.forEach(optDiv => {
            if (optDiv.textContent.startsWith(correctOption.item + ":")) {
              optDiv.style.fontWeight = "bold";
            }
          });
        }
      } else {
        // If no option is selected, mark as incorrect.
        card.classList.add("incorrect");
        const options = card.querySelectorAll(".option");
        options.forEach(optDiv => {
          if (optDiv.textContent.startsWith(correctOption.item + ":")) {
            optDiv.style.fontWeight = "bold";
          }
        });
      }
    });

    resultDiv.textContent = `Your score: ${score} / ${total}`;
    resultDiv.classList.remove("hidden");
  });

  // Reset exam: clears exam view and shows the generation form again
  resetExamBtn.addEventListener("click", () => {
    examData = null;
    examSection.classList.add("hidden");
    examContainer.innerHTML = "";
    examInfoPanel.innerHTML = "";
    resultDiv.textContent = "";
    examForm.reset();
    formSection.classList.remove("hidden");
  });
});
