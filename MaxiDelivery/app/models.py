# импорт необходимых модулей
from werkzeug.security import generate_password_hash, check_password_hash

from app.routes import session

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import app
from app import login

from flask_login import UserMixin

class Database(object):



    @classmethod
    def _connect_to_db(cls) -> psycopg2:
        try:
            # Подключение к существующей базе данных
            cls._connection = psycopg2.connect(user='max',
                                        password="qwerty",
                                        host='localhost',
                                        database='md')

        #обработка ошибок при подключении
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'other error:\n{ex}')
        else:
            print("Успешное подключение к БД\n")
        return cls._connection
    
    # метод для обработки запросов на добавление-обновление-удаление данных
    @classmethod
    def execute_query(cls, query) -> bool:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('Запрос выполнен успешно!\n')
            return True
        finally:
            if cls._connection:
                cursor.close()
                cls._connection.close()
                print("Соединение с PostgreSQL закрыто\n")
        return False

    # метод обработки селект-запросов
    @classmethod
    def select_query(cls, query) -> list:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('Вот результат селекта:\n')
            print(result)
            return result
        finally:
            if cls._connection:
                cursor.close()
                cls._connection.close()
                print("Соединение с PostgreSQL закрыто\n")
        return None

    @classmethod
    def insert_returning(cls, query: str) -> object:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('the insert returning query is successfully')
            return result
        return None

class Client(UserMixin):


    def __init__(self,
                id: int = 0,
                username: str = "",
                name: str = "",
                adress: str = "",
                password_hash: str = ""):

                self.id : int = id
                self.username: str = username
                self.name : str = name
                self.adress: str = adress
                self.password_hash: str = password_hash
                self.role = "client"

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.username}'
        return string

    def get_by_id(id):
        print(f"вот такой id передается для поиска {id}")
        query = f'''SELECT * FROM CLIENT WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print(f"Клиент с таким id {result}")
        if result is None or len(result)==0:
            return None
        else:
            params = result[0]
            return Client(* params)

        # генерация хэш-пароля
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        print("Пароль для пользователя успешно сгенерирован")
        print(self.password_hash)

        #добавляем пользователя
    def adduser(self):
        query = f'''INSERT INTO CLIENT (USERNAME, FIO, ADRESS, PASSWORD_HASH) 
        VALUES ('{self.username}', '{self.name}', '{self.adress}', '{self.password_hash}');'''
        return Database.execute_query(query)

    def get_by_username(username):
        query = f'''SELECT * FROM CLIENT WHERE USERNAME = '{username}';'''
        result = Database.select_query(query)
        if result is None or len(result)==0:
            return None
        else:
            print(result)
            params = result[0]
            return Client(* params)

    # проверка хэша
    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def get_district_by_client_id(id):
        query = f'''SELECT DISTRICT FROM ZONE JOIN CLIENT_ZONE
                    ON ZONE.ID=CLIENT_ZONE.ZONE_ID
                    JOIN CLIENT ON CLIENT.ID=CLIENT_ZONE.CLIENT_ID
                    WHERE CLIENT.ID='{id}';'''
        result = Database.select_query(query)
        result = list(map(lambda x: str(x[0]) , result))
        result = result[0]
        return result

    def set_district(id, username, zone_id):
        query = f'''INSERT INTO CLIENT_ZONE(CLIENT_ID, CLIENT_USERNAME, ZONE_ID) VALUES ('{id}', '{username}', '{zone_id}');'''
        return Database.execute_query(query)

    def get_id_by_username(username):
        query = f'''SELECT ID FROM CLIENT WHERE USERNAME='{username}';'''
        result = Database.select_query(query)
        result = list(map(lambda x: str(x[0]) , result))
        result = result[0]
        return result

class Courier(UserMixin):


    def __init__(self,
                id: int = 0,
                name: str = "",
                username: str = "",
                password_hash: str = "",
                district: str = ""):

                self.id : int = id
                self.name : str = name
                self.username: str = username
                self.district: str = district
                self.password_hash: str = password_hash
                self.role = "courier"

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.username}'
        return string

    def get_by_id(id):
        print(f"вот такой id передается для поиска {id}")
        query = f'''SELECT * FROM COURIER WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print(f"Курьер с таким id {result}")
        if result is None or len(result)==0:
            return None
        else:
            params = result[0]
            return Courier(* params)
    
    def get_by_username(username):
        query = f'''SELECT * FROM COURIER WHERE PHONE_NUMBER = '{username}';'''
        result = Database.select_query(query)
        if result is None or len(result)==0:
            return None
        else:
            print(result)
            params = result[0]
            return Courier(* params)

        # проверка пароля
    def check_password(self, password: str):
        if self.password_hash == password:
            print(self.password_hash)
            print(password)
            return True
        return False
        
    def get_district_by_courier_id(id):
        query = f'''SELECT DISTRICT FROM ZONE JOIN COURIER_ZONE
                    ON ZONE.ID=COURIER_ZONE.ZONE_ID
                    JOIN COURIER ON COURIER.ID=COURIER_ZONE.COURIER_ID
                    WHERE COURIER.ID='{id}';'''
        result = Database.select_query(query)
        result = list(map(lambda x: str(x[0]) , result))
        result = result[0]
        return result
    #def set_district(self, district):
        
    #def update_district(self)

