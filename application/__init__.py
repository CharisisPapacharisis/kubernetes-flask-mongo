from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import base64

app = Flask(__name__)
'''
#This client creation can be used when utilizing the "docker-compose"-based containerization
client = MongoClient(host='test_mongodb',  
                         port=27017, 
                         username="USERNAME", 
                         password="PASSWORD",
                        authSource="admin")
'''

#The below client creation can be used when utilizing the kubernetes YAML/Helm containerization

host_url = os.getenv("MONGO_CLIENT")

username = os.getenv("USERNAME")
print("username is: ", username)  

password = os.getenv("PASSWORD")

client = MongoClient(host_url,  
                        port=27017,
                        username=username, 
                        password=password)


# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#create/point to a db called "my_db"
db = client.my_db 

#create/point to a collection called "todos" into the my_db database. 
todos = db.todos 

#home page
@app.route('/')
def index():
    all_todos = todos.find()
    return render_template('list_todo.html', todos = all_todos)

#add a new to-do item
@app.route('/add', methods = (['GET','POST']))
def add():
    if request.method == "POST":
        task_name = request.form['task_name']
        status = request.form['status']
        priority = request.form['priority']
        date_due = request.form['date_due']
        
        todos.insert_one({'task_name':task_name, 'status':status, 'priority':priority, 'date_due':date_due})
        return redirect(url_for('index'))
    else: 
        return render_template("add_todo.html")

#delete item
@app.route('/delete/<id>', methods = (['GET','POST'])) 
def delete(id):
    todos.delete_one({"_id":ObjectId(id)})
    return redirect(url_for('index'))

#update item
@app.route('/update/<id>', methods = (['GET','POST']))
def update(id):
    if request.method == 'POST':
        task_name = request.form['task_name']
        status = request.form['status']
        priority = request.form['priority']
        date_due = request.form['date_due']
        todos.find_one_and_update({"_id":ObjectId(id)}, {'$set':{'task_name':task_name, 'status':status, 'priority':priority, 'date_due':date_due}})
        return redirect(url_for('index'))
    else: 
        todo = todos.find_one({"_id":ObjectId(id)})
        print(todo)
        task_name = todo['task_name']
        status = todo['status']
        priority = todo['priority']
        date_due = todo['date_due']

        return render_template("update_todo.html",placeholder_name=task_name, placeholder_status=status, placeholder_priority=priority, placeholder_date_due=date_due)
