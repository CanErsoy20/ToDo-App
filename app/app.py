
import re  
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
  
mysql = MySQL(app)  

@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return redirect(url_for('tasks'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)


@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
  
        elif not username or not password or not email:
            message = 'Please fill out the form!'

        else:
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, % s, % s, % s)', (username, email, password,))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':

        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/tasks', methods =['GET', 'POST'])
def tasks():
    if session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Task WHERE user_id = % s AND status != "Done" ORDER BY deadline DESC', (session['userid'],))
        todoTasks  = cursor.fetchall()

        cursor.execute('SELECT * FROM Task T WHERE user_id = % s AND status = "Done" ORDER BY (SELECT DATEDIFF((SELECT done_time FROM Task WHERE id = T.id), (SELECT creation_time FROM Task WHERE id = T.id))) ASC', (session['userid'],))
        completedTasks = cursor.fetchall()
        
        return render_template('tasks.html', todoTasks = todoTasks, completedTasks = completedTasks)
    else:
        message = 'Please login first!'
        return render_template('login_html', message = message)

@app.route('/doTask', methods =['GET', 'POST'])
def doTask():
    if request.method == 'POST' and 'taskid' and 'title' in request.form:
        taskId = request.form['taskid']
        taskTitle = request.form['title']
        doneTime = datetime.now()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Task SET done_time = % s, status = % s WHERE id = % s)', (doneTime, 'Done', taskId))
        mysql.connection.cursor(MySQLdb.cursors.DictCursor).commit()
        message = 'Successfully finished the task % s', (taskTitle)
        return redirect(url_for('tasks', message = message))
    else:
        message = 'Something went wrong!'
        return redirect(url_for('tasks', message = message))
    
@app.route('/analysis', methods =['GET', 'POST'])
def analysis():
    return "Analysis page"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
