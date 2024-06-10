from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    title = db.Column(db.String(200))
    text = db.Column(db.String(500))
    priority = db.Column(db.String(50))
    status = db.Column(db.String(50))
    complete = db.Column(db.Boolean, default=False)


@app.route('/')
def index():
    incomplete = Todo.query.filter_by(complete=False).all()
    complete = Todo.query.filter_by(complete=True).all()
    return render_template('index.html', incomplete=incomplete, complete=complete)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        text = request.form['text']
        priority = request.form['priority']
        status = request.form['status']

        if not category or not title or not text or not priority or not status:
            # flash('Все поля обязательны для заполнения!')
            return redirect(url_for('add'))

        todo = Todo(category=category, title=title, text=text, priority=priority, status=status, complete=False)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/complete/<id>')
def complete(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    todo.complete = True
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<id>')
def delete(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        text = request.form['text']
        priority = request.form['priority']
        status = request.form['status']

        if not category or not title or not text or not priority or not status:
            flash('Все поля обязательны для заполнения!')
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
def task_detail(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    return render_template('detail.html', todo=todo)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
