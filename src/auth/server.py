import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

server.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
server.config['MYSQL_USER'] = os.environ['MYSQL_USER']
server.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
server.config['MYSQL_DB'] = os.environ['MYSQL_DB']
server.config['MYSQL_PORT'] = os.environ['MYSQL_PORT']

@server.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return 'Invalid username or password', 401 
    
    # check db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM users WHERE username = %s AND password = %s", (auth.username, auth.password)
        )
    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username == email and auth.password == password:
            return createJWT(auth.username, os.environ.get['JWT_SECRET_KEY'], True)
        
    return 'Invalid username or password', 401

@server.route('/validate', methods=['POST'])
def validate():
    encoded_token = request.headers.get('Authorization')
    if encoded_token is None:
        return 'No token provided', 401
    encoded_token = encoded_token.split(' ')[1]
    try:
        decoded_token = jwt.decode(encoded_token, os.environ.get['JWT_SECRET_KEY'], algorithms=['HS256'])
    except jwt.exceptions.InvalidSignatureError:
        return 'Invalid token provided', 401
    except jwt.exceptions.ExpiredSignatureError:
        return 'Token expired', 401
    
    return decoded_token, 200

def createJWT(username, secret, is_admin):
    token = jwt.encode(
        {
            'username': username,
            'admin': is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow()
        },
        secret,
        algorithm='HS256'
    )
    return token

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)