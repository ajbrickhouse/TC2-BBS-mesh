import sqlite3

# Connect to your SQLite database (replace 'your_database.db' with your actual database file)
conn = sqlite3.connect('bulletins.db')
c = conn.cursor()


# Data to update (based on the provided example)
data = [
    {"node_id": "!7a6c47a4", "name": "The Ivan Device", "short_name": "🥷"},
    {"node_id": "!3369207c", "name": "Meshtastic 207c", "short_name": "207c"},
    {"node_id": "!7c2f6bbc", "name": "South Treasure Valley relay @IK", "short_name": "📡"},
    {"node_id": "!13227898", "name": "Star City Radio", "short_name": "STAR"},
    {"node_id": "!84889bc4", "name": "Base 1 Long 5689", "short_name": "B1L"},
    {"node_id": "!99a34093", "name": "Ravenhurst", "short_name": "Rvnh"},
    {"node_id": "!938bebec", "name": "KG7KVI-01", "short_name": "KVI1"}
]

# Update records in the TelemetryData table where sender_node_id matches the node_id from the data list
for item in data:
    c.execute('''
        UPDATE TelemetryData
        SET sender_short_name = ?,
            sender_long_name = ?
        WHERE sender_node_id = ?;
    ''', (item["short_name"], item["name"], item["node_id"]))

# Commit changes and close the connection
conn.commit()
conn.close()

print("TelemetryData updated successfully.")