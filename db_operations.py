import logging
import time
import sqlite3
import threading
import uuid
from datetime import datetime
import json

from meshtastic import BROADCAST_NUM

thread_local = threading.local()

def get_db_connection():
    if not hasattr(thread_local, 'connection'):
        thread_local.connection = sqlite3.connect('bulletins.db', check_same_thread=False)
    return thread_local.connection

def initialize_database():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS TelemetryData (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_node_id TEXT NOT NULL,
                to_node_id TEXT,
                sender_short_name TEXT,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                battery_level REAL,
                voltage REAL,
                uptime_seconds REAL,
                latitude REAL,
                longitude REAL,
                altitude REAL,
                sats_in_view INTEGER,
                neighbor_node_id TEXT,
                snr REAL,
                hardware_model TEXT,
                mac_address TEXT,
                sender_long_name TEXT,
                role TEXT
            );''')

    conn.commit()

    print("Database schema initialized.")



def insert_telemetry_data(sender_node_id, sender_short_name=None, to_node_id=None, temperature=None, humidity=None,
                          pressure=None, battery_level=None, voltage=None, uptime_seconds=None,
                          latitude=None, longitude=None, altitude=None, sats_in_view=None,
                          neighbor_node_id=None, snr=None, hardware_model=None, mac_address=None, sender_long_name=None, role=None):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('''
                INSERT INTO TelemetryData (
                    sender_node_id, sender_short_name, to_node_id, temperature, humidity, pressure, 
                    battery_level, voltage, uptime_seconds, latitude, longitude, altitude, 
                    sats_in_view, neighbor_node_id, snr, hardware_model, mac_address, sender_long_name, role
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sender_node_id, sender_short_name, to_node_id, temperature, humidity, pressure, 
                battery_level, voltage, uptime_seconds, latitude, longitude, altitude, 
                sats_in_view, neighbor_node_id, snr, hardware_model, mac_address, sender_long_name, role
            ))
    except sqlite3.Error as e:
        logging.error(f"Error inserting telemetry data: {e}")
    finally:
        # Close the connection only if it's not shared across threads
        pass  # Remove conn.close() to avoid prematurely closing in a multi-threaded environment

def process_and_insert_telemetry_data(interface):
    # Iterate over each entry in the data
    data_string = interface.showInfo().split('Nodes in mesh: ')[1]
    data = json.loads(data_string)
    for node_id, node_data in data.items():
        # Extract relevant fields
        user_data = node_data.get('user', {})
        position_data = node_data.get('position', {})
        device_metrics = node_data.get('deviceMetrics', {})
        
        # Use the provided insert_telemetry_data function to insert each record
        insert_telemetry_data(
            sender_node_id=user_data.get('id'),
            sender_short_name=user_data.get('shortName'),
            sender_long_name=user_data.get('longName'),
            mac_address=user_data.get('macaddr'),
            hardware_model=user_data.get('hwModel'),
            latitude=position_data.get('latitude'),
            longitude=position_data.get('longitude'),
            altitude=position_data.get('altitude'),
            sats_in_view=position_data.get('sats_in_view'),  # This key may or may not exist
            battery_level=device_metrics.get('batteryLevel'),
            voltage=device_metrics.get('voltage'),
            uptime_seconds=device_metrics.get('uptimeSeconds'),
            snr=node_data.get('snr'),
            role=user_data.get('role')  # This key may or may not exist
        )