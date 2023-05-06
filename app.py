from flask import Flask, render_template, request, redirect, url_for    #pip install Flask
import cv2                                                              #pip install opencv-python
from flask_cors import CORS                                             #pip install Flask-Cors
import pandas as pd                                                     #pip install pandas  and  pip install openpyxl
import time
from datetime import datetime
import qrcode                                                           #pip install qrcode  and  pip install pillow
from io import BytesIO
import base64





app = Flask(__name__)
cors = CORS(app, resources={r"/uploader": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['TEMPLATES_AUTO_RELOAD'] = True


result = ''
error = ''


@app.route('/')
def test():
    return """
        <h1>Добро пожаловать на главную страницу!</h1>
        <button onclick="location.href='/reg'">Регистрация</button>
        <button onclick="location.href='/success'">Вход</button>
        <button onclick="location.href='/cam'">Камера</button>
        """


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        name = request.form['name']
        password = request.form['password']
        surname = request.form['surname']
        user = {'Login': login, 'Name': name, 'Surname': surname, 'Password': password}
        print(user)
        df = pd.read_excel('users.xlsx')
        df = pd.concat([df, pd.DataFrame (user, index=df.columns [: len (user)])], ignore_index = True)
        df.to_excel('users.xlsx', index=False)

        return render_template('success.html')
    else:
        return render_template('register.html')
    
    
@app.route('/success', methods=['GET', 'POST'])
def success():
    login = request.form.get('login')
    password = request.form.get('password')

    # отладка
    print('##########################################', login, password)

    # Получение информации о пользователе из базы данных Excel
    df = pd.read_excel('users.xlsx')
    logins = df['Login'].to_list()
    passw  = df['Password'].to_list()
    try:
        name_index = logins.index(login)
    except:
        name_index = 0

    # отладка
    print(f"{logins[name_index]} : {passw[name_index]}")
    print(type(login), type(logins[name_index]))
    print(type(password), type(passw[name_index]))

    if logins[name_index] == login and str(passw[name_index]) == password:
            print('Ok!')
            return redirect(url_for('profile', login=login))
    else:
            print('error')
            error = 'Неверное имя пользователя или пароль'
            return render_template('success.html', error=error)
    

@app.route('/profile/<login>')
def profile(login):
    # Получение информации о пользователе из базы данных Excel
    df = pd.read_excel('users.xlsx')

    # отладка
    print(df.columns.tolist())
    print(df.head())

    if len(df[df['Login'] == login]) != 0:
        names = df['Name'].to_list()
        logins = df['Login'].to_list()
        try:
            name_index = logins.index(login)
        except:
            name_index = 0
        name = names[name_index]
        
        user_data = login
        # qr_data = str(name) + '_' + str(surname)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(f"{user_data} {datetime.now().strftime('%H:%M')}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        # Преобразование изображения в строку в формате base64
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        user_data = {'name': name, 'qr_code': qr_img_str, 'login': login}
        return render_template('user.html', user_data=user_data)
    
    else:
        error = 'Пользователь не найден'
        return render_template('success.html', error=error)
    

    



@app.route('/cam', methods = ['GET', 'POST'])
def cam():
    global result
    if request.method == 'POST':
        file = request.files.get('file')
        print(f'Got file: {request.files}')

        file.save('./photo/original.png')

    
        img = cv2.imread('photo/original.png')
        detector = cv2.QRCodeDetector()
        data, bbox, temp = detector.detectAndDecode(img)
        print(data)

        ep_time = time.time()
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ep_time))
        time_for_qr_test = datetime.now().strftime('%H:%M')


        login, time_qr = data.split()

        # отладка
        # print(name, '++++',  str(time_qr))
        
        df = pd.read_excel('users.xlsx')
        print(df['Login'])

        if len(df[df['Login'] == login]) and time_qr == time_for_qr_test:
            print('#######################################################################################                 YYYYYYYYYYYYYYYYY')
            names = df['Name'].to_list()
            surnames = df['Surname'].to_list()
            logins = df['Login'].to_list()
            try:
                name_index = logins.index(login)
            except:
                name_index = 0
            name = names[name_index]
            surname = surnames[name_index]
            print(name+ ' ' + surname)
            new = {'ФИО': [name+ ' ' + surname], 'Время': [time_now]}
            df1 = pd.read_excel('test.xlsx')
            df1 = pd.concat([df1, pd.DataFrame (new, index=df.columns [: len (new)])], ignore_index = True)
            df1.to_excel('test.xlsx', index=False)
            result = 'Все отлично, проходите'
            return render_template('cam.html', result=result)
        else:
            print('//////////////////////////////////////////////////////////////////////////////////////////               NONONONONONONONONO')
            result = 'Ошибка... Вас нет в базе данных'


    return render_template('cam.html', result=result)










# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    app.run(debug=True)
