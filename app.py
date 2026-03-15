import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import io

# إعداد شكل الصفحة
st.set_page_config(page_title="نظام إصدار الشهادات", page_icon="🎓", layout="centered")

# تنسيق العنوان الرئيسي وتوسيطه
st.markdown("<h3 style='text-align: center; color: #003366;'>  خدمة إصدار شهادات اللقاءات الرمضانية في التقويم المدرسي</h3>", unsafe_allow_html=True)

# تنسيق النص الترحيبي وتوسيطه
st.markdown("<p style='text-align: center; font-size: 18px;'> الرجاء إدخال رقم الهوية وتحميل شهاداتك</p>", unsafe_allow_html=True)
# دالة إصلاح النص العربي للصور
def fix_arabic(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

@st.cache_data
def load_data():
    return pd.read_excel('certificates_output.xlsx')

try:
    df = load_data()
    user_id = st.text_input(" ", placeholder="أدخل رقم الهوية المكون من 10 أرقام...")
    
    if st.button("🔍 البحث عن الشهادات"):
    
        if user_id:
            result = df[df['id'].astype(str) == str(user_id)]
            count = len(result)
            
            if count > 0:
                st.info(f"تم العثور على ({count}) سجل/سجلات. جاري تجهيز الشهادات...")
                
                for index, row in result.iterrows():
                    user_name = row['name']
                    date_val = row['date']
                    safe_date = str(date_val).replace("/", "-").replace("\\", "-")
                    
                    # 1. فتح صورة الشهادة الفارغة
                    img = Image.open("template.png")
                    draw = ImageDraw.Draw(img)
                    
                    # 2. تحميل الخط (تأكد من وجود ملف font.ttf في المجلد)
                    # يمكنك تغيير رقم 40 لتكبير أو تصغير الخط
                    font_large = ImageFont.truetype("majalla.ttf", 35) 
                    font_small = ImageFont.truetype("majalla.ttf", 30)
                    
                    # 3. تجهيز النصوص العربية
                    name_text = fix_arabic(user_name)
                    id_text = fix_arabic(user_id)
                    date_text = fix_arabic(date_val)
                    
                    # 4. كتابة النصوص على الصورة (الإحداثيات X و Y)
                    # --- التعديل الجديد لحل مشكلة الأسماء الطويلة ---

                    # 1. ضع هنا إحداثي X الثابت الذي يقع "مباشرة" على يسار كلمة (الأستاذ/ة :)
                    fixed_right_x = 1100 # (قم بتغيير هذا الرقم ليكون بجوار النقطتين الرأسيتين تماماً)
                    y_position = 470    # (ضع هنا إحداثي Y الخاص بالاسم كما كان لديك سابقاً)

                    # 2. أمر يجعل بايثون يقيس عرض الاسم بالبيكسل قبل طباعته
                    text_width = font_large.getlength(name_text)

                    # 3. حساب نقطة البداية الجديدة (نطرح عرض النص من النقطة الثابتة)
                    start_x = fixed_right_x - text_width

                    # 4. طباعة الاسم باستخدام نقطة البداية الجديدة
                    draw.text((start_x, y_position), name_text, font=font_large, fill=(0, 51, 102))

                    # ------------------------------------------------
                    draw.text((340, 480), id_text, font=font_small, fill=(0, 0, 0))   # الهوية
                    draw.text((1300, 810), date_text, font=font_small, fill=(0, 0, 0)) # التاريخ
                    draw.text((1080, 810), date_text, font=font_small, fill=(0, 0, 0)) # التاريخ
                    # 5. تحويل الصورة إلى ملف PDF في الذاكرة
                    pdf_buffer = io.BytesIO()

                    # التعديل هنا: نقوم بتحويل الصورة لنظام RGB الذي يقبله الـ PDF
                    img_rgb = img.convert('RGB')

                    # لاحظ أننا نستخدم img_rgb للحفظ الآن بدلاً من img القديمة
                    img_rgb.save(pdf_buffer, format='PDF') 

                    pdf_bytes = pdf_buffer.getvalue()
                    
                    # عرض زر التحميل
                    with st.container():
                        st.success(f"🎉 تم تجهيز شهادة حضور يوم: {date_val}")
                        st.download_button(
                            label=f"📥 تحميل شهادة ({date_val})",
                            data=pdf_bytes,
                            file_name=f"Certificate_{user_id}_{safe_date}.pdf",
                            mime="application/pdf",
                            key=f"btn_{user_id}_{index}" 
                        )
                        st.markdown("---")
            else:
                st.error("عفواً، لم يتم العثور على سجل يطابق رقم الهوية.")
        else:
            st.warning("الرجاء إدخال رقم الهوية أولاً.")

except FileNotFoundError as e:
    st.error(f"⚠️ خطأ في الملفات: {e}")
except Exception as e:
    st.error(f"حدث خطأ: {e}")
