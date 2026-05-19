from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from flask_login import current_user

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


app = Flask(__name__)

app.config['SECRET_KEY'] = 'mypassword'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskflow.db'

db = SQLAlchemy(app)


login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'


# USER TABLE
class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(200))


# TASK TABLE
class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    description = db.Column(db.String(500))

    status = db.Column(db.String(50), default='Pending')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# LOAD USER
@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# HOME PAGE
@app.route('/')
def home():

    return render_template('index.html')


# REGISTER PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        email = request.form['email']

        password = generate_password_hash(request.form['password'])

        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user:

            if check_password_hash(user.password, password):

                login_user(user)

                return redirect(url_for('dashboard'))

    return render_template('login.html')


# DASHBOARD PAGE
@app.route('/dashboard')
@login_required
def dashboard():

    tasks = Task.query.filter_by(user_id=current_user.id).all()

    return render_template('dashboard.html', tasks=tasks)


# ADD TASK
@app.route('/add_task', methods=['POST'])
@login_required
def add_task():

    title = request.form['title']

    description = request.form['description']

    new_task = Task(
        title=title,
        description=description,
        user_id=current_user.id
    )

    db.session.add(new_task)

    db.session.commit()

    return redirect(url_for('dashboard'))


# DELETE TASK
@app.route('/delete/<int:id>')
@login_required
def delete_task(id):

    task = Task.query.get(id)

    db.session.delete(task)

    db.session.commit()

    return redirect(url_for('dashboard'))


# EDIT TASK
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):

    task = Task.query.get(id)

    if request.method == 'POST':

        task.title = request.form['title']

        task.description = request.form['description']

        task.status = request.form['status']

        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('edit_task.html', task=task)


# LOGOUT
@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('home'))


# API
@app.route('/api/tasks')
@login_required
def api_tasks():

    tasks = Task.query.filter_by(user_id=current_user.id).all()

    all_tasks = []

    for task in tasks:

        all_tasks.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status
        })

    return jsonify(all_tasks)


# RUN APP
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)