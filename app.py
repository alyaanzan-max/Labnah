import streamlit as st

st.set_page_config(
    page_title="لَبِنَة | Labnah",
    page_icon="🧱",
    layout="wide",
)

# --- بنك المشاريع المتعددة ---
PROJECTS = {
    "سيارة تتفادى العقبات (2WD Smart Car)": {
        "level": "مبتدئ - متوسط",
        "summary": "روبوت بعجلتين يستخدم حساس مسافة لتفادي العوائق وتغيير المسار تلقائياً.",
        "parts": ["ESP32", "L298N Motor Driver", "Ultrasonic Sensor", "DC Motors"],
        "steps": [
            {
                "title": "الخطوة 1: تجهيز التوصيل الكهربائي وخط الأرضي المشترك",
                "task": "ثبّت القطع على الهيكل، ووصّل مداخل المحركات بالبطاقة، وتأكد من توحيد GND بين المتحكم والبطاقة.",
                "check": "هل تأكدت من أن الأسلاك مثبتة بإحكام وأن البطارية غير موصولة أثناء التوصيل؟",
            },
            {
                "title": "الخطوة 2: اختبار حركة العجلات للأمام والخلف",
                "task": "اكتب كود اختبار بسيط يفعّل المحرك الأيمن والأيسر لثوانٍ للتأكد من اتجاه الدوران.",
                "check": "هل تدور العجلات بالاتجاه الصحيح دون اهتزاز أو توقف مفاجئ؟",
            },
            {
                "title": "الخطوة 3: قراءة المسافة من الحساس",
                "task": "وصّل حساس المسافة واقرأ القيم بالسنتيمتر للتأكد من استجابته أمام العائق.",
                "check": "هل تظهر قراءات المسافة وتتغير بوضوح عند تقريب جسم أمام الحساس؟",
            },
            {
                "title": "الخطوة 4: ربط قرار التفادي بالحركة",
                "task": "أضف شرطاً: إذا قلّت المسافة عن حد معين، توقف السيارة وتلف لليمين أو اليسار ثم تكمل.",
                "check": "هل تتفادى السيارة العائق وتكمل طريقها بدون ما تعلق؟",
            },
        ],
    },
    "محطة مراقبة ذكية للتربة والنبات": {
        "level": "مبتدئ",
        "summary": "نظام يقرأ رطوبة التربة ويعطي تنبيهاً أو يشغّل مضخة صغيرة عند الحاجة.",
        "parts": ["ESP32", "Soil Moisture Sensor", "Relay Module", "Water Pump"],
        "steps": [
            {
                "title": "الخطوة 1: قراءة رطوبة التربة في التربة الجافة والرطبة",
                "task": "اقرأ قيمة الحساس وهو في الهواء ثم في تربة رطبة لتعرف المدى الفعلي للقراءات.",
                "check": "هل لاحظت فرقاً واضحاً بين القراءة في الجفاف والرطوبة؟",
            },
            {
                "title": "الخطوة 2: تحديد عتبة التنبيه أو الري",
                "task": "اختر رقماً مناسباً يمثل بداية جفاف التربة بناءً على تجاربك السابقة.",
                "check": "هل حددت قيمة واضحة قبل ربطها بالتحكم؟",
            },
            {
                "title": "الخطوة 3: اختبار التحكم بالري أو التنبيه",
                "task": "اربط القراءة بالمنبه أو المضخة مع فصلها عن دوائر التحكم الحساسة.",
                "check": "هل يستجيب النظام فقط عندما تتجاوز القراءة الحد المحدد؟",
            },
        ],
    },
    "منصة تنسيق مهام برمجية صغيرة (لَبِنَة)": {
        "level": "متوسط",
        "summary": "تطبيق ويب يقسّم المهام البرمجية إلى خطوات صغيرة ويساعد المبرمج على التنفيذ والمتابعة.",
        "parts": ["Python", "Streamlit", "GitHub"],
        "steps": [
            {
                "title": "الخطوة 1: تحديد قائمة المهام وحالتها",
                "task": "أنشئ قائمة بالمهام بحيث يكون لكل مهمة عنوان ووصف وحالة (قيد التنفيذ / مكتملة).",
                "check": "هل تستطيع عرض المهام وتحديث حالتها دون أخطاء؟",
            },
            {
                "title": "الخطوة 2: بناء التنقل بين الخطوات",
                "task": "أضف زر انتقال يحدّث الخطوة الحالية ويحفظ التقدم للمستخدم.",
                "check": "هل ينتقل المستخدم للخطوة التالية ويحتفظ بحالته الحالية؟",
            },
            {
                "title": "الخطوة 3: مراجعة الواجهة ورفع النسخة",
                "task": "تأكد من وضوح النصوص والأزرار ثم ارفع التعديلات على المستودع.",
                "check": "هل تعمل الصفحة كاملة بدون رسائل خطأ؟",
            },
        ],
    },
}

