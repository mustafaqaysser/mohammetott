# «نسافر قبلك» — ريلز إنستغرام (حفاوة المسافرون)

فيلم موشن جرافيك عمودي 1080×1920، مدته 80 ثانية، مبني بالكامل بالكود: الصورة والحركة والموسيقى والمؤثرات.
الفيديو يرجع لبدايته بدون فاصل: يبدأ بالفنجان وينتهي بالفنجان.

- `index.html`: المعاينة الحية. افتحه في المتصفح: R إعادة، F ملء الشاشة، مسافة للتشغيل بالصوت.
- `src/`: الكود (app.js المشاهد، style.css، template.html) ← `python3 build.py` يبني `index.html`.
- `audio.py`: الموسيقى والمؤثرات (عود بمقام الكرد، دف، ضربات، ساعة، صوت الفنجان) ← `build/music.wav`.
- `render.cjs`: يصوّر الإطارات بـ Playwright ← `node render.cjs frames build/frames 30 4`.
- `mix.py`: يركّب مقاطع الصوت من `voice/` فوق الموسيقى ويطلع الـ MP4.
- `voice/README.md`: قائمة مقاطع الصوت المطلوبة من Google AI Studio وتوقيت كل واحد.

ملاحظة: نقاط الدول الـ 21 على الخريطة توضيحية. ضع القائمة الحقيقية في `DEST` داخل `src/app.js`.

## الصوت (تسجيل واحد متواصل)
`voice/full-take.wav` هو تسجيل Google AI Studio. خطوات ربطه:

    python3 align.py     # يحدد مكان كل جملة في التسجيل
    python3 retime.py    # يضيف وقفات درامية، ويطلع خريطة توقيت الصورة والكلام المكتوب (src/timing.json)
    python3 audio.py && python3 build.py
    node render.cjs frames build/frames 30 4
    python3 mix.py       # -> hafawa-reel.mp4
