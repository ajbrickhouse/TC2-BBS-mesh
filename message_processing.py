from utils import get_node_short_name, get_node_id_from_num, send_message, log_text_to_file, get_node_info, get_node_names, format_real_number
from db_operations import insert_telemetry_data
import logging
import time
from datetime import datetime, timezone
import pytz
import tzlocal

def on_receive(conn, logger, system_config, packet, interface):
    # try:
    # Use .get() to avoid KeyError if 'decoded' does not exist
    decoded_packet = packet.get('decoded', {})
    if decoded_packet:
        portnum = decoded_packet.get('portnum')
        sender_node_id = packet.get('fromId')
        to_node_id = packet.get('toId')
        sender_short_name, sender_long_name = get_node_names(interface, sender_node_id)
        to_short_name, to_long_name = get_node_names(interface, to_node_id)
        rx_time = datetime.now(tzlocal.get_localzone()).strftime('%Y-%m-%d %H:%M:%S')
        logger.debug(f"rxPacket: {sender_short_name} to {to_short_name} at {rx_time}")

        logger.info(f"-------------------------------------------------------- {portnum} ")
        
        # Handle TEXT_MESSAGE_APP
        if portnum == 'TEXT_MESSAGE_APP':
            try:
                log_text_to_file(packet, './logs/TEXT_MESSAGE_APP.txt')
                message = decoded_packet.get('text')
                snr = format_real_number(packet.get('rxSnr'))
                
                logger.info(f"{sender_long_name} ({sender_short_name}) sent a message to {to_long_name} ({to_short_name})")
                logger.info(f"--- Message: \n\n{message}\n")
                logger.info(f"--------------------------------------------------------")

                insert_telemetry_data(conn, logger, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name, snr=snr)

            except Exception as e:
                logger.error(f"Error processing TEXT_MESSAGE_APP: {e}")

        # Handle TELEMETRY_APP
        elif portnum == 'TELEMETRY_APP':
            try:
                # log_text_to_file(packet, './logs/TELEMETRY_APP.txt')
                telemetry_data = decoded_packet.get('telemetry', {})
                temperature = format_real_number(telemetry_data.get('environmentMetrics', {}).get('temperature'))
                humidity = format_real_number(telemetry_data.get('environmentMetrics', {}).get('relativeHumidity'))
                pressure = format_real_number(telemetry_data.get('environmentMetrics', {}).get('barometricPressure'))
                battery = format_real_number(telemetry_data.get('deviceMetrics', {}).get('batteryLevel'))
                voltage = format_real_number(telemetry_data.get('deviceMetrics', {}).get('voltage'))
                uptime = format_real_number(telemetry_data.get('deviceMetrics', {}).get('uptimeSeconds'))

                insert_telemetry_data(conn, logger, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name,
                                         temperature=temperature, humidity=humidity, pressure=pressure, battery_level=battery, voltage=voltage, uptime_seconds=uptime)

            except Exception as e:
                logger.error(f"Error processing TELEMETRY_APP: {e}")

        # # Handle POSITION_APP
        elif portnum == 'POSITION_APP':
            try:
                # log_text_to_file(packet, './logs/POSITION_APP.txt')
                location_data = decoded_packet.get('position', {})
                latitude = location_data.get('latitude')
                longitude = location_data.get('longitude')
                altitude = format_real_number(location_data.get('altitude'))

                insert_telemetry_data(conn, logger, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name, 
                                        latitude=latitude, longitude=longitude, altitude=altitude)
            except Exception as e:
                logger.error(f"Error processing POSITION_APP: {e}")

        # Handle NEIGHBORINFO_APP
        elif portnum == 'NEIGHBORINFO_APP':
            try:
                log_text_to_file(packet, './logs/NEIGHBORINFO_APP.txt')
            except Exception as e:
                logger.info(f"Error processing NEIGHBORINFO_APP: {e}")

        # Handle WAYPOINT_APP
        elif portnum == 'WAYPOINT_APP':
            try:
                log_text_to_file(packet, './logs/WAYPOINT_APP.txt')
            except Exception as e:
                logger.info(f"Error processing WAYPOINT_APP: {e}")

        # Handle ROUTING_APP
        elif portnum == 'ROUTING_APP':
            try:
                log_text_to_file(packet, './logs/ROUTING_APP.txt')
            except Exception as e:
                logger.info(f"Error processing ROUTING_APP: {e}")

        # Handle NODEINFO_APP
        elif portnum == 'NODEINFO_APP':
            try:
                log_text_to_file(packet, './logs/NODEINFO_APP.txt')
                user_data = decoded_packet.get('user', {})
                mac_address = user_data.get('macaddr')
                hardware_model = user_data.get('hwModel')
                role = user_data.get('role')

                insert_telemetry_data(conn, logger, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name,
                                        mac_address=mac_address, hardware_model=hardware_model, role=role)

            except Exception as e:
                logger.error(f"Error processing NODEINFO_APP: {e}")
                    
    # except Exception as e:
    #     logger.info(f"General error processing packet: {e}")