# 🎙️ Voice-Based Question Answering System

A Flask web app that combines **speech and NLP**. You ask a question by voice, the app converts speech to text, finds the best answer from a knowledge base using NLP matching, displays it and reads it aloud.

## Features

- 🎙️ Voice input with the browser's Speech Recognition
- 📝 Speech-to-text with live transcript
- 💬 Question input box and conversation display
- 🧠 NLP-based question processing
- 🔎 Answer retrieval with topic and confidence
- 🔊 Text-to-speech reads the answer aloud (with stop and replay)
- 💡 Example questions and suggestions when no answer is found
- 🧹 Clear conversation
- 📱 Responsive layout with light and dark mode

## How it works

```
🎙️ User speaks
       ↓
Speech Recognition (Web Speech API)
       ↓
📝 Speech → Text
       ↓
NLP / Question Processing
(tokenization, stop-word removal, stemming)
       ↓
🔎 Find Answer (TF-IDF + cosine similarity)
       ↓
💬 Display Answer
       ↓
🔊 Text → Speech (Speech Synthesis)
       ↓
User hears the answer
```

1. The browser converts speech to text using the Web Speech API.
2. The question is sent to the Flask server (`POST /ask`).
3. `qa_engine.py` lowercases and tokenizes the question, expands abbreviations (NLP to natural language processing), removes stop and question words, and stems the words with the Porter stemmer.
4. The question is compared with every entry in the knowledge base using **TF-IDF vectors and cosine similarity**, plus a keyword coverage score.
5. The best match above a threshold is returned with its topic and confidence. Otherwise the app suggests questions it can answer.
6. The browser displays the answer and reads it aloud with Speech Synthesis.

## Example

**User speaks:** "What is artificial intelligence?"

**Answer:** Artificial Intelligence (AI) is the ability of machines or computer systems to perform tasks that normally require human intelligence, such as learning, reasoning, and decision-making.

## Questions it can answer

The knowledge base covers 40 topics: AI, machine learning, deep learning, NLP, neural networks, cloud computing, Python, Flask, APIs, databases, SQL, HTML, CSS, JavaScript, Git, GitHub, operating systems, networks, CDN, data structures, OOP, IoT, cybersecurity, blockchain, big data, TF-IDF, tokenization, speech recognition and more.

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| NLP | NLTK (stemming), TF-IDF, cosine similarity |
| Speech | Web Speech API (SpeechRecognition and SpeechSynthesis) |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render, Gunicorn |

## Project structure

```
Voice-QA-System/
│
├── app.py                 # Flask routes
├── qa_engine.py           # knowledge base and NLP matching
├── requirements.txt
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

## Run locally

```bash
git clone https://github.com/danyaramesh1647-lang/voice-qa-system.git
cd voice-qa-system
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5050 in **Chrome or Edge** and allow microphone access.

## Add your own questions

Open `qa_engine.py` and add a new entry to the `KNOWLEDGE` list:

```python
("Topic name", "keywords and aliases", "The answer the assistant will say."),
```

Voice input needs HTTPS, which Render provides automatically.

## Limitations

- Voice input works in Chrome and Edge. Firefox and some other browsers do not support speech recognition, so typing is available as a fallback.
- Chrome sends the audio to its own speech service, so voice input needs an internet connection.
- Answers come from a predefined knowledge base, not a generative AI model, so it only answers questions on the topics it contains.
- English only.

## Future improvements

- Larger knowledge base or answers retrieved from documents
- Extractive QA with a transformer model
- Multi-language voice support (Tamil and Hindi)

## Author

**Danya R**
GitHub: [danyaramesh1647-lang](https://github.com/danyaramesh1647-lang)