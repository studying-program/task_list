# app.py
from flask import Flask, render_template, request

# Flaskアプリケーションの作成
app = Flask(__name__)

# メモを保存するためのリスト（本来はデータベースを使うべきですが、例として簡易的に）
memos = []

# ルートURL ("/") にアクセスした時の処理
@app.route('/')
def index():
    return render_template('index.html', memos=memos)

# メモを追加する処理（POSTメソッドの場合のみ）
@app.route('/add_memo', methods=['POST'])
def add_memo():
    memo_text = request.form.get('memo')
    if memo_text:
        memos.append(memo_text)
    return render_template('index.html', memos=memos)

# アプリケーションの起動
if __name__ == '__main__':
    app.run(debug=True)