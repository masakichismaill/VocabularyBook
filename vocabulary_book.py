import tkinter as tk
import json
import os
import requests

root = tk.Tk()
root.title("英単語帳アプリ")
root.geometry("1000x600")
# 単語を保存するリスト
words = []  # 例: {"english": "apple","japanese": "りんご"}を入れていく
# 保存するファイル名
WORDS_FILE = "words.json"
# 例として、英英辞書APIのURLを用意する（実際に使うAPIに合わせて変更可）
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"


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
    # "1.0"「１行目の０文字目」という意味。tk.END「テキストの一番最後」
    # つまり「１行目の先頭から最後まで全部ください」という意味になる

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
    # ファイルにも保存
    save_words_to_file()


def on_select(event):
    """左のリストで選ばれた単語を右の入力欄に表示する"""
    if not words:
        return
    selection = (
        word_listbox.curselection()
    )  # 今選ばれている行の番号たちをリストでもらう
    if not selection:
        return

    index = selection[0]  # その中の最初の番号（＝選択中の行番号）を取り出す
    w = words[index]

    # 一旦クリア
    en_entry.delete(0, tk.END)
    ja_entry.delete(0, tk.END)
    example_text.delete("1.0", tk.END)
    # 選んだ単語の内容を入れ直す
    en_entry.insert(0, w["english"])
    ja_entry.insert(0, w["japanese"])
    # 例文があれば入れる（古いデータにexampleがない場合の保険も兼ねて）
    if "example" in w:  # 例文があれば入れてあげる
        example_text.insert("1.0", w["example"])


def fetch_example_from_api():
    """en_entryの英単語をAPIに送り、返ってきた例文をexample_textに表示する"""
    eng = en_entry.get().strip()

    if not eng:
        print("まず英単語を入力してください。")
        return

    # ① URLを作る
    url = DICTIONARY_API_URL.format(eng)
    print("APIにアクセス:", url)

    try:
        # ② APIにリクエストを送る
        resp = requests.get(url, timeout=5)
    except Exception as e:
        print("APIへの接続に失敗しました:", e)
        return

    # ③ ステータスコードで成功/失敗をチェック
    if resp.status_code != 200:
        print("辞書APIからエラーが返されました。status:", resp.status_code)
        return

    try:
        data = resp.json()  # ④ JSON → Pythonオブジェクト（リストや辞書）に変換
    except Exception as e:
        print("JSONの解析に失敗しました:", e)
        return

    # ⑤ 例文を取り出す（使うAPIの仕様に依存する部分）
    example = None
    try:
        # 例: data[0]["meanings"][0]["definitions"][0]["example"] に入っている想定
        meanings = data[0].get("meanings", [])
        for m in meanings:
            defs = m.get("definitions", [])
            for d in defs:
                ex = d.get("example")
                if ex:
                    example = ex
                    break
            if example:
                break
    except Exception as e:
        print("データ構造の解析中にエラー:", e)

    if not example:
        print("この単語の例文が見つかりませんでした。")
        return

    # ⑥ 例文テキストエリアに表示
    example_text.delete("1.0", tk.END)
    example_text.insert("1.0", example)
    print("例文をセットしました。")


def save_words_to_file():
    """words全体をJSONファイルに保存する"""
    with open(WORDS_FILE, "w", encoding="utf-8") as f:
        # ensure_ascii = False ->日本語もそのまま書き込む
        json.dump(words, f, ensure_ascii=False, indent=2)


def load_words_from_file():
    """起動時にJSONファイルから単語リストを読み込む"""
    global words
    if not os.path.exists(WORDS_FILE):
        return  # まだファイルがなければ何もしない
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        words = json.load(
            f
        )  # .load(f)ファイルオブジェクトから読む。.loads(s)文字列から読む
    # 読み込んだ内容を画面に反映
    refresh_word_list()


def update_word():
    """選択中の単語を、入力欄の内容で上書きする"""
    selection = word_listbox.curselection()
    if not selection:
        print("更新する単語を左の一覧から選んでください")
        return
    index = selection[0]  # 選択された行番号(0,1,2,...)
    eng = en_entry.get().strip()
    jp = ja_entry.get().strip()
    ex = example_text.get("1.0", tk.END).strip()

    if not eng or not jp:
        print("英単語と日本語の両方を入力してください")
        return
    # words[index]を書き換える（上書き）
    words[index] = {  # wordsの中のindex番号の要素を、この新しい辞書に差し替える
        "english": eng,
        "japanese": jp,
        "example": ex,
    }
    # ファイルにも保存
    save_words_to_file()
    # 左の一覧を描きなおす。wordsをもとにListboxを全部作り直す
    refresh_word_list()


def delete_word():
    """選択中の単語を削除する"""
    selection = word_listbox.curselection()
    if not selection:
        print("削除する単語を左の一覧から選んでください")
        return
    index = selection[0]
    # wordsから単語を取り除く
    words.pop(index)  # wordsのindex番目を取り出して削除
    # ファイルにも保存
    save_words_to_file()
    # 一覧も描きなおす
    refresh_word_list()
    # 右側の入力欄もクリアしておく
    en_entry.delete(0, tk.END)
    ja_entry.delete(0, tk.END)
    example_text.delete("1.0", tk.END)


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

add_button = tk.Button(button_frame, text="追加", width=10, command=add_word)
save_button = tk.Button(button_frame, text="保存", width=10)
delete_button = tk.Button(button_frame, text="削除", width=10)
quiz_button = tk.Button(button_frame, text="クイズ", width=10)

save_button.config(command=update_word)
delete_button.config(command=delete_word)

api_button = tk.Button(
    button_frame,
    text="辞書から例文",
    width=12,
    command=fetch_example_from_api,
)

add_button.pack(side="left", padx=5)
save_button.pack(side="left", padx=5)
delete_button.pack(side="left", padx=5)
quiz_button.pack(side="right", padx=5)
api_button.pack(side="right", padx=5)
load_words_from_file()  # 起動時にファイルから読み込む
root.mainloop()
