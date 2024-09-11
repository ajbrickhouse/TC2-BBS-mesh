import logging

from meshtastic import BROADCAST_NUM

from command_handlers import (
    handle_mail_command, handle_bulletin_command, handle_help_command, handle_stats_command, handle_fortune_command,
    handle_bb_steps, handle_mail_steps, handle_stats_steps, handle_wall_of_shame_command,
    handle_channel_directory_command, handle_channel_directory_steps, handle_send_mail_command,
    handle_read_mail_command, handle_check_mail_command, handle_delete_mail_confirmation, handle_post_bulletin_command,
    handle_check_bulletin_command, handle_read_bulletin_command, handle_read_channel_command,
    handle_post_channel_command, handle_list_channels_command, handle_quick_help_command
)
from db_operations import (
    add_bulletin, add_mail, delete_bulletin, delete_mail, get_db_connection, add_channel, insert_telemetry_data, add_waypoint,
    add_or_update_name_lookup, get_name_by_node_id
)
from js8call_integration import handle_js8call_command, handle_js8call_steps, handle_group_message_selection
from utils import get_user_state, get_node_short_name, get_node_id_from_num, send_message, log_text_to_file, get_node_info, get_node_names


def on_receive(packet, interface):
    # try:
    # Use .get() to avoid KeyError if 'decoded' does not exist
    decoded_packet = packet.get('decoded', {})
    if decoded_packet:
        portnum = decoded_packet.get('portnum')
        logging.info(f"-------------- {portnum}")
        sender_node_id = packet.get('fromId')
        to_node_id = packet.get('toId')
        sender_short_name, _ = get_name_by_node_id(sender_node_id)

        if sender_short_name is None:
            sender_short_name = get_node_short_name(sender_node_id, interface)
        
        logging.info(f"\n\nINFO'{interface.showInfo()}'\n\n")

        # Handle TEXT_MESSAGE_APP
        if portnum == 'TEXT_MESSAGE_APP':
            try:
                log_text_to_file(packet, './logs/TEXT_MESSAGE_APP.txt')
                message_bytes = decoded_packet.get('payload')
                if message_bytes:
                    message_string = message_bytes.decode('utf-8')
                sender_id = packet.get('fromId')
                to_id = packet.get('toId')
                channel = packet.get('channel', 0)

                receiver_short_name = get_node_short_name(to_id, interface) if to_id and to_id[0] == '!' else f"Channel {channel}"
                logging.info(f"Received message from '{sender_short_name}' to '{receiver_short_name}': {message_string}")
            except Exception as e:
                logging.error(f"Error processing TEXT_MESSAGE_APP: {e}")

        # Handle TELEMETRY_APP
        elif portnum == 'TELEMETRY_APP':
            try:
                telemetry_data = decoded_packet.get('telemetry', {})
                temp = telemetry_data.get('environmentMetrics', {}).get('temperature')
                humidity = telemetry_data.get('environmentMetrics', {}).get('relativeHumidity')
                pressure = telemetry_data.get('environmentMetrics', {}).get('barometricPressure')
                battery = telemetry_data.get('deviceMetrics', {}).get('batteryLevel')
                voltage = telemetry_data.get('deviceMetrics', {}).get('voltage')
                uptime = telemetry_data.get('deviceMetrics', {}).get('uptimeSeconds')

                sN, lN = get_node_names(interface, sender_node_id)

                # Initialize sender_long_name and sender_short_name with default values
                sender_short_name = sN if sN else sender_short_name
                sender_long_name = lN if lN else "Unknown"

                insert_telemetry_data(sender_node_id=sender_node_id, sender_short_name=sender_short_name, to_node_id=to_node_id,
                                        temperature=temp, humidity=humidity, pressure=pressure,
                                        battery_level=battery, voltage=voltage, uptime_seconds=uptime, sender_long_name=sender_long_name)
            except Exception as e:
                logging.error(f"Error processing TELEMETRY_APP: {e}")

        # Handle POSITION_APP
        elif portnum == 'POSITION_APP':
            try:
                log_text_to_file(packet, './logs/POSITION_APP.txt')
                position_data = decoded_packet.get('position', {})
                latitude = position_data.get('latitude')
                longitude = position_data.get('longitude')
                altitude = position_data.get('altitude')
                sats_in_view = position_data.get('satsInView')

                sN, lN = get_node_names(interface, sender_node_id)

                # Initialize sender_long_name and sender_short_name with default values
                sender_short_name = sN if sN else sender_short_name
                sender_long_name = lN if lN else "Unknown"

                logging.info(f"Position from '{sender_long_name} ({sender_short_name})' - Lat: {latitude}, Lon: {longitude}, Alt: {altitude}m, Sats in View: {sats_in_view}")

                # Inserting the telemetry data
                insert_telemetry_data(sender_node_id=sender_node_id, sender_short_name=sender_short_name, to_node_id=to_node_id, temperature=None, humidity=None,
                          pressure=None, battery_level=None, voltage=None, uptime_seconds=None,
                          latitude=None, longitude=None, altitude=None, sats_in_view=sats_in_view,
                          neighbor_node_id=None, snr=None, hardware_model=None, mac_address=None, sender_long_name=sender_long_name, role=None)

            except Exception as e:
                logging.error(f"Error processing POSITION_APP: {e}")

        # Handle NEIGHBORINFO_APP
        elif portnum == 'NEIGHBORINFO_APP':
            try:
                log_text_to_file(packet, './logs/NEIGHBORINFO_APP.txt')
                neighbor_info = decoded_packet.get('neighborinfo', {})
                node_id = neighbor_info.get('nodeId')
                neighbors = neighbor_info.get('neighbors', [])

                for neighbor in neighbors:
                    neighbor_id = neighbor.get('nodeId')
                    snr = neighbor.get('snr')
                    insert_telemetry_data(sender_node_id=sender_node_id, sender_short_name=sender_short_name, to_node_id=to_node_id,
                                            neighbor_node_id=neighbor_id, snr=snr)
            except Exception as e:
                logging.error(f"Error processing NEIGHBORINFO_APP: {e}")

        # Handle WAYPOINT_APP
        elif portnum == 'WAYPOINT_APP':
            try:
                log_text_to_file(packet, './logs/WAYPOINT_APP.txt')
                message_bytes = decoded_packet.get('payload')
                if message_bytes:
                    message_string = message_bytes.decode('utf-8')
                waypoint = decoded_packet.get('waypoint', {})
                name = waypoint.get('name')
                description = waypoint.get('description')
                latitude = waypoint.get('latitudeI')
                longitude = waypoint.get('longitudeI')
                expire = waypoint.get('expire')

                add_waypoint(sender_node_id, name, description, latitude, longitude, False, expire, message_string)
            except Exception as e:
                logging.error(f"Error processing WAYPOINT_APP: {e}")

        # Handle ROUTING_APP
        elif portnum == 'ROUTING_APP':
            try:
                log_text_to_file(packet, './logs/ROUTING_APP.txt')
                logging.info(f"Received ROUTING_APP packet from '{sender_short_name}'")
            except Exception as e:
                logging.error(f"Error processing ROUTING_APP: {e}")

        # Handle NODEINFO_APP
        elif portnum == 'NODEINFO_APP':
            try:
                log_text_to_file(packet, './logs/NODEINFO_APP.txt')
                node_info = decoded_packet.get('user', {})
                hw_model = node_info.get('hwModel')
                macaddr = node_info.get('macaddr')
                long_name = node_info.get('longName')
                short_name = node_info.get('shortName')
                sender_id = packet.get('fromId')
                to_id = packet.get('toId')
                role = node_info.get('role')

                logging.info(f"Received NODEINFO_APP packet from '{long_name}' ({short_name}), HW Model: {hw_model}, MAC: {macaddr}, Node ID: {node_info}")

                # insert_telemetry_data(sender_node_id=sender_node_id, sender_short_name=sender_short_name, to_node_id=to_node_id,
                #                       hardware_model=hw_model, mac_address=macaddr, long_name=long_name, short_name=short_name)
                insert_telemetry_data(sender_node_id=sender_id, sender_short_name=short_name, to_node_id=to_id, hardware_model=hw_model, mac_address=macaddr, sender_long_name=long_name, role=role)
                add_or_update_name_lookup(sender_id, short_name, long_name)

            except Exception as e:
                logging.error(f"Error processing NODEINFO_APP: {e}")
                    
    # except Exception as e:
    #     logging.error(f"General error processing packet: {e}")

