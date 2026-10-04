from flask import Flask, jsonify, render_template, request
from qa_engine import answer

app = Flask(__name__)
MAX_CHARS = 300


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask_route():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Ask a question first."}), 400
    if len(question) > MAX_CHARS:
        return jsonify({"error": f"Keep the question under {MAX_CHARS} characters."}), 400
    return jsonify(answer(question))


if __name__ == "__main__":
    app.run(debug=True, port=5050)