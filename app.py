import random
import streamlit as st
from PIL import Image, ImageStat

st.set_page_config(
    page_title="لَبِنَة | Labnah",
    page_icon="🧱",
    layout="wide",
)

# --- إعداد رمز الدخول الخاص بالمنصة (تقدرين تغيرينه بأي رمز) ---
ACCESS_CODE = "LABNAH2026"
SYSTEM_EDITION = "Labnah Sovereign Edition"

# --- بيانات المشاريع مع التركيب والكود البرمجي ---
PROJECTS = {
    "سيارة تتفادى العقبات (2WD Smart Car)": {
        "level": "مبتدئ - متوسط",
        "duration": "60 - 90 دقيقة",
        "summary": "روبوت بعجلتين يقرأ المسافة أمامه ويقرر الاتجاه تلقائياً لتفادي العوائق.",
        "parts": ["ESP32", "L298N Motor Driver", "Ultrasonic Sensor", "DC Motors"],
        "steps": [
            {
                "title": "الخطوة 1: التركيب الميكانيكي وتوحيد خط الأرضي (GND)",
                "wiring": (
                    "1. ثبّت المحركين على الهيكل وركّب العجلتين.\n"
                    "2. وصّل مداخل التحكم IN1, IN2, IN3, IN4 من بطاقة L298N إلى منافذ رقمية في المتحكم (مثلاً 25, 26, 27, 14).\n"
                    "3. وصّل خط GND بين البطارية وبطاقة L298N والمتحكم معاً."
                ),
                "code": (
                    "// تعريف منافذ التحكم بالمحركات\n"
                    "const int IN1 = 25;\n"
                    "const int IN2 = 26;\n"
                    "const int IN3 = 27;\n"
                    "const int IN4 = 14;\n\n"
                    "void setup() {\n"
                    "  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);\n"
                    "  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);\n"
                    "}"
                ),
                "lang": "cpp",
                "check": "هل تأكدت من أن البطارية مفصولة أثناء التوصيل وأن GND مشترك بين كل الأطراف؟",
            },
            {
                "title": "الخطوة 2: برمجة الحركة الأساسية (للأمام والتوقف)",
                "wiring": (
                    "تأكد من تثبيت أسلاك المحركات بإحكام في أطراف OUT1/OUT2 و OUT3/OUT4 "
                    "قبل رفع الكود واختبار دوران العجلات."
                ),
                "code": (
                    "void moveForward() {\n"
                    "  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);\n"
                    "  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);\n"
                    "}\n\n"
                    "void stopMotors() {\n"
                    "  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);\n"
                    "  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);\n"
                    "}"
                ),
                "lang": "cpp",
                "check": "هل تتحرك العجلتان للأمام فعلاً؟ إذا كانت إحداها ترجع للخلف، اعكس قطبية أسلاكها.",
            },
            {
                "title": "الخطوة 3: تركيب حساس الموجات فوق الصوتية وقياس المسافة",
                "wiring": (
                    "وصّل VCC إلى 5V/VIN، و GND إلى GND، و TRIG إلى منفذ إخراج (مثلاً 5)، "
                    "و ECHO إلى منفذ إدخال (مثلاً 18)."
                ),
                "code": (
                    "const int TRIG_PIN = 5;\n"
                    "const int ECHO_PIN = 18;\n\n"
                    "long readDistanceCM() {\n"
                    "  digitalWrite(TRIG_PIN, LOW);\n"
                    "  delayMicroseconds(2);\n"
                    "  digitalWrite(TRIG_PIN, HIGH);\n"
                    "  delayMicroseconds(10);\n"
                    "  digitalWrite(TRIG_PIN, LOW);\n"
                    "  long duration = pulseIn(ECHO_PIN, HIGH);\n"
                    "  return (duration * 0.034) / 2;\n"
                    "}"
                ),
                "lang": "cpp",
                "check": "هل تظهر قراءة المسافة بالسنتيمتر وتنخفض لما تقرب يدك أمام الحساس؟",
            },
            {
                "title": "الخطوة 4: دمج قرار التفادي الذكي في الحلقة الرئيسية",
                "wiring": (
                    "ثبّت الحساس في مقدمة السيارة بزاوية مستقيمة للأمام بحيث لا يلتقط أرضية السيارة نفسها."
                ),
                "code": (
                    "void loop() {\n"
                    "  long dist = readDistanceCM();\n"
                    "  if (dist > 0 && dist < 20) {\n"
                    "    stopMotors();\n"
                    "    delay(200);\n"
                    "    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);\n"
                    "    digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH);\n"
                    "    delay(450);\n"
                    "  } else {\n"
                    "    moveForward();\n"
                    "  }\n"
                    "}"
                ),
                "lang": "cpp",
                "check": "هل تتوقف السيارة وتلف عند اقترابها من عائق أقل من 20 سم ثم تكمل؟",
            },
        ],
    },
    "محطة مراقبة ذكية للتربة والنبات": {
        "level": "مبتدئ",
        "duration": "45 - 60 دقيقة",
        "summary": "نظام يقرأ رطوبة التربة ويعرض حالتها ويُفعّل تنبيهاً أو مضخة عند جفاف التربة.",
        "parts": ["ESP32", "Soil Moisture Sensor", "Relay Module", "Water Pump"],
        "steps": [
            {
                "title": "الخطوة 1: توصيل حساس الرطوبة وقراءة القيم الفعلية",
                "wiring": (
                    "وصّل VCC الحساس إلى 3.3V، و GND إلى GND، ومنفذ القراءة التناظرية AOUT إلى منفذ ADC (مثلاً 34)."
                ),
                "code": (
                    "from machine import ADC, Pin\n"
                    "import time\n\n"
                    "sensor = ADC(Pin(34))\n"
                    "sensor.atten(ADC.ATTN_11DB)\n\n"
                    "while True:\n"
                    "    val = sensor.read()\n"
                    "    print('قراءة الرطوبة:', val)\n"
                    "    time.sleep(1)"
                ),
                "lang": "python",
                "check": "هل سجّلت القراءة في الهواء (جاف) والقراءة داخل تربة مبللة لتعرف الفرق بينهما؟",
            },
            {
                "title": "الخطوة 2: تحديد عتبة الري وربط المرحّل (Relay)",
                "wiring": (
                    "وصّل IN في بطاقة المرحّل إلى منفذ رقمي (مثلاً 27)، و VCC إلى 5V، و GND إلى GND المشترك."
                ),
                "code": (
                    "relay = Pin(27, Pin.OUT)\n"
                    "DRY_THRESHOLD = 2400\n\n"
                    "if val > DRY_THRESHOLD:\n"
                    "    relay.value(1)\n"
                    "else:\n"
                    "    relay.value(0)"
                ),
                "lang": "python",
                "check": "هل يعمل المرحّل ويطفي في الوقت الصحيح حسب العتبة اللي حددتها؟",
            },
        ],
    },
    "أداة تقسيم مهام المشاريع برمجياً": {
        "level": "مبتدئ - متوسط",
        "duration": "45 دقيقة",
        "summary": "سكربت بايثون يقسّم فكرة المشروع إلى مهام صغيرة قابلة للتنفيذ ويتتبع نسبة الإنجاز.",
        "parts": ["Python", "Streamlit"],
        "steps": [
            {
                "title": "الخطوة 1: هيكلة المهام وحالة كل مهمة",
                "wiring": "لا يوجد توصيل هاردوير؛ ابدأ بملف بايثون نظيف (`tasks.py`) في بيئة عملك.",
                "code": (
                    "tasks = [\n"
                    "    {'title': 'إعداد الواجهة الرئيسية', 'done': True},\n"
                    "    {'title': 'بناء منطق التنقل بين الخطوات', 'done': False},\n"
                    "    {'title': 'اختبار الحالات الحدية', 'done': False},\n"
                    "]\n\n"
                    "completed = sum(1 for t in tasks if t['done'])\n"
                    "print(f'نسبة الإنجاز: {completed}/{len(tasks)}')"
                ),
                "lang": "python",
                "check": "هل يحسب الكود عدد المهام المكتملة من الإجمالي بشكل صحيح؟",
            },
            {
                "title": "الخطوة 2: تحويل المهام إلى خطوات متسلسلة",
                "wiring": "أضف دالة ترجع المهمة التالية غير المكتملة ليسهل عرضها للمستخدم.",
                "code": (
                    "def next_task(task_list):\n"
                    "    for t in task_list:\n"
                    "        if not t['done']:\n"
                    "            return t['title']\n"
                    "    return 'تم إتمام جميع المهام!'\n\n"
                    "print('المهمة القادمة:', next_task(tasks))"
                ),
                "lang": "python",
                "check": "هل يعرض الكود أول مهمة غير مكتملة ثم يخبرك عند انتهاء الكل؟",
            },
        ],
    },
}

