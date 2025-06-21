from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# بيانات المشاركين (تجريبية)
participants = {
    "1001": "أحمد علي",
    "1002": "سارة محمد",
    "1003": "خالد يوسف"
}

# الأسئلة التجريبية
questions = [
    {"type": "mcq", "question": "ما لون السماء؟", "options": ["أزرق", "أحمر", "أخضر", "أصفر"], "answer": "أزرق"},
    {"type": "true_false", "question": "الشمس تشرق من الغرب.", "answer": "خطأ"},
    {"type": "text", "question": "ما اسم عاصمة السعودية؟", "answer": "الرياض"},
]

# التوقيت المحلي (السعودية)
ksa_tz = pytz.timezone("Asia/Riyadh")
now_ksa = datetime.now(ksa_tz)
OFFICIAL_START_TIME = now_ksa.replace(hour=5, minute=30, second=0, microsecond=0)
if now_ksa > OFFICIAL_START_TIME:
    OFFICIAL_START_TIME += timedelta(days=1)

TEST_DURATION_MINUTES = 20

WAIT_PAGE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الانتظار لبدء الاختبار</title>
    <meta http-equiv="refresh" content="15">
    <style>
        body { font-family: 'Tahoma', sans-serif; background-color: #f2f2f2; text-align: center; padding-top: 100px; direction: rtl; }
        h2 { color: #333; }
    </style>
</head>
<body>
    <h2>🕒 الاختبار لم يبدأ بعد</h2>
    <p>الوقت المتبقي لبدء الاختبار: <strong>{minutes} دقيقة و {seconds} ثانية</strong></p>
    <p>توقيت السعودية الحالي: {current_time}</p>
    <p>يتم التحديث التلقائي كل 15 ثانية...</p>
</body>
</html>
"""

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تسجيل الدخول</title>
    <style>
        body { font-family: 'Tahoma', sans-serif; background-color: #fdfdfd; text-align: center; padding-top: 100px; direction: rtl; }
        input { padding: 10px; margin: 10px; width: 200px; }
        button { padding: 10px 20px; background-color: #3b7ddd; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2>🔐 تسجيل الدخول للاختبار</h2>
    <form method="post">
        <input name="user_id" placeholder="رقم المشارك"><br>
        <input name="user_name" placeholder="الاسم الكامل"><br>
        <button type="submit">دخول</button>
    </form>
</body>
</html>
"""

START_BUTTON_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>ابدأ الاختبار</title>
    <style>
        body { font-family: 'Tahoma', sans-serif; background-color: #e5f1fb; text-align: center; padding-top: 100px; direction: rtl; }
        button { padding: 15px 30px; font-size: 18px; background-color: #28a745; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2>👋 مرحبًا {user_name}</h2>
    <p>اضغط على الزر لبدء الاختبار</p>
    <form method="post">
        <input type="hidden" name="start" value="1">
        <button type="submit">ابدأ الاختبار الآن</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    now = datetime.now(ksa_tz)
    if now < OFFICIAL_START_TIME:
        remaining = OFFICIAL_START_TIME - now
        minutes, seconds = divmod(remaining.seconds, 60)
        current_time = now.strftime("%H:%M:%S")
        return WAIT_PAGE_HTML.format(minutes=minutes, seconds=seconds, current_time=current_time)

    if request.method == 'POST':
        user_id = request.form['user_id']
        user_name = request.form['user_name']
        if user_id in participants and participants[user_id] == user_name:
            session['user_id'] = user_id
            session['user_name'] = user_name
            return redirect(url_for('start'))
        else:
            return "<h3>❌ بيانات الدخول غير صحيحة</h3>"
    return LOGIN_PAGE_HTML

@app.route('/start', methods=['GET', 'POST'])
def start():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST' and request.form.get("start"):
        session['start_time'] = datetime.now(ksa_tz).isoformat()
        return redirect(url_for('exam'))

    return START_BUTTON_HTML.format(user_name=session['user_name'])

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if 'user_id' not in session or 'start_time' not in session:
        return redirect(url_for('login'))

    start_time = datetime.fromisoformat(session['start_time'])
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
            for option in q['options']:
                question_html += f'<input type="radio" name="q{i}" value="{option}"> {option}<br>'
        elif q['type'] == 'true_false':
            for option in ['صحيح', 'خطأ']:
                question_html += f'<input type="radio" name="q{i}" value="{option}"> {option}<br>'
        elif q['type'] == 'text':
            question_html += f'<input type="text" name="q{i}"><br>'
        question_html += "</p>"

    return render_template_string(f'''
        <h2>📝 الاختبار - {session['user_name']}</h2>
        <h3>⏳ الوقت المتبقي: {minutes} دقيقة و {seconds} ثانية</h3>
        <form method="post">
            {question_html}
            <button type="submit">إرسال الإجابات</button>
        </form>
    ''')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
