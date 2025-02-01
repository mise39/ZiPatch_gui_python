import os
import zipfile
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from tkinter import font as tkfont
import threading
import subprocess

# 預設路徑
downloads_path = Path("/home/deck/Downloads")
temp_path = downloads_path / "Temp"
default_destination = Path("/home/deck/.local/share/Steam/steamapps/common")

# 解壓縮功能（支援 zip, rar, 7z）
def extract_archive(archive_path, extract_to):
    """解壓縮檔案（支援 zip, rar, 7z）"""
    try:
        if archive_path.endswith(".zip"):
            with zipfile.ZipFile(archive_path, 'r') as archive_ref:
                archive_ref.extractall(extract_to)
        elif archive_path.endswith(".rar"):
            # 使用 unrar 解壓縮
            command = ["unrar", "x", archive_path, extract_to]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                if "password" in result.stderr.decode('utf-8').lower():
                    raise ValueError("有密碼的壓縮檔，SKIP!")
                raise Exception(f"解壓縮失敗: {result.stderr.decode('utf-8')}")
        elif archive_path.endswith(".7z"):
            # 使用 7z 解壓縮
            command = ["7z", "x", archive_path, f"-o{extract_to}"]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                if "password" in result.stderr.decode('utf-8').lower():
                    raise ValueError("有密碼的壓縮檔，SKIP!")
                raise Exception(f"解壓縮失敗: {result.stderr.decode('utf-8')}")
        else:
            raise ValueError("不支援的檔案格式")
        status_label.config(text=f"解壓縮完成！已解壓縮至: {extract_to}")  # 更新狀態

    except ValueError as e:
        messagebox.showwarning("跳過處理", str(e))
    except Exception as e:
        messagebox.showerror("錯誤", f"解壓縮失敗: {str(e)}")

# 總結目錄結構（從 Temp 下一層開始顯示，包含檔案和資料夾）
def summarize_directory(directory):
    """總結目錄結構"""
    summary = "📁 結構:\n"
    first_level_items = list(directory.iterdir())
    for item in first_level_items:
        if item.is_dir():
            summary += f"📂 {item.name}/\n"
            for sub_item in item.rglob("*"):  # 遞迴顯示子資料夾和檔案
                level = len(sub_item.relative_to(item).parts)
                indent = ' ' * 4 * level
                if sub_item.is_dir():
                    summary += f"{indent}📂 {sub_item.name}/\n"
                else:
                    summary += f"{indent}📄 {sub_item.name}\n"
        else:
            summary += f"📄 {item.name}\n"
    return summary

# 移動內容（覆蓋同名檔案）
def move_contents(src, dst):
    """移動 src 目錄中的所有內容到 dst 目錄，覆蓋同名檔案"""
    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)
        if os.path.exists(dst_item):  # 如果目標已存在，先刪除
            if os.path.isdir(dst_item):
                shutil.rmtree(dst_item)
            else:
                os.remove(dst_item)
        if os.path.isdir(src_item):
            shutil.move(src_item, dst_item)
        else:
            shutil.move(src_item, dst_item)

# 清空 Temp 目錄
def clear_temp_directory():
    """清空 Temp 目錄"""
    if temp_path.exists():
        for item in temp_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                os.remove(item)
        print("已清空 Temp 目錄")

# 主邏輯
def process_archive():
    # 清空 Temp 目錄
    clear_temp_directory()

    # 選擇壓縮檔案
    archive_path = filedialog.askopenfilename(
        initialdir=downloads_path,
        title="選擇壓縮檔",
        filetypes=(("壓縮檔", "*.zip *.rar *.7z"),)
    )
    if not archive_path:
        return

    # 更新標題為已選擇的檔案名
    selected_file_label.config(text=f"已選擇檔案: {os.path.basename(archive_path)}")

    # 顯示處理中狀態
    status_label.config(text="正在解壓縮，請稍候...")
    root.update()  # 更新畫面

    # 在背景執行解壓縮
    def extract_in_background():
        try:
            extract_archive(archive_path, temp_path)
            status_label.config(text="解壓縮完成！")  # 更新狀態
            update_summary()  # 更新目錄結構
            check_single_folder()  # 檢查是否只有一個資料夾
        except Exception as e:
            status_label.config(text="解壓縮失敗！")

    threading.Thread(target=extract_in_background).start()

# 更新目錄結構總結
def update_summary():
    summary = summarize_directory(temp_path)
    summary_text.delete(1.0, tk.END)  # 清空舊內容
    summary_text.insert(tk.END, summary)



