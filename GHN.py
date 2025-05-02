import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import gspread
import os
import sys
import threading
import time
import webbrowser
import zipfile
import requests
from google.oauth2.service_account import Credentials
from ping3 import ping
from queue import Queue
import shutil
import rarfile
import tempfile
import subprocess

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
GITHUB_ZIP_URL = "https://github.com/hoangdung997/DEVDungtau/archive/refs/tags/{}.zip"
CURRENT_VERSION = "1.0.0"  # Phiên bản hiện tại, thấp hơn v1.0.1 để kích hoạt cập nhật

def authenticate_google_sheets():
    """Authenticate with Google Sheets using embedded service account credentials"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = {
        "type": "service_account",
        "project_id": "earnest-vent-424814-h1",
        "private_key_id": "a15335bafd870b70c3f9d56e2ca00d6d3a860b19",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQClX8rmrM0hdqVq\nNd5Zhq3YMnvPitns24HlP9cRXMUMs2QVpDs7wv5xIsC221++z8BBPWrbgc423uvS\nZOIhTmnn8370TQ3+UbjrUzavnvIgzeghmExzsviJOlqGQb4+uYTi5G+tFOaVqcIv\nvL0OYqrBeXjRONWVEBZp3oPhmmskPjZO92yqZqF1G41Zhufb+H6rElFkSRtEh2wT\nA3NelEMpPQRGp85C2gfF4nlzQBB04Q5m5EJFlazh+k01aG55zNVgjln+Ll5ZlPye\nPaY75fC15ogFqOKUfS/MYuxfvGt/Kg5cpIB34wYjpGZwSxzSbF74PgQ/wPuvbrR3\nqPvUUpKTAgMBAAECggEAGRen2chud51hC/SQgFUHG77NOnh/CIll9Drzjxbcb0jo\n7r+0nSTBJrl3NEelB3bOXRfMlvHjMEAy2AGmrhcPyroPkVH/xY7w2AQQUCV157RW\nfIJ3VzbYrznDcouXKj1MBIFU0JZTRnIznLqulPgzoJel1VkiTzPZssaojBq6Fw16\n7UBzXsx2/KPjS6mahzerV/S1tLbqsDI6vzKZ0fNOo70b/Iwx1RVdq4dxnawFSxhU\n9q7JOIBfd8U8QgrwAe6kCYurKTXjsLAwgnim2CucYubh8HIK0hYMZurN56nNXU7u\nzSGRijCeZwhCppKBQ9K+1ZbVxruplDa06yjIMO6dgQKBgQDbpCqNgDysgs8AgpQW\nTFHZsSq7e6M3E+8tolOrfTQt4h2J0pkAPuHRW/2+hJtX0y4wV3b6ZQybCa8CecSQ\nWYVOyXvwYNKL4vesFOipnD2DmOG4goQzIbBZcgLx7nXk4fr3cRxAPDXD8YpUqSkz\nMtwFdILXqDegk1Qykzgs+5myKQKBgQDAv+0wvdYw2bdxDCoPiC4YhpHDY0b2VihV\n4dLEQxI3slQA5fIDUxOIkOSZBi7W7fZrKeX4zzG/DEd7Joz0PmIlYBcHP9QtvL6l\n8EdcKjOIix6i1nOv9cObvARpLo3cubNpZxg/G0lbIAMqUP0NFx6YUlzCy2ZV9tGS\nHVfNJ6IOWwKBgAmy8CYbeZJsnFN7cKqjaCHizu5EgWqXOMKdHnC+MKWuDHvfjt4R\n6Mrj8wqMtIdmTe3Yjupzt+DIxq+nTOTK7zYRc6WjwOhod2Nj8Po8agL7p0wMh2Xy\noOTyQesJCq+2wuxWVFcJ0Z37do5Sgf0+y7R59qUrSnmOx/MLyTlDSwAxAoGAZvVe\nPn347sktGr6zrO5CKSmgrOzX1/e3vgBNdDabgZLJGl25w5rZwUYcRb0uwfIEgcO0\nqw4J9ZIakKbL/h9gj7RfOKkYroG2mK7bf1ivhE1DxRmmXCR8IzDwbjrG3lN3iWLf\nab4qlflol28BbL+fwR+lmwvJEzwvP8xavSRhhScCgYEAiZWIMnPJZxvDP6Y6z9p1\nE08s2AWMwyxfz6PM2fJ1U9Fsegn8EkbDc4pRY7CL+zxUnUCy0/ROTMPkn5G+rrsV\n8pQslap5iSjGGB2TASa/NZBnf6yyBiXZrVZI6tb++9J366sC025XkLf0ITYmKScg\nLAZq5wj28vAWl4n1jA7BXzc=\n-----END PRIVATE KEY-----\n",
        "client_email": "devdungtau@earnest-vent-424814-h1.iam.gserviceaccount.com",
        "client_id": "107552062671135118901",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/devdungtau%40earnest-vent-424814-h1.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/1CQasbMxm1YnaZjguihYjz4p_OBkApArjeqvd_CRAAow/edit?gid=1769102994#gid=1769102994")

def check_credentials(username, password):
    """Check if username and password are valid in Google Sheets"""
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
        messagebox.showerror("Lỗi kết nối", f"Không thể kết nối với Google Sheets: {e}")
        return False

class GHNApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Basic window setup
        self.title("🌏 GHN Tool by HOÀNG DŨNG 🌏")
        self.geometry("1200x700")
        self.configure(bg=theme_colors["background"])
        
        # Center window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 700) // 2
        self.geometry(f"1200x700+{x}+{y}")

        # Setup styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Create monitoring frame
        self.setup_monitor_frame()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Create frames for each tab
        self.login_frame = ttk.Frame(self.notebook)
        self.home_frame = ttk.Frame(self.notebook)
        self.version_frame = ttk.Frame(self.notebook)

        # Add tabs
        self.notebook.add(self.login_frame, text="Đăng Nhập")
        self.notebook.add(self.home_frame, text="Trang Chủ")
        self.notebook.add(self.version_frame, text="Phiên Bản")

        # Initialize download path and download info variables
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.download_speed_var = tk.StringVar(value="0 KB/s")
        self.file_size_var = tk.StringVar(value="0 MB")

        # Setup login frame
        self.setup_login_frame()

        # Setup version frame
        self.setup_version_frame()

        # Start threads
        threading.Thread(target=self.update_ping, daemon=True).start()
        threading.Thread(target=self.command_worker, daemon=True).start()
        threading.Thread(target=self.sync_commands, daemon=True).start()
        threading.Thread(target=self.auto_update, daemon=True).start()

    def configure_styles(self):
        """Configure ttk styles for consistent UI"""
        self.style.configure('TFrame', background=theme_colors["background"])
        self.style.configure('TLabel', 
                           background=theme_colors["background"], 
                           foreground=theme_colors["text"],
                           font=('Helvetica', 10))
        self.style.configure('TButton', 
                           padding=10,
                           font=('Helvetica', 10, 'bold'))
        self.style.configure('Large.TButton',
                           padding=15,
                           font=('Helvetica', 12, 'bold'))
        self.style.configure('Status.TLabel',
                           background=theme_colors["background"],
                           foreground=theme_colors["text"],
                           font=('Helvetica', 9))

    def setup_monitor_frame(self):
        """Setup network monitoring frame"""
        self.monitor_frame = ttk.Frame(self)
        self.monitor_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        self.network_label = ttk.Label(self.monitor_frame, 
                                     text="Đang kiểm tra mạng...",
                                     style='Status.TLabel')
        self.network_label.pack(side="left")

    def setup_login_frame(self):
        """Setup login frame UI"""
        login_container = ttk.Frame(self.login_frame, padding="50 70 50 50")
        login_container.pack(expand=True)

        title_label = ttk.Label(login_container,
                              text="GHN Tool",
                              font=('Helvetica', 28, 'bold'),
                              foreground=theme_colors["primary"])
        title_label.pack(pady=30)

        subtitle_label = ttk.Label(login_container,
                                 text="Đăng nhập để tiếp tục",
                                 font=('Helvetica', 12),
                                 foreground=theme_colors["secondary"])
        subtitle_label.pack(pady=(0, 30))

        username_frame = ttk.Frame(login_container)
        username_frame.pack(fill="x", pady=5)
        
        ttk.Label(username_frame,
                 text="Tên đăng nhập:",
                 font=('Helvetica', 10)).pack(anchor="w")
        
        self.username_entry = ttk.Entry(username_frame, width=40)
        self.username_entry.pack(fill="x", pady=5)

        password_frame = ttk.Frame(login_container)
        password_frame.pack(fill="x", pady=5)
        
        ttk.Label(password_frame,
                 text="Mật khẩu:",
                 font=('Helvetica', 10)).pack(anchor="w")
        
        self.password_entry = ttk.Entry(password_frame, width=40, show="•")
        self.password_entry.pack(fill="x", pady=5)

        login_button = ttk.Button(login_container,
                                text="ĐĂNG NHẬP",
                                command=self.authenticate_user,
                                style='Large.TButton')
        login_button.pack(pady=30)

    def setup_home_frame(self):
        """Setup home frame UI"""
        for widget in self.home_frame.winfo_children():
            widget.destroy()

        main_container = ttk.Frame(self.home_frame, padding=20)
        main_container.pack(fill="both", expand=True)

        left_frame = ttk.LabelFrame(main_container, text="Thông tin hệ thống", padding=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ttk.Label(left_frame,
                 text=f"Xin chào, {current_user}",
                 font=('Helvetica', 14, 'bold')).pack(anchor="w", pady=5)

        self.status_label = ttk.Label(left_frame,
                                    text="Sẵn sàng",
                                    font=('Helvetica', 10))
        self.status_label.pack(anchor="w", pady=5)

        self.running_commands_frame = ttk.LabelFrame(left_frame,
                                                   text="Lệnh đang chạy",
                                                   padding=15)
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
            btn = ttk.Button(right_frame, text=text, command=command)
            btn.pack(fill="x", pady=3)

        ttk.Button(right_frame,
                  text="Đăng xuất",
                  command=self.logout,
                  style='Large.TButton').pack(fill="x", pady=(30, 3))

    def setup_version_frame(self):
        """Setup version frame UI with enhanced update progress display"""
        for widget in self.version_frame.winfo_children():
            widget.destroy()

        version_container = ttk.Frame(self.version_frame, padding=30)
        version_container.pack(fill="both", expand=True)

        # Download path frame
        download_frame = ttk.LabelFrame(version_container, text="Đường dẫn tải về", padding=10)
        download_frame.pack(fill="x", pady=10)
        path_entry = ttk.Entry(download_frame, textvariable=self.download_path, width=50)
        path_entry.pack(side="left", padx=5, expand=True, fill="x")
        browse_btn = ttk.Button(download_frame, text="Chọn thư mục", command=self.choose_download_path)
        browse_btn.pack(side="right", padx=5)

        # Progress frame
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

        # Version info
        try:
            response = requests.get(GITHUB_API_URL)
            response.raise_for_status()
            latest_release = response.json()
            new_version = latest_release['tag_name'].lstrip('v')  # Bỏ 'v' (v1.0.1 -> 1.0.1)

            ttk.Label(version_container, text="Thông tin phiên bản", font=('Helvetica', 20, 'bold')).pack(pady=20)
            ttk.Label(version_container, text=f"Phiên bản hiện tại: {CURRENT_VERSION}", font=('Helvetica', 14)).pack(pady=5)
            ttk.Label(version_container, text=f"Phiên bản mới nhất: {new_version}", font=('Helvetica', 14)).pack(pady=5)

            if CURRENT_VERSION != new_version:
                ttk.Label(version_container, text="Có phiên bản mới! Vui lòng cập nhật.", font=('Helvetica', 12, 'bold'), foreground=theme_colors["warning"]).pack(pady=5)
                update_button = ttk.Button(version_container, text="Tải và cài đặt phiên bản mới", command=lambda: self.start_auto_update(new_version), style='Large.TButton')
                update_button.pack(pady=10)
            else:
                ttk.Label(version_container, text="Bạn đang sử dụng phiên bản mới nhất", font=('Helvetica', 12), foreground=theme_colors["success"]).pack(pady=5)
        except Exception as e:
            ttk.Label(version_container, text=f"Lỗi khi kiểm tra phiên bản: {str(e)}", foreground=theme_colors["error"], wraplength=500).pack(pady=30)

    def choose_download_path(self):
        """Open dialog to choose download directory"""
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)

    def update_progress(self, message, progress=None):
        """Update progress bar and label with detailed status"""
        self.progress_label.config(text=message)
        if progress is not None:
            self.progress_bar['value'] = progress
        self.progress_frame.update()

    def update_download_info(self, speed, size):
        """Update download speed and file size display"""
        self.download_speed_var.set(f"{speed:.2f} KB/s")
        self.file_size_var.set(f"{size:.2f} MB")

    def start_auto_update(self, new_version):
        """Start auto-update process in a separate thread"""
        threading.Thread(target=lambda: self.auto_update_process(new_version), daemon=True).start()

    def auto_update_process(self, new_version):
        """Handle auto-update process from GitHub"""
        try:
            self.update_progress("Đang kiểm tra thông tin cập nhật...", 0)
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")

            # Tải file ZIP
            self.update_progress("Đang tải phiên bản mới từ GitHub...", 20)
            download_url = GITHUB_ZIP_URL.format(f"v{new_version}")  # Thêm 'v' (1.0.1 -> v1.0.1)
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            start_time = time.time()
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        elapsed_time = time.time() - start_time
                        speed = (downloaded_size / 1024) / elapsed_time if elapsed_time > 0 else 0
                        size_mb = downloaded_size / (1024 * 1024)
                        self.update_download_info(speed, size_mb)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 50
                            self.update_progress("Đang tải phiên bản mới...", progress)

            # Giải nén
            self.update_progress("Đã tải xong, đang giải nén...", 50)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Thay thế file
            self.update_progress("Đang cập nhật file...", 70)
            extracted_dir = os.path.join(temp_dir, f"DEVDungtau-v{new_version}")  # Tên thư mục giải nén
            if not os.path.exists(extracted_dir):
                self.update_progress("Lỗi: Không tìm thấy thư mục mã nguồn", 0)
                return
            app_dir = os.path.dirname(os.path.abspath(__file__))
            for item in os.listdir(extracted_dir):
                src_path = os.path.join(extracted_dir, item)
                dst_path = os.path.join(app_dir, item)
                if os.path.isdir(src_path):
                    if os.path.exists(dst_path):
                        shutil.rmtree(dst_path, ignore_errors=True)
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

            # Dọn dẹp
            self.update_progress("Đang dọn dẹp...", 90)
            shutil.rmtree(temp_dir, ignore_errors=True)

            # Khởi động lại
            self.update_progress("Cập nhật hoàn tất, đang khởi động lại...", 95)
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)
            subprocess.Popen([python_exe, script_path])
            self.update_progress("Hoàn tất! Đóng phiên bản cũ sau 2 giây...", 100)
            self.after(2000, self.quit)
        except Exception as e:
            self.update_progress(f"Lỗi trong quá trình cập nhật: {str(e)}", 0)

    def auto_update(self):
        """Periodically check for updates from GitHub"""
        while True:
            try:
                response = requests.get(GITHUB_API_URL)
                response.raise_for_status()
                latest_release = response.json()
                new_version = latest_release['tag_name'].lstrip('v')
                if CURRENT_VERSION != new_version:
                    self.setup_version_frame()
            except Exception as e:
                print(f"Lỗi kiểm tra cập nhật: {e}")
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
            self.notebook.select(1)
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

    def show_token_dialog(self):
        """Show dialog for updating token"""
        dialog = tk.Toplevel(self)
        dialog.title("Cập nhật Token")
        dialog.geometry("500x250")
        dialog.transient(self)
        dialog.grab_set()

        dialog.geometry(f"+{self.winfo_x() + 350}+{self.winfo_y() + 225}")

        ttk.Label(dialog,
                 text="Nhập token mới:",
                 font=('Helvetica', 12)).pack(pady=30)

        token_entry = ttk.Entry(dialog, width=50)
        token_entry.pack(pady=10)

        ttk.Button(dialog,
                  text="Cập nhật",
                  command=lambda: self.update_token(token_entry.get(), dialog),
                  style='Large.TButton').pack(pady=20)

    def update_token(self, token, dialog):
        """Update token in Google Sheets"""
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
        """Check token update status"""
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
        """Run a command and monitor its status"""
        try:
            sheet = authenticate_google_sheets()
            worksheet = sheet.worksheet("GHN")

            if worksheet.cell(row, 4).value == "1":
                command_id = f"{command_name}_{int(time.time())}"
                running_commands[command_id] = {
                    "name": command_name,
                    "status": "Đang chạy",
                    "start_time": time.time()
                }
                self.update_running_commands_display()

                self.status_label.config(text=f"Đang thực hiện: {command_name}")
                worksheet.update_cell(row, col, value)

                def check_result():
                    attempts = 0
                    while attempts < 1200:  # 20 minutes timeout
                        try:
                            result = worksheet.cell(row, 6).value
                            if result:
                                running_commands[command_id]["status"] = result
                                self.status_label.config(text=f"Kết quả: {result}")
                                worksheet.update_cell(row, 5, "")
                                worksheet.update_cell(row, 6, "")
                                self.update_running_commands_display()
                                break
                        except Exception:
                            pass
                        time.sleep(1)
                        attempts += 1

                    if attempts >= 1200:
                        running_commands[command_id]["status"] = "Hết thời gian chờ"
                        self.status_label.config(text="Hết thời gian chờ")
                        self.update_running_commands_display()

                threading.Thread(target=check_result, daemon=True).start()
            else:
                self.status_label.config(text="Chức năng đang bảo trì")

        except Exception as e:
            self.status_label.config(text=f"Lỗi: {e}")

    def update_running_commands_display(self):
        """Update display of running commands"""
        for widget in self.running_commands_frame.winfo_children():
            widget.destroy()

        for command_id, command_info in running_commands.items():
            label_text = f"{command_info['name']}"
            ttk.Label(self.running_commands_frame,
                     text=label_text,
                     font=('Helvetica', 9)).pack(anchor="w", pady=2)

    def sync_commands(self):
        """Sync commands from Google Sheets"""
        while True:
            try:
                sheet = authenticate_google_sheets()
                worksheet = sheet.worksheet("GHN")
                running_statuses = worksheet.range("E2:E8")
                result_statuses = worksheet.range("F2:F8")

                for i, (status, result) in enumerate(zip(running_statuses, result_statuses)):
                    if status.value == "1":
                        command_name = f"Command_{i+2}"
                        if command_name not in running_commands:
                            self.run_command(command_name, i+2, 5, 1)
            except Exception:
                pass
            time.sleep(5)

    def update_ping(self):
        """Update network ping status"""
        while True:
            try:
                latency = ping("8.8.8.8")
                if latency:
                    self.network_label.config(
                        text=f"Ping: {latency*1000:.0f}ms",
                        foreground=theme_colors["success"]
                    )
                else:
                    self.network_label.config(
                        text="Mất kết nối",
                        foreground=theme_colors["error"]
                    )
            except:
                self.network_label.config(
                    text="Lỗi kết nối",
                    foreground=theme_colors["error"]
                )
            time.sleep(1)

    def command_worker(self):
        """Process commands from queue"""
        while True:
            try:
                command = command_queue.get(timeout=1)
                if command:
                    self.run_command(*command)
            except:
                pass

    def reset_sheet(self):
        """Reset Google Sheets data"""
        if messagebox.askyesno("Xác Nhận", "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu không?"):
            try:
                sheet = authenticate_google_sheets()
                worksheet = sheet.worksheet("GHN")
                worksheet.batch_clear(["E1:F12"])
                self.status_label.config(text="Đã xóa dữ liệu thành công!")
            except Exception as e:
                self.status_label.config(text=f"Lỗi: {e}")
                messagebox.showerror("Lỗi Hệ Thống", f"Không thể xóa dữ liệu: {e}")

    def logout(self):
        """Log out current user"""
        if messagebox.askyesno("Xác Nhận", "Bạn có chắc muốn đăng xuất?"):
            global current_user
            current_user = None
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.notebook.select(0)

if __name__ == "__main__":
    app = GHNApp()
    app.mainloop()
