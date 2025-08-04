# 🎓 CareerScholar

**CareerScholar** is an intelligent guidance platform that helps students—especially those transitioning from 12th grade to B.Tech—navigate their future with clarity.  
It provides **career suggestions**, **personalized learning paths**, and **AI-driven scholarship recommendations**, all tailored to each student's interests, skills, and background.

---

## 🚀 Features

### 🧭 Career Guidance System

- 🌳 **AI-Powered Career Prediction**  
  Uses a Decision Tree ML model trained on a structured dataset containing:  
  `Interested Subjects`, `Skills`, `Current Stream`, `Job Market Demand`, and more.

- 🧠 **NLP-Based Skill Gap Analysis**  
  Analyses a student's current skillset and compares it with their desired domain using NLP, identifying gaps and recommending personalized learning strategies.

- 📘 **Bridging Courses for Biology Stream Students**  
  Tailored beginner courses and transition content for students coming from a biology background into technical streams like Computer Science, AI, or Engineering.

---

### 🎯 Scholarship Recommendation System

- 🧠 **NLP-Based Eligibility Matching**  
  Parses both student data and scholarship descriptions to intelligently match opportunities using natural language understanding.

- 🔄 **Real-Time Data Updates via Web Scraping**  
  A weekly automated web scraping script keeps the scholarship database up-to-date with the latest government and private listings.

- 🔗 **Direct Application Access**  
  Provides filtered results with application deadlines, criteria, and links for easy access.

---

### 🔍 Personalized Learning Suggestions

- 🎯 Career-specific learning paths curated using skill-gap data.
- 🧩 Course and mini project recommendations based on chosen stream.
- ⚙️ Groq (LLaMA 3) powered suggestions for ultra-fast, contextual advice.

---

## 🛠️ Tech Stack

| Module              | Technology Used                     |
|---------------------|-------------------------------------|
| Backend             | Flask / Django                      |
| Machine Learning    | Decision Tree, NLP (spaCy, TF-IDF)  |
| Voice Interaction   | Whisper / Vosk, pyttsx3             |
| Database            | Supabase / CSV                      |
| API Integration     | Groq (LLaMA 3), Web Scraping (BS4)  |
| Frontend            | HTML, Tailwind CSS, JavaScript      |

---

## 📁 Project Structure

CareerScholar/
├── frontend/
│ └── index.html, career.html, scholarship.html, style.css
├── backend/
│ └── app.py, decision_tree.py, nlp_matcher.py, scraper.py
├── models/
│ └── decision_tree_model.pkl, tfidf_vectorizer.pkl
├── data/
│ └── scholarships.csv, student_profiles.json
└── README.md


## 💡 Use Cases

- A student unsure about their ideal engineering field
- A biology stream student looking to switch to tech
- A B.Tech aspirant seeking scholarships based on eligibility
- Anyone needing personalized learning and project guidance


## 👥 Team Members

This project was developed by the following team:

- 🧑‍💻 [@sreenandha](https://github.com/sreenandharamesh)
- 🧪 [@Anupa Jose](https://github.com/anupa00) 

  
> Special thanks to our mentors and reviewers for their guidance and feedback.