def on_receive(packet, interface):
    # try:
    # Use .get() to avoid KeyError if 'decoded' does not exist
    decoded_packet = packet.get('decoded', {})
    if decoded_packet:
        portnum = decoded_packet.get('portnum')
        logging.info(f"-------------- {portnum}")
        # Handle TEXT_MESSAGE_APP
        if portnum == 'TEXT_MESSAGE_APP':
            try:
                pass
            except Exception as e:
                logging.error(f"Error processing TEXT_MESSAGE_APP: {e}")

        # Handle TELEMETRY_APP
        elif portnum == 'TELEMETRY_APP':
            try:
                pass
            except Exception as e:
                logging.error(f"Error processing TELEMETRY_APP: {e}")

        # Handle POSITION_APP
        elif portnum == 'POSITION_APP':
            try:
                pass
            except Exception as e:
                logging.error(f"Error processing POSITION_APP: {e}")

        # Handle NEIGHBORINFO_APP
        elif portnum == 'NEIGHBORINFO_APP':
            try:
                pass
            except Exception as e:
                logging.error(f"Error processing NEIGHBORINFO_APP: {e}")

        # Handle WAYPOINT_APP
        elif portnum == 'WAYPOINT_APP':
            try:
                pass
            except Exception as e:
                logging.error(f"Error processing WAYPOINT_APP: {e}")

        # Handle ROUTING_APP
        elif portnum == 'ROUTING_APP':
            try:
                pass
            except Exception as e:
                logging.error(f"Error processing ROUTING_APP: {e}")

        # Handle NODEINFO_APP
        elif portnum == 'NODEINFO_APP':
            try:
                pass
            except Exception as e:
                logging.error(f"Error processing NODEINFO_APP: {e}")
                    
    # except Exception as e:
    #     logging.error(f"General error processing packet: {e}")


def get_recipient_id_by_mail(unique_id):
    # Fix for Mail Delete sync issue
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT recipient FROM mail WHERE unique_id = ?", (unique_id,))
    result = c.fetchone()
    if result:
        return result[0]
    return None
