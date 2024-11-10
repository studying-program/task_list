from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

# タグとポストの中間テーブル
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)
    # タグとの多対多のリレーションシップを追加
    tags = db.relationship('Tag', secondary=post_tags, lazy='joined',
                          backref=db.backref('posts', lazy=True))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # タグによる絞り込み
        tag_name = request.args.get('tag')
        if tag_name:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                posts = tag.posts
            else:
                posts = []
        else:
            posts = Post.query.order_by(Post.due).all()
        tags = Tag.query.all()  # すべてのタグを取得
        return render_template('index.html', posts=posts, tags=tags)
    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')
        tag_names = request.form.getlist('tags')  # 複数のタグを取得

        due_datetime = datetime.strptime(due, '%Y-%m-%d')

        new_post = Post(
            title=title,
            detail=detail,
            due=due_datetime
        )

        # タグの処理
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_post.tags.append(tag)

        db.session.add(new_post)
        db.session.commit()
        return redirect('/')
    

@app.route('/archive/<int:post_id>', methods=['POST'])
def archive_task(post_id):
    post = Post.query.get(post_id)
    if post:
        # "アーカイブ"タグを取得
        archive_tag = Tag.query.filter_by(name="アーカイブ").first()
        if not archive_tag:
            # "アーカイブ"タグがない場合は新たに作成
            archive_tag = Tag(name="アーカイブ")
            db.session.add(archive_tag)
        
        # タスクにアーカイブタグを追加
        post.tags.append(archive_tag)
        db.session.commit()

    # タスク一覧にリダイレクト
    return redirect('/')


@app.route("/create")
def create():
    tags = Tag.query.all()
    return render_template('create.html', tags=tags)

@app.route("/detail/<int:id>")
def read(id):
    post = Post.query.get(id)
    return render_template('detail.html', post=post)

@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        tags = Tag.query.all()
        return render_template('update.html', post=post, tags=tags)
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')
        
        # タグの更新
        new_tag_names = request.form.getlist('tags')
        post.tags.clear()  # 既存のタグをクリア
        for tag_name in new_tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)

        db.session.commit()
        return redirect('/')

@app.route("/delete/<int:id>")
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

# タグの管理用エンドポイント
@app.route("/tags", methods=['GET', 'POST'])
def manage_tags():
    if request.method == 'POST':
        tag_name = request.form.get('tag_name')
        if tag_name:
            tag = Tag(name=tag_name)
            db.session.add(tag)
            db.session.commit()
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)

@app.route("/tag/delete/<int:id>")
def delete_tag(id):
    tag = Tag.query.get(id)
    if tag:
        db.session.delete(tag)
        db.session.commit()
    return redirect('/tags')

if __name__ == '__main__':
    app.run(debug=True)