# 檢查第一層是否只有一個資料夾
def check_single_folder():
    first_level_items = list(temp_path.iterdir())
    if len(first_level_items) == 1 and first_level_items[0].is_dir():
        single_folder = first_level_items[0]

        title_label_left.config(text="確認視窗")  # 更新狀態
        status_label.config(text=f"解壓縮完成！只有一個資料夾 {single_folder.name}，是否要刪除並將內容移出?")
        select_archive_button.grid_forget()
        yesdel_button.grid(row=3, column=0, padx=(10,200), pady=10, sticky="e")
        nodel_button.grid(row=3, column=0, padx=(200,10), pady=10, sticky="e")



def process_delyes():
    first_level_items = list(temp_path.iterdir())
    single_folder = first_level_items[0]
    move_contents(single_folder, temp_path)
    shutil.rmtree(single_folder)
    update_summary()  # 更新目錄結構
    title_label_left.config(text="解壓縮工具")
    status_label.config(text=f" {single_folder.name} 刪除成功")
    yesdel_button.grid_forget()
    nodel_button.grid_forget()
    root.after(2000,move_file)


def move_file():
    destination = filedialog.askdirectory(
        initialdir=default_destination,
        title="選擇目的地"
    )
    if not destination:
        return

    for item in temp_path.iterdir():
        dst_item = Path(destination) / item.name

        try:
            if item.is_dir():  # ⚡ 資料夾：合併內容
                dst_item.mkdir(exist_ok=True)  # 確保資料夾存在
                for sub_item in item.iterdir():  # 遍歷來源資料夾內的檔案
                    sub_dst = dst_item / sub_item.name
                    if sub_item.is_dir():
                        shutil.copytree(sub_item, sub_dst, dirs_exist_ok=True)  # 合併子資料夾
                    else:
                        shutil.copy2(sub_item, sub_dst)  # 覆蓋檔案
                shutil.rmtree(item)  # 刪除來源資料夾

            else:  # ⚡ 檔案：直接覆蓋
                shutil.copy2(item, dst_item)
                os.remove(item)  # 刪除來源檔案
            
        except Exception as e:
            status_label.config(text=f"發生錯誤: {e}")
            return

    status_label.config(text=f"移動完成, 已移動檔案至: {destination}")
    root.after(2000, close_app)


def close_app():
    # 詢問是否關閉程序
    if messagebox.askyesno("關閉程序", "是否關閉解壓縮工具？"):
        root.quit()  # 完全關閉程序
    else:
        title_label_left.config(text="解壓縮工具")
        selected_file_label.config(text="未選擇解縮檔", font=("Helvetica", 12))
        status_label.config(text="", font=("Helvetica", 12))
        select_archive_button.grid(row=3, column=0, columnspan=2, pady=10)
        summary_text.delete(1.0, tk.END)

# 創建 GUI
root = tk.Tk()
root.title("解壓縮工具")
root.geometry("800x600")

# 設置字型
default_font = tkfont.nametofont("TkDefaultFont")
default_font.configure(size=12)
root.option_add("*Font", default_font)

# 設置主題
style = ttk.Style()
style.theme_use("clam")  # 使用 "clam" 主題，支援更多自訂選項

# 主框架
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill="both", expand=True)

title_label_left = ttk.Label(main_frame, text="解壓縮工具", font=("Helvetica", 16, "bold"))
title_label_left.grid(row=0, column=0, columnspan=2, pady=10, sticky="ns")

# 已選擇檔案標籤
selected_file_label = ttk.Label(main_frame, text="未選擇解縮檔", font=("Helvetica", 12))
selected_file_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="ns")

# 狀態標籤
status_label = ttk.Label(main_frame, text="", font=("Helvetica", 12))
status_label.grid(row=2, column=0, columnspan=2, pady=10, sticky="ns")

# 選擇壓縮檔案按鈕
select_archive_button = ttk.Button(main_frame, text="選擇壓縮檔", command=process_archive)
select_archive_button.grid(row=3, column=0, columnspan=2, pady=10)


# yes button
yesdel_button = ttk.Button(main_frame, text="確定刪除", command=process_delyes)
yesdel_button.grid(row=3, column=0, padx=10, pady=10, sticky="e")

# no button
nodel_button = ttk.Button(main_frame, text="不刪除並繼續", command=move_file)
nodel_button.grid(row=3, column=1, padx=10, pady=10, sticky="w")

yesdel_button.grid_forget()
nodel_button.grid_forget()



# 顯示目錄結構的文本框
summary_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=20)
summary_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="")

main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# 運行主循環
root.mainloop()