class Restaurant():

    def get_list():
        query = f'''SELECT REST_NAME FROM RESTAURANT;'''
        result = Database.select_query(query)
        result = map(lambda x: x[0] , result)
        return result

    def get_adres_by_name(restaurant):
        query = f'''SELECT ADRES FROM RESTAURANT
                    WHERE REST_NAME = '{restaurant}';'''
        result = Database.select_query(query)
        result = list(map(lambda x: str(x[0]) , result))
        result = result[0]
        return result

    def get_zone_by_name(restaurant):
        query = f'''SELECT DISTRICT FROM ZONE JOIN RESTAURANT_ZONE
        ON ZONE.ID=RESTAURANT_ZONE.ZONE_ID
        JOIN RESTAURANT ON RESTAURANT.ID=RESTAURANT_ZONE.RESTAURANT_ID
        WHERE REST_NAME='{restaurant}';'''
        result = Database.select_query(query)
        result = list(map(lambda x: str(x[0]) , result))
        result = result[0]
        return result
        
        
    def get_id_by_name(name):
        query = f'''SELECT ID FROM RESTAURANT WHERE REST_NAME='{name}';'''
        result = Database.select_query(query)
        result = list(map(lambda x: str(x[0]) , result))
        result = result[0]
        return result

class Menu():

    def get_menu_by_restaurant(restaurant):
        query = f'''SELECT DISH FROM MENU JOIN RESTAURANT_MENU
        ON RESTAURANT_MENU.DISH_ID=MENU.ID
        JOIN RESTAURANT ON RESTAURANT_MENU.RESTAURANT_ID=RESTAURANT.ID
        WHERE RESTAURANT.REST_NAME='{restaurant}';'''
        result = Database.select_query(query)
        result = map(lambda x: x[0] , result)
        return result

    def get_ingridients_by_dish(dish):
        query = f'''SELECT ING_NAME FROM INGRIDIENTS JOIN MENU_INGRIDIENTS
        ON INGRIDIENTS.ID=MENU_INGRIDIENTS.INGRIDIENT_ID
        JOIN MENU ON MENU.ID=MENU_INGRIDIENTS.DISH_ID
        WHERE DISH='{dish}';'''
        result = Database.select_query(query)
        result = map(lambda x: x[0] , result)
        return result

    def get_id_by_name(dish):
        query = f'''SELECT ID FROM MENU WHERE DISH='{dish}';'''
        result = Database.select_query(query)
        result = list(map(lambda x: str(x[0]) , result))
        result = result[0]
        return result

class Zone():
    def get_list():
        query = f'''SELECT *
                    FROM ZONE'''
        result = Database.select_query(query)
        return result


