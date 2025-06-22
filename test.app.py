
import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.secret_key = "secret_key"

ksa_tz = pytz.timezone("Asia/Riyadh")
OFFICIAL_START_TIME = datetime.now(ksa_tz).replace(hour=7, minute=30, second=0, microsecond=0)
TEST_DURATION_MINUTES = 20

participants = {
    "1001": "أحمد علي",
    "1002": "سارة محمد"
}

questions = [
    {"type": "mcq", "question": "ما لون السماء؟", "options": ["أزرق", "أخضر", "أحمر"]},
    {"type": "true_false", "question": "الشمس تشرق من الشرق."},
    {"type": "text", "question": "ما عاصمة السعودية؟"},
]

@app.route("/", methods=["GET", "POST"])
def home():
    now = datetime.now(ksa_tz)
    if now < OFFICIAL_START_TIME:
        return render_template("waiting.html", now=now, start_time=OFFICIAL_START_TIME)

    if request.method == "POST":
        user_id = request.form["user_id"]
        user_name = request.form["user_name"]
        if user_id in participants and participants[user_id] == user_name:
            session["user_id"] = user_id
            session["user_name"] = user_name
            return redirect(url_for("start"))
        else:
            return render_template("login.html", error="بيانات غير صحيحة")

    return render_template("login.html")

@app.route("/start", methods=["GET", "POST"])
def start():
    if "user_id" not in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        session["start_time"] = datetime.now(ksa_tz).isoformat()
        return redirect(url_for("exam"))
    return render_template("start.html", name=session["user_name"])

@app.route("/exam", methods=["GET", "POST"])
def exam():
    if "user_id" not in session or "start_time" not in session:
        return redirect(url_for("home"))

    start_time = datetime.fromisoformat(session["start_time"])
    now = datetime.now(ksa_tz)
    elapsed = (now - start_time).total_seconds()
    remaining = TEST_DURATION_MINUTES * 60 - elapsed

    if remaining <= 0:
        return render_template("done.html")

    if request.method == "POST":
        answers = {}
        for i, q in enumerate(questions):
            answers[f"Q{i+1}"] = request.form.get(f"q{i}", "")
        session.clear()
        return render_template("submitted.html", answers=answers)

    return render_template("exam.html", name=session["user_name"], questions=questions, remaining=int(remaining))

@app.route("/done")
def done():
    return render_template("done.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
