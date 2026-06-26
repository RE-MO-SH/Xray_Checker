Xray Tester – Advanced GUI with Speed Test & VPN Toggle

English | فارسی
📖 Overview (English)

Xray Tester is a cross-platform GUI tool (built with Tkinter) for testing and managing VLESS proxy configurations. It supports:

    Loading VLESS links directly or from subscription URLs (base64‑encoded).

    Validating each config using xray.exe (test mode + real HTTP request) and measuring latency.

    Performing download speed tests on valid configs (1 MB file by default).

    Geolocation lookup (city & country) based on the server IP.

    Sorting results by ping or speed.

    Applying the best configuration as a system proxy (Windows) or as a local SOCKS5/HTTP proxy on 127.0.0.1:10808.

    Toggling VPN on/off with one click.

    Viewing, copying to clipboard, or generating a QR code for any config.

The tool is designed to be fast (multi‑threaded), robust (handles 403 errors, retries, and multiple geolocation services), and user‑friendly (progress bar, ETA, live log).
📦 Requirements & Dependencies

    Python 3.7+ (tested on Windows, but may work on Linux/macOS with adjustments).

    xray.exe – the Xray core binary (download from Xray‑core).

    Required Python libraries (install via pip if missing):
    bash

    pip install pillow qrcode

        tkinter – usually bundled with Python.

        Pillow – for image handling (icon, QR code).

        qrcode – optional, for QR code generation (skip if not needed).

    Windows – the system‑proxy feature uses winreg and ctypes; only available on Windows.

🚀 Installation & Setup

    Clone or download this repository.

    Place xray.exe in the same directory as the script, or specify its full path in the GUI.

    Install dependencies (if not already installed):
    bash

    pip install pillow qrcode

    Run the script:
    bash

    python xray_tester.py

    (If you use PyInstaller, you can compile to a standalone .exe.)

