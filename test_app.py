import streamlit as st
import time
from datetime import datetime, timedelta

# نموذج المشاركين
participants = {
    "1001": "أحمد علي",
    "1002": "سارة محمد",
    "1003": "خالد يوسف"
}

# الأسئلة التجريبية
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

# توقيت الاختبار
TEST_DURATION_MINUTES = 5
start_time = datetime.now()
end_time = start_time + timedelta(hours=1)

# إعداد الصفحة
st.set_page_config(page_title="اختبار تجريبي", layout="centered")
st.title("📝 منصة الاختبار التجريبي")

# تعريف حالة البداية
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "start_timestamp" not in st.session_state:
    st.session_state.start_timestamp = None

# تسجيل الدخول
if not st.session_state.logged_in:
    st.subheader("🔐 تسجيل الدخول")
    user_id = st.text_input("رقم المشارك")
    user_name = st.text_input("الاسم الكامل")
    if st.button("دخول"):
        if user_id in participants and participants[user_id] == user_name:
            now = datetime.now()
            if now < start_time:
                st.error("⏱️ الاختبار لم يبدأ بعد.")
            elif now > end_time:
                st.error("❌ انتهى وقت الاختبار.")
            else:
                st.success("✅ تم تسجيل الدخول! يمكنك بدء الاختبار.")
                st.session_state.logged_in = True
        else:
            st.error("❌ الاسم أو الرقم غير صحيح.")
    st.stop()

# بدء الاختبار
if st.session_state.logged_in and not st.session_state.quiz_started:
    if st.button("ابدأ الاختبار"):
        st.session_state.quiz_started = True
        st.session_state.start_timestamp = time.time()
    st.stop()

# واجهة الأسئلة
if st.session_state.quiz_started:
    st.subheader("📋 الأسئلة")
    answers = []
    with st.form(key='quiz_form'):
        for idx, q in enumerate(questions):
            st.markdown(f"**{idx+1}. {q['question']}**")
            if q["type"] == "mcq":
                ans = st.radio("اختر إجابة:", q["options"], key=idx)
            elif q["type"] == "true_false":
                ans = st.radio("اختر:", ["صحيح", "خطأ"], key=idx)
            elif q["type"] == "text":
                ans = st.text_input("إجابتك:", key=idx)
            answers.append(ans)
        submitted = st.form_submit_button("إرسال الإجابات")

    if submitted:
        duration = int(time.time() - st.session_state.start_timestamp)
        st.success("✅ تم إرسال إجاباتك.")
        st.info(f"⏱️ الوقت المستغرق: {duration} ثانية")

        for idx, q in enumerate(questions):
            correct = q["answer"]
            user_ans = answers[idx]
            result = "✅" if user_ans.strip() == correct else "❌"
            st.write(f"{idx+1}. {result} إجابتك: {user_ans} | الصحيح: {correct}")
