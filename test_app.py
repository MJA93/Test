import os
from flask import Flask, request, session, redirect, url_for, render_template_string
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.secret_key = 'secret_key'

# المشاركون التجريبيون
participants = {
    "1001": "أحمد علي",
    "1002": "سارة محمد"
}

# أسئلة تجريبية
questions = [
    {"type": "mcq", "question": "ما لون السماء؟", "options": ["أزرق", "أخضر", "أحمر"], "answer": "أزرق"},
    {"type": "true_false", "question": "الشمس تشرق من الشرق.", "answer": "صحيح"},
    {"type": "text", "question": "ما عاصمة السعودية؟", "answer": "الرياض"},
]

# توقيت السعودية
ksa_tz = pytz.timezone("Asia/Riyadh")
OFFICIAL_START_TIME = ksa_tz.localize(datetime(2025, 6, 21, 7, 30, 0))
TEST_DURATION_MINUTES = 20

# صفحة الانتظار المحسنة
WAIT_PAGE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الاختبار لم يبدأ بعد</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css">
    <style>
        body {
            background: linear-gradient(to bottom, #0f172a, #1e293b);
            color: white;
            font-family: 'Cairo', sans-serif;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            text-align: center;
        }
        .circle {
            width: 260px;
            height: 260px;
            border-radius: 50%;
            background-color: #1e40af;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            box-shadow: 0 0 30px rgba(255,255,255,0.1);
            animation: pulse 2s infinite;
            margin-bottom: 20px;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .time {
            font-size: 1.8rem;
            font-weight: bold;
        }
        .note {
            font-size: 1rem;
            margin-top: 10px;
            color: #cbd5e1;
        }
    </style>
</head>
<body>
    <h2 class="mb-4">⌛ الرجاء الانتظار - لم يبدأ الاختبار بعد</h2>
    <div class="circle text-center">
        <div class="time" id="countdown">--:--:--:--</div>
    </div>
    <div class="note" id="now">الساعة الآن بتوقيت السعودية: ...</div>

    <script>
        const countdownEl = document.getElementById("countdown");
        const nowEl = document.getElementById("now");
        const startTime = new Date("{{ start_time }}").getTime();

        function updateCountdown() {
            const now = new Date().getTime();
            const diff = startTime - now;

            if (diff <= 0) {
                window.location.href = "/login";
                return;
            }

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
            const minutes = Math.floor((diff / (1000 * 60)) % 60);
            const seconds = Math.floor((diff / 1000) % 60);

            countdownEl.textContent = `${days}:${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

            const saTime = new Intl.DateTimeFormat('ar-SA', {
                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
                timeZone: 'Asia/Riyadh'
            }).format(new Date());
            nowEl.textContent = `الساعة الآن بتوقيت السعودية: ${saTime}`;
        }

        setInterval(updateCountdown, 1000);
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def wait():
    now = datetime.now(ksa_tz)
    if now >= OFFICIAL_START_TIME:
        return redirect(url_for('login'))
    return render_template_string(WAIT_PAGE_HTML, start_time=OFFICIAL_START_TIME.isoformat())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user_name = request.form['user_name']
        if user_id in participants and participants[user_id] == user_name:
            session['user_id'] = user_id
            session['user_name'] = user_name
            return redirect(url_for('start'))
        else:
            return "<h3>❌ بيانات غير صحيحة</h3>"

    return '''
    <html dir='rtl'><body style='text-align:center;padding-top:80px;font-family:tahoma;'>
    <h3>🔐 تسجيل الدخول</h3>
    <form method='post'>
        <input name='user_id' placeholder='رقم المشارك'><br>
        <input name='user_name' placeholder='الاسم'><br>
        <button type='submit'>دخول</button>
    </form></body></html>
    '''

@app.route('/start', methods=['GET', 'POST'])
def start():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST' and request.form.get("start"):
        session['start_time'] = datetime.now(ksa_tz).isoformat()
        return redirect(url_for('exam'))

    return f"""
    <html dir='rtl'><body style='text-align:center;padding-top:80px;font-family:tahoma;'>
    <h3>مرحبًا 👋 {session['user_name']}</h3>
    <form method='post'>
        <input type='hidden' name='start' value='1'>
        <button type='submit'>🚀 ابدأ الاختبار</button>
    </form></body></html>"""

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if 'user_id' not in session or 'start_time' not in session:
        return redirect(url_for('login'))

    # استرجاع وقت البداية من الجلسة
    start_time = ksa_tz.localize(datetime.fromisoformat(session['start_time']).replace(tzinfo=None))
    now = datetime.now(ksa_tz)
    elapsed = (now - start_time).total_seconds()
    remaining = TEST_DURATION_MINUTES * 60 - elapsed

    if remaining <= 0:
        return "<h3>⏰ انتهى الوقت!</h3>"

    minutes = int(remaining // 60)
    seconds = int(remaining % 60)

    if request.method == 'POST':
        answers = {}
        for i, q in enumerate(questions):
            answers[f"Q{i+1}"] = request.form.get(f"q{i}", "")
        return f"<h3>✅ تم إرسال إجاباتك:</h3><pre>{answers}</pre>"

    question_html = ""
    for i, q in enumerate(questions):
        question_html += f"<p><b>{i+1}. {q['question']}</b><br>"
        if q['type'] == 'mcq':
            for opt in q['options']:
                question_html += f"<input type='radio' name='q{i}' value='{opt}'> {opt}<br>"
        elif q['type'] == 'true_false':
            for opt in ['صحيح', 'خطأ']:
                question_html += f"<input type='radio' name='q{i}' value='{opt}'> {opt}<br>"
        elif q['type'] == 'text':
            question_html += f"<input type='text' name='q{i}'><br>"
        question_html += "</p>"

    return render_template_string(f'''
    <html dir='rtl'><body style='font-family:tahoma;padding:40px;'>
    <h2>📝 الاختبار - {session['user_name']}</h2>
    <h4>⏳ الوقت المتبقي: {minutes} دقيقة و {seconds} ثانية</h4>
    <form method='post'>
    {question_html}
    <button type='submit'>📩 إرسال</button>
    </form></body></html>
    ''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