# --- تفاصيل القطع (تظهر فقط عند الاختيار أو السؤال) ---
PART_DETAILS = {
    "ESP32": {
        "role": "متحكم دقيق مدمج فيه Wi-Fi و Bluetooth مع معالج ثنائي النواة.",
        "how_it_works": "يستقبل أوامر الكود ويقرأ الحساسات عبر منافذ GPIO و ADC، ويرسل إشارات التحكم للقطع الخارجية أو يتصل بالشبكة.",
        "common_mistakes": "توصيل جهد أعلى من 3.3V على منافذ الإدخال الحساسة، أو نسيان وضع Boot عند رفع الكود على بعض اللوحات.",
        "snippet": "from machine import Pin\nled = Pin(2, Pin.OUT)\nled.on()",
    },
    "L298N Motor Driver": {
        "role": "بطاقة تشغيل محركات التيار المستمر (DC Motors) أو محركات الخطوة.",
        "how_it_works": "تستخدم جسر H لعكس اتجاه التيار في المحرك بناءً على إشارات IN1/IN2 مع توفير تيار أعلى من قدرة المتحكم المباشرة.",
        "common_mistakes": "عدم ربط خط GND المشترك بين المتحكم والبطاقة والبطارية، أو إزالة Jumper الـ 5V بدون فهم الجهد المغذي.",
        "snippet": "// تفعيل الاتجاه الأول للمحرك\ndigitalWrite(IN1, HIGH);\ndigitalWrite(IN2, LOW);",
    },
    "Ultrasonic Sensor": {
        "role": "حساس لقياس المسافة بدون تلامس باستخدام الموجات فوق الصوتية.",
        "how_it_works": "يرسل نبضة صوتية من TRIG ويحسب الزمن حتى رجوع الصدى إلى ECHO، ثم يحوّل الزمن إلى مسافة بالسنتيمتر.",
        "common_mistakes": "وجود عائق بزاوية حادة جداً تشتت الموجة الصوتية، أو قصر زمن الانتظار قبل القراءة التالية.",
        "snippet": "distance_cm = (duration_us * 0.0343) / 2",
    },
    "Soil Moisture Sensor": {
        "role": "حساس لقياس مستوى رطوبة التربة حول الجذور.",
        "how_it_works": "يقيس تغير التوصيل أو السعة الكهربائية في التربة ويخرج قيمة تتغير بتغير نسبة الماء.",
        "common_mistakes": "اعتماد رقم ثابت دون معايرة الحساس في التربة الجافة والرطبة الفعلية.",
        "snippet": "is_dry = moisture_value > dry_threshold",
    },
    "Relay Module": {
        "role": "مفتاح كهربائي يعمل بإشارة تحكم منخفضة الجهد.",
        "how_it_works": "عند وصول إشارة التحكم يغلق أو يفتح المسار الكهربائي لدائرة أخرى مثل مضخة أو لمبة.",
        "common_mistakes": "التعامل مع دوائر الجهد العالي دون عزل كافٍ أو فصل الطاقة أثناء التوصيل.",
        "snippet": "relay_pin.value(1)",
    },
}