# --- قصص القطع (تظهر فقط عند الطلب أو في قسم المسح) ---
PART_STORIES = {
    "ESP32": "متحكم يجمع بين المعالجة والاتصال اللاسلكي (Wi-Fi / Bluetooth) في شريحة واحدة، مما يجعله مناسباً للمشاريع المتصلة والذكية.",
    "L298N Motor Driver": "بطاقة تشغيل محركات تعتمد على جسر H للتحكم في اتجاه وسرعة محركات التيار المستمر عبر إشارات منخفضة القدرة من المتحكم.",
    "Ultrasonic Sensor": "حساس يرسل موجات فوق صوتية ويحسب الزمن المستغرق لعودة الصدى لتقدير المسافة أمامه.",
    "Soil Moisture Sensor": "حساس يقيس تغير التوصيل أو السعة في التربة لتقدير مستوى الرطوبة حول الجذور.",
    "Relay Module": "مفتاح إلكتروني يسمح لدائرة تحكم منخفضة الجهد بفتح أو إغلاق دائرة أخرى ذات حمل أعلى بأمان.",
}

# --- Session State ---
if "selected_project" not in st.session_state:
    st.session_state.selected_project = "سيارة تتفادى العقبات (2WD Smart Car)"

if "step_index" not in st.session_state:
    st.session_state.step_index = 0

if "points" not in st.session_state:
    st.session_state.points = 0

if "scanned_parts" not in st.session_state:
    st.session_state.scanned_parts = ["ESP32", "L298N Motor Driver"]

