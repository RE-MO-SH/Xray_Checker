# Xray Checker  
**Advanced GUI Tool for V2ray Proxy Validation, Speed Testing & VPN Toggle**

---

## 📖 English Documentation

### Overview

**Xray Checker** is a cross‑platform GUI application built with Python and Tkinter. It helps you:

- Load VLESS configuration links from a local file or from subscription URLs (base64‑encoded).
- Validate each configuration using `xray.exe` (test mode + real HTTP request) and measure latency.
- Run download speed tests on valid configs (default: 1 MB file).
- Fetch geolocation (city & country) of the server IP via multiple fallback services.
- Sort results by ping or speed.
- Apply the best config as a **System Proxy** (Windows) or as a **Local SOCKS5/HTTP Proxy** on `127.0.0.1:10808`.
- Toggle VPN on/off with one click.
- Copy any config to clipboard or generate a QR code.

The tool is **multi‑threaded** for high speed, **robust** against network errors (retries, rotating User‑Agents), and **user‑friendly** (progress bar, ETA, live log).

---

### Requirements & Dependencies

- **Python 3.7+** (tested on Windows; Linux/macOS may work with small adjustments).
- **xray.exe** – download from [Xray‑core releases](https://github.com/XTLS/Xray-core/releases).
- **Python packages** (install via `pip`):

  ```bash
  pip install pillow qrcode

    tkinter – normally bundled with Python.

    Pillow – for image handling (icons, QR codes).

    qrcode – optional; needed only for QR code generation.

    Windows – the system‑proxy feature uses winreg and ctypes; it works only on Windows.

Installation & Setup

    Clone or download this repository.

    Place xray.exe in the same directory as the script (or specify its full path later).

    Install dependencies (if missing):
    bash

    pip install pillow qrcode

    Run the script:
    bash

    python xray_tester.py

    (You can also package it as a standalone .exe with PyInstaller.)

How to Use

    Input file – a .txt file containing:

        VLESS links (one per line, starting with vless://), or

        Subscription URLs (starting with http:// or https://).
        The tool will download all subscriptions, remove duplicates, and save all fetched links.

    Output file – where validated configs are saved (default: sub_valid.txt).

    Valid Configs File (optional) – load an existing list of valid configs for re‑testing (e.g., to run speed tests again).

    xray.exe Path – browse to the location of xray.exe.

    Threads – number of concurrent workers (default 100). Adjust based on your CPU and network.

    Max Latency (ms) – configs with ping above this value are rejected (default 5000).

    Test URL – HTTP endpoint used for latency checks (default: http://www.gstatic.com/generate_204).

    Speed Test File – URL of a file to download for speed measurement (default: http://speedtest.tele2.net/1MB.zip).

    Checkboxes:

        Enable Speed Test – after validation, run speed tests on all valid configs.

        Auto‑apply VPN – automatically apply the best config as VPN after testing.

        Sort by Speed – sort results by speed (otherwise by ping).

    VPN Mode – choose between:

        System Proxy (Windows only) – sets the system proxy, routing all computer traffic.

        Local Proxy (SOCKS5/HTTP) – runs a local proxy on 127.0.0.1:10808; you can manually configure browsers/apps.

    Start – begins validation. If paused, the button changes to Resume.

    Stop – pauses the current operation; you can resume later.

    Re‑test Valid Configs – runs speed tests and geolocation on already validated configs (from the valid file or previous run).

    VPN ON/OFF – toggles VPN using the selected config (best or currently highlighted).

    Results Table – double‑click any row to copy the full config to clipboard and display its QR code. Single‑click selects it for VPN.

Workflow Explanation

    Reading Input

        The tool reads the input file line by line.

        Lines starting with http:// or https:// are treated as subscription URLs; these are downloaded (base64‑decoded) to extract VLESS links.

        All VLESS links are collected, deduplicated, and saved to an all_links_*.txt file.

    Validation

        For each VLESS link, a temporary JSON configuration is built for Xray.

        The tool runs xray -test to verify the config syntax.

        If successful, it launches Xray with that config on a free port, connects via SOCKS5, and sends an HTTP request to the test URL.

        If the response is 200 or 204 within the allowed latency, the config is marked valid and saved to the output file.

    Speed Testing (if enabled)

        Each valid config is started again, and a file download is performed through the proxy.

        Download speed is calculated in Mbps.

        Geolocation is fetched by resolving the server hostname and querying multiple IP‑geo services (with caching).

    Results Display

        Valid configs are shown in a table with columns: row number, ping, speed, and location.

        The table can be sorted by speed or ping.

    VPN Application

        The user can select any row (or let the tool pick the best) and click Apply VPN.

        Xray runs in the background with that config, and the chosen proxy mode is activated (system proxy or local SOCKS/HTTP).

        The VPN ON/OFF button toggles the service.

Troubleshooting

    xray.exe not found – verify the path or place it in the script folder.

    403 errors when downloading subscriptions – the tool retries with different User‑Agents; if it still fails, check the subscription URL.

    VPN not working – ensure the config is valid and Xray can start; read the log for errors.

    Geolocation shows "Unknown" – the tool tries many services, but if all fail, it falls back to "Unknown". You can manually check the IP.

    QR code not generated – install qrcode and Pillow (pip install qrcode pillow).

License

This project is open‑source and released under the MIT License. Feel free to modify and distribute.
<hr dir="rtl">
<div dir="rtl">راهنمای فارسی</div>
<div dir="rtl">
نمای کلی

نرم‌افزار Xray Checker یک برنامهٔ گرافیکی (ساخته‌شده با Python و Tkinter) است که به شما کمک می‌کند:

    لینک‌های تنظیمات VLESS را از یک فایل محلی یا از آدرس‌های اشتراک (کدگذاری base64) بارگذاری کنید.

    هر تنظیمات را با استفاده از xray.exe (حالت تست + درخواست HTTP واقعی) اعتبارسنجی کرده و تأخیر را اندازه‌گیری کنید.

    تست سرعت دانلود بر روی تنظیمات معتبر اجرا کنید (فایل ۱ مگابایتی به‌طور پیش‌فرض).

    موقعیت جغرافیایی (شهر و کشور) سرور را با استفاده از چندین سرویس پشتیبان دریافت کنید.

    نتایج را بر اساس پینگ یا سرعت مرتب کنید.

    بهترین تنظیمات را به‌عنوان پروکسی سیستمی (ویندوز) یا پروکسی محلی SOCKS5/HTTP روی پورت 10808 اعمال کنید.

    وضعیت VPN را با یک کلیک روشن/خاموش کنید.

    هر تنظیمات را در کلیپ‌بورد کپی کنید یا کد QR آن را تولید کنید.

این ابزار چند‌نخی (برای سرعت بالا)، مقاوم (در برابر خطاهای شبکه با تلاش مجدد و تغییر User‑Agent) و کاربرپسند (نوار پیشرفت، زمان باقیمانده و لاگ زنده) است.
پیش‌نیازها و کتابخانه‌ها

    Python 3.7+ (تست شده روی ویندوز؛ لینوکس/مک نیز با تغییرات جزئی قابل اجراست).

    فایل xray.exe – از صفحهٔ انتشارات Xray‑core دانلود کنید.

    کتابخانه‌های Python (با pip نصب کنید):
    bash

    pip install pillow qrcode


    ویندوز – ویژگی پروکسی سیستمی از winreg و ctypes استفاده می‌کند و فقط روی ویندوز کار می‌کند.

نصب و راه‌اندازی

    مخزن را کلون یا دانلود کنید.

    فایل xray.exe را در همان پوشهٔ اسکریپت قرار دهید (یا بعداً مسیر کامل آن را مشخص کنید).

    کتابخانه‌های مورد نیاز را نصب کنید (در صورت عدم نصب):
    bash

    pip install pillow qrcode

    اسکریپت را اجرا کنید:
    bash

    python xray_tester.py

    (همچنین می‌توانید با PyInstaller یک فایل .exe مستقل بسازید.)

نحوهٔ استفاده

    فایل ورودی – یک فایل .txt شامل:

        لینک‌های VLESS (هر خط یک لینک با شروع vless://)، یا

        آدرس‌های اشتراک (شروع با http:// یا https://).
        ابزار تمام اشتراک‌ها را دانلود، تکراری‌ها را حذف و همهٔ لینک‌های دریافت‌شده را ذخیره می‌کند.

    فایل خروجی – محل ذخیرهٔ تنظیمات معتبر (پیش‌فرض: sub_valid.txt).

    فایل تنظیمات معتبر (اختیاری) – می‌توانید لیست موجودی از تنظیمات معتبر را برای تست مجدد بارگذاری کنید (مثلاً برای اجرای مجدد تست سرعت).

    مسیر xray.exe – مسیر فایل xray.exe را انتخاب کنید.

    تعداد نخ‌ها – تعداد کارگرهای هم‌زمان (پیش‌فرض ۱۰۰). بر اساس پردازنده و شبکه تنظیم کنید.

    حداکثر تأخیر (ms) – تنظیماتی با پینگ بیشتر از این مقدار رد می‌شوند (پیش‌فرض ۵۰۰۰).

    آدرس تست HTTP – آدرسی که برای اندازه‌گیری تأخیر استفاده می‌شود (پیش‌فرض: http://www.gstatic.com/generate_204).

    فایل تست سرعت – آدرس فایلی که برای تست سرعت دانلود می‌شود (پیش‌فرض: http://speedtest.tele2.net/1MB.zip).

    چک‌باکس‌ها:

        فعال‌سازی تست سرعت – پس از اعتبارسنجی، تست سرعت روی همهٔ تنظیمات معتبر اجرا شود.

        اعمال خودکار VPN – پس از تست، بهترین تنظیمات به‌عنوان VPN اعمال شود.

        مرتب‌سازی بر اساس سرعت – جدول نتایج بر اساس سرعت مرتب شود (در غیر این صورت بر اساس پینگ).

    حالت VPN – انتخاب بین:

        پروکسی سیستمی (فقط ویندوز) – پروکسی سیستم را تنظیم کرده و تمام ترافیک کامپیوتر را هدایت می‌کند.

        پروکسی محلی (SOCKS5/HTTP) – یک پروکسی محلی روی 127.0.0.1:10808 راه‌اندازی می‌کند؛ می‌توانید مرورگر/برنامه‌ها را به‌صورت دستی تنظیم کنید.

    شروع – فرآیند اعتبارسنجی را آغاز می‌کند. در حالت مکث، دکمه به ادامه تغییر می‌کند.

    توقف – عملیات فعلی را متوقف می‌کند؛ بعداً می‌توانید ادامه دهید.

    تست مجدد تنظیمات معتبر – تست سرعت و موقعیت‌یابی روی تنظیمات معتبر (از فایل معتبر یا اجرای قبلی) اجرا می‌شود.

    تنظیم VPN روشن/خاموش – VPN را با استفاده از تنظیمات انتخاب‌شده (بهترین یا هایلایت‌شده) روشن/خاموش می‌کند.

    جدول نتایج – با دوبار کلیک روی هر سطر، لینک کامل در کلیپ‌بورد کپی شده و کد QR آن نمایش داده می‌شود. با یک کلیک، آن تنظیمات برای VPN انتخاب می‌شود.

شرح روند کار

    خواندن ورودی

        ابزار فایل ورودی را خط به خط می‌خواند.

        خطوطی که با http:// یا https:// شروع می‌شوند به‌عنوان آدرس اشتراک در نظر گرفته شده، دانلود شده (base64‑decoded) و لینک‌های VLESS استخراج می‌شوند.

        همهٔ لینک‌های VLESS جمع‌آوری، تکراری‌ها حذف و در فایل all_links_*.txt ذخیره می‌شوند.

    اعتبارسنجی

        برای هر لینک VLESS، یک فایل JSON موقت برای Xray ساخته می‌شود.

        ابزار xray -test را اجرا کرده و صحت تنظیمات را بررسی می‌کند.

        در صورت موفقیت، Xray را با آن تنظیمات روی یک پورت آزاد اجرا کرده، از طریق SOCKS5 متصل شده و یک درخواست HTTP به آدرس تست ارسال می‌کند.

        اگر پاسخ 200 یا 204 در بازهٔ تأخیر مجاز دریافت شود، آن تنظیمات معتبر محسوب شده و در فایل خروجی ذخیره می‌شود.

    تست سرعت (در صورت فعال بودن)

        هر تنظیمات معتبر دوباره اجرا شده و یک فایل از طریق پروکسی دانلود می‌شود.

        سرعت دانلود بر حسب مگابیت بر ثانیه محاسبه می‌شود.

        موقعیت‌یابی با حل کردن نام سرور و پرسش از چندین سرویس موقعیت‌یابی IP (با کش کردن نتایج) انجام می‌شود.

    نمایش نتایج

        تنظیمات معتبر در جدولی با ستون‌های: شماره سطر، پینگ، سرعت و موقعیت نمایش داده می‌شوند.

        جدول قابل مرتب‌سازی بر اساس سرعت یا پینگ است.

    اعمال VPN

        کاربر می‌تواند هر سطر را انتخاب کند (یا اجازه دهد ابزار بهترین را انتخاب کند) و روی اعمال VPN کلیک کند.

        Xray در پس‌زمینه با آن تنظیمات اجرا شده و حالت پروکسی انتخاب‌شده (سیستمی یا محلی) فعال می‌شود.

        دکمهٔ VPN روشن/خاموش این سرویس را قطع/وصل می‌کند.

عیب‌یابی

    xray.exe پیدا نشد – مسیر را بررسی کنید یا فایل را در پوشهٔ اسکریپت قرار دهید.

    خطای ۴۰۳ در دانلود اشتراک – ابزار با User‑Agentهای مختلف تلاش مجدد می‌کند؛ در صورت ادامهٔ خطا، آدرس اشتراک را بررسی کنید.

    VPN کار نمی‌کند – مطمئن شوید تنظیمات معتبر است و Xray می‌تواند اجرا شود. لاگ را برای خطاها بررسی کنید.

    موقعیت‌یابی "Unknown" نشان می‌دهد – ابزار از چندین سرویس استفاده می‌کند، اما در صورت شکست همه، "Unknown" نمایش داده می‌شود. می‌توانید IP را به‌صورت دستی بررسی کنید.

    کد QR تولید نمی‌شود – کتابخانه‌های qrcode و Pillow را نصب کنید (pip install qrcode pillow).

مجوز

این پروژه متن‌باز بوده و تحت مجوز MIT منتشر می‌شود. می‌توانید آزادانه آن را تغییر داده و توزیع کنید.
</div> ```
