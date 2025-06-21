import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd

# إعداد وقت بدء الاختبار الرسمي (5:30 صباحاً بتوقيت السعودية)
official_start_time = datetime.now().replace(hour=5, minute=30, second=0, microsecond=0)
if datetime.now().hour >= 5:
    official_start_time += timedelta(days=1)

# مدة الاختبار بالدقائق
TEST_DURATION_MINUTES = 20

# نموذج بيانات المشاركين
participants = {
    "1001": "أحمد علي",
    "1002": "سارة محمد",
    "1003": "خالد يوسف"
}

# نموذج الأسئلة
questions = [
    {
        "type": "mcq",
        "question": "ما هو لون السماء؟",
        "options": ["أزرق", "أحمر", "أخضر", "أصفر"],
        "answer": "أزرق"
    },
    {
        "type": "true_false",
        "question": "الشمس تشرق من الغرب.",
        "answer": "خطأ"
    },
    {
        "type": "text",
        "question": "ما اسم عاصمة المملكة العربية السعودية؟",
        "answer": "الرياض"
    }
]

# إعداد واجهة Streamlit
st.set_page_config(page_title="اختبار تجريبي", layout="centered")
st.title("📝 منصة الاختبار")

# تهيئة الجلسة
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "start_timestamp" not in st.session_state:
    st.session_state.start_timestamp = None
if "answers" not in st.session_state:
    st.session_state.answers = []
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# انتظار وقت البدء الرسمي
now = datetime.now()
if now < official_start_time:
    st.info(f"⏰ يبدأ الاختبار الساعة 5:30 صباحًا بتوقيت السعودية ({official_start_time.strftime('%Y-%m-%d %H:%M')})")
    st.stop()

# تسجيل الدخول
if not st.session_state.logged_in:
    st.subheader("🔐 تسجيل الدخول")
    user_id = st.text_input("رقم المشارك")
    user_name = st.text_input("الاسم الكامل")
    if st.button("دخول"):
        if user_id in participants and participants[user_id] == user_name:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.session_state.user_name = user_name
            st.success(f"مرحبًا {user_name}، يمكنك الآن بدء الاختبار.")
        else:
            st.error("❌ الاسم أو الرقم غير صحيح.")
    st.stop()

# شاشة بدء الاختبار
if st.session_state.logged_in and not st.session_state.quiz_started:
    st.subheader(f"👋 أهلاً {st.session_state.user_name}")
    if st.button("ابدأ الاختبار الآن"):
        st.session_state.quiz_started = True
        st.session_state.start_timestamp = time.time()
    st.stop()

# عرض الأسئلة مع عداد تنازلي
if st.session_state.quiz_started:
    elapsed = time.time() - st.session_state.start_timestamp
    remaining = TEST_DURATION_MINUTES * 60 - elapsed
    minutes = int(remaining // 60)
    seconds = int(remaining % 60)

    if remaining <= 0:
        st.warning("⏱️ انتهى الوقت المخصص للاختبار.")
        submitted_answers = []
        for i, q in enumerate(questions):
            ans = st.session_state.answers[i] if i < len(st.session_state.answers) else ""
            if ans.strip() != "":
                submitted_answers.append({
                    "رقم المشارك": st.session_state.user_id,
                    "الاسم": st.session_state.user_name,
                    "السؤال": q["question"],
                    "إجابته": ans
                })
        results_df = pd.DataFrame(submitted_answers)
        st.write("📋 إجاباتك:")
        st.dataframe(results_df)
        st.stop()

    st.info(f"⏳ الوقت المتبقي: {minutes} دقيقة و {seconds} ثانية")
    time.sleep(1)
    st.experimental_rerun()

    answers = []
    with st.form(key="quiz_form"):
        for idx, q in enumerate(questions):
            st.markdown(f"**{idx+1}. {q['question']}**")
            if q["type"] == "mcq":
                ans = st.radio("اختر:", q["options"], key=f"q{idx}")
            elif q["type"] == "true_false":
                ans = st.radio("اختر:", ["صحيح", "خطأ"], key=f"q{idx}")
            elif q["type"] == "text":
                ans = st.text_input("إجابتك:", key=f"q{idx}")
            answers.append(ans)
        if st.form_submit_button("إرسال الإجابات"):
            st.session_state.answers = answers
            st.experimental_rerun()
