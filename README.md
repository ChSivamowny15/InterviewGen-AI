# InterviewGen AI – AI-Based Mock Interview & Performance Analyzer

An AI-powered web application designed to help students and job seekers prepare for technical, HR, and behavioral interviews. InterviewGen AI combines **Retrieval-Augmented Generation (RAG), Large Language Model (LLM) integration, resume analysis, voice-based interaction, and performance analytics** to provide an interactive interview preparation experience.

## 🌐 Live Demo

**Try InterviewGen AI here:**

🔗 [InterviewGen AI – Live Website](https://interviewgen-ai-rtnk.onrender.com)

---

## 🌟 Key Features

### 1. Interactive Mock Interview System

- **Multiple Job Roles:** Python Developer, Software Engineer, AI/ML Engineer, Data Scientist, Web Developer, and Java Developer.
- **Interview Types:** Technical, HR, Behavioral, and Mixed interviews.
- **Difficulty Levels:** Beginner, Intermediate, and Advanced.
- **Question Bank:** Role-based questions selected according to interview type and difficulty.
- **Time Management:** Provides a time limit for answering interview questions.
- **Voice-Based Interaction:** Supports voice-based question readout and spoken answers.
- **Advanced Interview Modes:** Supports live video and text-based interview interaction.

### 2. Retrieval-Augmented Generation (RAG)

InterviewGen AI incorporates RAG-based context retrieval in selected AI workflows to improve the relevance of interview assistance.

**Role of RAG in InterviewGen AI:**

- **Context Retrieval:** Retrieves relevant information from available candidate and resume-related context.
- **Resume-Based Context:** Uses relevant skills, technical knowledge, and project information from candidate resume content where supported by the implemented workflow.
- **Context-Aware Assistance:** Supplies retrieved information as additional context to the LLM.
- **Personalised Interview Support:** Helps the AI workflow provide responses and interview assistance relevant to the candidate's background.
- **Reduced Dependence on Generic Responses:** Retrieved context helps make AI-generated responses more relevant to the available candidate information.

**RAG Workflow:**

1. Candidate information or resume-related content is made available to the application.
2. Relevant information is retrieved based on the current AI task.
3. The retrieved context is supplied to the LLM along with the user's input.
4. The LLM generates a response using the available context.
5. The application presents the generated interview assistance or feedback.

**Why RAG is used:**

RAG connects relevant external or candidate-specific information with the LLM at response-generation time. This helps InterviewGen AI provide more context-aware and personalised interview assistance instead of relying only on generic model knowledge.

### 3. Large Language Model (LLM) Integration

InterviewGen AI uses an LLM through the Groq API.

- **LLM:** GPT-OSS-120B.
- **API Integration:** Groq API.
- **AI Answer Evaluation:** Analyses candidate responses.
- **Context-Aware Generation:** Uses retrieved context in the RAG-supported workflows.
- **AI Feedback:** Generates suggestions for improving interview answers.
- **Natural Language Processing:** Processes candidate responses and generates understandable feedback.

### 4. AI-Based Answer Evaluation

- **Automated Evaluation:** Analyses candidate answers based on relevance, technical accuracy, completeness, and communication.
- **Performance Scoring:** Provides scores for different evaluation criteria.
- **Strength Identification:** Highlights strong points in candidate answers.
- **Weakness Detection:** Identifies areas that need improvement.
- **AI Feedback:** Provides suggestions to improve interview performance.
- **LLM-Based Evaluation:** Uses the configured Groq LLM integration for AI-based evaluation.

### 5. Resume Analysis

- Supports PDF and DOCX resume uploads.
- Extracts text from uploaded resumes.
- Analyses resume content and relevant skills.
- Identifies candidate strengths and improvement areas.
- Provides resume-related interview preparation support.
- Makes relevant resume information available to supported RAG-based workflows.

### 6. Voice and Video Interview Features

- **Speech Recognition:** Converts spoken answers into text.
- **Text-to-Speech:** Reads interview questions aloud.
- **Webcam Integration:** Supports live video interview interaction.
- **Face Detection:** Uses OpenCV for webcam-based face detection.
- **Voice Practice:** Helps candidates practise spoken interview answers.

### 7. Performance Analyzer Dashboard

- Displays interview scores and evaluation results.
- Tracks previous interview performance.
- Provides performance analytics and progress information.
- Highlights strengths and weaknesses.
- Offers personalised improvement suggestions.
- Displays interview history and performance reports.

### 8. AI Chatbot and Voice Practice

- Provides an AI chatbot for interview preparation.
- Supports technical and HR interview-related questions.
- Helps candidates understand programming concepts.
- Provides additional interview practice.
- Uses the configured LLM integration for AI-generated assistance.
- Supports context retrieval in the RAG-enabled workflows.

### 9. Certificate Generation and Rewards

- Generates interview performance certificates.
- Provides reward points for interview practice.
- Offers improvement plans based on performance.
- Helps candidates track their interview preparation progress.

---

## 🧠 RAG + LLM Integration Architecture

InterviewGen AI combines context retrieval and LLM generation in its supported AI workflows.

**RAG and LLM workflow:**

```text
       Candidate / Resume Information
                    |
                    v
          Relevant Context Retrieval
                    |
                    v
          Retrieved Context
                    |
                    v
       Candidate Question / User Input
                    |
                    v
          Context + User Input
                    |
                    v
             Groq API
                    |
                    v
          GPT-OSS-120B (LLM)
                    |
                    v
       Context-Aware AI Response
                    |
                    v
       Interview Assistance / Feedback
```

**RAG and LLM – Difference:**

| Component | Responsibility |
|---|---|
| RAG | Retrieves relevant information and supplies context |
| LLM | Understands the input and generates responses |
| Groq API | Provides access to the configured language model |
| GPT-OSS-120B | Generates AI responses and feedback |
| Flask | Connects the frontend, backend, retrieval workflow, and AI services |

RAG and LLM serve different purposes: RAG provides relevant information, while the LLM uses the supplied context to generate natural-language responses.

---

## 🛠️ Technology Stack

### Frontend
- **HTML5** – Website structure.
- **CSS3** – Styling and responsive design.
- **JavaScript** – Interactive functionality and browser-based features.

### Backend
- **Python** – Main backend programming language.
- **Flask** – Web application framework.
- **Jinja2** – Dynamic HTML templating.

### Database
- **SQLite** – Stores user information, interview history, scores, and related records.

### AI, RAG and Machine Learning Technologies
- **Retrieval-Augmented Generation (RAG)** – Retrieves relevant candidate or resume-related context for supported AI workflows.
- **Large Language Models (LLMs)** – Generates natural-language responses and AI feedback.
- **Groq API** – Connects the application with the configured language model.
- **GPT-OSS-120B** – LLM used for AI-based answer evaluation and feedback.
- **Natural Language Processing (NLP)** – Supports text processing and response analysis.
- **OpenCV** – Supports webcam-based face detection.
- **Web Speech API** – Supports speech recognition and text-to-speech functionality.

### Supporting Libraries
- **PyPDF** – Extracts text from PDF resumes.
- **python-docx** – Extracts text from DOCX resumes.
- **ReportLab** – Generates PDF certificates.
- **NumPy** – Supports numerical operations.
- **python-dotenv** – Manages environment variables.

### Development and Deployment Tools
- **Visual Studio Code** – Development environment.
- **Git** – Version control.
- **GitHub** – Source code repository.
- **Gunicorn** – WSGI application server.
- **Render** – Cloud deployment and hosting platform.

---

## 🏗️ System Architecture

1. **User Interface:** Candidates interact with the application through the frontend.
2. **User Authentication:** Flask manages registration, login, sessions, and account-related operations.
3. **Interview Configuration:** Candidates select their job role, interview type, and difficulty level.
4. **Question Selection:** The system selects relevant questions from the configured question bank.
5. **Answer Submission:** Candidates submit answers through text or voice interaction.
6. **Context Retrieval:** RAG-supported workflows retrieve relevant candidate or resume-related information.
7. **AI Processing:** The retrieved context and user input are supplied to the configured LLM workflow.
8. **AI Evaluation:** Groq API with GPT-OSS-120B generates evaluation results and feedback.
9. **Performance Analysis:** The system presents scores, strengths, weaknesses, and improvement suggestions.
10. **Report Generation:** Interview results are stored and presented through the dashboard.

---

## 📂 Project Structure

```text
InterviewGen-AI/
│
├── app.py
├── evaluator.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── ai_modules/
│   └── answer_evaluator.py
│
├── templates/
│   ├── welcome.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── settings.html
│   ├── interview_setup.html
│   ├── resume_analysis.html
│   ├── chatbot.html
│   ├── voice_practice.html
│   ├── analytics.html
│   ├── certificates.html
│   └── other HTML templates used by the application
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── other JavaScript files
│   │
│   ├── images/
│   │
│   └── other static files
│
└── instance/
    └── interviewgen.db
```

*Note: This is an illustrative project structure. Update the file and folder names to match the actual files in your repository. Do not create empty folders or files just to match this diagram.*

---

## 🚀 How to Run the Project Locally

### Prerequisites

- Python 3.10 or later, compatible with the installed dependencies.
- Visual Studio Code.
- Git.
- Groq API key.

### Step 1: Clone the Repository

```bash
git clone https://github.com/ChSivamowny15/InterviewGen-AI.git
```

### Step 2: Navigate to the Project Directory

```bash
cd InterviewGen-AI
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Configure the API Key

Create a `.env` file in the project root directory and add:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace `your_groq_api_key` with your actual Groq API key.

**Important:** Never upload your `.env` file or API key to GitHub.

### Step 7: Run the Application

```bash
python app.py
```

### Step 8: Open the Website

Visit:

http://127.0.0.1:5000

---

## ☁️ Deployment

InterviewGen AI is deployed on Render using GitHub integration.

### Deployment Tools

| Tool | Purpose |
|---|---|
| GitHub | Source code management and repository integration |
| Render | Cloud hosting and deployment |
| Gunicorn | Runs the Flask application in production |

### Deployment Configuration

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
gunicorn app:app
```

**Live Application:**

https://interviewgen-ai-rtnk.onrender.com

---

## 🔮 Future Enhancements

- **Advanced RAG Pipeline:** Expand context retrieval to support more comprehensive resume-based and knowledge-base-based retrieval.
- **Improved Resume Intelligence:** Improve document processing, skill extraction, and personalised question generation.
- **Advanced Embedding and Vector Search:** Introduce or extend semantic search and vector-based retrieval where required.
- **Adaptive Interviews:** Dynamically adjust question difficulty based on candidate performance.
- **Detailed Speech Analytics:** Enhance speaking pace, filler-word detection, and communication analysis.
- **Advanced Performance Analytics:** Provide deeper insights into candidate progress and interview readiness.
- **Expanded Personalisation:** Improve the use of candidate-specific information across interview workflows.

---

## 🎯 Project Objective

The main objective of InterviewGen AI is to provide an intelligent and interactive interview preparation platform that helps candidates practise interviews, evaluate their answers, identify weaknesses, and continuously improve their technical knowledge and communication skills.

By combining RAG-supported context retrieval with LLM-based response generation, the application aims to make interview preparation more relevant, personalised, and effective.

---

## 👩‍💻 Developed By

**InterviewGen AI – AI-Based Mock Interview & Performance Analyzer**

Developed as an academic project by the Computer Science and Engineering – Artificial Intelligence and Machine Learning team.
