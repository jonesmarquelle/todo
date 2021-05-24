from flask import Flask, redirect, url_for, request, render_template
import sys
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')
    
@app.route('/list/<name>', methods = ['POST', 'GET'])
def list(name):
    if request.method == 'GET':
        tasks = get_tasks(name)
        return render_template('todo.html', username=name, tasks=tasks)
    elif request.method == 'POST':
        button_pressed = request.form["action"]
        
        #Add new tasks
        if button_pressed == "add":
            new_task = request.form.get("new_task")
            if new_task: add_task(name, new_task)
    
        #Update Completion Status
        if button_pressed == "update":
            all_tasks = request.form.getlist('task')
            completed = [1 if x in request.form else 0 for x in all_tasks]
            update_tasks(name, all_tasks, completed)
        
        #Delete tasks
        if button_pressed.endswith("delete"):
            task = button_pressed.rsplit("_", 1)[0]
            delete_task(name, task)
        
        #Refresh page
        tasks = get_tasks(name)
        return render_template('todo.html', username=name, tasks=tasks)
    
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['name']
        return redirect(url_for('list', name = user))
    user = request.args.get('name')
    return redirect(url_for('list', name = user))

'''SQL Interaction Code'''
#import credentials
import mysql.connector
from mysql.connector import errorcode

SQL_USER = 'todo_app'#credentials.username
SQL_PASS = ''#credentials.password
SQL_HOST = '127.0.0.1'#credentials.host
SQL_DB = 'todo_tasks'#credentials.db

def init_sql():
    try:
        cnx = mysql.connector.connect(user = SQL_USER,
                                      password = SQL_PASS,
                                      host = SQL_HOST,
                                      database = SQL_DB)
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("DB does not exist")
        else:
            print(e)
        return
        
    return cnx
   
def add_task(name, task):
    cnx = init_sql()
    cursor = cnx.cursor()
    
    count_query = ("SELECT COUNT(*)" 
                   "FROM todo_tasks "
                   "WHERE task=%s")
    cursor.execute(count_query, (task,))
    result = cursor.fetchone()[0]
    print(result, file=sys.stderr)
    if result != 0:
        return
    
    add_query = ("INSERT INTO todo_tasks (name, task, complete) "
                 "VALUES (%s, %s, %s)")
    cursor.execute(add_query, (name, task, 0))
    
    cnx.commit()
    cursor.close()
    cnx.close()
   
def update_tasks(name, tasks, completed):
    cnx = init_sql()
    cursor = cnx.cursor()
    
    for i in range(len(tasks)):
        update_query = ("UPDATE todo_tasks "
                        "SET complete=%s "
                        "WHERE name=%s "
                        "AND task=%s")
        cursor.execute(update_query, (completed[i], name, tasks[i]))
    
    cnx.commit()
    cursor.close()
    cnx.close()
   
def delete_task(name, task):
    cnx = init_sql()
    cursor = cnx.cursor()
    
    delete_query = ("DELETE FROM todo_tasks "
                    "WHERE name = %s "
                    "AND task = %s "
                    "LIMIT 1")
    cursor.execute(delete_query, (name, task))
    
    cnx.commit()
    cursor.close()
    cnx.close()
   
def get_tasks(name):
    cnx = init_sql()
    cursor = cnx.cursor()
    
    tasks = dict()
    query = ("SELECT task, complete FROM todo_tasks WHERE name=%s")
    cursor.execute(query, (name,))
    for (task, completed) in cursor:
        tasks[task] = completed
    cursor.close()
    cnx.close()
    return tasks

if __name__ == '__main__':
    app.run()