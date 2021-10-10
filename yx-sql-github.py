#!/usr/bin/python
# -*- coding: utf-8 -*-

## yoox бот для телеги. поиск низшей цены
# https://www.codifylab.com/kak_sozdat_telegram_bota

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
##  Updater - это объект, который умеет связываться с сервером телеграма и получать от него обновления, т.е. новые сообщения от пользователей.
import random # для случайных ответов
import time # для засекания времени работы
from time import sleep # для драматических пауз

import mysql.connector as mysql # подключаемся к mysql
import pandas as pd # ворочаем таблицу
import re # коверкаем код 

import requests # для обращения по http и чтения html
from bs4 import BeautifulSoup # для парсинга






print("Бот запущен. Нажмите Ctrl+C для завершения")

def on_start(update, context):
	chat = update.effective_chat
	context.bot.send_message(chat_id=chat.id, text="Привет, я в разработке")
    
    
def on_message(update, context):
    anslist = ['Ссылка где? Сейчас же всё сметут', 'Попробуй прислать ссылку', 'Давай же. https, вот это всё. Ссылку на товар','Можешь, конечно, и без ссылки, целее деньги в кошельке','А жена знает, что ты такой шопоголик? ссылку!','Мы все тут просто посмотреть цену. Но ссылка нужна','Бранчини сами себя не купят. Ссыль!','Одна девочка прислала мне ссылку и купила новые туфли... в Кари', 'Ссылку пришлешь или ты уже в ИталБазар собрался?','Лучше секондсы с сьеры, чем ферсты с йокса, да? \n ссыль где?']
    chat = update.effective_chat
    text = update.message.text
    text = text.lower()
    sqllim = '30'
    try:
        text2 = text.split('ru')[0].split('.')[1]
        if (text.split('ru')[0].split('.')[1] == 'yoox'):
            context.bot.send_message(chat_id=chat.id, text='похоже на ссылку, да')
            sleep(1)
            try: 
                text2 = text.split('$$')[1]
                if (text2 == '30'):
                    context.bot.send_message(chat_id=chat.id, text='обнаружен VIP-аккаунт, глубина аналитики - 30 дней')
                    sqllim = '30'
            except Exception as e:
                pass
            start_time = time.time()
            context.bot.send_message(chat_id=chat.id, text='...')
            sleep(1)
            context.bot.send_message(chat_id=chat.id, text='Подключаю искусственный интеллект')
            sleep(1)
            context.bot.send_message(chat_id=chat.id, text= get_price(text, sqllim))
            script_run_time = time.time() - start_time
            context.bot.send_message(chat_id=chat.id, text='время выполнения ' + str(script_run_time))
        else:
            context.bot.send_message(chat_id=chat.id, text=anslist[random.randrange(len(anslist))])
    except:
        context.bot.send_message(chat_id=chat.id, text=anslist[random.randrange(len(anslist))])


def get_price (text, sqllim):
    mystring = text.split('ru/')[1].split('/')[0]
    mystring = (str(re.findall(r'\d+', mystring))).split('\'')[1]
    HOST = "" # or "domain.com"
    DATABASE = ""
    USER = ""
    PASSWORD = ""
    db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
#    sqllim = '30'
    query = "SELECT \
            yooxru.data.DataPrice, \
            yooxru.product.ProductColor, \
            yooxru.date.Date \
            FROM \
            (yooxru.product \
            LEFT JOIN yooxru.data ON ((yooxru.product.idProduct = yooxru.data.Product_idProduct)) \
            LEFT JOIN yooxru.date ON ((yooxru.date.idDate = yooxru.data.Date_idDate))) \
            WHERE ProductCode like \"" + mystring + "%\" \
            ORDER BY Date DESC \
            LIMIT " + sqllim  
            
    result_dataFrame = pd.read_sql(query,db_connection)
    db_connection.close()
    
    if result_dataFrame.empty == True:
        return  'Ошибка. За последние ' + sqllim + ' дней этого товара не было'
    
    result_dataFrame['DataPrice']= result_dataFrame['DataPrice'].replace(' руб','', regex=True)
    result_dataFrame['DataPrice']= result_dataFrame['DataPrice'].replace(' ','', regex=True)    
    result_dataFrame['DataPrice'] = result_dataFrame['DataPrice'].astype(int)

    currprice = get_current_price(text)
    rowmin = result_dataFrame['DataPrice'].idxmin()
    lowprice = int((result_dataFrame['DataPrice'][rowmin]))
    lowdate = (result_dataFrame['Date'][rowmin])
    lowcolor = (result_dataFrame['ProductColor'][rowmin])   
    if (lowprice < currprice):
        mystring = 'Текущая цена '+ str(currprice) + 'рублей - не самая низкая за последние ' + sqllim + ' дней \n'  + str(lowdate) + ' числа цена была ' + str(lowprice) + ' рублей за этот товар в цвете ' + str(lowcolor)
    else:
        mystring = 'За последние ' + sqllim + ' дней это самая низкая цена'
    
    
    return mystring

def get_current_price(text):

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 YaBrowser/21.3.3.230 Yowser/2.5 Safari/537.36',
    'From': 'youri2121@yandex.ru' 
    }
    
    r = requests.get(text, headers = headers)
    soup = BeautifulSoup (r.text, 'lxml')
    price = (int(str(soup).split('"руб","price":')[1].split(',"item')[0]))
    return price
    

token=""



updater = Updater(token, use_context=True)
# Мы создали новый Updater и сохранили его в переменную с именем updater. (Переменные умеют еще и объекты разные хранить.) При создании мы указали токен нашего бота, чтобы он используя этот токен мог получать сообщения именно для нашего бота.



dispatcher = updater.dispatcher
#dispatcher.add_handler(ConversationHandler
dispatcher.add_handler(CommandHandler("start", on_start, Filters.user(username="")))

dispatcher.add_handler(MessageHandler(Filters.user(username="") & Filters.text, on_message))


# У нас в программе есть объект Updater. 
#У него есть помощник, который называется dispatcher(диспетчер или распределитель). 
#Этот dispatcher распределяет сообщения, которые приходят от пользователей по разным обработчикам.
# Поэтому он должен знать о всех обработчиках.
#Мы скажем этому диспетчеру, что у нас есть новый обработчик для команды start:
    
updater.start_polling()
updater.idle()

# Первая строчка запускает, а вторая строчка ждет пока вы нажмете Ctrl+C, а когда нажмете завершает работу бота.