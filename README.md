# InterviewGen AI – AI-Based Mock Interview & Performance Analyzer

An interactive, responsive web application for simulating technical and behavioral job interviews with real-time AI evaluation, speech analysis, and performance analytics.

---

## 🌟 Key Features

1. **Interactive Mock Interview Studio**
   - **Multi-Track Support:** Frontend Engineering, Backend & Distributed Systems, Machine Learning & Data Science, System Design, and Behavioral (STAR method).
   - **Seniority Levels:** Adjust depth for Junior, Mid-Level, and Senior / Staff candidates.
   - **Voice Readout (TTS):** The AI interviewer audibly reads interview questions via the browser Web Speech API.
   - **Voice Dictation (STT):** Dictate your responses live via microphone or type them directly into the response editor.
   - **Live Stopwatch & Word Counter:** Practice under realistic time constraints.

2. **Automated AI Diagnostic Engine & Scorecard**
   - **4-Pillar Evaluation:**
     - **Technical Accuracy & Depth (35%):** Keyword coverage, architectural concepts, edge-case analysis.
     - **Problem Structuring & Logic (25%):** Coherence, STAR methodology (Situation, Task, Action, Result).
     - **Communication & Articulation (25%):** Fluency, signposting, conciseness.
     - **Confidence & Sentiment (15%):** Tone stability, composure.
   - **Strengths & Growth Areas:** Pinpoints exact weak spots.
   - **Exemplar Answers:** Generates 10/10 model answers for each question.

3. **Performance Analyzer Dashboard**
   - **Competency Radar Chart (Chart.js):** Compares candidate mastery across 6 dimensions against the FAANG 85th percentile benchmark.
   - **Delivery & Fluency Biometrics:** Measures speaking cadence (Words Per Minute), filler word frequency ("like", "basically", "um"), and tone sentiment.
   - **Progression Trajectory:** Tracks candidate endurance and scores across rounds Q1 through Q5.

4. **Modern UI/UX**
   - Sleek dark theme with glassmorphic cards, glowing ambient gradients, responsive grid layouts, and Lucide vector icons.

---

## 🚀 How to Run the Website

You can run this website instantly without any heavy installations or build steps!

### Option 1: Direct File Open (Fastest)
Simply double-click [`index.html`](file:///c:/Users/venub/OneDrive/Desktop/InterviewGen-AI/index.html) or open it directly in Google Chrome, Microsoft Edge, or any modern web browser.

### Option 2: Local HTTP Server (Recommended for Web Speech API)
In PowerShell or your terminal, navigate to the project directory and run:

```powershell
cd c:\Users\venub\OneDrive\Desktop\InterviewGen-AI
python -m http.server 3000
```

Then visit: [http://localhost:3000](http://localhost:3000)

*(Or using Node.js: `npx serve .`)*

---

## 📂 Project Structure

```
InterviewGen-AI/
├── index.html          # Main application page with Hero, Studio, Analytics & Rubric
├── css/
│   └── styles.css      # Custom animations, glassmorphism, scrollbars, and waveforms
├── js/
│   ├── app.js          # Studio interaction, Speech API, heuristic evaluator & Chart.js
│   └── questions.js    # Comprehensive question bank, keywords, and model answers
└── README.md           # Documentation and setup guide
```

---

## 📊 Evaluation Rubric

| Dimension | Weight | Description |
|---|---|---|
| **Technical Depth** | 35% | Accuracy of concepts, algorithmic complexity, trade-off understanding |
| **Structuring & STAR** | 25% | Logical breakdown: Situation, Task, Action, Result |
| **Communication Clarity** | 25% | Economy of language, minimal filler words, clear signposting |
| **Tone & Confidence** | 15% | Composure, pacing (target 130–150 WPM), objective language |
