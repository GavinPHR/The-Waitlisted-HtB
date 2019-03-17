import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Know, Learn, ChatThread, ChatThreadContent
from flask_login import login_user, current_user, logout_user, login_required

import pytz

@app.route("/")
@app.route("/home")
def home():
    matches = [
    {
        'language': 'English',
        'name': 'Sophie'
    },
    {
        'language': 'Spanish',
        'name': 'Aria'
    }
    ]

    user = {
        'language_learn': "English",
        'language_know': ['Norwegian', 'Esperanto']
    }

    #users.getUsers()
    if len(matches) == 0:
        matches = None
    return render_template('home.html', user=user, matches=matches)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/chatroom/<target_id>", methods=['GET', 'POST']) # TODO : target unique username
@login_required
def chatroom(target_id):

    user_id = current_user.id;

    threads = ChatThread.query.filter_by(user1_id=user_id, user2_id=target_id).all()
    if (len(threads) == 0):
        threads = ChatThread.query.filter_by(user1_id=target_id, user2_id=user_id).all()
    if (len(threads) == 0):
        thread = ChatThread(user1_id=user_id, user2_id=target_id)
        db.session.add(thread)
        db.session.commit()
    if (len(threads) == 1):
        thread = threads[0];

    if request.method == "POST":
        try:
            message = request.form["message"]
            print(message)
            db.session.add(ChatThreadContent(sender_id=int(user_id), thread_id=thread.id, content=message))
            db.session.commit();
        except:
            pass

        return redirect(url_for('chatroom', target_id=target_id))

    messages = []

    '''[
        {
            "me":   False,
            "time": "30 mins ago",
            "form": "Jack Sparrow",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur bibendum ornare dolor, quis ullamcorper ligula sodales."
        },
        {
            "me":   True,
            "time": "12 mins ago",
            "form": "Bhaumik Patel",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur bibendum ornare dolor, quis ullamcorper ligula sodales."
        },
        {
            "me":   True,
            "time": "12 mins ago",
            "form": "Bhaumik Patel",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur bibendum ornare dolor, quis ullamcorper ligula sodales."
        },
        {
            "me":   True,
            "time": "12 mins ago",
            "form": "Bhaumik Patel",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur bibendum ornare dolor, quis ullamcorper ligula sodales."
        },
        {
            "me":   False,
            "time": "30 mins ago",
            "form": "Jack Sparrow",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur bibendum ornare dolor, quis ullamcorper ligula sodales."
        },
    ]'''

    messages = list(ChatThreadContent.query.filter_by(thread_id=thread.id))

    for message in messages:
        message.me = message.sender_id == int(user_id);
        message.time = message.post_time[:-7]#.strftime("%Y-%m-%d %H:%M")


    return render_template('chat.html', title='Chat', messages=messages, nosidebar=True)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/language/<user_id>", methods=['GET', 'POST'])
@login_required
def language(user_id):
    if request.method == "POST":
        try:
            language = request.form["language"]
            if language is not None:
                languages = Know.query.filter_by(user_id=user_id).all()
                check = 0
                for language_know in languages:
                    if language_know.language == language:
                        check = 1
                if check == 0:
                    know = Know(language=language, user_id=user_id)
                    db.session.add(know)
                    db.session.commit()
                else:
                    flash('The language has already been chosen', 'danger')
        except:
            pass
        try:
            language_learn = request.form["language_learn"]
            if language_learn is not None:
                languages = Learn.query.filter_by(user_id=user_id).all()
                check=0
                for language in languages:
                    if language.language == language_learn:
                        check=1
                languages = Know.query.filter_by(user_id=user_id).all()
                for language in languages:
                    if language.language == language_learn:
                        check=2
                if check ==0:
                    learn = Learn(language=language_learn, user_id=user_id)
                    db.session.add(learn)
                    db.session.commit()
                elif check == 1:
                    flash('The language has already been chosen', 'danger')
                elif check == 2:
                    flash('You know that language', 'danger')
        except:
            pass
        return redirect(url_for('language', user_id=user_id))
    languages = Know.query.filter_by(user_id=user_id).all()
    languages_learn = Learn.query.filter_by(user_id=user_id).all()

    return render_template('language.html', title='language', languages=languages, languages_learn=languages_learn
                          )


@app.route("/delete_language/<mode>/<user_id>/<language_id>", methods=['GET', 'POST'])
@login_required
def delete_language(language_id,mode,user_id):
    if mode == "learn":
        learn = Learn.query.get_or_404(language_id)
        db.session.delete(learn)
        db.session.commit()
        flash('Delete successfully', 'success')
    if mode == "know":
        know = Know.query.get_or_404(language_id)
        db.session.delete(know)
        db.session.commit()
        flash('Delete successfully', 'success')
    return redirect(url_for('language', user_id=user_id))