class Cart():
    def add(client_id, client_username):
        query = f'''INSERT INTO CART(CLIENT_ID, CLIENT_USERNAME) VALUES ('{client_id}', '{client_username}');'''
        return Database.execute_query(query)
    def get_by_username(username):
        query = f'''SELECT ID FROM CART WHERE CLIENT_USERNAME='{username}' 
        AND ID IN (SELECT MAX(ID) FROM CART WHERE CLIENT_USERNAME='{username}');'''
        result = Database.select_query(query)
        result = list(map(lambda x: str(x[0]) , result))
        result = result[0]
        return result

class Position():
    def add(cart_id, dish_id, count, rest_id):
        query = f'''INSERT INTO POSITION(CART_ID, DISH_ID, COUNT, RESTAURANT_ID) VALUES ('{cart_id}', '{dish_id}', '{count}', '{rest_id}');'''
        return Database.execute_query(query)

    def get_cart_by_user(username):
        query = f'''SELECT MENU.DISH, MENU.COST, POSITION.COUNT
                    FROM MENU JOIN POSITION ON POSITION.DISH_ID=MENU.ID
                    JOIN CART ON POSITION.CART_ID=CART.ID
                    JOIN CLIENT ON CART.CLIENT_USERNAME=CLIENT.USERNAME
                    WHERE POSITION.OFFER_ID IS NULL AND CLIENT.USERNAME='{username}';'''
        result = Database.select_query(query)
        print('2222222')
        print(result)
        #result = map(lambda x: (str(x[0]), str(x[1]), str(x[2])) , result)
        return result

    def get_summ_by_user(username):
        query = f'''SELECT COST, COUNT FROM POSITION JOIN CART
        ON POSITION.CART_ID=CART.ID
        JOIN MENU ON MENU.ID=POSITION.DISH_ID
        WHERE CART.CLIENT_USERNAME='{username}' AND POSITION.OFFER_ID IS NULL;'''
        result = Database.select_query(query)
        print(result)
        return result

