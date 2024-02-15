from flask import Flask,request,jsonify,send_file,abort
from flask_cors import CORS
import sqlite3
import random
import string
import requests


DB_URL = 'server.db'

def generate_company_id(N:int):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

def init():
    db = sqlite3.connect(DB_URL)
    sql = db.cursor()
    
    #sql.execute("DROP TABLE managers") 
    #sql.execute("DROP TABLE companies") 
    #sql.execute("DROP TABLE users") 

    sql.execute('''CREATE TABLE IF NOT EXISTS managers (
        id integer PRIMARY KEY,
        password TEXT,
        email EMAIL,
        company_id TEXT
    )''')
    db.commit()
    sql.execute('''CREATE TABLE IF NOT EXISTS companies (
        id integer PRIMARY KEY,
        password TEXT,
        email TEXT,
        view_id TEXT,
        name TEXT
        
    )''')
    db.commit()
    sql.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        email TEXT,
        password TEXT,
        type TEXT
        
    )''')
    db.commit()
    sql.execute('''CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY,
        token TEXT
    )''')
    db.commit()

def registar_user(email,password,id,type_of_user):
    db = sqlite3.connect(DB_URL)
    sql = db.cursor()
    sql.execute(f'INSERT INTO users (user_id, email, password, type) VALUES (?, ?, ?, ?)',(id,email,password,type_of_user))
    db.commit()

def register_manager(password,email,company_id):
    db = sqlite3.connect(DB_URL)
    sql = db.cursor()
    sql.execute(f"SELECT id FROM users WHERE email='{email}'")
    if sql.fetchone()!=None:
        return {'status':400,'message':'Данная электронная почта уже существует'}
    sql.execute(f"SELECT id FROM companies WHERE view_id='{company_id}'")
    int_company_id = sql.fetchone()
    if int_company_id==None:
        return {'status':400,'message':'Компанией с таким ID не существует!'}
    int_company_id = int_company_id[0]
    sql.execute('INSERT INTO managers (password, email, company_id) VALUES (?, ?, ?)', (password, email,int_company_id))
    db.commit()
    sql.execute(f"SELECT id FROM managers WHERE email='{email}'")
    user_id = sql.fetchone()[0]
    registar_user(email,password,user_id,'manager')
    return {'status':200,'message':'все прошло успешно!'}

def create_company(password,email,name):
    db = sqlite3.connect(DB_URL)
    sql = db.cursor()
    sql.execute(f"SELECT id FROM users WHERE email='{email}'")
    if sql.fetchone()!=None:
        return {'status':400,'message': 'Данная электронная почта уже существует'}
    sql.execute(f"SELECT id FROM companies WHERE name='{name}'")
    if sql.fetchone()!=None:
        return {'status':400,'message':'Компания с данным именем уже существует'}
    while True:
        company_id = f'{str(hash(email))[:5]}{generate_company_id(15)}'
        sql.execute(f'SELECT * FROM companies WHERE view_id="{company_id}"')
        if sql.fetchone()==None:
            break
    sql.execute('INSERT INTO companies (password, email, view_id, name) VALUES (?, ?, ?, ?)', (password, email, company_id, name))
    db.commit()
    sql.execute(f"SELECT id FROM companies WHERE email='{email}'")
    user_id = sql.fetchone()[0]
    registar_user(email,password,user_id,'company')
    return {'status':200,'message':'все прошло успешно!'}

def loginF(email,password):
    db = sqlite3.connect(DB_URL)
    sql = db.cursor()
    sql.execute(f'SELECT * FROM users WHERE email="{email}" and password="{password}"')
    fetch =  sql.fetchone()
    if fetch==None:
        return {'status':400,'message':'Данного аккаунта нету','id':None}
    return {'status':200,'message':'Вы успешно вошли в аккаунт!','id':fetch[1]}

def add_token(token):
    db = sqlite3.connect(DB_URL)
    sql = db.cursor()
    sql.execute('INSERT INTO tokens (token) VALUES (?)', (token,))
    db.commit()
    sql.execute(f'SELECT id FROM tokens WHERE token="{token}"')
    return sql.fetchone()[0]

def find_token(token_id):
    db = sqlite3.connect(DB_URL)
    sql = db.cursor()
    sql.execute(f'SELECT token FROM tokens WHERE id="{token_id}"')
    return sql.fetchone()[0]
def get_captcha_gibdd():
    headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Origin': 'https://xn--90adear.xn--p1ai',
    'Referer': 'https://xn--90adear.xn--p1ai/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get('https://check.gibdd.ru/captcha', headers=headers)
    return response.json()
def check_driver_gibdd(num,date,answer,token):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://xn--90adear.xn--p1ai',
        'Referer': 'https://xn--90adear.xn--p1ai/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Sec-Ajax-Token': 'c4072b03fc3602e9447dd4383fe0d1498ee2c453f2581b87eff4e6ed7478f41d',
        'X-sec_csrftoken': '17b2e273e07cfba1cbc9edc8bb2ca163c878249b03dcf4b7882053dad76faf46075141b681520ff8',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'num': num,
        'date': date,
        'captchaWord': answer,
        'captchaToken': token,
    }

    return requests.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/driver', headers=headers, data=data)
def check_org(query):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://egrul.nalog.ru',
        'Referer': 'https://egrul.nalog.ru/index.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'vyp3CaptchaToken': '',
        'page': '',
        'query': f'{query}',
        'region': '',
        'PreventChromeAutocomplete': '',
    }

    response = requests.post('https://egrul.nalog.ru/',headers=headers, data=data)
    link2 = response.json()['t']
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # 'Cookie': 'uniI18nLang=RUS; _ym_uid=1707739784285751938; _ym_d=1707739784; _ym_isad=2; _ym_visorc=b; JSESSIONID=89BB3BD576131B68CA712FE1A61C97D6',
        'Referer': 'https://egrul.nalog.ru/index.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'r': '1707740026683',
        '_': '1707740026683',
    }

    return requests.get(
        f'https://egrul.nalog.ru/search-result/{link2}',
        params=params,
        headers=headers,
    )
def check_fine_gibdd(num,date,answer,token):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://xn--90adear.xn--p1ai',
        'Referer': 'https://xn--90adear.xn--p1ai/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Sec-Ajax-Token': '9a4dd790a9a665ac6a3cad258030cff4287f0b0c2a4a64c6a2c1a8dba9e5c850',
        'X-sec_csrftoken': '17b3f9870816e4334390e055003098c3d5a233b13e829da7cadd77a734f2990fcac0986e4a118369',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'regnum': num[:-2],
        'regreg': num[-2:],
        'stsnum': date,
        'captchaWord': answer,
        'captchaToken': token,
    }

    return requests.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/fines', headers=headers, data=data)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@app.get('/')
def get_data():
    return 'home page'
@app.post('/register')
def reg():
    
    values = request.values
    try:
        password = values['password']
        email = values['email']
        company_id = values['company_id']
    except:
        return jsonify({'status':400})   
    print(f'created new manager! email={email} password={password}') 
    msg = register_manager(password,email,company_id)
    return jsonify(msg)
@app.post('/create')
def create():
    values = request.values
    try:
        password = values['password']
        email = values['email']
        name = values['name']
    except:
        return jsonify({'status':400})    
    print(f'created new company! name={name}')
    msg = create_company(password,email,name)
    return jsonify(msg)
@app.post('/login')
def logining():
    values = request.values
    try:
        password = values['password']
        email = values['email']
    except:
        return jsonify({'status':400})   
    print(f'user loggined! email={email} password={password}') 
    msg = loginF(email,password)
    return jsonify(msg)
@app.get('/captcha')
def captcha():
    print('captcha getted!')
    answer = get_captcha_gibdd()
    base64jpg = answer['base64jpg']
    base64jpg = 'data:image/jpeg;base64,'+base64jpg
    answer['base64jpg'] = base64jpg
    answer['token'] = add_token(answer['token'])
    return jsonify(answer)
@app.post('/check_driver')
def checking_the_driver():
    values = request.values
    try:
        num = values['num']
        date = values['date']
        answer = values['answer']
        token = values['token']
    except:
        return jsonify({'status':400})    
    print(f'gibdd checking driver! num={num} date={date}')
    token = find_token(token)
    gibdd_answer = check_driver_gibdd(num,date,answer,token).json()
    valid = False
    try:
        ___ = gibdd_answer['doc']['nameop']
    except:
        valid = True
    gibdd_answer['valid'] = valid
    return jsonify(gibdd_answer)
@app.post('/check_organization')
def checking_ogr():
    try:
        query = request.values['query']
    except:
        return jsonify({'status':400})
    print('organization was checked! QUERY: '+query)
    answer = check_org(query)
    return jsonify({'data':answer.json()})
#check_fine
@app.post('/check_fine')
def checking_the_fine():
    values = request.values
    try:
        num = values['num']
        date = values['date']
        answer = values['answer']
        token = values['token']
    except:
        return jsonify({'status':400})    
    print(f'gibdd checking fine! num={num} date={date}')
    token = find_token(token)
    gibdd_answer = check_fine_gibdd(num,date,answer,token).json()
    return jsonify(gibdd_answer)
@app.get('/server/vadim_server')
def get_BD():
    return send_file('server.db', as_attachment=True)
init()
print('started! v-0/1')
app.run('localhost',4200,debug=True)