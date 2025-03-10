from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Post, Message
from forms import LoginForm, RegisterForm, PostForm, MessageForm
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('home.html', posts=posts)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Profile routes
@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('auth/profile.html', user=user, posts=posts)

@app.route('/profile')
@login_required
def current_profile():
    return redirect(url_for('profile', user_id=current_user.id))

# Post routes
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('posts/create.html', form=form)

@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('posts/view.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

# Message routes
@app.route('/messages')
@login_required
def messages():
    # Get all conversations (most recent first)
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(receiver_id=current_user.id).all()
    
    # Combine and sort conversations by most recent
    all_messages = sent_messages + received_messages
    all_messages.sort(key=lambda x: x.created_at, reverse=True)
    
    # Get unique conversation partners
    conversation_partners = set()
    conversations = []
    
    for message in all_messages:
        partner_id = message.receiver_id if message.sender_id == current_user.id else message.sender_id
        if partner_id not in conversation_partners:
            conversation_partners.add(partner_id)
            partner = User.query.get(partner_id)
            conversations.append({
                'user': partner,
                'last_message': message
            })
    
    return render_template('messages/inbox.html', conversations=conversations)

@app.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    user = User.query.get_or_404(user_id)
    
    # Can't message yourself
    if user.id == current_user.id:
        abort(403)
    
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            content=form.content.data,
            sender_id=current_user.id,
            receiver_id=user.id
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('conversation', user_id=user.id))
    
    # Get conversation messages
    sent_messages = Message.query.filter_by(sender_id=current_user.id, receiver_id=user.id).all()
    received_messages = Message.query.filter_by(sender_id=user.id, receiver_id=current_user.id).all()
    
    messages = sent_messages + received_messages
    messages.sort(key=lambda x: x.created_at)
    
    return render_template('messages/conversation.html', form=form, user=user, messages=messages)

@app.route('/users')
@login_required
def users():
    all_users = User.query.filter(User.id != current_user.id).all()
    return render_template('users.html', users=all_users)

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)