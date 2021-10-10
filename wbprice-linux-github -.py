# -*- coding: utf-8 -*-
"""
Created on Sun Sep 26 02:33:24 2021

@author: kryukoff
"""
import mysql.connector as mysql # подключаемся к mysql
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import pandas as pd #   ворочаем таблицу
from urllib.parse import quote # для перевода в %20
import json # для работы с JSON
from pandas.io.json import json_normalize # для работы с JSON внутри Pandas
import numpy as np # для быстрого счета
import subprocess #выполнение внешних шелл команд и разграбление ответов


from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

############################### Bot ############################################

print("Бот запущен. Нажмите Ctrl+C для завершения")



def get_req_db (query):
    HOST = "" # or "domain.com"
    DATABASE = ""
    USER = ""
    PASSWORD = ""
    PORT = '7731'
    db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD, port=PORT)
    #query = "SELECT ProxyType, ProxyAdress, ProxyPort FROM proxy.proxy WHERE ProxyRequestError < 20 and ProxyRequestNumber > 100"
    #query_2nd_level = 'SELECT idLink, LinkName  FROM wildberries.link;'
    #query_2nd_level = 'SELECT LinkName  FROM wildberries.link'
    print("Connected to:", db_connection.get_server_info())        
    
    cursor = db_connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    db_connection.close() # закрыть соединение с БД
    return (rows)

#def button(update, _):
def button(update, context):
    chat = update.effective_chat
    query = update.callback_query
    variant = query.data

    # `CallbackQueries` требует ответа, даже если 
    # уведомление для пользователя не требуется, в противном
    #  случае у некоторых клиентов могут возникнуть проблемы. 
    # смотри https://core.telegram.org/bots/api#callbackquery.
    query.answer()
    # редактируем сообщение, тем самым кнопки 
    # в чате заменятся на этот ответ.
    # print ('type query = ', type(query))
    # print ('\n query \n',query)
    # print('type variant = ',type(variant))
    # print('\n variant \n', variant)
    #query.edit_message_text(text=f"Выбранный вариант: {variant}")
    if variant.isnumeric() == True: #and int(variant) <= 17:
        button_list = second_level_keyboard(variant)

        reply_markup = InlineKeyboardMarkup(button_list)
        context.bot.send_message(chat_id=chat.id, text="выберите подкатегорию:", reply_markup=reply_markup)

    else:
        #query.edit_message_text(text=f"Выбранный вариант: {variant}")
            
        context.bot.send_message(chat_id=chat.id, text='Запускаю поиск в большом яндексе')
        #print(variant)
        res = y_search(variant)
        print(res)
        #print (str(type(res)))
        if res[0] == 'error' :
            context.bot.send_message(chat_id=chat.id, text='Ошибка '+res[1])
        else:
            # name link price img
            context.bot.send_message(chat_id=chat.id, text='Найдено в яндексе')
            context.bot.send_message(chat_id=chat.id, text='Цена в рублях: '+ str(res[0]))
            context.bot.send_message(chat_id=chat.id, text='Ссылка: '+ str(res[1]))
        
        # context.bot.send_message(chat_id=chat.id, text='Запускаю поиск в Ozon')
        # res = oz_search(variant)
        # print(res)
        # #print (str(type(res)))
        # if res[0] == 'error' :
        #     context.bot.send_message(chat_id=chat.id, text='Ошибка '+res[1])
        # else:
        #     # name link price img
        #     context.bot.send_message(chat_id=chat.id, text='Найдено в Ozon')
        #     context.bot.send_message(chat_id=chat.id, text='Цена в рублях: '+ str(res[0]))
        #     context.bot.send_message(chat_id=chat.id, text='Ссылка: '+ str(res[1]))
