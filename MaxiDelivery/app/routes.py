from app import app
from flask import render_template, flash, redirect, url_for, session
from flask import request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from app.forms import LoginForm, RegistrationForm, AddToCartForm, OfferForm, AcceptOffer, EndOffer
from app.models import Courier, Client, Restaurant, Menu, Zone, Cart, Position, Offer


# главная страница
@app.route("/")
@app.route("/index")
def index():
    restaurants = Restaurant.get_list()
    return render_template('index.html', title = 'Главная страница', restaurants = restaurants)

@app.route('/index/<restaurant>', methods = ['GET', 'POST'])
def restaurant_menu(restaurant):
    district = Restaurant.get_zone_by_name(restaurant)
    adres = Restaurant.get_adres_by_name(restaurant)
    menu_lst = Menu.get_menu_by_restaurant(restaurant)
    return render_template('menu.html', title = 'Меню ресторана', menu_lst=menu_lst, restaurant = restaurant, adres=adres, district=district)

@app.route('/index/<restaurant>/<dish>', methods = ['GET', 'POST'])
def about_dish(restaurant, dish):
    ingridients = Menu.get_ingridients_by_dish(dish)
    form = AddToCartForm()
    if form.validate_on_submit():
        cart_id = Cart.get_by_username(current_user.username)
        dish_id = Menu.get_id_by_name(dish)
        count = form.count.data
        Position.add(cart_id, dish_id, count)
        return redirect(url_for('restaurant_menu', restaurant=restaurant))
        
    return render_template('about_dish.html', title = 'О блюде', ingridients=ingridients, form=form, dish=dish)

# вход пользователя
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/index")
    form = LoginForm()
    if form.validate_on_submit():
        if form.role.data == True:
            # задаем переменной роль в сессии значение курьер
            # это нужно для определения, из какой таблицы получать пользователя в методе loas user
            session['role'] = 'courier'
            user = Courier.get_by_username(form.username.data)
            
        else:
            # если не поставлена галочка, значит роль пользователя - клиент
            session['role'] = 'client'
            user = Client.get_by_username(form.username.data)
        
        # если не нашелся пользователь с таким логином или пароль пользователя неверный
        if user is None or not user.check_password(form.password.data):
            # выдать ошибку на экран
            flash('Введен неправильный логин или пароль')
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = "/index"
        return redirect(next_page)
    return render_template('login.html', title = 'Личный кабинет пациента', form=form)

# регистрация клиента
@app.route("/registration", methods = ['GET', 'POST'])
def registration():
    form = RegistrationForm()
    zones = Zone.get_list()
    if zones is None:
        zones = []
    form.district.choices = zones
    if form.validate_on_submit():
        user = Client(username = form.username.data,
                name = f'{form.lastname.data} {form.firstname.data} {form.patronymic.data}',
                adress = form.adress.data)
        user.set_password(form.password1.data)
        user.adduser()
        flash('Вы создали нового пользователя')
        user_id = Client.get_id_by_username(form.username.data)
        Client.set_district(user_id, user.username, form.district.data)
        Cart.add(user_id, user.username)
        return redirect(url_for('login'))
    return render_template('registration.html', title = 'Регистрация в системе', form=form)


# мой профиль пациента
@app.route("/client/<username>", methods = ['GET', 'POST'])
@login_required
def client(username):
    user = Client.get_by_username(username)
    district = Client.get_district_by_client_id(user.id)
    cart = Position.get_cart_by_user(username)
    cost_count = Position.get_summ_by_user(username)
    cart_summ = 0
    for c in cost_count:
        cart_summ += int(c[0])*int(c[1])
    form = OfferForm()
    if form.validate_on_submit():
        offer_id = Offer.add(user.id, username, datetime.date(datetime.now()))
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        print(offer_id)
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        Offer.set_offer(offer_id, username)
        #создать новую корзину
        Cart.add(current_user.id, username)
        return redirect(url_for('index'))
    return render_template('client.html', title = 'Мой профиль', user=user, district=district, cart=cart, cart_summ=cart_summ, form=form)

@app.route("/offers/<username>", methods = ['GET', 'POST'])
@login_required
def offers(username):
    offers = Offer.get_by_user(username)
    return render_template('offers.html', title = 'Мои заказы', offers=offers, username=username)


@app.route("/delevered_offers/<username>", methods = ['GET', 'POST'])
@login_required
def delivered_offers(username):
    offers = Offer.get_delivered_by_username(username)
    return render_template('delivered_offers.html', title = 'История заказов', offers=offers, username=username)

# мой профиль пациента
@app.route("/courier/<username>", methods = ['GET'])
@login_required
def courier(username):
    user = Courier.get_by_username(username)
    zone = Courier.get_district_by_courier_id(user.id)
    notdelivery_offers = Offer.get_notdelivery()
    return render_template('courier.html', title = 'Личный кабинет курьера', user=user, zone=zone, notdelivery_offers = notdelivery_offers)

@app.route("/accept_offer/<offer_id>", methods = ['GET', 'POST'])
@login_required
def accept_offer(offer_id):
    form = AcceptOffer()
    if form.validate_on_submit():
        Offer.add_for_courier_by_id(offer_id, current_user.id, current_user.username)
        return redirect(url_for('courier', username = current_user.username))
    return render_template('accept_offer.html', title = 'Подтверждение доставки', form=form, offer_id = offer_id)

@app.route("/my_delivers/<username>", methods = ['GET'])
@login_required
def my_delivers(username):
    offers = Offer.get_offers_delivers_by_this_courier(username)
    return render_template('my_delivers.html', title = 'Мои доставки', username=username, offers = offers)

@app.route("/endoffer/<offer_id>", methods = ['GET', 'POST'])
@login_required
def endoffer(offer_id):
    form = EndOffer()
    if form.validate_on_submit():
        Offer.set_delivered_status_by_offer_id(offer_id)
        return redirect(url_for('my_delivers', username=current_user.username))
    return render_template('endoffer.html', title = 'Завершить заказ', form=form, offer_id=offer_id)

@app.route("/offers_history/<username>", methods = ['GET'])
@login_required
def offers_history(username):
    delivers = Offer.get_delivered_offers_by_courier(username)
    return render_template('offers_history.html', title='История доставок', delivers=delivers)

# выйти из аккаунта
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/index")