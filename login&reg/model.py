from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Initialize Flask app
# app = Flask(__name__)

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Diksha@26",
    database="log"
)

# Fetch data from the database
def fetch_data():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM hospitals")  # Ensure this matches your actual table name
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=columns)

# Load the dataset from the database
data = fetch_data()

# Function to split rows with multiple organ types into separate rows
def split_rows(df):
    new_rows = []
    for index, row in df.iterrows():
        organ_types = row['Organ_type'].split(',')
        for organ_type in organ_types:
            new_row = row.copy()
            new_row['Organ_type'] = organ_type.strip()
            new_rows.append(new_row)
    return pd.DataFrame(new_rows)

# Preprocess the data for the Random Forest model
data_split = split_rows(data)
data_split['City'] = data_split['City'].str.lower()
data_split['Organ_type'] = data_split['Organ_type'].str.lower()

# Encode categorical variables
label_encoders = {}
for column in ['City', 'Organ_type', 'Hospital_name']:
    le = LabelEncoder()
    data_split[column] = le.fit_transform(data_split[column])
    label_encoders[column] = le

# Prepare features and target variable
X = data_split[['City', 'Organ_type']]
y = data_split['Hospital_name']

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Classifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Function to recommend hospital based on city and organ type
def recommend_hospital(city, organ_type):
    # Preprocess user input by converting to lowercase
    city = city.lower()
    organ_type = organ_type.lower()

    # Transform inputs using label encoders
    city_encoded = label_encoders['City'].transform([city])[0]
    organ_type_encoded = label_encoders['Organ_type'].transform([organ_type])[0]

    # Predict hospital using the Random Forest model
    prediction = rf.predict([[city_encoded, organ_type_encoded]])
    predicted_hospital_encoded = prediction[0]

    # Decode the predicted hospital name
    predicted_hospital = label_encoders['Hospital_name'].inverse_transform([predicted_hospital_encoded])[0]

    # Filter data for the given city and organ type
    filtered_data = data_split[(data_split['City'] == city_encoded) & (data_split['Organ_type'] == organ_type_encoded)]

    # Find the hospital with the maximum feedback points
    recommended_hospital = filtered_data.loc[filtered_data['Feedback_points'].idxmax(), 'Hospital_name']

    # Get other top recommendations
    other_recommendations = filtered_data.sort_values(by='Feedback_points', ascending=False)['Hospital_name'].tolist()[1:3]

    # Decode hospital names
    recommended_hospital = label_encoders['Hospital_name'].inverse_transform([recommended_hospital])[0]
    other_recommendations = label_encoders['Hospital_name'].inverse_transform(other_recommendations)

    return recommended_hospital, other_recommendations

# Flask route for recommendations
# @app.route('/recommend', methods=['POST'])
def recommend():
    city = request.form['city']
    organ_type = request.form['organ_type']
    recommended_hospital_name, other_recommendations = recommend_hospital(city, organ_type)
    return render_template('result.html', recommended_hospital=recommended_hospital_name, other_recommendations=other_recommendations)
