from flask import Flask, flash, render_template,request,redirect

from flask_login import LoginManager,login_user,UserMixin,logout_user

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt,bcrypt

import requests


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
app.config['SECRET_KEY'] = 'secretkey'  
db = SQLAlchemy(app)
login_manager = LoginManager() 
login_manager.init_app(app)


@app.route('/')
def main():
    # city_name = request.form.get['city']
    return render_template('register.html')

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(120), nullable=False)

    def __repr__(self):
        return self.name


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        enc_password = bcrypt.generate_password_hash(password).decode('utf-8')
        data = User(name=name,email=email,password=enc_password)
        db.session.add(data)
        db.session.commit()
        flash('user registered successfully:','Success')
        return render_template('login.html')
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password,password):
            login_user(user)
            return redirect('/result')
        else:
            flash('Email and password did not matched!!!','warning')
            return redirect('/login')
    else:
        return render_template("login.html")



@app.route('/result', methods=['GET','POST'])
def result():
    if request.method== 'POST':
        city = request.form['city'] 
        api_key = 'adbffb22e94a4d8a269a5fae4a06a117'
        data = weather(city_name=city,api_key=api_key)
        temp= data["list"][1]["main"]["temp"]
        hum=  data["list"][1]["main"]["humidity"]
        wind= data["list"][1]["wind"]["speed"]
        pressure= data["list"][1]["main"]["pressure"]
        sea = data["list"][1]["main"]["sea_level"]
        ground = data["list"][1]["main"]["grnd_level"]
        feels = data["list"][1]["main"]["feels_like"]
        visiblity = data["list"][0]['visibility']
        gust = data["list"][1]["wind"]["gust"]
        degree = data["list"][1]["wind"]["deg"]
        rain = data["list"][0]["pop"]
        return render_template('main.html',city=city,temp=temp,hum=hum,wind=wind,pressure=pressure,sea=sea,ground=ground,feels=feels,visiblity=visiblity,gust=gust,degree=degree,rain=rain)
    return render_template('main.html')


@login_manager.user_loader
def load_user(user_id):              
    return User.query.get(int(user_id))


@app.route("/logout")
def logout():
    logout_user()
    flash('User logout Suceessfully!','success')
    return redirect('/login')
 
def weather(city_name,api_key):
    url = 'https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}'.format(city_name,api_key)
    js = requests.get(url)
    return js.json()



if __name__=='__main__':
    app.run(debug=True)
