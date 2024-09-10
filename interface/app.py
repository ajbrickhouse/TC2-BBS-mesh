import sqlite3
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Route to serve the HTML template
@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html is in the 'templates' folder

# Route to provide telemetry data as JSON
@app.route('/get-telemetry-data', methods=['GET'])
def get_telemetry_data():
    conn = sqlite3.connect('../bulletins.db')  # Replace with your actual database path
    cursor = conn.cursor()

    # Query to get the most recent record per sender_node_id
    query = '''
        SELECT sender_node_id, sender_short_name, timestamp, temperature, humidity,
               pressure, battery_level, voltage, latitude, longitude, altitude, sats_in_view
        FROM TelemetryData
        WHERE id IN (
            SELECT MAX(id) FROM TelemetryData
            GROUP BY sender_node_id
        )
        AND latitude IS NOT NULL
        AND longitude IS NOT NULL
        AND latitude != 0
        AND longitude != 0;
    '''
    cursor.execute(query)
    data = cursor.fetchall()

    telemetry_data = []
    for row in data:
        telemetry_data.append({
            "sender_node_id": row[0],
            "sender_short_name": row[1],
            "timestamp": row[2],
            "temperature": row[3],
            "humidity": row[4],
            "pressure": row[5],
            "battery_level": row[6],
            "voltage": row[7],
            "latitude": row[8],
            "longitude": row[9],
            "altitude": row[10],
            "sats_in_view": row[11]
        })

    conn.close()
    return jsonify(telemetry_data)

if __name__ == '__main__':
    app.run(debug=True)