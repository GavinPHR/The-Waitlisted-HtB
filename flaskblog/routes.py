import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Know, Learn, ChatThread, ChatThreadContent, Matches
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('root.html')

@app.route("/home")
@login_required
def home():
    matches = [ {
        'language': match.language,
        'user': User.query.get(match.user2_id)
    } for match in Matches.query.filter_by(user1_id=current_user.id).all()]

    user = {
        'language_learn': [ll.language for ll in current_user.language_learn]
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

allowed_languages = ["Afrikaans","Akan","Albanian","Amharic","Arabic","Armenian","ASL","Assamese","Assyrian","Azerbaijani","Bahdini","Bambara","Bashkir","Basque","Belarusian","Bengali","Bosnian","Bravanese","Bulgarian","Burmese","Cambodian","Cantonese","Catalan","Cebuano","Chaldean","Chamorro","Chaozhou","Chavacano","Chin","Chuukese","Cree","Croatian","Czech","Dakota","Danish","Dari","Dinka","Dioula","Dutch","Dzongkha","English","Estonian","Ewe","Fante","Faroese","Farsi","Fijian  Hindi","Finnish","Flemish","French","French Canadian","Frisian","Fujianese","Fukienese","Fula","Fulani","Fuzhou","Ga","Gaelic","Galician","Ganda","Georgian","German","Gorani","Greek","Gujarati","Haitian Creole","Hakka","Hassaniyya","Hausa","Hebrew","Hiligaynon","Hindi","Hmong","Hungarian","Ibanag","Icelandic","Igbo","Ilocano","Ilonggo","Indian","Indonesian","Inuktitut","Irish","Italian","Jakartanese","Japanese","Javanese","Kanjobal","Kannada","Karen","Kashmiri","Kazakh","Khalkha","Khmer","Kikuyu","Kinyarwanda","Kirundi","Korean","Kosovan","Kotokoli","Krio","Kurdish","Kurmanji","Kyrgyz","Lakota","Laotian","Latin","Latvian","Lingala","Lithuanian","Luganda","Luo","Lusoga","Luxembourgeois","Maay","Macedonian","Malagasy","Malay","Malayalam","Maldivian","Maltese","Mandarin","Mandingo","Mandinka","Maori","Marathi","Marshallese","Mien","Mirpuri","Mixteco","Moldovan","Mongolian","Navajo","Neapolitan","Nepali","Norwegian","Nuer","Nyanja","Ojibaway","Oriya","Oromo","Ossetian","Pahari","Pampangan","Pashto","Patois","Pidgin English","Polish","Portuguese","Pothwari","Pulaar","Punjabi","Putian","Quanxi","Quechua","Romani","Romanian","Romansch","Rundi","Russian","Samoan","Sango","Sanskrit","Serbian","Shanghainese","Shona","Sichuan","Sicilian","Sindhi","Sinhala","Sinhalese","Siswati/Swazi","Slovak","Slovene","Slovenian","Somali","Soninke","Sorani","Sotho","Spanish","Sundanese","Susu","Swahili","Swedish","Sylhetti","Tagalog","Taiwanese","Tajik","Tamil","Telugu","Thai","Tibetan","Tigrinya","Tongan","Tshiluba","Tsonga","Tswana","Turkish","Turkmen","Uighur","Ukrainian","Urdu","Uzbek","Venda","Vietnamese","Visayan","Welsh","Wolof","Xhosa","Yao","Yiddish","Yoruba","Yupik","Zulu"]

@app.route("/profile/<user_id>", methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if request.method == "POST":
        try:
            language = request.form["language"]
            print("b")
            if language is not None:
                languages = Know.query.filter_by(user_id=user_id).all()
                check = 0
                for language_know in languages:
                    if language_know.language == language:
                        check = 1
                if check == 0 and language in allowed_languages:
                    print('a')
                    know = Know(language=language, user_id=user_id)
                    db.session.add(know)
                    db.session.commit()
                else:
                    flash('The language has already been chosen', 'danger')
        except:
            pass
        try:
            language_learn = request.form["language_learn"]
            print("c")
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
                if check ==0 and (language_learn in allowed_languages):
                    learn = Learn(language=language_learn, user_id=user_id)
                    db.session.add(learn)
                    db.session.commit()
                elif check == 1:
                    flash('The language has already been chosen', 'danger')
                elif check == 2:
                    flash('You know that language', 'danger')
        except:
            pass
        return redirect(url_for('profile', user_id=user_id))
    languages = Know.query.filter_by(user_id=user_id).all()
    languages_learn = Learn.query.filter_by(user_id=user_id).all()
    user = User.query

    return render_template('profile.html', title='Profile', languages=languages, languages_learn=languages_learn, user=user, user_id=user_id)


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

    return redirect(url_for('profile', user_id=user_id))


@app.route("/start_match/<user_id>", methods=['GET', 'POST'])
@login_required
def start_match(user_id):
    user = User.query.get_or_404(user_id)
    user.match = '1'
    db.session.commit()
    return redirect(url_for('profile', user_id=user_id))

@app.route("/stop_match/<user_id>", methods=['GET', 'POST'])
@login_required
def stop_match(user_id):
    user = User.query.get_or_404(user_id)
    user.match = '0'
    db.session.commit()
    return redirect(url_for('profile', user_id=user_id))
