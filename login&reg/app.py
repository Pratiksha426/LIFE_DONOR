from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import model

app = Flask(__name__)
app.secret_key="dikshapratiksha"
# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Diksha@26",
    database="log"
)

# Create cursor object to execute queries
cursor = db.cursor()

# Route for rendering the home page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/help')
def help():
    return render_template('help.html')

# Route for rendering the hospital form page
@app.route('/hospital')
def hospital():
    return render_template('hospital.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/account')
def account():
    return render_template('account.html')
@app.route('/profile')
# def profile():
#     return render_template('profile.html')

# Route for rendering the profile page
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        # Fetch user data from the database based on the username
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            # Assuming the user table has columns like id, username, email, etc.
            # You can create a dictionary with user data
            user_data = {
                'id': user[0],
                'username': user[1],
                'password': user[2]
                # Add more fields as needed
            }
            return render_template('profile.html', user=user_data)
        else:
            # Handle the case where the user is not found
            return "User not found"
    else:
        # Handle the case where the user is not logged in
        return redirect(url_for('login_page'))


# Route for handling form submission and showing result
@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        city = request.form['city']
        organ_type = request.form['organ_type']

        # Call recommend_hospital function from model.py
        recommended_hospital, other_recommendations = model.recommend_hospital(city, organ_type)

        return render_template('result.html', recommended_hospital=recommended_hospital,
                               other_recommendations=other_recommendations)

# Route for rendering the login page
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the home page or any other desired page after logout
    return redirect(url_for('home'))

# Route for rendering the register page and handling registration form submission
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return "Username already exists. Please choose another one."
        else:
            # Insert new user into the database
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            return "Registration successful."
    else:
        return render_template('register.html')

# Route for handling login form submission
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        # If user is already logged in, redirect to profile page
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            # Store username in session upon successful login
            session['username'] = username
            app.logger.info(f"Logged in user: {username}")  # Logging for debugging
            return redirect(url_for('profile'))
        else:
            # User not found or incorrect password, render login page with error message
            app.logger.info("Login failed: Incorrect username or password")  # Logging for debugging
            error_message = "Incorrect username or password."
            return render_template('login.html', error_message=error_message)
    else:
        # Render the login page for GET requests
        return render_template('login.html')



if __name__ == "__main__":
    app.run(debug=True)
