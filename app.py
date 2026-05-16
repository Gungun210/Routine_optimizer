import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'data/routines.csv'

# Ensure data directory and file exist
os.makedirs('data', exist_ok=True)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        'Date', 'Start Time', 'End Time', 'Activity', 'Category', 
        'Productivity', 'Energy', 'Duration (Hours)'
    ])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def calculate_duration(start_time, end_time):
    fmt = '%H:%M'
    t1 = datetime.strptime(start_time, fmt)
    t2 = datetime.strptime(end_time, fmt)
    duration = (t2 - t1).total_seconds() / 3600.0
    if duration < 0:
        duration += 24.0 # Handle cross-midnight
    return round(duration, 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        activity = request.form['activity']
        category = request.form['category']
        productivity = int(request.form['productivity'])
        energy = int(request.form['energy'])
        
        duration = calculate_duration(start_time, end_time)
        
        new_row = {
            'Date': date,
            'Start Time': start_time,
            'End Time': end_time,
            'Activity': activity,
            'Category': category,
            'Productivity': productivity,
            'Energy': energy,
            'Duration (Hours)': duration
        }
        
        df = load_data()
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        
        return redirect(url_for('index'))
    
    df = load_data()
    # Sort by Date descending for display
    if not df.empty:
        df = df.sort_values(by=['Date', 'Start Time'], ascending=[False, False])
    records = df.to_dict('records')
    return render_template('index.html', records=records)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_dashboard_data():
    df = load_data()
    if df.empty:
        return jsonify({})

    # Process data for charts
    
    # Time spent per category
    category_data = df.groupby('Category')['Duration (Hours)'].sum().to_dict()
    
    # Time spent per activity (top 5)
    activity_data = df.groupby('Activity')['Duration (Hours)'].sum().sort_values(ascending=False).head(5).to_dict()
    
    # Average productivity and energy
    avg_productivity = round(df['Productivity'].mean(), 2)
    avg_energy = round(df['Energy'].mean(), 2)
    
    # Productivity vs Time (group by start time hour)
    df['Hour'] = pd.to_datetime(df['Start Time'], format='%H:%M').dt.hour
    prod_by_hour = df.groupby('Hour')['Productivity'].mean().round(2).to_dict()
    
    # Generate Insights
    insights = []
    
    if prod_by_hour:
        best_hour = max(prod_by_hour, key=prod_by_hour.get)
        insights.append(f"Most productive time of the day starts around {best_hour}:00.")
        
    waste_time = category_data.get('Waste', 0)
    total_time = df['Duration (Hours)'].sum()
    if total_time > 0 and (waste_time / total_time) > 0.2:
        insights.append(f"You spend a significant portion ({round((waste_time/total_time)*100)}%) of your tracked time on 'Waste' activities. Consider minimizing them.")
    
    if avg_energy < 3:
        insights.append("Your average energy levels are low. Try incorporating more breaks or adjusting your sleep schedule.")
    elif avg_productivity >= 4:
        insights.append("Great job! Your average productivity is high. Keep up the good work.")
        
    return jsonify({
        'category_data': category_data,
        'activity_data': activity_data,
        'prod_by_hour': prod_by_hour,
        'stats': {
            'avg_productivity': avg_productivity,
            'avg_energy': avg_energy,
            'total_hours_tracked': round(total_time, 2)
        },
        'insights': insights
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
