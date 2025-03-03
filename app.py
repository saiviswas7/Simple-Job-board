from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import secrets  # Secure secret key

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ajantha@123'  # Change this
app.config['MYSQL_DB'] = 'job_portal'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Secure Secret Key
app.secret_key = secrets.token_hex(16)

@app.route('/')
def home():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM jobs")
    jobs = cur.fetchall()
    cur.close()
    return render_template('home.html', jobs=jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username already exists!', 'danger')
        finally:
            cur.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", [username])
        user = cur.fetchone()
        cur.close()
        
        if user and 'password' in user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'username' not in session:
        flash('Please log in to post a job.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jobs (title, description) VALUES (%s, %s)", (title, description))
        mysql.connection.commit()
        cur.close()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('post_job.html')

@app.route('/apply/<int:job_id>', methods=['POST'])
def apply(job_id):
    if 'username' not in session:
        flash('Please log in to apply for jobs.', 'warning')
        return redirect(url_for('login'))
    
    user = session['username']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO applications (job_id, username) VALUES (%s, %s)", (job_id, user))
    mysql.connection.commit()
    cur.close()
    
    flash('Application submitted!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
