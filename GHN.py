import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import gspread
import os
import sys
import threading
import time
import webbrowser
import requests
from google.oauth2.service_account import Credentials
from ping3 import ping
from queue import Queue
import shutil
import rarfile
import tempfile
import subprocess
import json

# Global variables
command_queue = Queue()
current_user = None
running_commands = {}

# Theme colors
theme_colors = {
    "primary": "#2E3B4E",
    "secondary": "#3F72AF",
    "accent": "#FFA41B",
    "background": "#F9F7F7",
    "text": "#112D4E",
    "error": "#E63946",
    "success": "#2A9D8F",
    "warning": "#F9C74F"
}

# GitHub repository info
GITHUB_API_URL = "https://api.github.com/repos/hoangdung997/DEVDungtau/releases/latest"
CURRENT_VERSION = "1.0.0"

# Ensure debug log directory and file exist
LOG_DIR = "c:/Users/ADMIN/Desktop/GHN2/tess/"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, "debug_log.txt")
with open(LOG_FILE, "a", encoding="utf-8") as log_file:
    log_file.write(f"{time.ctime()}: Bắt đầu ứng dụng - Đã tạo file log\n")

def authenticate_google_sheets():
    """Authenticate with Google Sheets using service account"""
    try:
        if not os.path.exists(os.path.join(LOG_DIR, "credentials.json")):
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(f"{time.ctime()}: Lỗi - File credentials.json không tồn tại!\n")
            raise FileNotFoundError("File credentials.json không tồn tại!")
        with open(os.path.join(LOG_DIR, "credentials.json"), "r", encoding="utf-8") as f:
            creds_data = json.load(f)
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(f"{time.ctime()}: Đọc credentials.json thành công\n")
                log_file.write(f"{time.ctime()}: Client email: {creds_data.get('client_email', 'Không tìm thấy')}\n")
        creds = Credentials.from_service_account_info(creds_data, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1CQasbMxm1YnaZjguihYjz4p_OBkApArjeqvd_CRAAow/edit?gid=1769102994#gid=1769102994")
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"{time.ctime()}: Kết nối Google Sheets thành công\n")
        return sheet
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"{time.ctime()}: Lỗi - {str(e)}\n")
        raise Exception(f"Không thể kết nối Google Sheets: {str(e)}")

def check_credentials(username, password):
    """Check if username and password are valid"""
    try:
        if not username or not password:
            return False
        sheet = authenticate_google_sheets().worksheet("GHN")
        accounts = sheet.get_all_values()
        for row in accounts:
            if len(row) >= 2 and row[0] == username and row[1] == password:
                return True
        return False
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể kiểm tra thông tin: {str(e)}")
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"{time.ctime()}: Lỗi check_credentials - {str(e)}\n")
        return False

class GHNApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌏 GHN Tool by HOÀNG DŨNG 🌏")
        self.geometry("1200x700")
        self.configure(bg=theme_colors["background"])
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 700) // 2
        self.geometry(f"1200x700+{x}+{y}")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        self.setup_monitor_frame()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        self.login_frame = ttk.Frame(self.notebook)
        self.home_frame = ttk.Frame(self.notebook)
        self.version_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Đăng Nhập")
        self.notebook.add(self.home_frame, text="Trang Chủ")
        self.notebook.add(self.version_frame, text="Phiên Bản")
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.download_speed_var = tk.StringVar(value="0 KB/s")
        self.file_size_var = tk.StringVar(value="0 MB")
        self.setup_login_frame()
        self.setup_version_frame()
        threading.Thread(target=self.update_ping, daemon=True).start()
        threading.Thread(target=self.command_worker, daemon=True).start()
        threading.Thread(target=self.sync_commands, daemon=True).start()
        threading.Thread(target=self.auto_update, daemon=True).start()

    def configure_styles(self):
        self.style.configure('TFrame', background=theme_colors["background"])
        self.style.configure('TLabel', background=theme_colors["background"], foreground=theme_colors["text"], font=('Helvetica', 10))
        self.style.configure('TButton', padding=10, font=('Helvetica', 10, 'bold'))
        self.style.configure('Large.TButton', padding=15, font=('Helvetica', 12, 'bold'))
        self.style.configure('Status.TLabel', background=theme_colors["background"], foreground=theme_colors["text"], font=('Helvetica', 9))

    def setup_monitor_frame(self):
        self.monitor_frame = ttk.Frame(self)
        self.monitor_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.network_label = ttk.Label(self.monitor_frame, text="Đang kiểm tra mạng...", style='Status.TLabel')
        self.network_label.pack(side="left")

    def setup_login_frame(self):
        login_container = ttk.Frame(self.login_frame, padding="50 70 50 50")
        login_container.pack(expand=True)
        ttk.Label(login_container, text="GHN Tool", font=('Helvetica', 28, 'bold'), foreground=theme_colors["primary"]).pack(pady=30)
        ttk.Label(login_container, text="Đăng nhập để tiếp tục", font=('Helvetica', 12), foreground=theme_colors["secondary"]).pack(pady=(0, 30))
        username_frame = ttk.Frame(login_container)
        username_frame.pack(fill="x", pady=5)
        ttk.Label(username_frame, text="Tên đăng nhập:", font=('Helvetica', 10)).pack(anchor="w")
        self.username_entry = ttk.Entry(username_frame, width=40)
        self.username_entry.pack(fill="x", pady=5)
        password_frame = ttk.Frame(login_container)
        password_frame.pack(fill="x", pady=5)
        ttk.Label(password_frame, text="Mật khẩu:", font=('Helvetica', 10)).pack(anchor="w")
        self.password_entry = ttk.Entry(password_frame, width=40, show="•")
        self.password_entry.pack(fill="x", pady=5)
        ttk.Button(login_container, text="ĐĂNG NHẬP", command=self.authenticate_user, style='Large.TButton').pack(pady=30)

    def setup_home_frame(self):
        for widget in self.home_frame.winfo_children():
            widget.destroy()
        main_container = ttk.Frame(self.home_frame, padding=20)
        main_container.pack(fill="both", expand=True)
        left_frame = ttk.LabelFrame(main_container, text="Thông tin hệ thống", padding=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Safeguard for current_user
        if not current_user:
            messagebox.showerror("Lỗi", "Không có thông tin người dùng!")
            return
        ttk.Label(left_frame, text=f"Xin chào, {current_user}", font=('Helvetica', 14, 'bold')).pack(pady=5)
        
        self.status_label = ttk.Label(left_frame, text="Sẵn sàng", font=('Helvetica', 10))
        self.status_label.pack(pady=5)
        self.running_commands_frame = ttk.LabelFrame(left_frame, text="Lệnh đang chạy", padding=15)
        self.running_commands_frame.pack(fill="both", expand=True, pady=10)
        right_frame = ttk.LabelFrame(main_container, text="Chức năng", padding=15)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        functions = [
            ("Đổi Mã Token", lambda: self.show_token_dialog()),
            ("Định Hóa Đơn", lambda: self.run_command("Định Hóa Đơn", 2, 5, 1)),
            ("Phú Lương", lambda: self.run_command("Phú Lương", 3, 5, 1)),
            ("Kinh Doanh", lambda: self.run_command("Kinh Doanh", 4, 5, 1)),
            ("Giao Thất Bại Thu Tiền", lambda: self.run_command("Giao Thất Bại Thu Tiền", 5, 5, 1)),
            ("Giải Trình ZNS", lambda: self.run_command("Giải Trình ZNS", 6, 5, 1)),
            ("Đơn Lấy Chưa Gán", lambda: self.run_command("Đơn Lấy Chưa Gán", 7, 5, 1)),
            ("Phiếu Thu COD", lambda: self.run_command("Phiếu Thu COD", 8, 5, 1)),
            ("Làm Mới GHN", lambda: self.reset_sheet())
        ]
        for text, command in functions:
            ttk.Button(right_frame, text=text, command=command).pack(fill="x", pady=3)
        ttk.Button(right_frame, text="Đăng xuất", command=self.logout, style='Large.TButton').pack(fill="x", pady=(30, 3))

    def setup_version_frame(self):
        for widget in self.version_frame.winfo_children():
            widget.destroy()
        version_container = ttk.Frame(self.version_frame, padding=30)
        version_container.pack(fill="both", expand=True)
        download_frame = ttk.LabelFrame(version_container, text="Đường dẫn tải về", padding=10)
        download_frame.pack(fill="x", pady=10)
        ttk.Entry(download_frame, textvariable=self.download_path, width=50).pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(download_frame, text="Chọn thư mục", command=self.choose_download_path).pack(side="right", padx=5)
        self.progress_frame = ttk.LabelFrame(version_container, text="Tiến trình cập nhật", padding=10)
        self.progress_frame.pack(fill="x", pady=10)
        self.progress_label = ttk.Label(self.progress_frame, text="Sẵn sàng", wraplength=500)
        self.progress_label.pack(fill="x", pady=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', maximum=100)
        self.progress_bar.pack(fill="x", pady=5)
        download_info_frame = ttk.Frame(self.progress_frame)
        download_info_frame.pack(fill="x", pady=5)
        ttk.Label(download_info_frame, text="Tốc độ tải:", style='Status.TLabel').pack(side="left")
        ttk.Label(download_info_frame, textvariable=self.download_speed_var, style='Status.TLabel').pack(side="left", padx=10)
        ttk.Label(download_info_frame, text="Kích thước:", style='Status.TLabel').pack(side="left")
        ttk.Label(download_info_frame, textvariable=self.file_size_var, style='Status.TLabel').pack(side="left", padx=10)
        try:
            response = requests.get(GITHUB_API_URL)
            response.raise_for_status()
            latest_release = response.json()
            new_version = latest_release['tag_name'].lstrip('v')
            ttk.Label(version_container, text="Thông tin phiên bản", font=('Helvetica', 20, 'bold')).pack(pady=20)
            ttk.Label(version_container, text=f"Phiên bản hiện tại: {CURRENT_VERSION}", font=('Helvetica', 14)).pack(pady=5)
            ttk.Label(version_container, text=f"Phiên bản mới nhất: {new_version}", font=('Helvetica', 14)).pack(pady=5)
            if CURRENT_VERSION != new_version:
                ttk.Label(version_container, text="Có phiên bản mới! Vui lòng cập nhật.", font=('Helvetica', 12, 'bold'), foreground=theme_colors["warning"]).pack(pady=5)
                ttk.Button(version_container, text="Tải và cài đặt phiên bản mới", command=lambda: self.start_auto_update(new_version), style='Large.TButton').pack(pady=10)
            else:
                ttk.Label(version_container, text="Bạn đang sử dụng phiên bản mới nhất", font=('Helvetica', 12), foreground=theme_colors["success"]).pack(pady=5)
        except Exception as e:
            ttk.Label(version_container, text=f"Lỗi: {str(e)}", foreground=theme_colors["error"], wraplength=500).pack(pady=30)

    def choose_download_path(self):
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)

    def update_progress(self, message, progress=None):
        self.progress_label.config(text=message)
        if progress is not None:
            self.progress_bar['value'] = progress
        self.progress_frame.update()

    def update_download_info(self, speed, size):
        self.download_speed_var.set(f"{speed:.2f} KB/s")
        self.file_size_var.set(f"{size:.2f} MB")

    def start_auto_update(self, new_version):
        if messagebox.askyesno("Xác nhận", "Cập nhật phiên bản mới?"):
            threading.Thread(target=lambda: self.auto_update_process(new_version), daemon=True).start()

    def auto_update_process(self, new_version):
        try:
            self.update_progress("Đang kiểm tra cập nhật..." , 0)
            response = requests.get(GITHUB_API_URL)
            response.raise_for_status()
            release_info = response.json()
            rar_url = next((asset['browser_download_url'] for asset in release_info['assets'] if asset['name'] == 'GHN.rar'), None)
            if not rar_url:
                self.update_progress("Không tìm thấy GHN.rar", 0)
                return
            temp_dir = tempfile.mkdtemp()
            rar_path = os.path.join(temp_dir, "GHN.rar")
            self.update_progress("Đang tải GHN.rar...", 20)
            response = requests.get(rar_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            with open(rar_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        progress = (downloaded_size / total_size) * 50 if total_size else 20
                        self.update_progress("Đang tải GHN.rar...", progress)
            if not os.path.exists(rar_path):
                self.update_progress("Lỗi tải GHN.rar", 0)
                return
            self.update_progress("Đang giải nén GHN.rar...", 50)
            with rarfile.RarFile(rar_path) as rar_ref:
                rar_ref.extractall(temp_dir)
            self.update_progress("Đang cập nhật file...", 70)
            app_dir = os.path.dirname(os.path.abspath(__file__))
            if os.path.exists(os.path.join(temp_dir, "GHN.py")):
                shutil.copy2(os.path.join(temp_dir, "GHN.py"), os.path.join(app_dir, "GHN.py"))
            else:
                self.update_progress("Không tìm thấy GHN.py trong file RAR", 0)
                return
            self.update_progress("Đang dọn dẹp...", 90)
            shutil.rmtree(temp_dir, ignore_errors=True)
            self.update_progress("Cập nhật hoàn tất, khởi động lại...", 100)
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)
            subprocess.Popen([python_exe, script_path])
            self.after(2000, self.quit)
        except Exception as e:
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(f"{time.ctime()}: Lỗi cập nhật - {str(e)}\n")
            self.update_progress(f"Lỗi: {str(e)}", 0)

    def auto_update(self):
        while True:
            try:
                response = requests.get(GITHUB_API_URL)
                response.raise_for_status()
                latest_release = response.json()
                new_version = latest_release['tag_name'].lstrip('v')
                if CURRENT_VERSION != new_version:
                    self.setup_version_frame()
            except Exception as e:
                with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                    log_file.write(f"{time.ctime()}: Lỗi kiểm tra cập nhật - {str(e)}\n")
            time.sleep(300)

    def authenticate_user(self):
        """Authenticate user credentials"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        if check_credentials(username, password):
            global current_user
            current_user = username
            messagebox.showinfo("Thành công", "Đăng nhập thành công!")
            self.setup_home_frame()
            self.setup_version_frame()
            self.notebook.select(1)  # Switch to the "Trang Chủ" tab
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

    def show_token_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Cập nhật Token")
        dialog.geometry("500x250")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry(f"+{self.winfo_x() + 350}+{self.winfo_y() + 225}")
        ttk.Label(dialog, text="Nhập token mới:", font=('Helvetica', 12)).pack(pady=30)
        token_entry = ttk.Entry(dialog, width=50)
        token_entry.pack(pady=10)
        ttk.Button(dialog, text="Cập nhật", command=lambda: self.update_token(token_entry.get(), dialog), style='Large.TButton').pack(pady=20)

    def update_token(self, token, dialog):
        if not token:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập token!")
            return
        try:
            sheet = authenticate_google_sheets()
            worksheet = sheet.worksheet("GHN")
            worksheet.update_cell(1, 7, token)
            worksheet.update_cell(1, 5, "1")
            dialog.destroy()
            self.status_label.config(text="Đang cập nhật token...")
            threading.Thread(target=self.check_token_update, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật token: {e}")

    def check_token_update(self):
        try:
            sheet = authenticate_google_sheets()
            worksheet = sheet.worksheet("GHN")
            attempts = 0
            while attempts < 30:
                result = worksheet.cell(1, 6).value
                if result:
                    self.status_label.config(text=f"Kết quả: {result}")
                    worksheet.update_cell(1, 5, "")
                    worksheet.update_cell(1, 6, "")
                    break
                time.sleep(10)
                attempts += 1
            if attempts >= 30:
                self.status_label.config(text="Hết thời gian chờ")
        except Exception as e:
            self.status_label.config(text=f"Lỗi: {e}")

    def run_command(self, command_name, row, col, value):
        try:
            sheet = authenticate_google_sheets()
            worksheet = sheet.worksheet("GHN")
            if worksheet.cell(row, 4).value == "1":
                command_id = f"{command_name}_{int(time.time())}"
                running_commands[command_id] = {"name": command_name, "status": "Đang chạy", "start_time": time.time()}
                self.update_running_commands_display()
                self.status_label.config(text=f"Đang thực hiện: {command_name}")
                worksheet.update_cell(row, col, value)
                threading.Thread(target=lambda: self.check_result(command_id, row), daemon=True).start()
            else:
                self.status_label.config(text="Chức năng đang bảo trì")
        except Exception as e:
            self.status_label.config(text=f"Lỗi: {e}")

    def check_result(self, command_id, row):
        try:
            sheet = authenticate_google_sheets()
            worksheet = sheet.worksheet("GHN")
            attempts = 0
            while attempts < 1200:
                result = worksheet.cell(row, 6).value
                if result:
                    running_commands[command_id]["status"] = result
                    self.status_label.config(text=f"Kết quả: {result}")
                    worksheet.update_cell(row, 5, "")
                    worksheet.update_cell(row, 6, "")
                    self.update_running_commands_display()
                    break
                time.sleep(1)
                attempts += 1
            if attempts >= 1200:
                running_commands[command_id]["status"] = "Hết thời gian chờ"
                self.status_label.config(text="Hết thời gian chờ")
                self.update_running_commands_display()
        except Exception as e:
            self.status_label.config(text=f"Lỗi: {e}")

    def update_running_commands_display(self):
        for widget in self.running_commands_frame.winfo_children():
            widget.destroy()
        for command_id, command_info in running_commands.items():
            ttk.Label(self.running_commands_frame, text=f"{command_info['name']} - {command_info['status']}", font=('Helvetica', 9)).pack(anchor="w", pady=2)

    def sync_commands(self):
        while True:
            try:
                sheet = authenticate_google_sheets()
                worksheet = sheet.worksheet("GHN")
                running_statuses = worksheet.range("E2:E8")
                for i, status in enumerate(running_statuses):
                    if status.value == "1":
                        command_name = f"Command_{i+2}"
                        if command_name not in running_commands:
                            self.run_command(command_name, i+2, 5, 1)
            except Exception as e:
                with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                    log_file.write(f"{time.ctime()}: Lỗi sync_commands - {str(e)}\n")
            time.sleep(5)

    def update_ping(self):
        while True:
            try:
                latency = ping("8.8.8.8")
                if latency:
                    self.network_label.config(text=f"Ping: {latency*1000:.0f}ms", foreground=theme_colors["success"])
                else:
                    self.network_label.config(text="Mất kết nối", foreground=theme_colors["error"])
            except:
                self.network_label.config(text="Lỗi kết nối", foreground=theme_colors["error"])
            time.sleep(1)

    def command_worker(self):
        while True:
            try:
                command = command_queue.get(timeout=1)
                if command:
                    self.run_command(*command)
            except:
                pass

    def reset_sheet(self):
        if messagebox.askyesno("Xác Nhập", "Xóa toàn bộ dữ liệu?"):
            try:
                sheet = authenticate_google_sheets()
                worksheet = sheet.worksheet("GHN")
                worksheet.batch_clear(["E1:F12"])
                self.status_label.config(text="Đã xóa dữ liệu thành công!")
            except Exception as e:
                self.status_label.config(text=f"Lỗi: {e}")
                messagebox.showerror("Lỗi", f"Không thể xóa dữ liệu: {e}")

    def logout(self):
        if messagebox.askyesno("Xác Nhận", "Đăng xuất?"):
            global current_user
            current_user = None
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.notebook.select(0)

if __name__ == "__main__":
    app = GHNApp()
    app.mainloop()
