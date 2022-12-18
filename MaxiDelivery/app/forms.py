from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Client

# авторизация
class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    role = BooleanField('Войти как курьер')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')

# регистрация клиента
class RegistrationForm(FlaskForm):
    lastname = StringField('Фамилия', validators=[DataRequired()])
    firstname = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    adress = StringField('Адрес для доставок', validators=[DataRequired()])
    username = StringField('Номер телефона', validators=[DataRequired()])
    password1 = PasswordField('Задайте пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])
    district = SelectField('Укажите Ваш район', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    '''def validate_username(self, username):
        user = Client.get_by_username(username.data)
        if user is not None:
            raise ValidationError('Пожалуйста, введите номер телефона, принадлежащий Вам!')
        return'''

class AddToCartForm(FlaskForm):
    count = IntegerField('Количество порций')
    submit = SubmitField('Добавить в корзину')

    def validate_count(self, count):
        if count.data < 1:
            raise ValidationError('Введите количество >= 1!')
        return
class OfferForm(FlaskForm):
    submit = SubmitField('Сделать заказ')

class AcceptOffer(FlaskForm):
    submit = SubmitField('Взять заказ на доставку')

class EndOffer(FlaskForm):
    submit = SubmitField('Завершить заказ')