from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the dataset
data = pd.read_csv('dataset1.csv')

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

# Function to recommend hospital based on feedback points
def recommend_hospital(city, organ_type):
    # Preprocess user input by converting to lowercase
    city = city.lower()
    organ_type = organ_type.lower()

    # Split rows with multiple organ types into separate rows
    data_split = split_rows(data)

    # Filter data for the given city and organ type
    filtered_data = data_split[(data_split['City'].str.lower() == city) & (data_split['Organ_type'].str.lower() == organ_type.strip())]

    # Find the hospital with the maximum feedback points
    recommended_hospital = filtered_data.loc[filtered_data['Feedback_points'].idxmax(), 'Hospital_name']

    # Get other top recommendations
    other_recommendations = filtered_data.sort_values(by='Feedback_points', ascending=False)['Hospital_name'].tolist()[1:3]

    return recommended_hospital, other_recommendations

@app.route('/hospital')
def hospital():
    return render_template('hospital.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    city = request.form['city']
    organ_type = request.form['organ_type']
    recommended_hospital_name, other_recommendations = recommend_hospital(city, organ_type)
    return render_template('result.html', recommended_hospital=recommended_hospital_name, other_recommendations=other_recommendations)

if __name__ == '__main__':
    app.run(debug=True)