class Offer():
    def get_courier_by_id(id):
        query = f'''SELECT COURIER.FIO FROM
                    COURIER JOIN OFFER
                    ON OFFER.COURIER_PHONE_NUMBER=COURIER.PHONE_NUMBER
                    WHERE OFFER.ID='{id}';'''
        result = Database.select_query(query)
        return result

    def get_information_by_id(id):
        query = f'''SELECT RESTAURANT.REST_NAME, to_char(OFFER.DAYDATE, 'dd-MM-YYYY'), CLIENT.ADRESS
                    FROM OFFER JOIN CLIENT ON OFFER.CLIENT_USERNAME=CLIENT.USERNAME
                    JOIN POSITION ON OFFER.ID=POSITION.OFFER_ID
                    JOIN RESTAURANT ON POSITION.RESTAURANT_ID=RESTAURANT.ID
                    WHERE OFFER.ID='{id}';'''
        result = Database.select_query(query)
        return result

    def get_positions_by_id(id):
        query = f'''SELECT MENU.DISH, POSITION.COUNT, MENU.COST
                    FROM MENU JOIN POSITION ON POSITION.DISH_ID=MENU.ID
                    WHERE POSITION.OFFER_ID='{id}';'''
        result = Database.select_query(query)
        return result

    def add(cl_id, cl_username, day_date):
        query = f'''INSERT INTO OFFER(CLIENT_ID, CLIENT_USERNAME, DAYDATE)
                VALUES ('{cl_id}', '{cl_username}', '{day_date}') RETURNING ID;'''
        result =  Database.insert_returning(query)
        return result[0]

    def set_offer(offer_id, username):
        query = f'''UPDATE POSITION
                    SET OFFER_ID='{offer_id}'
                    WHERE OFFER_ID IS NULL AND CART_ID IN (SELECT ID FROM CART JOIN POSITION ON CART.ID=POSITION.CART_ID WHERE CLIENT_USERNAME='{username}');'''
        return Database.execute_query(query)

    def get_by_user(username):
        query = f'''SELECT DISTINCT POSITION.OFFER_ID, RESTAURANT.REST_NAME
                    FROM POSITION JOIN CART ON POSITION.CART_ID=CART.ID
                    JOIN RESTAURANT ON POSITION.RESTAURANT_ID=RESTAURANT.ID
                    JOIN CLIENT ON CART.CLIENT_USERNAME=CLIENT.USERNAME
                    JOIN OFFER ON OFFER.ID=POSITION.OFFER_ID
                    WHERE POSITION.OFFER_ID IS NOT NULL AND CLIENT.USERNAME='{username}' AND DELIVERED=false;'''
        result = Database.select_query(query)
        print('2222222')
        print(result)
        #result = map(lambda x: (str(x[0]), str(x[1]), str(x[2])) , result)
        return result


    def get_delivered_by_username(username):
        query = f'''SELECT DISTINCT POSITION.OFFER_ID, RESTAURANT.REST_NAME, OFFER.DAYDATE
                    FROM POSITION JOIN CART ON POSITION.CART_ID=CART.ID
                    JOIN RESTAURANT ON POSITION.RESTAURANT_ID=RESTAURANT.ID
                    JOIN CLIENT ON CART.CLIENT_USERNAME=CLIENT.USERNAME
                    JOIN OFFER ON OFFER.ID=POSITION.OFFER_ID
                    WHERE POSITION.OFFER_ID IS NOT NULL AND CLIENT.USERNAME='{username}' AND DELIVERED=true;'''
        result = Database.select_query(query)
        print('2222222')
        print(result)
        #result = map(lambda x: (str(x[0]), str(x[1]), str(x[2])) , result)
        return result

    def get_notdelivery():
        query = f'''SELECT OFFER.ID, REST_NAME FROM OFFER JOIN POSITION
                    ON POSITION.OFFER_ID=OFFER.ID
                    JOIN RESTAURANT ON POSITION.RESTAURANT_ID=RESTAURANT.ID
                    WHERE DELIVERY=false;'''
        result = Database.select_query(query)
        return result

    def add_for_courier_by_id(offer_id, cour_id, cour_ph_n):
        query = f'''UPDATE OFFER
                    SET COURIER_ID='{cour_id}', COURIER_PHONE_NUMBER='{cour_ph_n}', DELIVERY=true
                    WHERE ID='{offer_id}';'''
        return Database.execute_query(query)

    def get_offers_delivers_by_this_courier(cour_username):
        query = f'''SELECT DISTINCT POSITION.OFFER_ID, RESTAURANT.REST_NAME
                    FROM POSITION JOIN CART ON POSITION.CART_ID=CART_ID
                    JOIN RESTAURANT ON POSITION.RESTAURANT_ID=RESTAURANT.ID
                    JOIN CLIENT ON CART.CLIENT_USERNAME=CLIENT.USERNAME
                    JOIN OFFER ON OFFER.ID=POSITION.OFFER_ID
                    WHERE OFFER.COURIER_PHONE_NUMBER='{cour_username}' AND DELIVERED=false;'''
        result = Database.select_query(query)
        return result

    def set_delivered_status_by_offer_id(id):
        query = f'''UPDATE OFFER
                    SET DELIVERED=true
                    WHERE ID='{id}';'''
        return Database.execute_query(query)

    def get_delivered_offers_by_courier(username):
        query = f'''SELECT DISTINCT POSITION.OFFER_ID, RESTAURANT.REST_NAME
                    FROM POSITION JOIN CART ON POSITION.CART_ID=CART_ID
                    JOIN RESTAURANT ON POSITION.RESTAURANT_ID=RESTAURANT.ID
                    JOIN OFFER ON OFFER.ID=POSITION.OFFER_ID
                    WHERE OFFER.COURIER_PHONE_NUMBER='{username}' AND DELIVERED=true;'''
        result = Database.select_query(query)
        return result

#метод загрузки клиента:
@login.user_loader
def load_user(id: str):
    if session['role'] == 'courier':
        user = Courier.get_by_id(int(id))
    elif session['role'] == 'client':
        user = Client.get_by_id(int(id))
    print(f'user loaded, user = {user}')
    return user