# --- Session State ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "selected_project" not in st.session_state:
    st.session_state.selected_project = "سيارة تتفادى العقبات (2WD Smart Car)"
if "step_index" not in st.session_state:
    st.session_state.step_index = 0
if "points" not in st.session_state:
    st.session_state.points = 150
if "completed_log" not in st.session_state:
    st.session_state.completed_log = []
if "scanned_parts" not in st.session_state:
    st.session_state.scanned_parts = []

# --- التصميم البصري: هوية «سياج» الفخمة (#F4F7F9 + #1E3A8A + Almarai + الجواز الذهبي) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');

    * {
        font-family: 'Almarai', sans-serif;
        direction: rtl;
        text-align: right;
    }

    .stApp {
        background: #F4F7F9;
        color: #0F172A;
    }

    .sovereign-banner {
        background: #FFFFFF;
        padding: 28px 32px;
        border-radius: 0 0 45px 45px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
        border-bottom: 5px solid #1E3A8A;
        margin-bottom: 28px;
        animation: slideDown 0.65s ease-out;
    }

    @keyframes slideDown {
        from { transform: translateY(-30px); opacity: 0.3; }
        to { transform: translateY(0); opacity: 1; }
    }

    .sovereign-banner h1, .sovereign-banner h2, .sovereign-banner p {
        color: #1E3A8A !important;
        margin: 0 0 6px 0;
    }

    .sovereign-banner p {
        color: #334155 !important;
        font-size: 16px;
    }

    .feature-card {
        background: #FFFFFF;
        padding: 24px 26px;
        border-radius: 20px;
        border-right: 12px solid #1E3A8A;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
        margin-bottom: 20px;
        transition: all 0.25s ease;
    }

    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 26px rgba(30, 58, 138, 0.14);
    }

    .feature-card h3, .feature-card p, .feature-card strong, .feature-card div {
        color: #0F172A !important;
    }

    .guide-strip {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-right: 5px solid #1E3A8A;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }

    .guide-strip, .guide-strip * {
        color: #1E3A8A !important;
    }

    .passport-box {
        background: linear-gradient(145deg, #0B1E3D 0%, #1E3A8A 100%);
        color: #FFFFFF;
        padding: 36px;
        border-radius: 28px;
        border: 3px solid #D4AF37;
        box-shadow: 0 18px 36px rgba(11, 30, 61, 0.22);
        margin-bottom: 22px;
    }

    .passport-box h3, .passport-box p, .passport-box strong {
        color: #FFFFFF !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #1E3A8A, #2563EB) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        transition: all 0.25s ease !important;
    }

    .stButton > button:hover {
        filter: brightness(1.12);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# بوابة الدخول الفخمة (الاسم + الإيميل + الرمز)
# ==========================================
if not st.session_state.authenticated:
    st.markdown(
        """
        <div class="sovereign-banner">
            <h1>🧱 لَبِنَة | Labnah</h1>
            <p>منظومة تحويل أفكار الهاكثون إلى لبنات تنفيذ عملية — تركيب، كود، وتوثيق خطوة بخطوة.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown(
            """
            <div class="feature-card">
                <h3>مركز الدخول إلى المنظومة</h3>
                <p>أدخل اسمك، بريدك الإلكتروني، ورمز الدخول الخاص لفتح المساحة.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("labnah_login"):
            name_val = st.text_input("الاسم الكامل أو اسمك في المنصة", placeholder="مثال: عاليا صالح")
            email_val = st.text_input("البريد الإلكتروني", placeholder="example@labnah.sa")
            code_val = st.text_input("رمز الدخول الخاص", type="password", placeholder="أدخل رمز الدخول")
            enter_btn = st.form_submit_button("فتح المنظومة 🔐")

            if enter_btn:
                if not name_val.strip() or not email_val.strip():
                    st.error("يرجى إدخال الاسم والبريد الإلكتروني أولاً.")
                elif code_val.strip() != ACCESS_CODE:
                    st.error("رمز الدخول غير صحيح. تأكد من الرمز المخصص لك.")
                else:
                    st.session_state.user_profile = {
                        "name": name_val.strip(),
                        "email": email_val.strip(),
                        "badge_id": f"LBN-{random.randint(1000, 9999)}",
                    }
                    st.session_state.authenticated = True
                    st.rerun()
    st.stop()

# ==========================================
# القائمة الجانبية
# ==========================================
with st.sidebar:
    st.markdown(f"## 🧱 لَبِنَة")
    st.caption(SYSTEM_EDITION)
    st.write(f"**المستخدم:** {st.session_state.user_profile['name']}")
    st.write(f"**الرمز:** `{st.session_state.user_profile['badge_id']}`")
    st.divider()

    section = st.radio(
        "انتقل إلى الأقسام:",
        [
            "💡 أفكار المشاريع",
            "🪜 مسار التنفيذ (تركيب وكود)",
            "📸 المسح الذكي للقطع",
            "🔍 اسأل عن قطعة",
            "🛠️ مختبر التشخيص السريع",
            "🎫 جواز لَبِنَة وملفي",
        ],
    )

    st.divider()
    st.write(f"**المشروع الحالي:**\n{st.session_state.selected_project}")
    st.metric("نقاط الشجاعة", f"{st.session_state.points} نقطة")

    if st.button("تسجيل الخروج 🚪"):
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# 1. قسم أفكار المشاريع
# ==========================================
if section == "💡 أفكار المشاريع":
    st.markdown(
        f"""
        <div class="sovereign-banner">
            <h2>💡 أفكار المشاريع</h2>
            <p>أهلاً {st.session_state.user_profile['name']} — اختر مشروعاً واحداً لبدء تنفيذه خطوة بخطوة.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="guide-strip">
            <strong>وش هذا القسم؟</strong> يعرض لك المشاريع المتاحة مع مستواها ووقتها وعدد خطواتها. بمجرد اعتماد مشروع، يبدأ مسار التنفيذ بالتركيب والكود من الخطوة الأولى.
        </div>
        """,
        unsafe_allow_html=True,
    )

    for proj_name, info in PROJECTS.items():
        active_label = " — ✅ المختار حالياً" if proj_name == st.session_state.selected_project else ""
        st.markdown(
            f"""
            <div class="feature-card">
                <h3>{proj_name}{active_label}</h3>
                <p><strong>المستوى:</strong> {info['level']} &nbsp;|&nbsp; <strong>المدة:</strong> {info['duration']} &nbsp;|&nbsp; <strong>الخطوات:</strong> {len(info['steps'])}</p>
                <p>{info['summary']}</p>
                <p><strong>القطع الرئيسية:</strong> {'، '.join(info['parts'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"اعتماد هذا المشروع: {proj_name}", key=f"select_{proj_name}"):
            st.session_state.selected_project = proj_name
            st.session_state.step_index = 0
            st.success(f"تم اعتماد المشروع: {proj_name}. انتقل إلى «🪜 مسار التنفيذ (تركيب وكود)».")

# ==========================================
# 2. مسار التنفيذ (تركيب + كود + زر التالي)
# ==========================================
elif section == "🪜 مسار التنفيذ (تركيب وكود)":
    proj_name = st.session_state.selected_project
    steps = PROJECTS[proj_name]["steps"]
    idx = st.session_state.step_index
    step = steps[idx]

    st.markdown(
        f"""
        <div class="sovereign-banner">
            <h2>🪜 مسار التنفيذ</h2>
            <p>المشروع: <strong>{proj_name}</strong> — الخطوة {idx + 1} من {len(steps)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="guide-strip">
            <strong>وش هذا القسم؟</strong> يوضح لك طريقة التركيب والتوصيل مع الكود البرمجي للخطوة الحالية، وبعد التحقق تضغط <strong>«التالي»</strong> للانتقال للخطوة التي تليها.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress((idx + 1) / len(steps))

    st.markdown(
        f"""
        <div class="feature-card">
            <h3>{step['title']}</h3>
            <p><strong>طريقة التركيب والتوصيل:</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text(step["wiring"])

    st.markdown("**الكود البرمجي لهذه الخطوة:**")
    st.code(step["code"], language=step["lang"])

    st.markdown(
        f"""
        <div class="feature-card">
            <p><strong>نقطة التحقق قبل الانتقال:</strong> {step['check']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    verified = st.checkbox("تحققت من التركيب والكود وأن الخطوة تعمل بشكل سليم")

    col_prev, col_next = st.columns(2)
    with col_prev:
        if idx > 0 and st.button("⬅️ الخطوة السابقة"):
            st.session_state.step_index -= 1
            st.rerun()

    with col_next:
        if idx < len(steps) - 1:
            if st.button("التالي ➡️"):
                if verified:
                    st.session_state.points += 75
                    st.session_state.completed_log.append(f"{proj_name} — {step['title']}")
                st.session_state.step_index += 1
                st.rerun()
        else:
            if st.button("إتمام المشروع 🏆"):
                if verified:
                    st.session_state.points += 150
                    st.session_state.completed_log.append(f"{proj_name} — {step['title']}")
                st.balloons()
                st.success("مبروك! أنهيت جميع خطوات المشروع بنجاح.")

# ==========================================
# 3. المسح الذكي للقطع
# ==========================================
elif section == "📸 المسح الذكي للقطع":
    st.markdown(
        """
        <div class="sovereign-banner">
            <h2>📸 المسح الذكي للقطع</h2>
            <p>ارفع صورة للقطعة أو الأدوات التي أمامك لفحص الصورة واعتماد القطع المتوفرة لديك.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="guide-strip">
            <strong>وش هذا القسم؟</strong> يقرأ أبعاد الصورة ومتوسط سطوعها ويعرض لك معلومات القطعة المحددة لتسجيلها ضمن أدواتك الحالية.
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_img = st.file_uploader("ارفع صورة القطعة (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    candidate_part = st.selectbox("القطعة المراد مطابقتها مع الصورة:", list(PART_DETAILS.keys()))

    if uploaded_img is not None:
        img = Image.open(uploaded_img).convert("RGB")
        w, h = img.size
        avg_rgb = ImageStat.Stat(img).mean
        brightness = round(sum(avg_rgb) / 3, 1)

        c1, c2 = st.columns([1, 1.4])
        with c1:
            st.image(img, caption=f"{uploaded_img.name} ({w}×{h})", use_container_width=True)
        with c2:
            st.markdown(
                f"""
                <div class="feature-card">
                    <h3>نتيجة فحص الصورة</h3>
                    <p><strong>الأبعاد:</strong> {w} × {h} بكسل</p>
                    <p><strong>متوسط سطوع الإضاءة:</strong> {brightness} / 255</p>
                    <p><strong>القطعة المحددة:</strong> {candidate_part}</p>
                    <p><strong>الوظيفة الأساسية:</strong> {PART_DETAILS[candidate_part]['role']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("إضافة القطعة إلى قائمة أدواتي ✅"):
                if candidate_part not in st.session_state.scanned_parts:
                    st.session_state.scanned_parts.append(candidate_part)
                    st.session_state.points += 25
                st.success(f"تمت إضافة {candidate_part} إلى قائمة القطع المسجلة.")

    st.markdown(
        f"""
        <div class="feature-card">
            <strong>القطع المسجلة لديك حالياً:</strong>
            {('، '.join(st.session_state.scanned_parts) if st.session_state.scanned_parts else 'لم يتم تسجيل أي قطعة بعد.')}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# 4. اسأل عن قطعة (تفاصيل كاملة عند الطلب فقط)
# ==========================================
elif section == "🔍 اسأل عن قطعة":
    st.markdown(
        """
        <div class="sovereign-banner">
            <h2>🔍 اسأل عن قطعة</h2>
            <p>اطلب تفاصيل أي قطعة إلكترونية وقت ما تحتاج تفهمها، بدون أي حشو تلقائي.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="guide-strip">
            <strong>وش هذا القسم؟</strong> اختر القطعة واكتب سؤالك ثم اضغط <strong>«عرض التفاصيل والإجابة»</strong> ليظهر لك الشرح الكامل والأخطاء الشائعة ومثال الكود.
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_part = st.selectbox("اختر القطعة:", list(PART_DETAILS.keys()))
    user_q = st.text_input("اكتب سؤالك المحدد عن هذه القطعة:")

    if st.button("عرض التفاصيل والإجابة"):
        info = PART_DETAILS[selected_part]
        st.markdown(
            f"""
            <div class="feature-card">
                <h3>{selected_part}</h3>
                <p><strong>وش وظيفتها؟</strong> {info['role']}</p>
                <p><strong>كيف تشتغل؟</strong> {info['how_it_works']}</p>
                <p><strong>أشهر الأخطاء الشائعة:</strong> {info['common_mistakes']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.code(info["snippet"], language="python" if selected_part == "Soil Moisture Sensor" else "cpp")

        if user_q.strip():
            st.markdown(
                f"""
                <div class="feature-card">
                    <p><strong>سؤالك:</strong> {user_q.strip()}</p>
                    <p><strong>التوجيه المباشر:</strong> راجع قسم «أشهر الأخطاء الشائعة» أعلاه وتأكد من توصيل الأطراف والجهد المناسب قبل التشغيل، ثم اختبر القطعة بمثال الكود المرفق لوحدها.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ==========================================
# 5. مختبر التشخيص السريع
# ==========================================
elif section == "🛠️ مختبر التشخيص السريع":
    st.markdown(
        """
        <div class="sovereign-banner">
            <h2>🛠️ مختبر التشخيص السريع</h2>
            <p>إذا واجهتك مشكلة أثناء التنفيذ أو البرمجة، اختر نوع الملاحظة لتبدأ فحصاً منظماً.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="guide-strip">
            <strong>وش هذا القسم؟</strong> يساعدك تفصل بين مشاكل التوصيل والطاقة، مشاكل القراءة أو الحساسات، ومشاكل الكود والمنطق.
        </div>
        """,
        unsafe_allow_html=True,
    )

    diag_type = st.selectbox(
        "ما نوع المشكلة التي تواجهها الآن؟",
        [
            "القطعة أو المحرك لا يستجيب رغم التوصيل",
            "القراءات متذبذبة أو غير دقيقة",
            "خطأ برمجي أو الكود لا يرفع/لا يعمل كما هو متوقع",
        ],
    )
    extra_note = st.text_area("اكتب وصفاً مختصراً للي صار معك (اختياري):")

    if st.button("تشخيص الآن 🔧"):
        if diag_type == "القطعة أو المحرك لا يستجيب رغم التوصيل":
            advice = "تحقق أولاً من وجود خط GND مشترك بين المتحكم ومصدر الطاقة والقطعة، ثم تأكد من سلامة مستوى الجهد وقوة البطارية."
        elif diag_type == "القراءات متذبذبة أو غير دقيقة":
            advice = "تأكد من ثبات الأسلاك في المنافذ، وافحص الحساس في بيئة ثابتة بعيداً عن التداخل، ثم قارن القراءات قبل وبعد التعديل."
        else:
            advice = "راجع أسماء المنافذ والأقواس والنقطة الفاصلة في الكود، واختبر كل جزء بمفرده قبل دمجه مع باقي الخطوات."

        st.markdown(
            f"""
            <div class="feature-card">
                <h3>نتيجة التشخيص</h3>
                <p><strong>المسار:</strong> {diag_type}</p>
                <p><strong>أول خطوة فحص:</strong> {advice}</p>
                {f"<p><strong>ملاحظتك:</strong> {extra_note.strip()}</p>" if extra_note.strip() else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# 6. جواز لَبِنَة وملفي
# ==========================================
elif section == "🎫 جواز لَبِنَة وملفي":
    prof = st.session_state.user_profile
    st.markdown(
        f"""
        <div class="sovereign-banner">
            <h2>🎫 جواز لَبِنَة وملفي</h2>
            <p>بطاقة الإنجاز والرحلة التقنية لـ <strong>{prof['name']}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="passport-box">
            <h3>جواز لَبِنَة التقني</h3>
            <p><strong>الاسم:</strong> {prof['name']} &nbsp;|&nbsp; <strong>الرمز التعريفي:</strong> {prof['badge_id']}</p>
            <p><strong>البريد الإلكتروني:</strong> {prof['email']}</p>
            <p><strong>المشروع الحالي:</strong> {st.session_state.selected_project}</p>
            <p><strong>نقاط الشجاعة:</strong> {st.session_state.points} نقطة &nbsp;|&nbsp; <strong>الخطوات المنجزة:</strong> {len(st.session_state.completed_log)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="feature-card">
            <h3>سجل الخطوات المنجزة</h3>
            {('<br>'.join([f'✅ {item}' for item in reversed(st.session_state.completed_log)]) if st.session_state.completed_log else 'لم يتم تسجيل خطوات مكتملة بعد — ابدأ من «🪜 مسار التنفيذ» واضغط «التالي» بعد التحقق.')}
        </div>
        """,
        unsafe_allow_html=True,
    )
