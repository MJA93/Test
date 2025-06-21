from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # استخدم مفتاح حقيقي في الإنتاج

# بيانات المشاركين (تجريبية)
participants = {
    "1001": "أحمد علي",
    "1002": "سارة محمد",
    "1003": "خالد يوسف"
}

# بيانات الأسئلة
questions = [
    {"type": "mcq", "question": "ما لون السماء؟", "options": ["أزرق", "أحمر", "أخضر", "أصفر"], "answer": "أزرق"},
    {"type": "true_false", "question": "الشمس تشرق من الغرب.", "answer": "خطأ"},
    {"type": "text", "question": "ما اسم عاصمة السعودية؟", "answer": "الرياض"},
]

OFFICIAL_START_TIME = datetime.now().replace(hour=5, minute=30, second=0, microsecond=0)
if datetime.now() > OFFICIAL_START_TIME:
    OFFICIAL_START_TIME += timedelta(days=1)

TEST_DURATION_MINUTES = 20


@app.route('/', methods=['GET', 'POST'])
def login():
    now = datetime.now()
    if now < OFFICIAL_START_TIME:
        remaining = OFFICIAL_START_TIME - now
        return f"<h3>الاختبار لم يبدأ بعد. الوقت المتبقي: {remaining}</h3>"

    if request.method == 'POST':
        user_id = request.form['user_id']
        user_name = request.form['user_name']
        if user_id in participants and participants[user_id] == user_name:
            session['user_id'] = user_id
            session['user_name'] = user_name
            session['start_time'] = datetime.now().isoformat()
            return redirect(url_for('exam'))
        else:
            return "<h3>بيانات الدخول غير صحيحة</h3>"
    return '''
        <form method="post">
            رقم المشارك: <input name="user_id"><br>
            الاسم الكامل: <input name="user_name"><br>
            <input type="submit" value="دخول">
        </form>
    '''


@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    start_time = datetime.fromisoformat(session['start_time'])
    elapsed = (datetime.now() - start_time).total_seconds()
    remaining = TEST_DURATION_MINUTES * 60 - elapsed

    if remaining <= 0:
        return "<h3>انتهى الوقت!</h3>"

    minutes = int(remaining // 60)
    seconds = int(remaining % 60)

    if request.method == 'POST':
        answers = {}
        for i, q in enumerate(questions):
            answers[f"Q{i+1}"] = request.form.get(f"q{i}", "")
        return f"<h3>تم إرسال إجاباتك:</h3><pre>{answers}</pre>"

    # بناء صفحة الأسئلة
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
        <h2>مرحبًا {session['user_name']}</h2>
        <h3>الوقت المتبقي: {minutes} دقيقة و {seconds} ثانية</h3>
        <form method="post">
            {question_html}
            <input type="submit" value="إرسال الإجابات">
        </form>
    ''')


if __name__ == '__main__':
    app.run(debug=True)
