#!/usr/bin/python
# -*- coding: utf-8 -*-

## бот для телеги. поиск низшей цены по запросу
##  Eggfinderbot



from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
##  Updater - это объект, который умеет связываться с сервером телеграма и получать от него обновления, т.е. новые сообщения от пользователей.
import random #   для случайных ответов
import time #   для засекания времени работы
from time import sleep #   для драматических пауз

import mysql.connector as mysql #   подключаемся к mysql
import pandas as pd #   ворочаем таблицу
import re # коверкаем код 
from urllib.parse import quote # для перевода в %20
import json # для работы с JSON
from pandas.io.json import json_normalize # для работы с JSON внутри Pandas
import numpy as np # для быстрого счета


import requests #   для обращения по http и чтения html
from bs4 import BeautifulSoup #   для парсинга

import logging # для логирования
import ssl # для генерации ссл сертификатов для подключения. похоже, в этом дело в ответе 403

import subprocess #выполнение внешних шелл команд и разграбление ответов

import codecs # для цивилизованного декодирования ссылок -  codecs.decode(url3, 'unicode-escape')



project_name = 'EFB bot'

# для логгирования
logging.basicConfig(filename=project_name+'.log', level=logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ssl._create_default_https_context = ssl._create_unverified_context


def ym_search(text):
    try:
        print ('вошли в подпрограмму яндекс-маркет')
        url_ym = 'https://market.yandex.ru/search?&text='
        tovar_req = quote(text)
        url = url_ym + tovar_req
        result = subprocess.run(['./datahtml', url], stdout=subprocess.PIPE, timeout=120)
    #  , encoding='UTF-8')
    #    result.stdout.decode('cp1251')
        print ('скачали текст')
        #print (result.stdout)
        a = result.stdout.decode('utf-8')
        b = a.split('@@@@@')[1].split('@#@#@')[0]
        b = b.split('\<\!--BEGIN \[\@MarketNode\/SearchPartition\]')[0]\
        .split('\"SearchResults\"><div>')[1]\
        .split('<!--BEGIN \[@MarketNode/SearchPager\]')[0]
        
        link = b.split('<a href=\"/')[1].split('?')[0]
        prod_link = 'https://market.yandex.ru/' + link
        
        #price = b.split('data-autotest-currency=\"?\"')[1].split('><span>')[1].split('</span>')[0]
        price = b.split('data-autotest-currency=')[1].split('><span>')[1].split('</span>')[0]
        price
        
        img = b.split('data-zone-name=\"picture\">')[1].split('data-tid')[0].split('src=\"')[1].split('\" srcSet')[0]
        img = 'https:' + img
        
        name = b.split('<a href=\"/')[1].split('<img alt=\"')[1].split('\" class=')[0]
        ret=[]
        ret.append(name)
        ret.append(prod_link)
        ret.append(price)
        ret.append(img)
        # name link price img
        return (ret)
    except Exception as e:
        print ('Ошибка ' + str(e))
        ret=[]
        ret.append('error')
        ret.append(str(e))
        return (ret)
    
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
            if page > 0:
               url = str(nxt_ynd) + str(page)
               print(url)
            
            result = subprocess.run(['./datahtml', url], stdout=subprocess.PIPE, timeout=120)
        #  , encoding='UTF-8')
        #    result.stdout.decode('cp1251')
            print ('скачали текст')
            #print (result.stdout)
            a = result.stdout.decode('utf-8')
            b = a.split('@@@@@')[1].split('@#@#@')[0]
            
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

def wb_search(text):
    try:
        print ('вошли в подпрограмму WB')
        tovar_req = quote(text)
        url = 'https://www.wildberries.ru/search/extsearch/catalog?spp=0&regions=75,64,4,38,30,33,70,66,40,71,22,31,68,80,69,48,1&stores=119261,122252,122256,117673,122258,122259,121631,122466,122467,122495,122496,122498,122590,122591,122592,123816,123817,123818,123820,123821,123822,124093,124094,124095,124096,124097,124098,124099,124100,124101,124583,124584,125238,125239,125240,132318,132320,132321,125611,133917,132871,132870,132869,132829,133084,133618,132994,133348,133347,132709,132597,132807,132291,132012,126674,126676,127466,126679,126680,127014,126675,126670,126667,125186,116433,119400,507,3158,117501,120602,6158,121709,120762,124731,1699,130744,2737,117986,1733,686,132043&pricemarginCoeff=1.0&reg=0&appType=1&offlineBonus=0&onlineBonus=0&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&search=' + tovar_req +  '&xparams=search%3D' + tovar_req + '&xshard=&search=' + tovar_req + '&xsearch=true&sort=popular'
        result = subprocess.run(['./datahtml', url], stdout=subprocess.PIPE, timeout=120)
        print ('скачали текст')
        
        a = result.stdout.decode('utf-8')
        b = a.split('@@@@@')[1].split('@#@#@')[0]
        c = json.loads(b)
        df = pd.json_normalize(c['data']['products'])
        #df = df.drop(['siteBrandId','brandId', 'rating','diffPrice', 'isNew', 'feedbacks', 'pics', 'colors', 'sizes', 'isAdult', 'isDigital', 'subjectId'], axis=1)
        try:
            price = df['salePrice'][0]
        except:
            price = df['price'][0]
        price = int(price*0.5)
        df = df.drop(df[df['price'] < price].index)
        rowmin = df['price'].idxmin()
        price = int (df['price'][rowmin])
        link = 'https://www.wildberries.ru/catalog/' + str(df['id'][rowmin]) + '/detail.aspx'
        
        ret=[]
        ret.append(price)
        ret.append(link)
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
        while len(b) < 10000:
            try:
                result = subprocess.run(['./datahtml', url], stdout=subprocess.PIPE, timeout=120)#, encoding='UTF-8')
            except:
                #context.bot.send_message(chat_id=chat.id, text='Ozon сопротивляется')
                pass
            #result.stdout.decode('cp1251')
            try:
                a = result.stdout.decode('utf-8')
                b = a.split('@@@@@')[1].split('@#@#@')[0]
            except:
                #context.bot.send_message(chat_id=chat.id, text='Ozon противится')
                pass
            print(b)
        
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
                result = subprocess.run(['./datahtml', url2], stdout=subprocess.PIPE, timeout=120)#, encoding='UTF-8')
                #result.stdout.decode('cp1251')
                a = result.stdout.decode('utf-8')
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
    
# def sb_search(text):
#     try:
#         print ('вошли в подпрограмму SberMega')
#         tovar_req = quote(text)
#         url = 'https://sbermegamarket.ru/catalog/?q=' + tovar_req 

#         result = subprocess.run(['./datahtml', url], stdout=subprocess.PIPE, timeout=120)
#         print ('скачали текст')
#         a = result.stdout.decode('utf-8')
#         b = a.split('@@@@@')[1].split('@#@#@')[0]
        
#         c = b.split('catalog-department-header__title catalog-department-header__title_assumed')[1].split('</main>')[0]
#         y_quant = len(c.split('<meta itemprop=\"priceCurrency\" content=\"RUB\"><span>'))
        
#         prices=[]
#         prod_links=[]
        
#         for i in range (1, y_quant):
#             print(c.split('<meta itemprop=\"priceCurrency\" content=\"RUB\"><span>')[i].split('?')[0].replace(' ',''))
#             price = int(c.split('<meta itemprop=\"priceCurrency\" content=\"RUB\"><span>')[i].split('?')[0].replace(' ',''))
#             print(c.split('<meta itemprop=\"priceCurrency\" content=\"RUB\"><span>')[i].split('<a href=\"')[1].split('"')[0])
#             prod_link = c.split('<meta itemprop=\"priceCurrency\" content=\"RUB\"><span>')[i].split('<a href=\"')[1].split('"')[0]
#             prices.append(int(price.encode("ascii", "ignore")).split('\'')[1])
#             prod_links.append(prod_link)
        
#         ind = np.argmin(prices)
#         lowest_link = prod_links[ind]
#         lowest_link = quote(lowest_link.split('#')[0])
#         lowest_link = 'https://sbermegamarket.ru' + lowest_link
#         lowest_price = prices[ind]
        
        
#         ret=[]
#         ret.append(lowest_price)
#         ret.append(lowest_link)
#         return (ret)
#     except Exception as e:
#         print ('Ошибка ' + str(e))
#         ret=[]
#         ret.append('error')
#         ret.append(str(e))
#         return (ret)

# def isalnumspace(string):
#     letters = 'abcdefghijklmnopqrstuvwxyz0123456789 '
#  #   print(set(string.lower()) <= set(letters))
#     return(set(string.lower()) <= set(letters))



print("Бот запущен. Нажмите Ctrl+C для завершения")



# function to handle the /start command
def start(update, context):
    update.message.reply_text('start command received')

# function to handle the /help command
def help(update, context):
    update.message.reply_text('help command received')

# function to handle errors occured in the dispatcher 
def error(update, context):
    update.message.reply_text('an error occured')



def text(update, context):
    chat = update.effective_chat
    text = update.message.text
    #text = text.lower()
    context.bot.send_message(chat_id=chat.id, text='Запускаю поиск яндекс маркет')
    res = ym_search(text)
    print(res)
    #print (str(type(res)))
    if res[0] == 'error' :
        context.bot.send_message(chat_id=chat.id, text='Ошибка '+res[1])
    else:
        # name link price img
        context.bot.send_message(chat_id=chat.id, text='Найдено на яндекс-маркете')
        #context.bot.send_message(chat_id=chat.id, text=(str(type(res))))
        context.bot.send_message(chat_id=chat.id, text=res[0])
        context.bot.send_message(chat_id=chat.id, text=res[1])
        context.bot.send_message(chat_id=chat.id, text='Цена в рублях: '+ res[2])
        context.bot.send_photo(chat_id=chat.id, photo=res[3])
    
    context.bot.send_message(chat_id=chat.id, text='Запускаю поиск в большом яндексе')
    res = y_search(text)
    print(res)
    #print (str(type(res)))
    if res[0] == 'error' :
        context.bot.send_message(chat_id=chat.id, text='Ошибка '+res[1])
    else:
        # name link price img
        context.bot.send_message(chat_id=chat.id, text='Найдено в яндексе')
        context.bot.send_message(chat_id=chat.id, text='Цена в рублях: '+ str(res[0]))
        context.bot.send_message(chat_id=chat.id, text='Ссылка: '+ str(res[1]))
        
    context.bot.send_message(chat_id=chat.id, text='Запускаю поиск в WB')
    res = wb_search(text)
    print(res)
    #print (str(type(res)))
    if res[0] == 'error' :
        context.bot.send_message(chat_id=chat.id, text='Ошибка '+res[1])
    else:
        # name link price img
        context.bot.send_message(chat_id=chat.id, text='Найдено в WB')
        context.bot.send_message(chat_id=chat.id, text='Цена в рублях: '+ str(res[0]))
        context.bot.send_message(chat_id=chat.id, text='Ссылка: '+ str(res[1]))

    context.bot.send_message(chat_id=chat.id, text='Запускаю поиск в Ozon')
    res = oz_search(text)
    print(res)
    #print (str(type(res)))
    if res[0] == 'error' :
        context.bot.send_message(chat_id=chat.id, text='Ошибка '+res[1])
    else:
        # name link price img
        context.bot.send_message(chat_id=chat.id, text='Найдено в Ozon')
        context.bot.send_message(chat_id=chat.id, text='Цена в рублях: '+ str(res[0]))
        context.bot.send_message(chat_id=chat.id, text='Ссылка: '+ str(res[1]))
        
    # context.bot.send_message(chat_id=chat.id, text='Запускаю поиск в SberMega')
    # res = sb_search(text)
    # print(res)
    # if res[0] == 'error' :
    #     context.bot.send_message(chat_id=chat.id, text='Ошибка '+res[1])
    # else:
    #     # name link price img
    #     context.bot.send_message(chat_id=chat.id, text='Найдено в SberMega')
    #     context.bot.send_message(chat_id=chat.id, text='Цена в рублях: '+ str(res[0]))
    #     context.bot.send_message(chat_id=chat.id, text='Ссылка: '+ str(res[1]))

        #context.bot.send_message(chat_id=chat.id, text=(str(type(res))))
        # context.bot.send_message(chat_id=chat.id, text=res[0])
        # context.bot.send_message(chat_id=chat.id, text=res[1])
        # context.bot.send_message(chat_id=chat.id, text='Цена в рублях: '+ res[2])
        # context.bot.send_photo(chat_id=chat.id, photo=res[3])
    
 

def main():
    TOKEN = ""

    # create the updater, that will automatically create also a dispatcher and a queue to 
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))


    dispatcher.add_handler(MessageHandler(Filters.text, text))



    # start your shiny new bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
