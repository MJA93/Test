import streamlit as st
import time
from datetime import datetime, timedelta

# نموذج بيانات افتراضي للمشاركين
participants = {
    "1001": "أحمد علي",
    "1002": "سارة محمد",
    "1003": "خالد يوسف"
}

# نموذج أسئلة افتراضي
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

# تحديد مدة الاختبار
TEST_DURATION_MINUTES = 5

# تحديد وقت السماح بالاختبار
start_time = datetime.now()
end_time = start_time + timedelta(hours=1)

# واجهة Streamlit
st.set_page_config(page_title="اختبار تجريبي", layout="centered", initial_sidebar_state="collapsed")
st.title("📝 منصة الاختبار التجريبي")

# تسجيل الدخول
st.subheader("🔐 تسجيل الدخول")
user_id = st.text_input("رقم المشارك")
user_name = st.text_input("الاسم الكامل")

if st.button("دخول"):
    if user_id in participants and participants[user_id] == user_name:
        now = datetime.now()
        if now < start_time:
            st.error("الاختبار لم يبدأ بعد.")
        elif now > end_time:
            st.error("انتهى وقت الاختبار.")
        else:
            st.success("تم التحقق! يمكنك بدء الاختبار الآن.")
            start_quiz = st.button("ابدأ الاختبار")
            if start_quiz:
                score = 0
                answers = []
                start = time.time()
                with st.form(key='quiz_form'):
                    st.subheader("📋 الأسئلة")
                    for idx, q in enumerate(questions):
                        st.markdown(f"**{idx+1}. {q['question']}**")
                        if q["type"] == "mcq":
                            answer = st.radio("اختر إجابة:", q["options"], key=idx)
                        elif q["type"] == "true_false":
                            answer = st.radio("اختر:", ["صحيح", "خطأ"], key=idx)
                        elif q["type"] == "text":
                            answer = st.text_input("إجابتك:", key=idx)
                        answers.append(answer)
                    submitted = st.form_submit_button("إرسال الإجابات")
                if submitted:
                    end = time.time()
                    duration = int(end - start)
                    st.success("✅ تم إرسال إجاباتك.")
                    st.info(f"⏱️ الوقت المستغرق: {duration} ثانية")

                    # عرض الإجابات والتقييم البسيط
                    for idx, q in enumerate(questions):
                        correct = q["answer"]
                        user_ans = answers[idx]
                        result = "✅" if user_ans.strip() == correct else "❌"
                        st.write(f"{idx+1}. {result} إجابتك: {user_ans} | الصحيح: {correct}")
    else:
        st.error("بيانات غير صحيحة. تأكد من الاسم والرقم.")