🧭 How to Use

    Input file – provide a .txt file containing:

        VLESS links (one per line, starting with vless://), or

        Subscription URLs (starting with http:// or https://).
        The tool will download all subscriptions, deduplicate, and save all fetched links.

    Output file – where valid configs will be saved (default: sub_valid.txt).

    Valid Configs File (optional) – you can load an existing list of valid configs to re‑test (e.g., for speed tests).

    xray.exe Path – browse to the location of xray.exe.

    Threads – number of concurrent workers (default 100). Adjust based on your CPU and network.

    Max Latency (ms) – reject configs with ping above this value (default 5000).

    Test URL – the HTTP endpoint used for latency checks (default: http://www.gstatic.com/generate_204).

    Speed Test File – the URL of a file to download for speed measurement (default: http://speedtest.tele2.net/1MB.zip).

    Checkboxes:

        Enable Speed Test – after validation, run download speed tests on all valid configs.

        Auto‑apply VPN – automatically apply the best config as VPN after testing.

        Sort by Speed – sort the results table by speed (else by ping).

    VPN Mode – choose between:

        System Proxy (Windows only) – sets the system proxy, routing all computer traffic.

        Local Proxy (SOCKS5/HTTP) – runs a local proxy on 127.0.0.1:10808; you can configure browsers/apps manually.

    Start – begins the validation process. If paused, the button changes to Resume.

    Stop – pauses the current operation. You can resume later.

    Re‑test Valid Configs – runs speed tests and geolocation on already validated configs (from the valid file or from the previous run).

    VPN ON/OFF – toggles VPN using the selected config (best or currently highlighted).

    Results Table – double‑click any row to copy the full config to clipboard and show its QR code. Single‑click selects it for VPN.

⚙️ Features in Detail

    Subscription download – handles HTTP 403 errors by rotating User‑Agents.

    Deduplication – removes duplicate links automatically.

    Validation – for each config:

        Builds a temporary Xray JSON config.

        Runs xray -test to check the config syntax.

        Starts Xray in the background, connects via SOCKS5, and sends a test HTTP request.

        Records latency if successful.

    Speed test – downloads a file (1 MB by default) through the proxy and calculates download speed in Mbps.

    Geolocation – tries over 20 different IP‑geolocation services to fetch city and country. Caches results.

    VPN Toggle – starts/stops Xray with the selected config. In system‑proxy mode, it modifies Windows proxy settings automatically.

    QR Code – generates a QR code from any config (requires qrcode and Pillow).

    Progress & ETA – real‑time progress bar, percentage, and estimated remaining time.

🛠 Troubleshooting

    xray.exe not found – ensure the path is correct, or place xray.exe in the same folder as the script.

    403 errors when downloading subscriptions – the tool will retry with different User‑Agents; if it still fails, check the subscription URL.

    VPN not working – make sure the config is valid and Xray can start. Check the log for errors.

    Geolocation shows "Unknown" – the tool tries many services, but if all fail, it defaults to "Unknown". You can manually check the IP.

    QR code not generated – install qrcode and Pillow (pip install qrcode pillow).

📜 License

This project is open‑source and available under the MIT License. Feel free to modify and distribute.
<hr dir="rtl">
<div dir="rtl">خوانش (فارسی)</div>
<div dir="rtl">
📖 نمای کلی

Xray Tester یک ابزار گرافیکی (ساخته‌شده با Tkinter) برای تست و مدیریت تنظیمات پروکسی VLESS است. قابلیت‌های کلیدی:

    بارگذاری لینک‌های VLESS به‌طور مستقیم یا از طریق آدرس‌های اشتراک (کدگذاری base64).

    اعتبارسنجی هر تنظیمات با استفاده از xray.exe (حالت تست + درخواست HTTP واقعی) و اندازه‌گیری تأخیر.

    انجام تست سرعت دانلود بر روی تنظیمات معتبر (فایل ۱ مگابایتی به‌طور پیش‌فرض).

    تشخیص موقعیت جغرافیایی (شهر و کشور) بر اساس IP سرور.

    مرتب‌سازی نتایج بر اساس پینگ یا سرعت.

    اعمال بهترین تنظیمات به‌عنوان پروکسی سیستمی (ویندوز) یا پروکسی محلی SOCKS5/HTTP روی 127.0.0.1:10808.

    روشن/خاموش کردن VPN با یک کلیک.

    مشاهده، کپی در کلیپ‌بورد یا تولید کد QR برای هر تنظیمات.

این ابزار سریع (چند‌نخی)، مقاوم (مدیریت خطاهای ۴۰۳، تلاش مجدد و استفاده از چندین سرویس موقعیت‌یابی) و کاربرپسند (نوار پیشرفت، زمان باقیمانده و لاگ زنده) است.
📦 پیش‌نیازها و کتابخانه‌ها

    Python 3.7+ (تست شده روی ویندوز، اما احتمالاً روی لینوکس/مک نیز قابل اجراست).

    xray.exe – فایل اجرایی Xray (از Xray‑core دانلود کنید).

    کتابخانه‌های Python (در صورت نیاز نصب کنید):
    bash

    pip install pillow qrcode

        tkinter – معمولاً همراه با Python نصب می‌شود.

        Pillow – برای پردازش تصویر (آیکون، کد QR).

        qrcode – اختیاری، برای تولید کد QR (در صورت نیاز نصب کنید).

    ویندوز – ویژگی پروکسی سیستمی از winreg و ctypes استفاده می‌کند و فقط روی ویندوز کار می‌کند.

🚀 نصب و راه‌اندازی

    مخزن را کلون یا دانلود کنید.

    فایل xray.exe را در همان پوشه اسکریپت قرار دهید، یا مسیر آن را در رابط کاربری مشخص کنید.

    کتابخانه‌های مورد نیاز را نصب کنید (در صورت عدم نصب):
    bash

    pip install pillow qrcode

    اسکریپت را اجرا کنید:
    bash

    python xray_tester.py

    (اگر از PyInstaller استفاده می‌کنید، می‌توانید یک فایل .exe مستقل بسازید.)

🧭 نحوه استفاده

    فایل ورودی – یک فایل .txt شامل:

        لینک‌های VLESS (هر خط یک لینک، با شروع vless://)، یا

        آدرس‌های اشتراک (شروع با http:// یا https://).
        ابزار تمام اشتراک‌ها را دانلود، تکراری‌ها را حذف و همه لینک‌ها را ذخیره می‌کند.

    فایل خروجی – محل ذخیره تنظیمات معتبر (پیش‌فرض: sub_valid.txt).

    فایل تنظیمات معتبر (اختیاری) – می‌توانید لیست موجودی از تنظیمات معتبر را برای تست مجدد بارگذاری کنید (مثلاً برای تست سرعت).

    مسیر xray.exe – مسیر فایل xray.exe را انتخاب کنید.

    تعداد نخ‌ها – تعداد کارگرهای هم‌زمان (پیش‌فرض ۱۰۰). بر اساس پردازنده و شبکه تنظیم کنید.

    حداکثر تأخیر (ms) – تنظیماتی با پینگ بیشتر از این مقدار رد می‌شوند (پیش‌فرض ۵۰۰۰).

    آدرس تست HTTP – آدرسی که برای اندازه‌گیری تأخیر استفاده می‌شود (پیش‌فرض: http://www.gstatic.com/generate_204).

    فایل تست سرعت – آدرس فایلی که برای تست سرعت دانلود می‌شود (پیش‌فرض: http://speedtest.tele2.net/1MB.zip).

    چک‌باکس‌ها:

        فعال‌سازی تست سرعت – پس از اعتبارسنجی، تست سرعت روی همه تنظیمات معتبر انجام شود.

        اعمال خودکار VPN – پس از تست، بهترین تنظیمات به‌عنوان VPN اعمال شود.

        مرتب‌سازی بر اساس سرعت – جدول نتایج بر اساس سرعت مرتب شود (در غیر این صورت بر اساس پینگ).

    حالت VPN – انتخاب بین:

        پروکسی سیستمی (فقط ویندوز) – پروکسی سیستم را تنظیم کرده و تمام ترافیک کامپیوتر را هدایت می‌کند.

        پروکسی محلی (SOCKS5/HTTP) – یک پروکسی محلی روی 127.0.0.1:10808 راه‌اندازی می‌کند؛ می‌توانید مرورگر/برنامه‌ها را به‌صورت دستی تنظیم کنید.

    شروع – فرآیند اعتبارسنجی را آغاز می‌کند. در حالت مکث، دکمه به ادامه تغییر می‌کند.

    توقف – عملیات فعلی را متوقف می‌کند. بعداً می‌توانید ادامه دهید.

    تست مجدد تنظیمات معتبر – تست سرعت و موقعیت‌یابی روی تنظیمات معتبر (از فایل معتبر یا اجرای قبلی) انجام می‌دهد.

    VPN روشن/خاموش – VPN را با استفاده از تنظیمات انتخاب‌شده (بهترین یا هایلایت‌شده) روشن/خاموش می‌کند.

    جدول نتایج – با دوبار کلیک روی هر سطر، لینک کامل در کلیپ‌بورد کپی شده و کد QR آن نمایش داده می‌شود. با یک کلیک، آن تنظیمات برای VPN انتخاب می‌شود.

⚙️ جزئیات قابلیت‌ها

    دانلود اشتراک – با چرخش User‑Agent خطاهای ۴۰۳ را مدیریت می‌کند.

    حذف تکراری‌ها – به‌طور خودکار لینک‌های تکراری را حذف می‌کند.

    اعتبارسنجی – برای هر تنظیمات:

        یک فایل JSON موقت برای Xray می‌سازد.

        xray -test را اجرا کرده و صحت تنظیمات را بررسی می‌کند.

        Xray را در پس‌زمینه اجرا کرده، از طریق SOCKS5 متصل شده و یک درخواست HTTP تست ارسال می‌کند.

        در صورت موفقیت، تأخیر را ثبت می‌کند.

    تست سرعت – یک فایل (۱ مگابایت پیش‌فرض) را از طریق پروکسی دانلود کرده و سرعت دانلود را بر حسب مگابیت بر ثانیه محاسبه می‌کند.

    موقعیت‌یابی – بیش از ۲۰ سرویس موقعیت‌یابی IP را امتحان کرده و شهر و کشور را استخراج می‌کند. نتایج کش می‌شوند.

    کلید VPN – Xray را با تنظیمات انتخاب‌شده شروع/متوقف می‌کند. در حالت پروکسی سیستمی، تنظیمات پروکسی ویندوز را به‌طور خودکار تغییر می‌دهد.

    کد QR – از هر تنظیمات یک کد QR تولید می‌کند (نیازمند qrcode و Pillow).

    نوار پیشرفت و زمان باقیمانده – نمایش زنده درصد پیشرفت و زمان تخمینی باقیمانده.

🛠 عیب‌یابی

    xray.exe پیدا نشد – مسیر را بررسی کنید یا xray.exe را در پوشه اسکریپت قرار دهید.

    خطای ۴۰۳ در دانلود اشتراک – ابزار با User‑Agentهای مختلف تلاش مجدد می‌کند؛ در صورت ادامه خطا، آدرس اشتراک را بررسی کنید.

    VPN کار نمی‌کند – مطمئن شوید تنظیمات معتبر است و Xray می‌تواند اجرا شود. لاگ را برای خطاها بررسی کنید.

    موقعیت‌یابی "Unknown" نشان می‌دهد – ابزار از چندین سرویس استفاده می‌کند، اما در صورت شکست همه، "Unknown" نمایش داده می‌شود. می‌توانید IP را به‌صورت دستی بررسی کنید.

    کد QR تولید نمی‌شود – کتابخانه‌های qrcode و Pillow را نصب کنید (pip install qrcode pillow).

📜 مجوز

این پروژه متن‌باز بوده و تحت مجوز MIT منتشر می‌شود. می‌توانید آزادانه آن را تغییر داده و توزیع کنید.
</div>
This response is AI-generated, for reference only.