##############################################searches##################################
def y_search(text):
    prices=[]
    links=[]
    
    try:
        for page in range (0, 3):
            
            print ('вошли в подпрограмму большой яндекс, страница ', page)
            base_url_ynd = 'https://yandex.ru/search/?text='
            url_add = ' купить цена москва'
            tovar_req = quote(text)
            url_add = quote(url_add)
            url = base_url_ynd + tovar_req + url_add
            #print(url)
            if page > 0:
               url = str(nxt_ynd) + str(page)
               print(url)
            
            result = subprocess.run(['./datahtml', url], stdout=subprocess.PIPE, timeout=120)
        #  , encoding='UTF-8')
        #    result.stdout.decode('cp1251')
            print ('скачали текст')
            #print (result.stdout)
            a = result.stdout.decode('utf-8')
            #a = result.stdout.decode('cp1251')
            b = a.split('@@@@@')[1].split('@#@#@')[0]
            print(b)
            
            y_quant = len(b.split('<span class=\"PriceValue\">'))
            y_quant -= 1
            y_quant
            
            
            
            for i in range (1, y_quant):
                price = (str(b.split('<span class=\"PriceValue\">')[i].split('<span class=\"Rub\">')[0]).replace('<span>','').replace('</span>',''))
                #print (price)
                #print (str(b.split('<span class=\"PriceValue\">')[i].split('<span class=\"Rub\">')[0]).replace('<span>','').replace('</span>',''))
                lnk = (b.split('<span class=\"PriceValue\">')[i-1].split('href=\"')[-1].split('\"')[0])
                #print (lnk)
                if 'market-click2.yandex.ru' in lnk:
                    tag = '\"priceValue\":' + price
                    a = str(tag.strip())
                    lnk =  (b.split(sep=a)[1].split('\"logHref\":\"')[1].split('?')[0])
                    if 'marketDocumentUrl' in lnk:
                        lnk = lnk.split('marketDocumentUrl')[0]
                        # try:
                        #     lnk = lnk.split('\",\"')[0]
                        # except:
                        #     lnk = lnk.split('\', \'')[0]
                    #print (lnk2)
                    #print (b.split(sep=str(tag))#[1]#.split('\"logHref\":\"')[1].split('\":\"')[0]
                if 'marketDocumentUrl' in lnk:
                    lnk = lnk.split('marketDocumentUrl')[0]
                prices.append(int(price))
                links.append(lnk)
            if page == 0:
                # nxt_lnk = b.split('p=2\" data-counter')[0].split('href=\"')[-1]
                # nxt_ynd = 'https://yandex.ru' + nxt_lnk + 'p='
                nxt_lnk = b.split(',\"rlr\"')[0].split('\"lr\":')[1]
                nxt_ynd = url + '&amp;lr=' + str(nxt_lnk) + '&amp;p='
        
        results = {'Price':prices, 'Link':links}
        df = pd.DataFrame.from_dict(results)
        rowmin = df['Price'].idxmin()
        #print (df['Price'][rowmin], ' \n', df['Link'][rowmin])
        print (df)
        

        ret=[]
        ret.append(df['Price'][rowmin])
        ret.append(df['Link'][rowmin])
        print(ret[0])
        print (ret[1])
        print (ret)

        # name link price img
        return (ret)
    except Exception as e:
        print ('Ошибка ' + str(e))
        ret=[]
        ret.append('error')
        ret.append(str(e))
        return (ret)    




def oz_search(text):
    try:
        print ('вошли в подпрограмму Ozon')
        tovar_req = quote(text)
        url = 'https://www.ozon.ru/search/?text=' + tovar_req +  '&from_global=true'
        #print(url)
        
        b = "ошибка " * 100
        u = 1
        while len(b) < 5000 or u < 21:
            print('url = ', url)
            try:
                result = subprocess.run(['datahtml', url], stdout=subprocess.PIPE, timeout=220)#, encoding='UTF-8')
            except:
                #context.bot.send_message(chat_id=chat.id, text='Ozon сопротивляется')
                pass
            #result.stdout.decode('cp1251')
            try:
                #a = result.stdout.decode('utf-8')
                a = result.stdout.decode('cp1251')
                b = a.split('@@@@@')[1].split('@#@#@')[0]
            except:
                #context.bot.send_message(chat_id=chat.id, text='Ozon противится')
                pass
            print(b)
            u +=1
        
        # получили ссылку-редирект. формируем ссылку-редирект
        #print(b)
        #print(type(b))
        print ('получили редирект от  Ozon')

        if 'location.href' in str(b):
            url2 = 'https://www.ozon.ru' + b.split('location.href')[1].split('\";</')[0].replace('\\','').split('\"')[1]
            url2.replace('u0026', '&').replace('u002b', '+')
            url2 = url2.replace('u0026', '&').replace('u002b', '+')
            print(url2)
            print ('сформировали ссылку')
    
            
            b = "ошибка " * 100
            
            while len(b) < 20000:
                result = subprocess.run(['datahtml', url2], stdout=subprocess.PIPE, timeout=120)#, encoding='UTF-8')
                #result.stdout.decode('cp1251')
                #a = result.stdout.decode('utf-8')
                a = result.stdout.decode('cp1251')
                b = a.split('@@@@@')[1].split('@#@#@')[0]
                
        
        print ('скачали основной озон')
  
        
        c = b.split('NUXT__=JSON.parse(\'')[1].split('</script>')[0] #забрали только кусок с ценами - json
        c = c.replace('\\','')  # убрали все слеш слеш
        d = len(c.split('finalPrice\":')) #забрали все цены со страницы
        
        prices=[]
        prod_ids=[]
        prod_links=[]
        # массивчики под ID , ссылки и цены (хотя ID пока не надо)
        print ('дошли до массивчиков')

        for i in range (2, d): # бегаем по всем ценам и чистимся
            #print(c.split('finalPrice\":')[i].split(',\"')[0] + ' ' , end ='')
            price = (c.split('finalPrice\":')[i].split(',\"')[0])
            #print(c.split('finalPrice\":')[i].split('id\":')[1].split(',')[0])
            prod_id = (c.split('finalPrice\":')[i].split('id\":')[1].split(',')[0])
            try:
                #print(c.split('finalPrice\":')[i].split('link\":\"')[1].split('\",\"')[0].split('?')[0])#.split('id\":')[1].split(',')[0]
                prod_link = (c.split('finalPrice\":')[i].split('link\":\"')[1].split('\",\"')[0].split('?')[0])
            except:
                #print ('нет ссылки')
                prod_link = 'none'
            if prod_id.isnumeric() == True and prod_link != 'none':
                prices.append(int(price))
                prod_links.append(prod_link)
        
        ind = np.argmin(prices) # берем самую низкую цену из валидных, пишем ее индекс
        lowest_link = prod_links[ind]
        lowest_link = lowest_link.replace('u002F', '/')
        lowest_link = 'https://www.ozon.ru' + lowest_link
        lowest_price = prices[ind]
        
        ret=[]
        ret.append(lowest_price)
        ret.append(lowest_link)
        return (ret)
    except Exception as e:
        print ('Ошибка ' + str(e))
        ret=[]
        ret.append('error')
        ret.append(str(e))
        return (ret)

        
