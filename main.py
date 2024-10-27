# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# メール設定（実際の値に置き換えてください）
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "your-email@gmail.com"
MAIL_PASSWORD = "your-app-specific-password"  # Gmailの場合、アプリパスワードを使用

# パスワードリセットトークンを保存する辞書（実際はデータベースを使用）
reset_tokens = {}

# ユーザーデータ（実際はデータベースを使用）
users = {
    'test@example.com': {
        'password': 'test123',
        'name': 'テストユーザー'
    }
}

def send_reset_email(email, token):
    """パスワードリセットメールを送信する関数"""
    msg = MIMEMultipart()
    msg['From'] = MAIL_USERNAME
    msg['To'] = email
    msg['Subject'] = "パスワードリセットのご案内"
    
    reset_link = f"http://localhost:5000/reset_password/{token}"
    body = f"""
    パスワードリセットのリクエストを受け付けました。
    
    以下のリンクからパスワードを再設定してください：
    {reset_link}
    
    このリンクは30分間有効です。
    
    ※このメールに心当たりがない場合は、無視してください。
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if email in users:
            # トークンを生成
            token = secrets.token_urlsafe(32)
            # トークンを保存（30分間有効）
            reset_tokens[token] = {
                'email': email,
                'expiry': datetime.now() + timedelta(minutes=30)
            }
            
            # リセットメールを送信
            if send_reset_email(email, token):
                flash('パスワードリセットのメールを送信しました。メールをご確認ください。')
                return redirect(url_for('index'))
            else:
                flash('メールの送信に失敗しました。後でもう一度お試しください。')
        else:
            # セキュリティのため、メールアドレスが存在しない場合も同じメッセージを表示
            flash('パスワードリセットのメールを送信しました。メールをご確認ください。')
        
        return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # トークンの有効性をチェック
    if token not in reset_tokens or \
       datetime.now() > reset_tokens[token]['expiry']:
        flash('無効または期限切れのリンクです。')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('パスワードが一致しません。')
            return render_template('reset_password.html', token=token)
        
        # パスワードを更新
        email = reset_tokens[token]['email']
        users[email]['password'] = new_password
        
        # 使用済みトークンを削除
        del reset_tokens[token]
        
        flash('パスワードが正常に更新されました。新しいパスワードでログインしてください。')
        return redirect(url_for('index'))
    
    return render_template('reset_password.html', token=token)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email in users and users[email]['password'] == password:
        session['user_id'] = email
        return redirect(url_for('dashboard'))
    else:
        flash('メールアドレスまたはパスワードが正しくありません')
        return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if email in users:
            flash('このメールアドレスは既に登録されています')
            return redirect(url_for('register'))
        
        users[email] = {
            'password': password,
            'name': name
        }
        flash('登録が完了しました。ログインしてください。')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = users[session['user_id']]
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)