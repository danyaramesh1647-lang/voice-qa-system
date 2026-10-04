const $ = (id) => document.getElementById(id);
const chat = $("chat");
const input = $("question");
const micBtn = $("mic");
const statusEl = $("status");
const autoRead = $("auto-read");

const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const canSpeak = "speechSynthesis" in window;
let recognition = null;
let listening = false;

// ---------- chat ----------
function addMessage(role, text, extra) {
  $("empty").hidden = true;
  const wrap = document.createElement("div");
  wrap.className = "msg " + role;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);

  if (extra && extra.matched) {
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `Topic: ${extra.topic} | Confidence: ${extra.confidence}%`;
    const play = document.createElement("button");
    play.type = "button";
    play.className = "link";
    play.textContent = "Read aloud";
    play.addEventListener("click", () => speak(text));
    meta.appendChild(play);
    wrap.appendChild(meta);
  }
  if (extra && extra.suggestions && extra.suggestions.length) {
    const row = document.createElement("div");
    row.className = "chips";
    extra.suggestions.forEach((s) => row.appendChild(chip(s)));
    wrap.appendChild(row);
  }
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
}

function chip(text) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "chip";
  b.textContent = text;
  b.addEventListener("click", () => ask(text));
  return b;
}

async function ask(question) {
  question = (question || "").trim();
  if (!question) return;
  input.value = "";
  addMessage("user", question);
  setStatus("Thinking...");
  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    addMessage("bot", data.answer, data);
    setStatus("");
    if (autoRead.checked) speak(data.answer);
  } catch (err) {
    addMessage("bot", err.message);
    setStatus("");
  }
}

// ---------- text to speech ----------
function speak(text) {
  if (!canSpeak) return setStatus("Text to speech is not supported in this browser.");
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  const voices = speechSynthesis.getVoices();
  const voice = voices.find((v) => v.lang === "en-IN") || voices.find((v) => v.lang.startsWith("en"));
  if (voice) u.voice = voice;
  u.lang = voice ? voice.lang : "en-US";
  u.rate = 0.95;
  u.onstart = () => { setStatus("Speaking..."); $("stop").hidden = false; };
  u.onend = u.onerror = () => { setStatus(""); $("stop").hidden = true; };
  speechSynthesis.speak(u);
}

// ---------- speech to text ----------
if (Recognition) {
  recognition = new Recognition();
  recognition.lang = "en-IN";
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    listening = true;
    micBtn.classList.add("live");
    micBtn.setAttribute("aria-pressed", "true");
    setStatus("Listening... speak now");
  };
  recognition.onresult = (e) => {
    let text = "";
    for (let i = e.resultIndex; i < e.results.length; i++) text += e.results[i][0].transcript;
    input.value = text;
    if (e.results[e.results.length - 1].isFinal) ask(text);
  };
  recognition.onerror = (e) => {
    const msg = {
      "not-allowed": "Microphone permission was denied. Allow it in the browser address bar.",
      "no-speech": "I did not hear anything. Tap the mic and try again.",
      "audio-capture": "No microphone was found.",
      network: "Speech recognition needs an internet connection.",
    }[e.error] || "Speech recognition error: " + e.error;
    setStatus(msg);
  };
  recognition.onend = () => {
    listening = false;
    micBtn.classList.remove("live");
    micBtn.setAttribute("aria-pressed", "false");
    if (statusEl.textContent.startsWith("Listening")) setStatus("");
  };
} else {
  micBtn.disabled = true;
  setStatus("Voice input is not supported in this browser. Use Chrome or Edge, or type your question.");
}

micBtn.addEventListener("click", () => {
  if (!recognition) return;
  if (canSpeak) speechSynthesis.cancel();
  if (listening) recognition.stop();
  else recognition.start();
});

// ---------- controls ----------
$("send").addEventListener("click", () => ask(input.value));
input.addEventListener("keydown", (e) => { if (e.key === "Enter") ask(input.value); });
$("stop").addEventListener("click", () => { speechSynthesis.cancel(); $("stop").hidden = true; setStatus(""); });
$("clear").addEventListener("click", () => {
  if (canSpeak) speechSynthesis.cancel();
  if (recognition && listening) recognition.stop();
  chat.querySelectorAll(".msg").forEach((m) => m.remove());
  $("empty").hidden = false;
  setStatus("");
  input.focus();
});
document.querySelectorAll("#examples .chip").forEach((c) => c.addEventListener("click", () => ask(c.dataset.q)));

function setStatus(t) { statusEl.textContent = t; }
if (canSpeak) speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();