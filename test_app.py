from flask import Flask, request, session, redirect, url_for, render_template_string
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.secret_key = 'secret_key'

# بيانات المشاركين التجريبية
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

ksa_tz = pytz.timezone("Asia/Riyadh")
now_ksa = datetime.now(ksa_tz)
OFFICIAL_START_TIME = now_ksa.replace(hour=5, minute=30, second=0, microsecond=0)
if now_ksa > OFFICIAL_START_TIME:
    OFFICIAL_START_TIME += timedelta(days=1)
TEST_DURATION_MINUTES = 20

@app.route('/', methods=['GET', 'POST'])
def login():
    now = datetime.now(ksa_tz)
    if now < OFFICIAL_START_TIME:
        remaining = OFFICIAL_START_TIME - now
        minutes, seconds = divmod(remaining.seconds, 60)
        current_time = now.strftime("%H:%M:%S")
        return f"""
        <html dir='rtl'>
        <body style="text-align:center;padding-top:80px;font-family:tahoma;">
        <h3>الاختبار لم يبدأ بعد</h3>
       <p>الوقت المتبقي: {minutes} دقيقة و {seconds} ثانية</p>
       <p>الساعة الآن بتوقيت السعودية: {current_time}</p>
       <meta http-equiv='refresh' content='15'>
       </body>
       </html>
       """


    if request.method == 'POST':
        user_id = request.form['user_id']
        user_name = request.form['user_name']
        if user_id in participants and participants[user_id] == user_name:
            session['user_id'] = user_id
            session['user_name'] = user_name
            return redirect(url_for('start'))
        else:
            return "<h3>بيانات غير صحيحة</h3>"

    return '''
    <html dir='rtl'><body style='text-align:center;padding-top:80px;font-family:tahoma;'>
    <h3>تسجيل الدخول</h3>
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
    <h3>مرحبًا {session['user_name']}</h3>
    <form method='post'>
        <input type='hidden' name='start' value='1'>
        <button type='submit'>ابدأ الاختبار</button>
    </form></body></html>"""

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
    <button type='submit'>إرسال</button>
    </form></body></html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
