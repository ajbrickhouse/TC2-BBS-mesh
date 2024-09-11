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
    conn = sqlite3.connect('bulletins.db')  # Replace with your actual database path
    cursor = conn.cursor()

    # Query to get the most recent non-null values for each field per sender_node_id
    query = '''
        SELECT
            td.sender_node_id,
            MAX(td.sender_short_name) AS sender_short_name,
            MAX(td.timestamp) AS timestamp,
            (SELECT temperature FROM TelemetryData WHERE temperature IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS temperature,
            (SELECT humidity FROM TelemetryData WHERE humidity IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS humidity,
            (SELECT pressure FROM TelemetryData WHERE pressure IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS pressure,
            (SELECT battery_level FROM TelemetryData WHERE battery_level IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS battery_level,
            (SELECT voltage FROM TelemetryData WHERE voltage IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS voltage,
            (SELECT uptime_seconds FROM TelemetryData WHERE uptime_seconds IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS uptime_seconds,
            (SELECT latitude FROM TelemetryData WHERE latitude IS NOT NULL AND latitude != 0 AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS latitude,
            (SELECT longitude FROM TelemetryData WHERE longitude IS NOT NULL AND longitude != 0 AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS longitude,
            (SELECT altitude FROM TelemetryData WHERE altitude IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS altitude,
            (SELECT sats_in_view FROM TelemetryData WHERE sats_in_view IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS sats_in_view,
            (SELECT snr FROM TelemetryData WHERE snr IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS snr,
            (SELECT hardware_model FROM TelemetryData WHERE hardware_model IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS hardware_model,
            (SELECT sender_long_name FROM TelemetryData WHERE sender_long_name IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS sender_long_name,
            (SELECT role FROM TelemetryData WHERE role IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS role
        FROM TelemetryData td
        GROUP BY td.sender_node_id;
    '''
    
    cursor.execute(query)
    data = cursor.fetchall()

    telemetry_data = []
    for row in data:
        telemetry_data.append({
            "sender_node_id": row[0],
            "sender_short_name": row[1],  # Check if this value exists in your DB
            "timestamp": row[2],
            "temperature": row[3],
            "humidity": row[4],
            "pressure": row[5],
            "battery_level": row[6],
            "voltage": row[7],
            "uptime_seconds": row[8],
            "latitude": row[9],
            "longitude": row[10],
            "altitude": row[11],
            "sats_in_view": row[12],
            "snr": row[13],
            "hardware_model": row[14],
            "sender_long_name": row[15],
            "role": row[16]
        })

    # drop any rows without latitude
    telemetry_data = [row for row in telemetry_data if row['latitude'] is not None]

    # Change any null values to '---'
    for row in telemetry_data:
        for key, value in row.items():
            if value is None:
                row[key] = '---'

    # Sort telemetry_data by timestamp (assuming timestamps are in a sortable format like ISO 8601)
    telemetry_data = sorted(telemetry_data, key=lambda x: x['timestamp'], reverse=False)

    conn.close()
    return jsonify(telemetry_data)


if __name__ == '__main__':
    app.run(debug=True)