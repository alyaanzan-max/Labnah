import streamlit as st

st.set_page_config(
    page_title="لَبِنَة | Labnah",
    page_icon="🧱",
    layout="wide",
)

# --- حالة التطبيق (Session State) ---
if "points" not in st.session_state:
    st.session_state.points = 450

if "completed_blocks" not in st.session_state:
    st.session_state.completed_blocks = [
        {
            "title": "تجهيز الهيكل وتحديد مسار الحركة",
            "story_note": "تجاوزت أول تجربة وضبطت اتجاه العجلات بدقة.",
            "points": 250,
        }
    ]

if "detected_parts" not in st.session_state:
    st.session_state.detected_parts = ["ESP32", "L298N Motor Driver", "Ultrasonic Sensor"]

if "current_block" not in st.session_state:
    st.session_state.current_block = "توصيل المحركات ببطاقة L298N"

# --- تنسيق خفيف لتحسين الشكل ---
st.markdown(
    """
    <style>
    .hero-box {
        background: linear-gradient(135deg, #0A192F 0%, #112240 100%);
        color: #F8F9FA;
        padding: 20px;
        border-radius: 14px;
        border-right: 6px solid #00F5D4;
        margin-bottom: 18px;
    }
    .story-box {
        background-color: #F0FDF9;
        color: #0A192F;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #00C4A7;
        margin: 12px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- القائمة الجانبية للتنقل بين الأقسام ---
st.sidebar.title("🧱 لَبِنَة | Labnah")
st.sidebar.caption("من اللبنة.. تكتمل الفكرة")

page = st.sidebar.radio(
    "الأقسام",
    [
        "🏠 الرئيسية",
        "📸 المسح واللبنات",
        "🧪 المختبر والمساعد",
        "🏆 ملفي",
    ],
)

st.sidebar.markdown("---")
st.sidebar.metric("نقاط الشجاعة", f"{st.session_state.points} نقطة")
st.sidebar.progress(min(len(st.session_state.completed_blocks) / 3, 1.0))

# ==========================================
# 1. الشاشة الرئيسية
# ==========================================
if page == "🏠 الرئيسية":
    st.markdown(
        """
        <div class="hero-box">
            <h2>أهلاً بك يا صانع التقنية 🚀</h2>
            <p>خطوتك اليوم تضعك ضمن فئة قليلة قررت تبني بإيدها وتفهم كيف تشتغل الأشياء خطوة بخطوة.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("المشروع الحالي", "سيارة تتفادى العقبات")
    col2.metric("اللبنات المكتملة", f"{len(st.session_state.completed_blocks)} / 3")
    col3.metric("رصيد النقاط", f"{st.session_state.points}")

    st.subheader("اللبنة الجارية الآن")
    st.info(f"**اللبنة الحالية:** {st.session_state.current_block}")
    st.write(
        "في هذه الخطوة تتعلم كيف تنتقل الإشارة من المتحكم إلى مشغل المحركات، "
        "وليش نحتاج نضبط اتجاه الحركة قبل ما نربط حساس المسافة."
    )

# ==========================================
# 2. المسح واللبنات
# ==========================================
elif page == "📸 المسح واللبنات":
    st.title("📸 المسح واللبنات")
    st.write("اختر القطع المتوفرة عندك أو ارفع صورة لها عشان نحدد اللبنات المناسبة لبدايتك.")

    uploaded_img = st.file_uploader("ارفع صورة للقطع الموجودة أمامك (اختياري في النسخة التجريبية)", type=["png", "jpg", "jpeg"])
    available_choices = st.multiselect(
        "القطع المتوفرة حالياً:",
        ["ESP32", "Arduino UNO", "L298N Motor Driver", "Ultrasonic Sensor", "DC Motors", "Jumper Wires"],
        default=st.session_state.detected_parts,
    )

    if st.button("تحليل القطع وتحديث اللبنات"):
        st.session_state.detected_parts = available_choices
        if uploaded_img is not None:
            st.success(f"تم استلام الصورة ({uploaded_img.name}) وتحديث قائمة القطع!")
        else:
            st.success("تم تحديث قائمة القطع المتوفرة بنجاح!")

    st.markdown("### اللبنات المقترحة لمشروعك")

    blocks_data = [
        {
            "name": "اللبنة 1: توصيل المحركات ببطاقة L298N",
            "level": "مبتدئ",
            "origin": (
                "قبل ما تصير وحدات التحكم الصغيرة تتحكم بالمحركات بسهولة، كان التحكم في اتجاه "
                "الدوران يحتاج مفاتيح ثقيلة ودوائر معقدة. فكرة الجسر الإلكتروني (H-Bridge) سمحت "
                "بعكس اتجاه التيار بأمان، واليوم تطبق نفس المبدأ لتحريك سيارتك."
            ),
            "steps": [
                "تأكد من فصل الطاقة قبل توصيل الأسلاك.",
                "اربط مداخل التحكم (IN1, IN2) بأطراف الإخراج المحددة في المتحكم.",
                "وحّد خط الأرضي (GND) بين المتحكم وبطاقة المحركات والمصدر.",
            ],
        },
        {
            "name": "اللبنة 2: قراءة المسافة بحساس الموجات فوق الصوتية",
            "level": "مبتدئ",
            "origin": (
                "فكرة قياس المسافة بالصوت مستوحاة من الطبيعة (مثل الخفافيش والدلافين) التي ترسل "
                "نبضة وتقيس زمن رجوع الصدى لتفهم محيطها دون لمس."
            ),
            "steps": [
                "ثبّت الحساس في مقدمة السيارة بزاوية مستقيمة.",
                "صِل أطراف Trigger و Echo بالمنافذ الرقمية المناسبة.",
                "اختبر قراءة المسافة في الشاشة التسلسلية قبل ربطها بالحركة.",
            ],
        },
    ]

    for blk in blocks_data:
        with st.expander(f"{blk['name']} — المستوى: {blk['level']}", expanded=True):
            st.markdown(
                f"""
                <div class="story-box">
                    <strong>📜 أصل الحكاية:</strong><br>
                    {blk['origin']}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("**خطوات التنفيذ:**")
            for idx, step in enumerate(blk["steps"], start=1):
                st.write(f"{idx}. {step}")

            if st.button(f"اعتماد هذه اللبنة كـ (جارية الآن)", key=blk["name"]):
                st.session_state.current_block = blk["name"]
                st.success(f"تم تعيين ({blk['name']}) كلبنة حالية.")

# ==========================================
# 3. المختبر والمساعد
# ==========================================
elif page == "🧪 المختبر والمساعد":
    st.title("🧪 المختبر الذكي ومستشار الأخطاء")
    st.write(f"أنت الآن تعمل على: **{st.session_state.current_block}**")

    st.subheader("مخطط الفهم والمسار")
    st.code(
        """
        [المتحكم (ESP32 / Arduino)]
                 │
                 ▼ (إشارة تحكم + GND مشترك)
        [بطاقة تشغيل المحركات (L298N)]
                 │
                 ▼ (طاقة الحركة)
        [المحركات والعجلات]
        """,
        language="text",
    )

    st.subheader("مستشار الأخطاء والأدلة العلمية")
    issue_desc = st.text_area(
        "وش واجهتك من مشكلة أو ملاحظة أثناء التجربة؟",
        placeholder="مثال: المحرك ما يدور رغم إن اللمبات شغالة...",
    )

    if st.button("تشخيص المشكلة 🔍"):
        if issue_desc.strip():
            st.warning(
                "**السبب المحتمل والدليل العلمي:** في كثير من مشاريع المحركات، عدم وجود أرضي مشترك (Common Ground) "
                "أو انخفاض الجهد تحت حد التشغيل يسبب عدم استجابة المحرك. في الدوائر الكهربائية، فرق الجهد يُقاس "
                "بالنسبة لنقطة مرجعية مشتركة، وبدونها تصبح الإشارة غير مستقرة."
            )
        else:
            st.info("اكتب وصفاً مختصراً للمشكلة أولاً عشان نحللها لك.")

    st.markdown("---")
    st.subheader("توثيق لحظة النجاح ✨")
    success_story = st.text_input(
        "اكتب جملة تحفظ فيها وش تعلمته أو وش اللي ضبط معك:",
        placeholder="مثال: عرفت إن توحيد الـ GND خلّى الإشارة توصل صح والمحرك اشتغل!",
    )
    earned_pts = st.slider("نقاط إنجاز هذه اللبنة", min_value=50, max_value=300, value=150, step=50)

    if st.button("إتمام اللبنة وإضافة النقاط 🏆"):
        note_text = success_story.strip() if success_story.strip() else "أنجزت اللبنة وطبقت الخطوات بنجاح."
        st.session_state.completed_blocks.append(
            {
                "title": st.session_state.current_block,
                "story_note": note_text,
                "points": earned_pts,
            }
        )
        st.session_state.points += earned_pts
        st.balloons()
        st.success(f"كفو! تمت إضافة {earned_pts} نقطة إلى ملفك الشخصي.")

# ==========================================
# 4. ملفي
# ==========================================
elif page == "🏆 ملفي":
    st.title("🏆 ملف الإنجاز")

    c1, c2 = st.columns(2)
    c1.metric("إجمالي نقاط الشجاعة", f"{st.session_state.points} نقطة")
    c2.metric("عدد اللبنات المنجزة", f"{len(st.session_state.completed_blocks)}")

    st.subheader("الأوسمة")
    badges = ["🏅 أول خطوة"]
    if st.session_state.points >= 500:
        badges.append("⚡ مثابر واصل")
    if len(st.session_state.completed_blocks) >= 2:
        badges.append("🧱 باني اللبنات")
    st.write("  •  ".join(badges))

    st.subheader("سجل اللبنات المنجزة وقصصها")
    for item in reversed(st.session_state.completed_blocks):
        st.markdown(
            f"""
            <div class="story-box">
                <strong>✅ {item['title']}</strong> (+{item['points']} نقطة)<br>
                <span>قصة الإنجاز: {item['story_note']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
