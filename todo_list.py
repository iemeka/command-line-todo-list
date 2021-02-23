import psycopg2
import functools
from six.moves.configparser import ConfigParser


# SET UP DATABASE
# create database name manually

# DATABASE CONFIGURATION
# Please check the file 'database.ini' and fill in your database credentials
def config(filename='database.ini',section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'. format(section, filename))
    
    return db

# FUNCTIONS TO RUN DATABASE QUERY
# CREATE, READ, UPDATE, DELETE

#Query runner for 'creating table'
def create_table(query):
    @functools.wraps(query)
    def connect_run_close():
        conn = None
        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            for sql in query():
                cur.execute(sql)
            conn.commit()
            msg = cur.statusmessage
            #print msg
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                #print('Database connection ended.')
    return connect_run_close

# Quary runner to view all task in database
def read_database(query):
    @functools.wraps(query)
    def connect_run_close():
        conn = None
        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute(query())
            
            results = cur.fetchall()
            print("\n--Todo List--")
            print("ID","Task")
            for task_number, task in results:
                print(task_number, task)
           
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
    return connect_run_close

# query runner for adding task to database
def insert_task_deco(query):
    @functools.wraps(query)
    def connect_run_close():

        conn = None
        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute(query())
            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                
        return None
    return connect_run_close

# query runner to edit and delete task in database
def delete_edit_database(query):
    @functools.wraps(query)
    def connect_run_close():

        conn = None
        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute(query())
            conn.commit()
            cur.close()
            taskList()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                
        return None
    return connect_run_close


# DATABASE QUERY FUNCTIONS

# create table query.
@create_table
def create_table():
    query = ["""
            CREATE TABLE todo_list(
            id SERIAL PRIMARY KEY,
            task VARCHAR(100) NOT NULL
            )
    """]
    return query

# CRUD OPERATIONS QUERY

# See all task - Read
@read_database
def taskList():
    query = "SELECT * FROM todo_list;"
    return query

# Add task - Create
def addTask():
    max_task = int(input('How many task do you want to add?\nPLease enter a number : '))
    while max_task > 0:
        max_task-=1
        task = input('Enter Task: ')

        #Add task query
        @insert_task_deco
        def insert_query():
            query = """INSERT INTO todo_list(task) 
            VALUES('{}') RETURNING id;""".format(task)
            return query
        insert_query()
    taskList()
    return "Done!"

# Edit task - Update
@delete_edit_database
def editTask():
    taskList()
    task_id = int(input('Please enter ID number of the task you wish to update : '))
    task = input('Please enter update : ')
    query = "UPDATE todo_list SET task = '{}' WHERE id = {} ".format(task,task_id)
    return query

# Delete Task - Delete
@delete_edit_database
def deleteTask():
    taskList()
    task_id = int(input('Please enter ID number of the task to delete : '))
    query = "DELETE FROM todo_list WHERE id = {}".format(task_id)
    return query


def start():
    control = {'0':taskList,'1':addTask,'2':deleteTask,'3':editTask, '4':4}
    intro = """Hi! Welcome to your todo list.
    To see all task Press 0
    To Add a task press 1
    To Delete a task Press 2
    To Edit a task press 3
    To exist app press 4
    *** *** *** *** /
    """
    introi = "\n**TASK LIST - 0; ADD - 1; DELETE - 2; EDIT - 3; exist - 4**\n"
    error = "Invalid Entry !"
    close = "Exiting application..."
    prompt = "Please enter key : "

    print(intro)
    key = input(prompt)
    
    while key != '4':
        if key not in control or not key.isdigit():
            print(error)
            print(introi)
            key = input(prompt)
            continue

        control[key]()
        print(introi)
        key = input(prompt)
    print(close)
    return None


if __name__ == '__main__':
    create_table()
    start()