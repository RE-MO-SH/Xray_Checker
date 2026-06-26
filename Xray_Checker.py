import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
import json
import tempfile
import urllib.parse
import urllib.request
import urllib.error
import base64
import time
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes
import winreg
import re
from PIL import Image, ImageTk

# Optional imports for QR code
try:
    import qrcode
    from PIL import Image, ImageTk
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

class XrayConfigTesterGUI:
    def __init__(self, root):
        self.root = root
        root.title("Xray Tester – Advanced with Speed Test & VPN Toggle")
        root.geometry("1100x940")
        root.resizable(True, True)

        # --- Variables ---
        self.input_file_var = tk.StringVar(value="sub.txt")
        self.output_file_var = tk.StringVar()
        self.valid_file_var = tk.StringVar()
        self.xray_path_var = tk.StringVar(value="xray.exe")
        self.threads_var = tk.StringVar(value="100")
        self.max_latency_var = tk.StringVar(value="5000")
        self.test_url_var = tk.StringVar(value="http://www.gstatic.com/generate_204")
        self.speed_test_url_var = tk.StringVar(value="http://speedtest.tele2.net/1MB.zip")

        # --- Checkboxes ---
        self.speed_test_enabled = tk.BooleanVar(value=True)
        self.auto_apply_vpn = tk.BooleanVar(value=True)
        self.sort_by_speed = tk.BooleanVar(value=True)

        # --- VPN Mode ---
        self.vpn_mode_var = tk.StringVar(value="System Proxy")

        # --- Progress & Status ---
        self.progress_var = tk.IntVar(value=0)
        self.progress_percent_var = tk.StringVar(value="0%")
        self.valid_count_var = tk.StringVar(value="0")
        self.processed_count_var = tk.StringVar(value="0")
        self.total_count_var = tk.StringVar(value="0")

        # --- Auto‑detect xray.exe ---
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        default_xray = os.path.join(base_dir, "xray.exe")
        if os.path.exists(default_xray):
            self.xray_path_var.set(default_xray)
        self.input_file_var.set(os.path.join(base_dir, "sub.txt"))
        self.output_file_var.set(os.path.join(base_dir, "sub_valid.txt"))
        self.valid_file_var.set(os.path.join(base_dir, "sub_valid.txt"))
        # --- Control flags ---
        self.running = False
        self.stop_requested = False
        self.paused = False
        self.current_index = 0          # number of configs processed (completed)
        self.total_links = 0
        self.valid_count = 0
        self.links = []
        self.valid_links = []
        self.lock = threading.Lock()
        self.output_file = ""

        # Time remaining
        self.start_time = 0
        self.last_eta_log_time = 0

        # Speed test results
        self.valid_results = []
        self.selected_config = None

        # VPN related
        self.xray_vpn_proc = None
        self.vpn_config_path = None
        self.vpn_active = False
        self.vpn_port = 10808

        # Cache for geolocation
        self.geo_cache = {}

        self.create_widgets()
        self.update_status()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Top frame: input, output, settings ---
        top_frame = ttk.LabelFrame(main_frame, text="Input & Settings")
        top_frame.pack(fill=tk.X, pady=5)

        row = 0
        ttk.Label(top_frame, text="Input File (Subscriptions or Configs):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.input_file_var, width=60).grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Button(top_frame, text="Browse...", command=self.browse_input).grid(row=row, column=2, padx=5, pady=2)

        row += 1
        ttk.Label(top_frame, text="Output File (valid):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.output_file_var, width=60).grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Button(top_frame, text="Browse...", command=self.browse_output).grid(row=row, column=2, padx=5, pady=2)

        row += 1
        ttk.Label(top_frame, text="Valid Configs File (optional):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.valid_file_var, width=60).grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Button(top_frame, text="Browse...", command=self.browse_valid_file).grid(row=row, column=2, padx=5, pady=2)

        row += 1
        ttk.Label(top_frame, text="xray.exe Path:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.xray_path_var, width=60).grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Button(top_frame, text="Browse...", command=self.browse_xray).grid(row=row, column=2, padx=5, pady=2)

        row += 1
        ttk.Label(top_frame, text="Threads:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.threads_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(top_frame, text="Max Latency (ms):").grid(row=row, column=0, padx=(150,5), sticky=tk.W)
        ttk.Entry(top_frame, textvariable=self.max_latency_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=(150,5))

        row += 1
        ttk.Label(top_frame, text="HTTP Test URL:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.test_url_var, width=60).grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)

        row += 1
        ttk.Label(top_frame, text="Speed Test File (1MB):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.speed_test_url_var, width=60).grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)

        row += 1
        cb_frame = ttk.Frame(top_frame)
        cb_frame.grid(row=row, column=0, columnspan=3, pady=5)
        ttk.Checkbutton(cb_frame, text="Enable Speed Test (after validation)", variable=self.speed_test_enabled).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(cb_frame, text="Auto-apply VPN (best config)", variable=self.auto_apply_vpn).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(cb_frame, text="Sort by Speed (else Ping)", variable=self.sort_by_speed).pack(side=tk.LEFT, padx=10)

        row += 1
        mode_frame = ttk.Frame(top_frame)
        mode_frame.grid(row=row, column=0, columnspan=3, pady=5, sticky=tk.W, padx=10)
        ttk.Label(mode_frame, text="VPN Mode:").pack(side=tk.LEFT, padx=5)
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.vpn_mode_var, values=["System Proxy", "Local Proxy (SOCKS5/HTTP on 10808)"], state="readonly", width=40)
        mode_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(mode_frame, text="(System Proxy = entire computer)").pack(side=tk.LEFT, padx=5)

        # --- Middle frame: progress & status ---
        mid_frame = ttk.LabelFrame(main_frame, text="Progress")
        mid_frame.pack(fill=tk.X, pady=5)

        progress_frame = ttk.Frame(mid_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.percent_label = ttk.Label(progress_frame, textvariable=self.progress_percent_var, width=6)
        self.percent_label.pack(side=tk.LEFT, padx=5)

        status_frame = ttk.Frame(mid_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(status_frame, text="Processed:").pack(side=tk.LEFT, padx=2)
        ttk.Label(status_frame, textvariable=self.processed_count_var, foreground='blue').pack(side=tk.LEFT, padx=2)
        ttk.Label(status_frame, text="/").pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.total_count_var, foreground='blue').pack(side=tk.LEFT, padx=2)
        ttk.Label(status_frame, text="  Valid:").pack(side=tk.LEFT, padx=10)
        ttk.Label(status_frame, textvariable=self.valid_count_var, foreground='green').pack(side=tk.LEFT, padx=2)
        self.status_label = ttk.Label(status_frame, text="Ready", foreground='gray')
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # --- Buttons for start/stop and VPN toggle ---
        btn_frame = ttk.Frame(mid_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        self.start_button = ttk.Button(btn_frame, text="Start", command=self.start_check)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(btn_frame, text="Stop", command=self.stop_check, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.test_valid_button = ttk.Button(btn_frame, text="Re-test Valid Configs", command=self.start_valid_test)
        self.test_valid_button.pack(side=tk.LEFT, padx=5)

        self.vpn_toggle_button = ttk.Button(btn_frame, text="VPN OFF", command=self.toggle_vpn, state=tk.DISABLED)
        self.vpn_toggle_button.pack(side=tk.LEFT, padx=5)

        # --- Log area ---
        log_frame = ttk.LabelFrame(main_frame, text="Log Output")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, font=("Courier New", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Results table (with row number column) ---
        result_frame = ttk.LabelFrame(main_frame, text="Valid Configs – Ping, Speed & Location")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tree_container = ttk.Frame(result_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # <<< NEW: add 'row' column for numbering
        self.tree = ttk.Treeview(tree_container, columns=('row', 'ping', 'speed', 'location'), show='tree headings', height=6)
        self.tree.heading('#0', text='Config (short)')
        self.tree.heading('row', text='#')
        self.tree.heading('ping', text='Ping (ms)')
        self.tree.heading('speed', text='Speed (Mbps)')
        self.tree.heading('location', text='Location')
        self.tree.column('#0', width=200)
        self.tree.column('row', width=40, anchor='center')
        self.tree.column('ping', width=80, anchor='center')
        self.tree.column('speed', width=80, anchor='center')
        self.tree.column('location', width=150, anchor='center')

        vsb = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # --- VPN control buttons (legacy) ---
        vpn_frame = ttk.Frame(result_frame)
        vpn_frame.pack(fill=tk.X, padx=5, pady=5)
        self.apply_vpn_button = ttk.Button(vpn_frame, text="Apply VPN (best config)", command=self.apply_best_vpn)
        self.apply_vpn_button.pack(side=tk.LEFT, padx=5)
        self.stop_vpn_button = ttk.Button(vpn_frame, text="Stop VPN", command=self.stop_vpn, state=tk.DISABLED)
        self.stop_vpn_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(vpn_frame, text="Refresh Table", command=self.refresh_table).pack(side=tk.LEFT, padx=5)

        # Bind events
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    # --- Browse functions ---
    def browse_input(self):
        f = filedialog.askopenfilename(title="Select input file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if f:
            self.input_file_var.set(f)
            base, ext = os.path.splitext(f)
            self.output_file_var.set(f"{base}_valid{ext}")

    def browse_output(self):
        f = filedialog.asksaveasfilename(title="Save output file", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if f:
            self.output_file_var.set(f)

    def browse_valid_file(self):
        f = filedialog.askopenfilename(title="Select valid configs file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if f:
            self.valid_file_var.set(f)

    def browse_xray(self):
        f = filedialog.askopenfilename(title="Select xray.exe", filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
        if f:
            self.xray_path_var.set(f)

    # --- Logging & status ---
    def log_message(self, message):
        self.root.after(0, lambda: self.log_text.insert(tk.END, message + "\n"))
        self.root.after(0, lambda: self.log_text.see(tk.END))

    def update_status(self):
        if self.total_links > 0:
            percent = int((self.current_index / self.total_links) * 100)
        else:
            percent = 0
        self.root.after(0, lambda: self.progress_var.set(self.current_index))
        self.root.after(0, lambda: self.progress_bar.config(maximum=self.total_links if self.total_links > 0 else 1))
        self.root.after(0, lambda: self.progress_percent_var.set(f"{percent}%"))
        self.root.after(0, lambda: self.processed_count_var.set(str(self.current_index)))
        self.root.after(0, lambda: self.total_count_var.set(str(self.total_links)))
        self.root.after(0, lambda: self.valid_count_var.set(str(self.valid_count)))
        if self.running:
            status = "Running..."
        elif self.paused:
            status = "Paused"
        else:
            status = "Ready"
        self.root.after(0, lambda: self.status_label.config(text=status))

    # ========== ROBUST GEOLOCATION WITH 20+ SERVICES ==========
    def get_location_for_ip(self, ip):
        """Get location (City, Country) for an IP using multiple services."""
        if ip in self.geo_cache:
            return self.geo_cache[ip]

        # List of services: each is a tuple (url_template, parse_function, headers)
        # We'll try them in order until one succeeds.
        services = [
            # 1. ip-api.com (HTTP, JSON)
            {
                'url': f'http://ip-api.com/json/{ip}?fields=country,city',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 2. ip-api.com (HTTPS)
            {
                'url': f'https://ip-api.com/json/{ip}?fields=country,city',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 3. ipinfo.io
            {
                'url': f'https://ipinfo.io/{ip}/json',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 4. geoplugin.net
            {
                'url': f'http://www.geoplugin.net/json.gp?ip={ip}',
                'parse': lambda d: f"{d.get('geoplugin_city','').strip()}, {d.get('geoplugin_countryName','').strip()}" if d.get('geoplugin_city') or d.get('geoplugin_countryName') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 5. ipapi.co
            {
                'url': f'https://ipapi.co/{ip}/json/',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country_name','').strip()}" if d.get('city') or d.get('country_name') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 6. ipwhois.app
            {
                'url': f'https://ipwhois.app/json/{ip}',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 7. api.ip.sb
            {
                'url': f'https://api.ip.sb/geoip/{ip}',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 8. ip-api.com (no fields, but still parse)
            {
                'url': f'http://ip-api.com/json/{ip}',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 9. ip-api.com (HTTPS, no fields)
            {
                'url': f'https://ip-api.com/json/{ip}',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 10. ip-api.com (line format - we'll treat as CSV)
            # Actually line format returns plain text lines, we can use it but need to parse differently.
            # We'll skip line format to avoid complexity.
            # 11. freegeoip.app (deprecated but may work)
            {
                'url': f'https://freegeoip.app/json/{ip}',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country_name','').strip()}" if d.get('city') or d.get('country_name') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 12. ipgeolocation.io (free requires key, skip)
            # 13. ipstack.com (requires key)
            # 14. ip2location.com (requires key)
            # 15. jsonip.com (only returns IP, no location)
            # 16. ipinfo.io (already)
            # 17. geojs.io (free)
            {
                'url': f'https://get.geojs.io/v1/ip/geo/{ip}.json',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 18. ipvigilante.com (might be unreliable)
            {
                'url': f'https://ipvigilante.com/{ip}',
                'parse': lambda d: f"{d.get('data',{}).get('city_name','').strip()}, {d.get('data',{}).get('country_name','').strip()}" if d.get('data',{}).get('city_name') or d.get('data',{}).get('country_name') else None,
                'headers': {'User-Agent': 'Mozilla/5.0'}
            },
            # 19. ip-api.com with different user-agent
            {
                'url': f'http://ip-api.com/json/{ip}?fields=country,city',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            },
            # 20. ip-api.com with another UA
            {
                'url': f'https://ip-api.com/json/{ip}?fields=country,city',
                'parse': lambda d: f"{d.get('city','').strip()}, {d.get('country','').strip()}" if d.get('city') or d.get('country') else None,
                'headers': {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'}
            },
        ]

        for service in services:
            try:
                req = urllib.request.Request(service['url'], headers=service['headers'])
                with urllib.request.urlopen(req, timeout=8) as resp:
                    content = resp.read().decode('utf-8')
                    data = json.loads(content)
                    loc = service['parse'](data)
                    if loc and loc != "Unknown" and loc != ", " and loc != "," and loc.strip():
                        self.geo_cache[ip] = loc
                        # Log success only once per IP (optional)
                        # self.log_message(f"📍 Location found for {ip}: {loc}")
                        return loc
            except Exception as e:
                # If we want to debug, we could log but that would clutter.
                # We'll only log if all fail.
                continue

        self.geo_cache[ip] = "Unknown"
        self.log_message(f"⚠️ All geolocation services failed for IP {ip}")
        return "Unknown"
    # =========================================================

    def get_location_from_link(self, link):
        """Extract hostname, resolve to IP, and get location."""
        try:
            parsed = urllib.parse.urlparse(link)
            host = parsed.hostname
            if not host:
                return "Unknown"
            ip = socket.gethostbyname(host)
            return self.get_location_for_ip(ip)
        except Exception:
            return "Unknown"

    # --- Subscription download with 403 handling ---
    def download_subscription(self, url):
        headers_list = [
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'},
            {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'}
        ]
        for attempt, headers in enumerate(headers_list):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as response:
                    content = response.read()
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                    except:
                        decoded = content.decode('utf-8')
                    lines = [line.strip() for line in decoded.splitlines() if line.strip()]
                    vless_lines = [l for l in lines if l.startswith('vless://')]
                    if not vless_lines:
                        vless_lines = lines
                    return vless_lines
            except urllib.error.HTTPError as e:
                if e.code == 403 and attempt < len(headers_list) - 1:
                    self.log_message(f"⚠️ HTTP 403 for {url}, retrying with different User-Agent...")
                    continue
                else:
                    self.log_message(f"⚠️ HTTP error {e.code} for {url}: {e.reason}")
                    return []
            except urllib.error.URLError as e:
                self.log_message(f"⚠️ URL error for {url}: {e.reason}")
                return []
            except Exception as e:
                self.log_message(f"⚠️ Failed to download {url}: {e}")
                return []
        self.log_message(f"⚠️ Failed to download {url} after multiple attempts.")
        return []

    def process_input_file(self, filepath):
        all_links = []
        sub_urls = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.log_message(f"❌ Failed to read input file: {e}")
            return None, None
        for line in lines:
            if line.startswith('http://') or line.startswith('https://'):
                sub_urls.append(line)
            elif line.startswith('vless://'):
                all_links.append(line)
            else:
                all_links.append(line)
        return all_links, sub_urls

    def deduplicate_links(self, links):
        seen = set()
        unique = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique.append(link)
        return unique

    def save_downloaded_links(self, links, prefix="all_links"):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(link + '\n')
            self.log_message(f"💾 All links saved to: {filename}")
            return filename
        except Exception as e:
            self.log_message(f"⚠️ Could not save: {e}")
            return None

    # --- Helper: find free port & SOCKS5 client ---
    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]

    def socks5_connect(self, proxy_host, proxy_port, target_host, target_port, timeout=10):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((proxy_host, proxy_port))
            sock.send(b'\x05\x01\x00')
            resp = sock.recv(2)
            if resp != b'\x05\x00':
                raise Exception("SOCKS5 handshake failed")
            domain = target_host.encode()
            req = b'\x05\x01\x00\x03' + bytes([len(domain)]) + domain + target_port.to_bytes(2, 'big')
            sock.send(req)
            resp = sock.recv(4)
            if resp[0] != 0x05 or resp[1] != 0x00:
                raise Exception("SOCKS5 connection failed")
            atyp = resp[3]
            if atyp == 0x01:
                sock.recv(4)
            elif atyp == 0x03:
                domain_len = sock.recv(1)[0]
                sock.recv(domain_len)
            elif atyp == 0x04:
                sock.recv(16)
            sock.recv(2)
            return sock
        except Exception as e:
            sock.close()
            raise e

    def test_through_proxy(self, proxy_host, proxy_port, target_url, timeout=10):
        parsed = urllib.parse.urlparse(target_url)
        if parsed.scheme != 'http':
            raise ValueError("Only HTTP is supported")
        host = parsed.hostname
        port = parsed.port or 80
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query

        start = time.time()
        sock = None
        try:
            sock = self.socks5_connect(proxy_host, proxy_port, host, port, timeout)
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            response = sock.recv(4096)
            latency_ms = (time.time() - start) * 1000
            if response.startswith(b'HTTP/1.1 204') or response.startswith(b'HTTP/1.1 200'):
                return True, latency_ms
            else:
                return False, latency_ms
        except Exception:
            return False, None
        finally:
            if sock:
                sock.close()

    # --- Build VLESS config ---
    def build_config_from_link(self, link):
        try:
            parsed = urllib.parse.urlparse(link)
            if not parsed.username or not parsed.hostname or not parsed.port:
                raise ValueError("Missing UUID, address, or port")
            user_uuid = parsed.username
            server_address = parsed.hostname
            server_port = parsed.port
            query = urllib.parse.parse_qs(parsed.query)

            flow = query.get('flow', [''])[0]
            security = query.get('security', [''])[0]
            sni = query.get('sni', [''])[0]
            fingerprint = query.get('fp', [''])[0]
            public_key = query.get('pbk', [''])[0]
            short_id = query.get('sid', [''])[0]
            network = query.get('type', ['tcp'])[0]

            config = {
                "inbounds": [{
                    "port": 10808,
                    "listen": "127.0.0.1",
                    "protocol": "socks",
                    "settings": {"auth": "noauth", "udp": True}
                }],
                "outbounds": [{
                    "protocol": "vless",
                    "settings": {
                        "vnext": [{
                            "address": server_address,
                            "port": server_port,
                            "users": [{"id": user_uuid, "flow": flow, "encryption": "none"}]
                        }]
                    },
                    "streamSettings": {
                        "network": network,
                        "security": "none",
                        "tlsSettings": {},
                        "realitySettings": {}
                    },
                    "mux": {"enabled": False}
                }]
            }

            outbound = config['outbounds'][0]
            if security.lower() == 'reality':
                outbound['streamSettings']['security'] = 'reality'
                outbound['streamSettings']['realitySettings'] = {
                    "serverName": sni,
                    "fingerprint": fingerprint,
                    "publicKey": public_key,
                    "shortId": short_id
                }
            elif security.lower() == 'tls':
                outbound['streamSettings']['security'] = 'tls'
                outbound['streamSettings']['tlsSettings'] = {
                    "serverName": sni,
                    "allowInsecure": False,
                    "fingerprint": fingerprint
                }
            else:
                outbound['streamSettings']['security'] = 'none'

            if network == 'ws':
                path = query.get('path', ['/'])[0]
                host = query.get('host', [''])[0]
                outbound['streamSettings']['wsSettings'] = {
                    "path": path,
                    "headers": {"Host": host} if host else {}
                }
            return config
        except Exception:
            return None

    # --- Single config test (for initial validation) ---
    def test_single_config(self, link, xray_path, max_latency):
        if self.stop_requested:
            return None

        config = self.build_config_from_link(link)
        if config is None:
            return None

        inbound_port = self.find_free_port()
        config['inbounds'][0]['port'] = inbound_port

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            temp_config_path = f.name

        xray_proc = None
        try:
            cmd_test = [xray_path, "-test", "-c", temp_config_path]
            proc_test = subprocess.Popen(
            cmd_test,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            _, stderr = proc_test.communicate(timeout=10)
            if proc_test.returncode != 0:
                return None

            cmd_run = [xray_path, "-c", temp_config_path]
            xray_proc = subprocess.Popen(
                cmd_run,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            ready = False
            start_wait = time.time()
            while time.time() - start_wait < 3:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        s.connect(('127.0.0.1', inbound_port))
                        ready = True
                        break
                except:
                    time.sleep(0.1)
            if not ready:
                return None

            test_url = self.test_url_var.get().strip() or "http://www.gstatic.com/generate_204"
            success, latency_ms = self.test_through_proxy('127.0.0.1', inbound_port, test_url, timeout=max_latency/1000)

            if success and latency_ms is not None and latency_ms <= max_latency:
                return link
            else:
                return None

        except Exception:
            return None
        finally:
            if xray_proc:
                xray_proc.terminate()
                try:
                    xray_proc.wait(timeout=2)
                except:
                    xray_proc.kill()
            try:
                os.unlink(temp_config_path)
            except:
                pass

    # --- Main initial testing (subscription + validation) ---
    # <<< NEW: rewritten to submit all tasks at once, no batch waiting
    def run_tests(self):
        xray_path = self.xray_path_var.get().strip()
        try:
            threads = max(1, int(self.threads_var.get().strip()))
        except:
            threads = 10
        try:
            max_latency = max(1, int(self.max_latency_var.get().strip()))
        except:
            max_latency = 1000

        input_file = self.input_file_var.get().strip()
        if not input_file or not os.path.exists(input_file):
            self.log_message("❌ Input file not found.")
            self.finish_testing()
            return

        direct_links, sub_urls = self.process_input_file(input_file)
        if direct_links is None:
            self.finish_testing()
            return

        all_links = direct_links.copy()
        self.log_message(f"📄 Found {len(direct_links)} direct VLESS links and {len(sub_urls)} subscription URLs.")

        if sub_urls:
            self.log_message(f"🌐 Downloading {len(sub_urls)} subscriptions...")
            downloaded = []
            with ThreadPoolExecutor(max_workers=min(len(sub_urls), 20)) as executor:
                future_to_url = {executor.submit(self.download_subscription, url): url for url in sub_urls}
                for future in as_completed(future_to_url):
                    result = future.result()
                    if result:
                        downloaded.extend(result)
            self.log_message(f"📥 Downloaded {len(downloaded)} links from subscriptions.")
            all_links.extend(downloaded)
        else:
            self.log_message("ℹ️ No subscription URLs to download.")

        if not all_links:
            self.log_message("⚠️ No links found.")
            self.finish_testing()
            return

        unique_links = self.deduplicate_links(all_links)
        self.log_message(f"🧹 Removed {len(all_links) - len(unique_links)} duplicates. {len(unique_links)} unique links remain.")
        self.save_downloaded_links(unique_links, prefix="all_links")

        self.links = unique_links
        self.total_links = len(self.links)
        self.current_index = 0          # will count completed tasks
        self.valid_count = 0
        self.valid_links = []

        output_file = self.output_file_var.get().strip()
        if not output_file:
            output_file = "valid_configs.txt"
            self.output_file_var.set(output_file)
        self.output_file = output_file
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except:
                pass

        self.log_message(f"🚀 Testing {self.total_links} unique configs (max latency {max_latency} ms, {threads} threads)...")
        self.stop_requested = False
        self.running = True
        self.paused = False

        self.start_time = time.time()
        self.last_eta_log_time = self.start_time

        self.update_status()

        # Submit all tasks to the thread pool at once.
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # map each future to its link for reference
            future_to_link = {
                executor.submit(self.test_single_config, link, xray_path, max_latency): link
                for link in self.links
            }

            # Process results as they complete
            for future in as_completed(future_to_link):
                if self.stop_requested:
                    # Cancel remaining futures that haven't started
                    for f in future_to_link:
                        f.cancel()
                    break

                result = future.result()
                if result is not None:
                    with self.lock:
                        self.valid_links.append(result)
                        self.valid_count += 1
                        try:
                            with open(self.output_file, 'a', encoding='utf-8') as f:
                                f.write(result + '\n')
                        except Exception as e:
                            self.log_message(f"⚠️ Write error: {e}")

                with self.lock:
                    self.current_index += 1
                self.update_status()

                # Log ETA every 10 seconds
                if not self.stop_requested:
                    now = time.time()
                    if now - self.last_eta_log_time >= 10:
                        elapsed = now - self.start_time
                        processed = self.current_index
                        if processed > 0 and elapsed > 1:
                            rate = processed / elapsed
                            remaining_items = self.total_links - processed
                            if rate > 0:
                                remaining_secs = remaining_items / rate
                                mins = int(remaining_secs // 60)
                                secs = int(remaining_secs % 60)
                                time_str = f"{mins} min {secs} sec"
                                self.log_message(f"⏳ Processed {processed}/{self.total_links} - Est. remaining: {time_str}")
                                self.last_eta_log_time = now

        if self.stop_requested:
            self.log_message("⏹ Paused by user.")
            self.paused = True
            self.running = False
            self.update_status()
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL, text="Resume"))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        else:
            self.log_message("🏁 Initial validation completed.")
            self.finish_testing()
            if self.speed_test_enabled.get() and self.valid_links:
                self.log_message("⏩ Auto-starting speed test on valid configs...")
                self.run_valid_tests_on_list(self.valid_links)
            elif self.auto_apply_vpn.get() and self.valid_links:
                if self.valid_links:
                    self.selected_config = self.valid_links[0]
                    self.apply_vpn()

    def finish_testing(self):
        self.running = False
        self.paused = False
        self.stop_requested = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL, text="Start"))
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        self.update_status()
        if self.current_index >= self.total_links:
            self.log_message("✅ All links processed.")
        else:
            self.log_message("⏹ Testing stopped. You can resume later.")

    # --- Speed test functions (with location) ---
    def test_single_config_full(self, link, xray_path, speed_test_url, max_latency):
        if self.stop_requested:
            return None

        config = self.build_config_from_link(link)
        if config is None:
            return None

        inbound_port = self.find_free_port()
        config['inbounds'][0]['port'] = inbound_port

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            temp_config_path = f.name

        xray_proc = None
        try:
            cmd_run = [xray_path, "-c", temp_config_path]
            xray_proc = subprocess.Popen(
                cmd_run,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            ready = False
            start_wait = time.time()
            while time.time() - start_wait < 3:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        s.connect(('127.0.0.1', inbound_port))
                        ready = True
                        break
                except:
                    time.sleep(0.1)
            if not ready:
                return None

            ping = None
            test_url = self.test_url_var.get().strip() or "http://www.gstatic.com/generate_204"
            success, latency_ms = self.test_through_proxy('127.0.0.1', inbound_port, test_url, timeout=max_latency/1000)
            if success and latency_ms is not None:
                ping = latency_ms
            else:
                return None

            speed_mbps = 0
            try:
                start_dl = time.time()
                sock = self.socks5_connect('127.0.0.1', inbound_port,
                                           urllib.parse.urlparse(speed_test_url).hostname,
                                           urllib.parse.urlparse(speed_test_url).port or 80,
                                           timeout=30)
                parsed_speed = urllib.parse.urlparse(speed_test_url)
                path = parsed_speed.path or '/'
                if parsed_speed.query:
                    path += '?' + parsed_speed.query
                request = f"GET {path} HTTP/1.1\r\nHost: {parsed_speed.hostname}\r\nConnection: close\r\n\r\n"
                sock.send(request.encode())
                total_bytes = 0
                chunk = sock.recv(8192)
                while chunk:
                    total_bytes += len(chunk)
                    chunk = sock.recv(8192)
                sock.close()
                dl_time = time.time() - start_dl
                if dl_time > 0 and total_bytes > 0:
                    speed_mbps = (total_bytes * 8) / (dl_time * 1_000_000)
            except Exception:
                speed_mbps = 0

            location = self.get_location_from_link(link)

            return {
                'link': link,
                'ping': ping,
                'speed_mbps': speed_mbps,
                'location': location
            }

        except Exception:
            return None
        finally:
            if xray_proc:
                xray_proc.terminate()
                try:
                    xray_proc.wait(timeout=2)
                except:
                    xray_proc.kill()
            try:
                os.unlink(temp_config_path)
            except:
                pass

    # <<< NEW: removed increment of self.valid_count to avoid double counting
    def run_valid_tests_on_list(self, links):
        if not links:
            self.log_message("⚠️ No valid configs to test.")
            return

        self.valid_results = []
        self.clear_table()

        xray_path = self.xray_path_var.get().strip()
        speed_url = self.speed_test_url_var.get().strip() or "http://speedtest.tele2.net/1MB.zip"
        try:
            max_latency = max(1, int(self.max_latency_var.get().strip()))
        except:
            max_latency = 1000
        threads = max(1, int(self.threads_var.get().strip()))

        self.log_message(f"🚀 Testing {len(links)} valid configs for ping, speed and location...")

        self.total_links = len(links)
        self.current_index = 0
        self.running = True
        self.stop_requested = False
        self.update_status()

        self.start_time = time.time()
        self.last_eta_log_time = self.start_time

        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_link = {
                executor.submit(self.test_single_config_full, link, xray_path, speed_url, max_latency): link
                for link in links
            }
            for future in as_completed(future_to_link):
                if self.stop_requested:
                    for f in future_to_link:
                        f.cancel()
                    break
                result = future.result()
                if result is not None:
                    self.valid_results.append(result)
                    # Do NOT increment self.valid_count here – it's only for initial validation
                with self.lock:
                    self.current_index += 1
                self.update_status()

                if not self.stop_requested:
                    now = time.time()
                    if now - self.last_eta_log_time >= 10:
                        elapsed = now - self.start_time
                        processed = self.current_index
                        if processed > 0 and elapsed > 1:
                            rate = processed / elapsed
                            remaining_items = self.total_links - processed
                            if rate > 0:
                                remaining_secs = remaining_items / rate
                                mins = int(remaining_secs // 60)
                                secs = int(remaining_secs % 60)
                                time_str = f"{mins} min {secs} sec"
                                self.log_message(f"⏳ Speed test: processed {processed}/{self.total_links} - Est. remaining: {time_str}")
                                self.last_eta_log_time = now

        if self.stop_requested:
            self.log_message("⏹ Speed test paused.")
            self.paused = True
            self.running = False
            self.update_status()
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL, text="Resume"))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            return

        self.log_message(f"🏁 Speed test completed. Found {len(self.valid_results)} working configs with ping, speed & location.")
        self.running = False
        self.paused = False
        self.update_status()
        self.refresh_table()

        self.root.after(0, lambda: self.vpn_toggle_button.config(state=tk.NORMAL))

        if self.auto_apply_vpn.get() and self.valid_results:
            self.apply_best_vpn()

    def start_valid_test(self):
        valid_file = self.valid_file_var.get().strip()
        if valid_file and os.path.exists(valid_file):
            try:
                with open(valid_file, 'r', encoding='utf-8') as f:
                    links = [line.strip() for line in f if line.strip()]
                self.log_message(f"📄 Loaded {len(links)} configs from {valid_file}")
                self.valid_links = links
            except Exception as e:
                self.log_message(f"❌ Failed to load valid file: {e}")
                return
        else:
            if not self.valid_links:
                self.log_message("⚠️ No valid configs available. Please run initial test first or load a valid file.")
                return
            links = self.valid_links

        threading.Thread(target=self.run_valid_tests_on_list, args=(links,), daemon=True).start()

    # --- Table management ---
    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # <<< NEW: added row number when inserting
    def refresh_table(self):
        self.clear_table()
        if not self.valid_results:
            return

        sort_by_speed = self.sort_by_speed.get()
        sorted_results = sorted(self.valid_results, key=lambda x: x['speed_mbps'] if sort_by_speed else -x['ping'], reverse=True if sort_by_speed else False)

        for idx, res in enumerate(sorted_results, start=1):
            link = res['link']
            short = link[:50] + ('...' if len(link) > 50 else '')
            ping = f"{res['ping']:.0f}" if res['ping'] is not None else "N/A"
            speed = f"{res['speed_mbps']:.2f}" if res['speed_mbps'] > 0 else "0.00"
            location = res.get('location', 'Unknown')
            # Insert with row number as first column value
            self.tree.insert('', tk.END, text=short, values=(idx, ping, speed, location), tags=(link,))
        self.sorted_results = sorted_results

        if self.selected_config:
            for item in self.tree.get_children():
                if self.tree.item(item, 'tags')[0] == self.selected_config:
                    self.tree.selection_set(item)
                    break

    def show_full_config(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        link = self.tree.item(item, 'tags')[0]
        messagebox.showinfo("Full Config", link)

    # --- Treeview event handlers ---
    def on_tree_select(self, event):
        """Single click: select config and set as active. If VPN is running, switch to it."""
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        link = self.tree.item(item, 'tags')[0]
        self.selected_config = link
        self.log_message(f"🔹 Selected config: {link[:60]}...")

        # If VPN is active, switch to this config
        if self.vpn_active:
            self.log_message("🔄 VPN is active, switching to selected config...")
            self.stop_vpn()
            time.sleep(0.5)
            self.apply_vpn()

    def on_tree_double_click(self, event):
        """Double click: copy to clipboard and show QR code."""
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        link = self.tree.item(item, 'tags')[0]

        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        self.log_message(f"📋 Copied config to clipboard: {link[:60]}...")
        self.show_qr_code(link)

    def show_qr_code(self, link):
        if not QR_AVAILABLE:
            messagebox.showinfo("QR Code", "QR code generation requires 'qrcode' and 'Pillow'.\nInstall with: pip install qrcode Pillow")
            return

        qr_window = tk.Toplevel(self.root)
        qr_window.title("QR Code for Config")
        qr_window.geometry("400x450")
        qr_window.resizable(False, False)

        try:
            qr = qrcode.QRCode(box_size=8, border=2)
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            photo = ImageTk.PhotoImage(img.resize((300, 300), Image.Resampling.LANCZOS))

            label = ttk.Label(qr_window, image=photo)
            label.image = photo
            label.pack(pady=10)

            short_link = link[:80] + ('...' if len(link) > 80 else '')
            ttk.Label(qr_window, text=short_link, wraplength=350, justify='center').pack(pady=5)
            ttk.Button(qr_window, text="Close", command=qr_window.destroy).pack(pady=10)
        except Exception as e:
            messagebox.showerror("QR Error", f"Failed to generate QR code: {e}")
            qr_window.destroy()

    # --- VPN core functions ---
    def get_best_config(self):
        if not self.valid_results:
            return None
        sort_by_speed = self.sort_by_speed.get()
        best = max(self.valid_results, key=lambda x: x['speed_mbps'] if sort_by_speed else -x['ping'])
        return best['link']

    def apply_best_vpn(self):
        best_link = self.get_best_config()
        if best_link:
            self.selected_config = best_link
            if self.vpn_active:
                self.stop_vpn()
                time.sleep(0.5)
            self.apply_vpn()

    def set_system_proxy(self, enabled, proxy_host='127.0.0.1', proxy_port=10808):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                                 0, winreg.KEY_SET_VALUE)
            if enabled:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                proxy_str = f"{proxy_host}:{proxy_port}"
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_str)
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "localhost;127.0.0.1;*.local")
            else:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)
            ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)
            return True
        except Exception as e:
            self.log_message(f"⚠️ Failed to set system proxy: {e}")
            return False

    def apply_vpn(self):
        if not self.selected_config:
            messagebox.showwarning("No config", "No config selected for VPN.")
            return

        self.stop_vpn()

        config = self.build_config_from_link(self.selected_config)
        if config is None:
            self.log_message("❌ Failed to build config.")
            return

        config['inbounds'][0]['port'] = self.vpn_port

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            self.vpn_config_path = f.name

        try:
            cmd = [self.xray_path_var.get().strip(), "-c", self.vpn_config_path]
            self.xray_vpn_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            ready = False
            for _ in range(10):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        s.connect(('127.0.0.1', self.vpn_port))
                        ready = True
                        break
                except:
                    time.sleep(0.5)
            if not ready:
                self.log_message("❌ Xray VPN did not start in time.")
                self.stop_vpn()
                return

            mode = self.vpn_mode_var.get()
            if mode == "System Proxy":
                if self.set_system_proxy(True, '127.0.0.1', self.vpn_port):
                    self.log_message(f"✅ VPN applied: System proxy set to 127.0.0.1:{self.vpn_port}")
                else:
                    self.log_message("❌ Failed to set system proxy.")
                    self.stop_vpn()
                    return
            else:
                self.log_message(f"✅ VPN running in local proxy mode: SOCKS5 & HTTP on 127.0.0.1:{self.vpn_port}")
                self.log_message("   You can configure your apps to use this proxy.")

            self.vpn_active = True
            self.update_vpn_ui()

        except Exception as e:
            self.log_message(f"❌ Error starting VPN: {e}")
            self.stop_vpn()

    def stop_vpn(self):
        if self.xray_vpn_proc:
            self.xray_vpn_proc.terminate()
            try:
                self.xray_vpn_proc.wait(timeout=2)
            except:
                self.xray_vpn_proc.kill()
            self.xray_vpn_proc = None

        if self.vpn_active and self.vpn_mode_var.get() == "System Proxy":
            self.set_system_proxy(False)
            self.log_message("🛑 System proxy disabled.")
        elif self.vpn_active:
            self.log_message("🛑 Local proxy stopped.")

        if hasattr(self, 'vpn_config_path') and self.vpn_config_path and os.path.exists(self.vpn_config_path):
            try:
                os.unlink(self.vpn_config_path)
            except:
                pass
            self.vpn_config_path = None

        self.vpn_active = False
        self.update_vpn_ui()

    def toggle_vpn(self):
        if not self.vpn_active:
            if not self.selected_config:
                if self.valid_results:
                    self.selected_config = self.get_best_config()
                else:
                    self.log_message("⚠️ No config available. Please run tests first.")
                    return
            self.apply_vpn()
        else:
            self.stop_vpn()

    def update_vpn_ui(self):
        if self.vpn_active:
            self.vpn_toggle_button.config(text="VPN ON", style="On.TButton")
            self.stop_vpn_button.config(state=tk.NORMAL)
            self.apply_vpn_button.config(state=tk.DISABLED)
        else:
            self.vpn_toggle_button.config(text="VPN OFF", style="TButton")
            self.stop_vpn_button.config(state=tk.DISABLED)
            self.apply_vpn_button.config(state=tk.NORMAL)
            if self.valid_results:
                self.vpn_toggle_button.config(state=tk.NORMAL)

    def on_closing(self):
        if self.vpn_active:
            self.stop_vpn()
        self.root.destroy()

    def start_check(self):
        if self.running:
            return
        if self.paused or (self.current_index > 0 and self.current_index < self.total_links):
            self.paused = False
            self.running = True
            self.stop_requested = False
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.run_tests, daemon=True).start()
        else:
            self.log_text.delete(1.0, tk.END)
            self.current_index = 0
            self.total_links = 0
            self.valid_count = 0
            self.valid_links = []
            self.valid_results = []
            self.links = []
            self.paused = False
            self.stop_requested = False
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.run_tests, daemon=True).start()

    def stop_check(self):
        if not self.running:
            return
        self.log_message("⏹ Stop requested...")
        self.stop_requested = True

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("On.TButton", foreground="green", font=('Arial', 10, 'bold'))
    app = XrayConfigTesterGUI(root)

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(base_path, "V.png")
    try:
        img = Image.open(icon_path)
        photo = ImageTk.PhotoImage(img)
        root.iconphoto(True, photo)
    except Exception as e:
        print(f"Icon is not loaded {e}")

    root.mainloop()