##############################################searches##################################




def start(bot, update):
  bot.message.reply_text(main_menu_message(),
                         reply_markup=main_menu_keyboard())

def main_menu(bot, update):
  bot.callback_query.message.edit_text(main_menu_message(),
                          reply_markup=main_menu_keyboard())
  
def second_level(bot, update):
    bot.callback_query.message.edit_text(second_level_message(),
                                         reply_markup=second_level_keyboard())



def error(update, context):
    print(f'Update {update} caused error {context.error}')

############################ Keyboards #########################################



def main_menu_keyboard():
    print('майн меню кейборд, мы тут ')
    
    sql_req = 'SELECT idLink, LinkName FROM wildberries.link'
    print ('лезем в базу')
    keyboard = []
    buttons = get_req_db(sql_req)
    
    for each in buttons:
        a = str(each[1])
        keyboard.append([InlineKeyboardButton(a, callback_data=str(each[0]))])
    
   

    return InlineKeyboardMarkup(keyboard)
    


def second_level_keyboard(idlink):
    print('секонд левел кейборд, мы тут ')
    
    sql_req_17 = 'SELECT ProductSubjectId, ProductSubjectId FROM wildberries.vi_product where Link_idLink = ' + str(idlink) + ' group by ProductSubjectId;'
    sql_req_1xx = 'SELECT ProductName, max(CAST(DataOrders AS UNSIGNED)), max(CAST(DataSalePriceU AS UNSIGNED)) FROM wildberries.vi_product where ProductSubjectId = ' + str(idlink) + ' group by ProductName order by max(CAST(DataOrders AS UNSIGNED)) DESC limit 5;'
   
    keyboard = []
    if (int(idlink) <= 17): 
        sql_req = sql_req_17
    else:
        sql_req = sql_req_1xx
    print(sql_req)
    buttons = get_req_db(sql_req)
   
    
    xls_name = 'cats.xls'
    xl = pd.ExcelFile(xls_name)
    df = xl.parse ((xl.sheet_names)[0])
    numlist = df['num'].tolist()
    namelist = df['name'].tolist()
    print (type(numlist[3]))
  
    
    for each in buttons:
        a = str(each[1])# название кнопки
     
        
        try:
            index = numlist.index(int(a))
            print ('нашли')
            print(namelist[index])
            a = str(namelist[index])
        except Exception:
            pass
        
        b = str(each[0]) # callback ответ категория/название товара
        
        try:
            #a = str(each[0]) + ' продано ' + str(each[1]) + ', по цене ' + (str(each[2])[:-2])
            a = str(each[0]) + ' прод.' + str(each[1]) + 'шт по' + (str(each[2])[:-2]) + 'р'
        except Exception:
            pass 
        
        try:
            a = a.replace('\\','')
        except:
            pass
        
        try:
            b = b.replace('\\','')
        except:
            pass
        
        try:
            a = a.replace('/','')
        except:
            pass
        
        try:
            b = b.replace('/','')
        except:
            pass
        
                
        try:
            a = a.replace('\'','')
        except:
            pass
        
        try:
            b = b.replace('\'','')
        except:
            pass

                        
        try:
            a = a.replace('\"','')
        except:
            pass
        
        try:
            b = b.replace('\"','')
        except:
            pass
        
        a = a[:60] if len(a)>60 else a
        
        
        print('текст ',a,'запрос ',b)
        if a.isdigit() == False:
            keyboard.append([InlineKeyboardButton(text=a, callback_data=b)])
    return (keyboard)







############################# Messages #########################################
def main_menu_message():
  return 'Выберите категорию:'

def second_level_message():
    return 'Выберите подкатегорию:'



############################# Handlers #########################################
token = ''
updater = Updater(token, use_context=True)

# Мы создали новый Updater и сохранили его в переменную с именем updater. (Переменные умеют еще и объекты разные хранить.) При создании мы указали токен нашего бота, чтобы он используя этот токен мог получать сообщения именно для нашего бота.

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(button))



updater.dispatcher.add_error_handler(error)

updater.start_polling()
updater.idle()
################################################################################


