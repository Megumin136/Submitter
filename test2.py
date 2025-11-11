import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import os
import requests
import threading

BASE_URL = "https://stevec.pythonanywhere.com/assignments"
KEY_URL = f"{BASE_URL}/api-key"
PASS_URL = f"{BASE_URL}/password"

# ------------------ Helper Functions ------------------
def sha256sum(filename):
    """计算文件 SHA256 / Compute file SHA256"""
    h = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def submit_assignment(student_id, group_id, password, filename, assignment):
    if not os.path.exists(filename):
        messagebox.showerror("Error / 错误", "File not found / 文件不存在")
        return

    data = {"student_id": student_id, "password": password, "assignment": assignment}
    if group_id:
        data["group_id"] = group_id

    try:
        with open(filename, "rb") as f:
            files = {"file": f}
            r = requests.post(BASE_URL, data=data, files=files)
    except Exception as e:
        messagebox.showerror("Error / 错误", f"Submission failed / 提交失败:\n{e}")
        return

    sha = sha256sum(filename)
    messagebox.showinfo("Submission Result / 提交结果",
                        f"Server Response / 服务器返回:\n{r.text}\n\n"
                        f"Local SHA256 / 本地 SHA256:\n{sha}\n\n"
                        "Please compare SHA256 with server response.\n如果不匹配，请联系 Steve / Please contact Steve if mismatched.")

def change_password(student_id, old_password, new_password):
    if len(new_password) < 8:
        messagebox.showerror("Error / 错误", "New password must be at least 8 characters / 新密码长度必须至少 8 位")
        return
    try:
        r = requests.post(PASS_URL, json={
            "student_id": student_id,
            "current_password": old_password,
            "new_password": new_password
        })
        messagebox.showinfo("Change Password Result / 修改密码结果", r.text)
    except Exception as e:
        messagebox.showerror("Error / 错误", f"Change password failed / 修改密码失败:\n{e}")

def get_api_key(student_id, password):
    try:
        r = requests.post(KEY_URL, json={"student_id": student_id, "password": password})
        messagebox.showinfo("API Key / API 密钥", r.text)
    except Exception as e:
        messagebox.showerror("Error / 错误", f"Get API Key failed / 获取 API 密钥失败:\n{e}")

# ------------------ GUI Actions ------------------
def browse_file():
    path = filedialog.askopenfilename()
    if path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, path)

def submit_action():
    sid = entry_sid_submit.get().strip()
    gid = entry_gid.get().strip() or None
    pwd = entry_pwd_submit.get().strip()
    assignment = entry_assignment.get().strip()
    file_path = entry_file.get().strip()

    if not (sid and pwd and assignment and file_path):
        messagebox.showwarning("Missing Info / 信息缺失", "Student ID, Assignment Name, Password and File are required / 学号、作业名、密码和文件均为必填")
        return

    threading.Thread(target=submit_assignment, args=(sid, gid, pwd, file_path, assignment), daemon=True).start()

def change_password_action():
    sid = entry_sid_pw.get().strip()
    old_pw = entry_old_pw.get().strip()
    new_pw = entry_new_pw.get().strip()
    new_pw2 = entry_new_pw_repeat.get().strip()

    if not (sid and old_pw and new_pw and new_pw2):
        messagebox.showwarning("Missing Info / 信息缺失", "Please fill all password fields / 请填写所有密码信息")
        return

    if new_pw != new_pw2:
        messagebox.showerror("Error / 错误", "New passwords do not match / 两次输入的新密码不一致")
        return

    threading.Thread(target=change_password, args=(sid, old_pw, new_pw), daemon=True).start()

def api_key_action():
    sid = entry_sid_submit.get().strip()
    pwd = entry_pwd_submit.get().strip()

    if not (sid and pwd):
        messagebox.showwarning("Missing Info / 信息缺失", "Please enter Student ID and Password / 请填写学号和密码")
        return

    threading.Thread(target=get_api_key, args=(sid, pwd), daemon=True).start()

# ------------------ GUI Layout ------------------
root = tk.Tk()
root.title("Steve Assignment Helper / 作业助手")

# ======= Password / 改密码 Block =======
frame_pw = tk.LabelFrame(root, text="Change Password / 修改密码", padx=10, pady=10)
frame_pw.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

tk.Label(frame_pw, text="Student ID / 学号:").grid(row=0, column=0, sticky="e")
entry_sid_pw = tk.Entry(frame_pw, width=30)
entry_sid_pw.grid(row=0, column=1)

tk.Label(frame_pw, text="Current Password / 当前密码:").grid(row=1, column=0, sticky="e")
entry_old_pw = tk.Entry(frame_pw, show="*", width=30)
entry_old_pw.grid(row=1, column=1)

tk.Label(frame_pw, text="New Password / 新密码:").grid(row=2, column=0, sticky="e")
entry_new_pw = tk.Entry(frame_pw, show="*", width=30)
entry_new_pw.grid(row=2, column=1)

tk.Label(frame_pw, text="Repeat New Password / 重复新密码:").grid(row=3, column=0, sticky="e")
entry_new_pw_repeat = tk.Entry(frame_pw, show="*", width=30)
entry_new_pw_repeat.grid(row=3, column=1)

tk.Button(frame_pw, text="Change Password / 修改密码", command=change_password_action).grid(row=4, column=0, columnspan=2, pady=5)

# ======= Submission / 提交作业 Block =======
frame_submit = tk.LabelFrame(root, text="Submit Assignment / 提交作业", padx=10, pady=10)
frame_submit.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

tk.Label(frame_submit, text="Student ID / 学号:").grid(row=0, column=0, sticky="e")
entry_sid_submit = tk.Entry(frame_submit, width=30)
entry_sid_submit.grid(row=0, column=1)

tk.Label(frame_submit, text="Group ID (optional) / 小组ID(可选):").grid(row=1, column=0, sticky="e")
entry_gid = tk.Entry(frame_submit, width=30)
entry_gid.grid(row=1, column=1)

tk.Label(frame_submit, text="Password / 密码:").grid(row=2, column=0, sticky="e")
entry_pwd_submit = tk.Entry(frame_submit, show="*", width=30)
entry_pwd_submit.grid(row=2, column=1)

tk.Label(frame_submit, text="Assignment Name / 作业名称:").grid(row=3, column=0, sticky="e")
entry_assignment = tk.Entry(frame_submit, width=30)
entry_assignment.grid(row=3, column=1)

tk.Label(frame_submit, text="File / 文件:").grid(row=4, column=0, sticky="e")
entry_file = tk.Entry(frame_submit, width=30)
entry_file.grid(row=4, column=1)
tk.Button(frame_submit, text="Browse / 浏览", command=browse_file).grid(row=4, column=2)

tk.Button(frame_submit, text="Submit Assignment / 提交作业", command=submit_action).grid(row=5, column=0, columnspan=3, pady=5)
tk.Button(frame_submit, text="Get API Key / 获取 API 密钥", command=api_key_action).grid(row=6, column=0, columnspan=3, pady=5)

tk.Label(root, text="Note / 注意: Do NOT share your password / 请勿泄露密码", fg="red").grid(row=2, column=0, pady=5)

root.mainloop()
