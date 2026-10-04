"""Question answering engine: NLP matching against a predefined knowledge base.
Pipeline: lowercase -> tokenize -> expand abbreviations -> remove stop and
question words -> Porter stemming -> TF-IDF vectors -> cosine similarity."""
import math
import re
from collections import Counter

from nltk.stem import PorterStemmer

stem = PorterStemmer().stem

# (title, extra keywords / aliases, answer)
KNOWLEDGE = [
    ("Artificial Intelligence", "ai artificial intelligence smart machines",
     "Artificial Intelligence (AI) is the ability of machines or computer systems to perform tasks that normally require human intelligence, such as learning, reasoning, and decision-making."),
    ("Machine Learning", "ml machine learning learn from data",
     "Machine learning is a branch of AI where computers learn patterns from data and improve their performance on a task without being explicitly programmed for every rule."),
    ("Deep Learning", "deep learning dl",
     "Deep learning is a subset of machine learning that uses neural networks with many layers to learn complex patterns from large amounts of data, such as images, speech, and text."),
    ("Natural Language Processing", "nlp natural language processing language understanding",
     "Natural Language Processing (NLP) is a field of AI that helps computers understand, interpret, and generate human language, for example in chatbots, translation, and sentiment analysis."),
    ("Neural Network", "neural network neurons layers",
     "A neural network is a computing model inspired by the human brain. It is made of connected layers of nodes called neurons that learn to map inputs to outputs by adjusting weights during training."),
    ("Computer Vision", "computer vision image recognition",
     "Computer vision is a field of AI that enables computers to understand and analyze images and videos, for example face detection and object recognition."),
    ("Data Science", "data science data scientist analytics",
     "Data science is the field of extracting useful insights from data using statistics, programming, and machine learning."),
    ("Cloud Computing", "cloud computing cloud services aws azure",
     "Cloud computing is the delivery of computing services such as servers, storage, databases, and software over the internet, so you pay only for what you use instead of owning the hardware."),
    ("Python", "python programming language",
     "Python is a high-level, general-purpose programming language known for its simple, readable syntax. It is widely used in web development, data science, automation, and AI."),
    ("Flask", "flask web framework",
     "Flask is a lightweight Python web framework used to build web applications and APIs. It provides the basics, like routing and templates, and lets you add other tools as needed."),
    ("API", "api application programming interface",
     "An API (Application Programming Interface) is a set of rules that lets one software program talk to another, for example a web app requesting data from a server."),
    ("REST API", "rest restful api http json",
     "A REST API is a web API that uses standard HTTP methods like GET, POST, PUT, and DELETE to work with resources, usually exchanging data in JSON format."),
    ("Database", "database data storage dbms",
     "A database is an organized collection of data stored electronically so it can be easily stored, searched, updated, and managed."),
    ("SQL", "sql structured query language queries",
     "SQL (Structured Query Language) is the standard language used to create, query, and manage data in relational databases."),
    ("HTML", "html hypertext markup language web page structure",
     "HTML (HyperText Markup Language) is the standard language used to structure the content of web pages using elements such as headings, paragraphs, links, and images."),
    ("CSS", "css cascading style sheets styling",
     "CSS (Cascading Style Sheets) is used to control how HTML content looks, including colors, fonts, spacing, and layout."),
    ("JavaScript", "javascript js scripting browser",
     "JavaScript is a programming language that runs in the browser and makes web pages interactive, such as handling clicks, updating content, and fetching data."),
    ("Git", "git version control",
     "Git is a distributed version control system that tracks changes in code, so teams can work together, review history, and go back to earlier versions."),
    ("GitHub", "github repository hosting",
     "GitHub is an online platform that hosts Git repositories, making it easy to store code, collaborate with others, and manage projects."),
    ("Operating System", "os operating system windows linux android",
     "An operating system (OS) is system software that manages the computer's hardware and resources and provides services for other programs. Examples are Windows, Linux, macOS, and Android."),
    ("Computer Network", "computer network networking protocols lan wan",
     "A computer network is a group of connected devices that share data and resources, using links like cables or wireless signals and rules called protocols."),
    ("Internet", "internet web tcp ip",
     "The internet is a global network of connected computers that communicate using standard protocols such as TCP/IP, which allows services like the web and email to work."),
    ("Content Delivery Network", "cdn content delivery network latency caching",
     "A Content Delivery Network (CDN) is a network of servers spread across locations that stores copies of content closer to users, which reduces latency and speeds up websites."),
    ("Data Structure", "data structure array stack queue tree graph linked list",
     "A data structure is a way of organizing and storing data so it can be used efficiently. Examples are arrays, linked lists, stacks, queues, trees, and graphs."),
    ("Algorithm", "algorithm steps instructions",
     "An algorithm is a step-by-step set of instructions for solving a problem or completing a task."),
    ("Object Oriented Programming", "oop object oriented programming class object inheritance",
     "Object-oriented programming (OOP) is a style of programming that organizes code into objects, based on four main ideas: encapsulation, abstraction, inheritance, and polymorphism."),
    ("Internet of Things", "iot internet of things sensors smart devices",
     "The Internet of Things (IoT) is a network of physical devices with sensors and software that collect and exchange data over the internet, such as smart home devices."),
    ("Cybersecurity", "cybersecurity security hacking attacks protection",
     "Cybersecurity is the practice of protecting computers, networks, and data from attacks, theft, and damage."),
    ("Blockchain", "blockchain ledger cryptocurrency",
     "A blockchain is a shared digital ledger where records are grouped into blocks and linked using cryptography, which makes the data very hard to change."),
    ("Big Data", "big data large datasets volume velocity variety",
     "Big data refers to extremely large and complex datasets that are too big for traditional tools, usually described by volume, velocity, and variety."),
    ("Speech Recognition", "speech recognition speech to text voice input asr",
     "Speech recognition is a technology that converts spoken language into written text. It is the first step in voice assistants."),
    ("Text to Speech", "text to speech tts speech synthesis voice output",
     "Text-to-speech (TTS) is a technology that converts written text into spoken audio."),
    ("Sentiment Analysis", "sentiment analysis opinion positive negative",
     "Sentiment analysis is an NLP task that finds whether a piece of text expresses a positive, negative, or neutral opinion."),
    ("TF-IDF", "tf idf term frequency inverse document frequency",
     "TF-IDF (Term Frequency, Inverse Document Frequency) is a score that shows how important a word is to a document, by combining how often it appears with how rare it is across other documents."),
    ("Tokenization", "tokenization tokens tokenizer",
     "Tokenization is the NLP step of splitting text into smaller units called tokens, such as words or sentences."),
    ("Stop Words", "stop words stopwords",
     "Stop words are very common words like the, is, and and, which are usually removed in NLP because they carry little meaning."),
    ("Chatbot", "chatbot bot conversation",
     "A chatbot is a program that simulates conversation with users through text or voice, often using NLP to understand questions."),
    ("Voice Assistant", "voice assistant siri alexa google assistant",
     "A voice assistant is software that understands spoken commands using speech recognition and NLP, and replies with speech. Siri, Alexa, and Google Assistant are examples."),
    ("About This Assistant", "who are you what can you do help hello hi about yourself",
     "I am a voice question answering assistant built with speech recognition and NLP. Ask me about topics like artificial intelligence, machine learning, NLP, cloud computing, or Python."),
]

