from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'f3cfe9ed8fae309f02079dbf'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
login_manager.login_view = 'login'
login_manager.login_message = ''


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    title = db.Column(db.String(200))
    text = db.Column(db.String(500))
    priority = db.Column(db.String(50))
    status = db.Column(db.String(50))
    complete = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('todos', lazy=True))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Имя пользователя уже существует! Пожалуйста введите другое имя пользователя.')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)

        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Пожалуйста войдите.')
        return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Не удалосб войти. Пожалуйста проверьте имя пользователя и пароль.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    category = request.args.get('category')
    if category:
        incomplete = Todo.query.filter_by(complete=False, category=category, user_id=current_user.id).all()
        complete = Todo.query.filter_by(complete=True, category=category, user_id=current_user.id).all()
    else:
        incomplete = Todo.query.filter_by(complete=False, user_id=current_user.id).all()
        complete = Todo.query.filter_by(complete=True, user_id=current_user.id).all()
    categories = Todo.query.with_entities(Todo.category).distinct()
    return render_template('index.html', incomplete=incomplete, complete=complete, categories=categories, selected_category=category, username=current_user.username)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        text = request.form['text']
        priority = request.form['priority']
        status = request.form['status']

        if not category or not title or not text or not priority or not status:
            flash('All fields are required!')
            return redirect(url_for('add'))

        todo = Todo(category=category, title=title, text=text, priority=priority, status=status, complete=False, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/complete/<id>')
@login_required
def complete(id):
    todo = Todo.query.filter_by(id=int(id), user_id=current_user.id).first()
    todo.complete = True
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<id>')
@login_required
def delete(id):
    todo = Todo.query.filter_by(id=int(id), user_id=current_user.id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    todo = Todo.query.filter_by(id=int(id), user_id=current_user.id).first()
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        text = request.form['text']
        priority = request.form['priority']
        status = request.form['status']

        if not category or not title or not text or not priority or not status:
            flash('All fields are required!')
            return redirect(url_for('edit', id=id))

        todo.category = category
        todo.title = title
        todo.text = text
        todo.priority = priority
        todo.status = status
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', todo=todo)


@app.route('/task/<id>')
@login_required
def task_detail(id):
    todo = Todo.query.filter_by(id=int(id), user_id=current_user.id).first()
    return render_template('detail.html', todo=todo)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
