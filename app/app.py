
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
    return render_template('login.html', message = message, )


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
        
        cursor.execute('SELECT * FROM Task WHERE user_id = % s AND status != "Done" ORDER BY deadline ASC', (session['userid'],))
        todoTasks = cursor.fetchall()

        cursor.execute('SELECT * FROM Task T WHERE user_id = % s AND status = "Done" ORDER BY done_time ASC', (session['userid'],))
        completedTasks = cursor.fetchall()
        
        cursor.execute('SELECT * FROM TaskType')
        taskTypes = cursor.fetchall()

        return render_template('tasks.html', todoTasks = todoTasks, completedTasks = completedTasks, taskTypes = taskTypes)
    else:
        message = 'Please login first!'
        return render_template('login_html', message = message)

@app.route('/doTask', methods =['GET', 'POST'])
def doTask():
    message = ''
    if request.method == 'POST' and 'taskid' in request.form:
        taskId = request.form['taskid']
        doneTime = datetime.now()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Task SET done_time = % s, status = % s WHERE id = % s', (doneTime, 'Done', taskId))
        mysql.connection.commit()
        
        return redirect(url_for('tasks', message = message))
    else:
        message = 'Something went wrong!'
        return redirect(url_for('tasks', message = message))
    
@app.route('/deleteTask', methods =['GET', 'POST'])
def deleteTask():
    message = ''
    if request.method == 'POST' and 'taskid' in request.form:
        taskId = request.form['taskid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM Task WHERE id = % s', (taskId))
        mysql.connection.commit()
        return redirect(url_for('tasks', message = message))
    else:
        message = 'Something went wrong!'
        return redirect(url_for('tasks', message = message))
    
@app.route('/addTask', methods =['GET', 'POST'])
def addTask():
    message = ''
    if request.method == 'POST' and 'title' in request.form and 'description' in request.form and 'deadline' in request.form and 'tasktype' in request.form:
        userId = session['userid']
        title = request.form['title']
        description = request.form['description']
        status = "Todo"
        deadline = request.form['deadline']
        creationTime = datetime.now()
        taskType = request.form['tasktype']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Task VALUES (NULL, % s, % s,% s,% s,% s, NULL, % s,% s)', (title, description, status, deadline, creationTime, userId, taskType))
        mysql.connection.commit()
        return redirect(url_for('tasks', message = message))
    else: 
        message = 'Please fill all fields'
        return redirect(url_for('tasks', message = message))
@app.route('/editTask', methods =['GET', 'POST'])
def editTask():
    message = ''
    if request.method == 'POST' and 'editid' in request.form:
        editid = request.form['editid']
        return redirect(url_for('tasks', editid = editid))
    else: 
        message = 'Please fill all fields'
        return redirect(url_for('tasks', message = message))
@app.route('/analysis', methods =['GET', 'POST'])
def analysis():
    message = ''
    if session['loggedin']:
        userId = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT title, TIMESTAMPDIFF(MINUTE, deadline, done_time) as latency FROM Task WHERE user_id = % s AND status = % s AND done_time > deadline", (userId, "Done"))
        lateTasks= cursor.fetchall()
       
        cursor.execute("SELECT AVG(TIMESTAMPDIFF(MINUTE, creation_time, done_time)) as avg_time FROM Task WHERE user_id = % s AND status = % s", (userId, "Done"))
        avgCompTime = cursor.fetchone()
        
        cursor.execute("SELECT task_type, COUNT(task_type) as number from Task WHERE user_id = % s AND status = % s GROUP BY task_type", (userId, "Done"))
        numCompTasks = cursor.fetchall()

        cursor.execute("SELECT title, deadline FROM Task WHERE user_id = % s AND status != 'Done' ORDER BY deadline DESC", (session['userid'],))
        uncompletedTasks = cursor.fetchall()

        cursor.execute("SELECT title, TIMESTAMPDIFF(MINUTE, creation_time, done_time) as compTime FROM Task where user_id = % s AND status = % s ORDER BY compTime DESC LIMIT 2", (userId, "Done"))
        top2Longest = cursor.fetchall()
    return render_template('analysis.html', message = message, lateTasks = lateTasks, avgCompTime = avgCompTime, numCompTasks = numCompTasks, uncompletedTasks = uncompletedTasks, top2Longest = top2Longest)

@app.route('/logout', methods =['GET', 'POST'])
def logout():
    message = ''
    session['loggedin'] = False
    session['userid'] = ''
    session['username'] = ''
    session['email'] = ''
    session.clear()
    return redirect(url_for('login', message = message))
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