ABBREVIATIONS = {
    "ai": "artificial intelligence", "ml": "machine learning", "dl": "deep learning",
    "nlp": "natural language processing", "os": "operating system",
    "oop": "object oriented programming", "iot": "internet of things",
    "tts": "text to speech", "cdn": "content delivery network",
    "api": "application programming interface", "css": "cascading style sheets",
    "sql": "structured query language", "html": "hypertext markup language",
}

STOP = set("""a an the is are was were be been am do does did what whats which who whom whose
when where why how can could would should will shall may might of in on at to for from by with
about into as it its this that these those me my you your i we they he she him her them tell
explain define describe mean meaning means please give short brief simple term concept called
and or but if then so than there here also any some more most very just like work works
used use""".split())


def _tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower().replace("'", ""))


def _expand(tokens):
    out = []
    for t in tokens:
        out.append(t)
        if t in ABBREVIATIONS:
            out.extend(ABBREVIATIONS[t].split())
    return out


def _stems(text, drop_stop=True):
    toks = _expand(_tokens(text))
    return [stem(t) for t in toks if not (drop_stop and t in STOP)]


# ---- build the TF-IDF index once at startup ----
DOCS = []
for title, keywords, answer_text in KNOWLEDGE:
    key_stems = _stems(f"{title} {keywords}")
    DOCS.append({
        "title": title, "answer": answer_text,
        "key": set(key_stems),
        "tf": Counter(key_stems * 3 + _stems(answer_text)),  # title and keywords weigh more
    })
N = len(DOCS)
DF = Counter(s for d in DOCS for s in d["tf"])
IDF = {s: math.log((N + 1) / (c + 1)) + 1 for s, c in DF.items()}


def _vec(counter):
    v = {s: c * IDF.get(s, math.log(N + 1) + 1) for s, c in counter.items()}
    norm = math.sqrt(sum(x * x for x in v.values())) or 1
    return v, norm


for d in DOCS:
    d["vec"], d["norm"] = _vec(d["tf"])

GREETINGS = {"hello", "hi", "hey", "namaste", "vanakkam"}
THRESHOLD = 0.30


def answer(question):
    q = _stems(question)
    raw = set(_tokens(question))
    if not q:  # only stop words, for example "hello" or "what can you do"
        if raw & (GREETINGS | {"you", "your", "yourself"}):
            return _result(DOCS[-1], 95)
        return _fallback()

    qv, qn = _vec(Counter(q))
    qset = set(q)
    best, best_score = None, 0.0
    for d in DOCS:
        dot = sum(w * d["vec"].get(s, 0) for s, w in qv.items())
        cosine = dot / (qn * d["norm"])
        coverage = len(qset & d["key"]) / len(qset)  # how much of the question the topic covers
        exact = 0.25 if qset <= d["key"] and len(d["key"] - qset) <= 4 else 0
        score = 0.5 * cosine + 0.5 * coverage + exact
        if score > best_score:
            best, best_score = d, score
    if best is None or best_score < THRESHOLD or not (qset & best["key"]):
        return _fallback()
    return _result(best, min(98, round(best_score * 100)))


def _result(d, confidence):
    return {"matched": True, "topic": d["title"], "answer": d["answer"],
            "confidence": confidence, "suggestions": []}


def _fallback():
    return {"matched": False, "topic": None, "confidence": 0,
            "answer": "Sorry, I do not have an answer for that yet. I can answer questions about topics like AI, machine learning, NLP, cloud computing and Python.",
            "suggestions": ["What is artificial intelligence?", "What is NLP?", "What is cloud computing?"]}