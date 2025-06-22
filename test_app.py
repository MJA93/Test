import os
from flask import Flask, request, session, redirect, url_for, render_template
from datetime import datetime, timedelta
import pytz
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secret_key'

# إعداد التوقيت
ksa_tz = pytz.timezone("Asia/Riyadh")
OFFICIAL_START_TIME = ksa_tz.localize(datetime(2025, 6, 22, 7, 30))
TEST_DURATION_MINUTES = 20

# تحميل المشاركين من Excel
participants_df = pd.read_excel("participants.xlsx")
participants = dict(zip(participants_df['id'].astype(str), participants_df['name']))

# تحميل الأسئلة من Excel
questions_df = pd.read_excel("questions.xlsx")
questions = []
for _, row in questions_df.iterrows():
    q = {"type": row['type'], "question": row['question']}
    if row['type'] == 'mcq':
        q["options"] = [row['opt1'], row['opt2'], row['opt3']]
    questions.append(q)

@app.route("/", methods=["GET"])
def wait_page():
    now = datetime.now(ksa_tz)
    if now >= OFFICIAL_START_TIME:
        return redirect(url_for("login"))
    return render_template("waiting.html", start_time=OFFICIAL_START_TIME.isoformat())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        user_name = request.form["user_name"]
        if user_id in participants and participants[user_id] == user_name:
            session["user_id"] = user_id
            session["user_name"] = user_name
            return redirect(url_for("start"))
        return render_template("login.html", error="بيانات غير صحيحة")
    return render_template("login.html")

@app.route("/start", methods=["GET", "POST"])
def start():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        session["start_time"] = datetime.now(ksa_tz).isoformat()
        return redirect(url_for("exam"))
    return render_template("start.html", name=session['user_name'])

@app.route("/exam", methods=["GET", "POST"])
def exam():
    if "user_id" not in session or "start_time" not in session:
        return redirect(url_for("login"))
    start_time = ksa_tz.localize(datetime.fromisoformat(session["start_time"]))
    now = datetime.now(ksa_tz)
    elapsed = (now - start_time).total_seconds()
    remaining = TEST_DURATION_MINUTES * 60 - elapsed
    if remaining <= 0:
        session.clear()
        return redirect(url_for("submitted"))
    minutes = int(remaining // 60)
    seconds = int(remaining % 60)
    if request.method == "POST":
        answers = {f"Q{i+1}": request.form.get(f"q{i}", "") for i in range(len(questions))}
        session.clear()
        # سيتم هنا لاحقًا ربط Google Sheet
        return redirect(url_for("submitted"))
    return render_template("exam.html", questions=questions, minutes=minutes, seconds=seconds)

@app.route("/submitted")
def submitted():
    return render_template("submitted.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
