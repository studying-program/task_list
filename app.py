from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///todo.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(30),nullable = False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime,nullable = False)
                       
@app.route("/",methods=['GET','POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html',posts=posts)
    else:
        # フォームからデータを取得
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')
        
        # 日付文字列をdatetimeオブジェクトに変換
        due_datetime = datetime.strptime(due, '%Y-%m-%d')

        # 実際のフォームの値を使用して新しい投稿を作成
        new_post = Post(
            title=title,     # 'title' ではなく変数 title を使用
            detail=detail,   # 'detail' ではなく変数 detail を使用
            due=due_datetime # 'due' ではなく変換済みの due_datetime を使用
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect('/')
    
@app.route("/create")
def create():
    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)