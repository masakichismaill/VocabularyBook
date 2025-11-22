import tkinter as tk


root = tk.Tk()
root.title("英単語帳アプリ")
root.geometry("900x600")
# 単語を保存するリスト
words = []  # 例: {"english": "apple","japanese": "りんご"}を入れていく


# ======================
# 関数エリア
# ======================
def refresh_word_list():
    """wordsの中身を左の画面(Listbox)に反映する"""
    word_listbox.delete(0, tk.END)
    for w in words:
        # ここでは「apple - りんご」のような表示にしておく
        line = f"{w['english']} - {w['japanese']}"
        word_listbox.insert(tk.END, line)


def add_word():
    """入力欄から単語を読み取ってwordsに追加する"""
    eng = en_entry.get().strip()
    jp = ja_entry.get().strip()
    ex = example_text.get("1.0", tk.END).strip()

    if not eng or not jp:
        print("英単語と日本語の両方を入力してください。")
        return
    # １つの単語を辞書で表現
    word = {"english": eng, "japanese": jp, "example": ex}
    # リスト（箱）に追加
    words.append(word)
    # 入力欄をクリア
    en_entry.delete(0, tk.END)
    ja_entry.delete(0, tk.END)
    example_text.delete("1.0", tk.END)
    # 画面のリストを更新
    refresh_word_list()


def on_select(event):
    """左のリストで選ばれた単語を右の入力欄に表示する"""
    if not words:
        return
    selection = word_listbox.curselection()
    if not selection:
        return

    index = selection[0]
    w = words[index]

    # 一旦クリア
    en_entry.delete(0, tk.END)
    ja_entry.delete(0, tk.END)
    example_text.delete("1.0", tk.END)
    # 選んだ単語の内容を入れ直す
    en_entry.insert(0, w["english"])
    ja_entry.insert(0, w["japanese"])
    # 例文があれば入れる（古いデータにexampleがない場合の保険も兼ねて）
    if "example" in w:
        example_text.insert("1.0", w["example"])


# ======================
# 左側: 単語一覧エリア
# ======================
left_frame = tk.Frame(root, padx=10, pady=10)
left_frame.pack(side="left", fill="y")

# 一覧ラベル
list_label = tk.Label(left_frame, text="単語一覧", font=("メイリオ", 11, "bold"))
list_label.pack(anchor="w")

# Listbox(単語リスト)
word_listbox = tk.Listbox(left_frame, width=30, height=25)
word_listbox.pack(side="left", fill="y")
word_listbox.bind("<<ListboxSelect>>", on_select)

# スクロールバー
scrollbar = tk.Scrollbar(left_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

# Listboxとスクロールバーを連動
word_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=word_listbox.yview)

# ==================
# 右側: 単語編集エリア
# ==================
right_frame = tk.Frame(root, padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True)

# ---英単語---
en_label = tk.Label(right_frame, text="英単語(English)", font=("メイリオ", 11, "bold"))
en_label.pack(anchor="w")

en_entry = tk.Entry(right_frame)
en_entry.pack(fill="x")

# ---日本語---
ja_label = tk.Label(right_frame, text="日本語(Japanese)", font=("メイリオ", 11, "bold"))
ja_label.pack(anchor="w", pady=(10, 0))

ja_entry = tk.Entry(right_frame)
ja_entry.pack(fill="x")

# ---例文---
example_label = tk.Label(
    right_frame, text="例文(Example sentence)", font=("メイリオ", 10)
)
example_label.pack(anchor="w", pady=(10, 0))

example_text = tk.Text(right_frame, wrap="word", height=10)
example_text.pack(fill="both", expand=True)

# ==========================
# ボタンエリア
# ==========================
button_frame = tk.Frame(right_frame, pady=10)
button_frame.pack(fill="x")

new_button = tk.Button(button_frame, text="新規", width=10, command=add_word)
save_button = tk.Button(button_frame, text="保存", width=10)
delete_button = tk.Button(button_frame, text="削除", width=10)
quiz_button = tk.Button(button_frame, text="クイズ", width=10)

new_button.pack(side="left", padx=5)
save_button.pack(side="left", padx=5)
delete_button.pack(side="left", padx=5)
quiz_button.pack(side="right", padx=5)
root.mainloop()
