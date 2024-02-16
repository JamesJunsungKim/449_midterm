from flask import Flask, request, url_for, redirect, jsonify, make_response
import sqlite3, uuid

app = Flask(__name__)


'''
REQUIREMENTS
X 1. Implement the routing (endpoints) and dynamic URL (variable rules/path variables in endpoints)
X 2. Implement the use case for url_for() and redirect() method     
X 3. use of HTTP methods based on the type of request sent
X 4. use of request object and response object, header accessing, and sent headers in response back
X 5. able to return various error codes according to the data sent and operation performed
X 6. Implement the query parameters
X 7. use of form data and JSON data
X 8. connecting with database
X 9. perform CRUD (CREATE, READ, UPDATE, and DELETE) operations on the database
'''

def connect_db():
    conn = sqlite3.connect('identifier.sqlite')
    return conn

def get_user_by_id(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()
    return row

def insert_user(name, email, nickname):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, nickname) VALUES (?, ?, ?)", (name, email, nickname))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_user(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()

def update_user_name(email, new_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=? WHERE email=?", (new_name, email))
    conn.commit()
    conn.close()

@app.route('/error')
def handle_error():
    # Retrieve status_code and error message from request parameters
    status_code = request.args.get('status_code', 400)
    error_message = request.args.get('error', 'Unknown error')

    # Create and return the error response
    response = {'error': error_message}
    return make_response(jsonify(response), status_code)

@app.route('/auth/token', methods=['POST'])
def handle_token():

    user_agent = request.headers.get('User-Agent')
    response = make_response("Response body")
    response.status_code = 200

    token = uuid.uuid4()
    # need to add header
    response = jsonify({
        "token": token,
        "user_agent": user_agent,
        "status_code": response.status_code
    })
    response.headers['token'] = token
    return  response

@app.route('/user', methods=['GET', 'POST', 'DELETE', 'PUT'])
def handle_users():
    method = request.method
    if method == 'GET':
        args = request.args
        user_id = args.get('id')
        # query from sqlite
        if not user_id:
            return redirect(url_for('handle_error', status_code=400, error='user_id is required'))

        result = get_user_by_id(user_id)
        if not result:
            return redirect(url_for('handle_error', status_code=404, error='user not found'))

        return jsonify({
            'user': {
                'id': result[0],
                'name': result[1],
                'email': result[2]
            }
        })

    elif method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        nickname = data.get('nickname')

        if not name or not email or not nickname:
            return redirect(url_for('handle_error', status_code=400, error='name, email, and nickname are required'))

        if get_user_by_email(email):
            return redirect(url_for('handle_error', status_code=400, error='email already exists'))

        insert_user(name, email, nickname)
        return jsonify({'users': {
            'name': name,
            'email': email,
            'nickname': nickname
        }})

    elif method == 'DELETE':
        data = request.get_json()
        email = data.get('email')
        if not email:
            return redirect(url_for('handle_error', status_code=400, error='email is required'))

        if not get_user_by_email(email):
            return redirect(url_for('handle_error', status_code=404, error='user not found'))

        delete_user(email)
        return jsonify({'user': {
            'email': email
        }})

    elif method == 'PUT':

        data = request.get_json()
        email = data.get('email')
        new_name = data.get('name')
        if not email or not new_name:
            return redirect(url_for('handle_error', status_code=400, error='email and new_name are required'))

        if not get_user_by_email(email):
            return redirect(url_for('handle_error', status_code=404, error='user not found'))

        update_user_name(email, new_name)

        return jsonify({
            'user': {
                'email': email,
                'name': new_name
            }
        })

@app.route('/user/<int:user_id>')
def get_user(user_id):
    return redirect(url_for('handle_users', id=user_id))

if __name__ == '__main__':
    app.run()