# --- تنسيق أزرق مريح للعين ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(160deg, #07192F 0%, #0D2B4E 55%, #123C69 100%);
        color: #EBF5FF;
        direction: rtl;
        text-align: right;
    }
    .blue-card {
        background: rgba(16, 52, 89, 0.78);
        border: 1px solid rgba(103, 212, 255, 0.28);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 16px;
        color: #F0F9FF;
    }
    .step-card {
        background: rgba(9, 34, 62, 0.88);
        border-right: 5px solid #38BDF8;
        border-top: 1px solid rgba(125, 211, 252, 0.22);
        border-bottom: 1px solid rgba(125, 211, 252, 0.22);
        border-left: 1px solid rgba(125, 211, 252, 0.22);
        border-radius: 12px;
        padding: 18px 20px;
        margin: 14px 0;
        color: #F0F9FF;
    }
    .part-note {
        background: rgba(14, 74, 110, 0.65);
        border: 1px solid rgba(125, 211, 252, 0.35);
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 10px;
        color: #E0F2FE;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- القائمة الجانبية ---
st.sidebar.title("🧱 لَبِنَة | Labnah")
section = st.sidebar.radio(
    "الأقسام:",
    [
        "💡 أفكار المشاريع",
        "🪜 مسار التنفيذ (خطوة بخطوة)",
        "📸 المسح",
        "🤖 اسأل عن قطعة",
    ],
)

st.sidebar.markdown("---")
st.sidebar.write(f"**المشروع المختار:**\n{st.session_state.selected_project}")
st.sidebar.metric("نقاط الشجاعة", f"{st.session_state.points} نقطة")

# ==========================================
# 1. قسم أفكار المشاريع
# ==========================================
if section == "💡 أفكار المشاريع":
    st.title("💡 أفكار المشاريع")
    st.markdown(
        """
        <div class="blue-card">
            اختر مشروعاً واحداً من المشاريع المتاحة لتبدأ العمل عليه خطوة بخطوة،
            مع زر <strong>«التالي»</strong> للانتقال بعد إتمام كل خطوة.
        </div>
        """,
        unsafe_allow_html=True,
    )

    for proj_name, proj_info in PROJECTS.items():
        is_current = (proj_name == st.session_state.selected_project)
        badge = " — ✅ المختار حالياً" if is_current else ""
        st.markdown(
            f"""
            <div class="blue-card">
                <h3>{proj_name}{badge}</h3>
                <p><strong>المستوى:</strong> {proj_info['level']} | <strong>عدد الخطوات:</strong> {len(proj_info['steps'])}</p>
                <p>{proj_info['summary']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"اختيار هذا المشروع: {proj_name}", key=f"btn_{proj_name}"):
            st.session_state.selected_project = proj_name
            st.session_state.step_index = 0
            st.success(f"تم اختيار المشروع: {proj_name}. انتقل إلى قسم «مسار التنفيذ (خطوة بخطوة)» للبدء.")

# ==========================================
# 2. مسار التنفيذ (خطوة بخطوة + زر التالي)
# ==========================================
elif section == "🪜 مسار التنفيذ (خطوة بخطوة)":
    proj_name = st.session_state.selected_project
    steps = PROJECTS[proj_name]["steps"]
    idx = st.session_state.step_index

    st.title("🪜 مسار التنفيذ")
    st.markdown(
        f"""
        <div class="blue-card">
            <strong>المشروع الحالي:</strong> {proj_name}<br>
            <strong>الخطوة:</strong> {idx + 1} من {len(steps)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress((idx + 1) / len(steps))

    current_step = steps[idx]
    st.markdown(
        f"""
        <div class="step-card">
            <h3>{current_step['title']}</h3>
            <p><strong>المطلوب تنفيذه:</strong><br>{current_step['task']}</p>
            <p><strong>نقطة التحقق قبل الانتقال:</strong><br>{current_step['check']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    done_check = st.checkbox("أنهيت هذه الخطوة وتحققت منها")

    col1, col2 = st.columns([1, 1])
    with col1:
        if idx > 0:
            if st.button("⬅️ الخطوة السابقة"):
                st.session_state.step_index -= 1
                st.rerun()

    with col2:
        if idx < len(steps) - 1:
            if st.button("التالي ➡️"):
                if done_check:
                    st.session_state.points += 50
                st.session_state.step_index += 1
                st.rerun()
        else:
            if st.button("إنهاء المشروع 🏆"):
                if done_check:
                    st.session_state.points += 100
                st.balloons()
                st.success("أتممت جميع خطوات المشروع بنجاح!")

# ==========================================
# 3. قسم المسح
# ==========================================
elif section == "📸 المسح":
    st.title("📸 المسح")
    st.markdown(
        """
        <div class="blue-card">
            ارفع صورة للقطع أو حدد القطع الموجودة أمامك لتسجيلها ضمن أدواتك الحالية.
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("ارفع صورة للقطعة أو الأدوات", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption=f"الصورة المرفوعة: {uploaded_file.name}", width=320)

    selected_parts = st.multiselect(
        "القطع المتوفرة لديك:",
        list(PART_STORIES.keys()) + ["DC Motors", "Water Pump", "Python", "Streamlit", "GitHub"],
        default=[p for p in st.session_state.scanned_parts if p in (list(PART_STORIES.keys()) + ["DC Motors", "Water Pump", "Python", "Streamlit", "GitHub"])],
    )

    if st.button("حفظ القطع الممسوحة"):
        st.session_state.scanned_parts = selected_parts
        st.success("تم حفظ القطع المحددة.")

    if st.session_state.scanned_parts:
        st.write("**القطع المسجلة حالياً:** " + "، ".join(st.session_state.scanned_parts))

# ==========================================
# 4. اسأل عن قطعة (فقط عند سؤال المبرمج)
# ==========================================
elif section == "🤖 اسأل عن قطعة":
    st.title("🤖 اسأل عن قطعة")
    st.markdown(
        """
        <div class="blue-card">
            هذا القسم مخصص فقط إذا حبيت تسأل عن قطعة معينة؛ لن تظهر أي معلومات عن القطع إلا إذا اخترتها وسألت عنها.
        </div>
        """,
        unsafe_allow_html=True,
    )

    chosen_part = st.selectbox("اختر القطعة التي تريد السؤال عنها:", list(PART_STORIES.keys()))
    question = st.text_input("اكتب سؤالك عن هذه القطعة (اختياري):")

    if st.button("عرض معلومة القطعة"):
        st.markdown(
            f"""
            <div class="part-note">
                <strong>{chosen_part}</strong><br>
                {PART_STORIES[chosen_part]}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if question.strip():
            st.info(f"سؤالك حول «{chosen_part}»: {question.strip()}")
