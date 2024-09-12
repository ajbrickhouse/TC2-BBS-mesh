from utils import get_node_short_name, get_node_id_from_num, send_message, log_text_to_file, get_node_info, get_node_names, format_real_number
from db_operations import insert_telemetry_data
import logging
import time
from datetime import datetime, timezone
import pytz
import tzlocal

def on_receive(conn, system_config, packet, interface):
    # try:
    # Use .get() to avoid KeyError if 'decoded' does not exist
    decoded_packet = packet.get('decoded', {})
    if decoded_packet:
        portnum = decoded_packet.get('portnum')
        sender_node_id = packet.get('fromId')
        to_node_id = packet.get('toId')
        sender_short_name, sender_long_name = get_node_names(interface, sender_node_id)
        to_short_name, to_long_name = get_node_names(interface, to_node_id)

        # handle time. If None, insert_text_message will use current time
        rx_time = None
        unix_timestamp = packet.get('rxTime')
        if unix_timestamp is not None:
            # rx_time = datetime.fromtimestamp(rx_time_value, tz=timezone.utc).astimezone(pytz.timezone(system_config['timezone']))
            rx_time = datetime.fromtimestamp(unix_timestamp,  tzlocal.get_localzone()).strftime('%Y-%m-%d %H:%M:%S')

        logging.info(f"-------------------------------------------------------- {portnum} ")
        
        # Handle TEXT_MESSAGE_APP
        if portnum == 'TEXT_MESSAGE_APP':
            try:
                message = decoded_packet.get('text')
                snr = format_real_number(packet.get('rxSnr'))
                
                logging.info(f"{sender_long_name} ({sender_short_name}) sent a message to {to_long_name} ({to_short_name})")
                logging.info(f"--- Message: \n\n{message}\n")
                logging.info(f"--------------------------------------------------------")

                insert_telemetry_data(conn, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name, snr=snr)

            except Exception as e:
                logging.error(f"Error processing TEXT_MESSAGE_APP: {e}")

        # Handle TELEMETRY_APP
        elif portnum == 'TELEMETRY_APP':
            try:
                log_text_to_file(packet, './logs/TELEMETRY_APP.txt')
                telemetry_data = decoded_packet.get('telemetry', {})
                temperature = format_real_number(telemetry_data.get('environmentMetrics', {}).get('temperature'))
                humidity = format_real_number(telemetry_data.get('environmentMetrics', {}).get('relativeHumidity'))
                pressure = format_real_number(telemetry_data.get('environmentMetrics', {}).get('barometricPressure'))
                battery = format_real_number(telemetry_data.get('deviceMetrics', {}).get('batteryLevel'))
                voltage = format_real_number(telemetry_data.get('deviceMetrics', {}).get('voltage'))
                uptime = format_real_number(telemetry_data.get('deviceMetrics', {}).get('uptimeSeconds'))

                insert_telemetry_data(conn, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name,
                                         temperature=temperature, humidity=humidity, pressure=pressure, battery_level=battery, voltage=voltage, uptime_seconds=uptime)

            except Exception as e:
                logging.error(f"Error processing TELEMETRY_APP: {e}")

        # # Handle POSITION_APP
        elif portnum == 'POSITION_APP':
            try:
                location_data = decoded_packet.get('position', {})
                latitude = location_data.get('latitude')
                longitude = location_data.get('longitude')
                altitude = format_real_number(location_data.get('altitude'))

                insert_telemetry_data(conn, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name, 
                                        latitude=latitude, longitude=longitude, altitude=altitude)
            except Exception as e:
                logging.error(f"Error processing POSITION_APP: {e}")

        # # Handle NEIGHBORINFO_APP
        # elif portnum == 'NEIGHBORINFO_APP':
        #     try:
        #         pass
        #     except Exception as e:
        #         logging.error(f"Error processing NEIGHBORINFO_APP: {e}")

        # # Handle WAYPOINT_APP
        # elif portnum == 'WAYPOINT_APP':
        #     try:
        #         pass
        #     except Exception as e:
        #         logging.error(f"Error processing WAYPOINT_APP: {e}")

        # # Handle ROUTING_APP
        # elif portnum == 'ROUTING_APP':
        #     try:
        #         pass
        #     except Exception as e:
        #         logging.error(f"Error processing ROUTING_APP: {e}")

        # Handle NODEINFO_APP
        elif portnum == 'NODEINFO_APP':
            try:
                user_data = decoded_packet.get('user', {})
                mac_address = user_data.get('macaddr')
                hardware_model = user_data.get('hwModel')

                insert_telemetry_data(conn, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name,
                                        mac_address=mac_address, hardware_model=hardware_model)

            except Exception as e:
                logging.error(f"Error processing NODEINFO_APP: {e}")
                    
    # except Exception as e:
    #     logging.error(f"General error processing packet: {e}")