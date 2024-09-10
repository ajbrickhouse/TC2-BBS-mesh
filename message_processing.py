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
from db_operations import add_bulletin, add_mail, delete_bulletin, delete_mail, get_db_connection, add_channel, insert_telemetry_data
from js8call_integration import handle_js8call_command, handle_js8call_steps, handle_group_message_selection
from utils import get_user_state, get_node_short_name, get_node_id_from_num, send_message

main_menu_handlers = {
    "q": handle_quick_help_command,
    "b": lambda sender_id, interface: handle_help_command(sender_id, interface, 'bbs'),
    "u": lambda sender_id, interface: handle_help_command(sender_id, interface, 'utilities'),
    "x": handle_help_command
}

bbs_menu_handlers = {
    "m": handle_mail_command,
    "b": handle_bulletin_command,
    "c": handle_channel_directory_command,
    "j": handle_js8call_command,
    "x": handle_help_command
}


utilities_menu_handlers = {
    "s": handle_stats_command,
    "f": handle_fortune_command,
    "w": handle_wall_of_shame_command,
    "x": handle_help_command
}


bulletin_menu_handlers = {
    "g": lambda sender_id, interface: handle_bb_steps(sender_id, '0', 1, {'board': 'General'}, interface, None),
    "i": lambda sender_id, interface: handle_bb_steps(sender_id, '1', 1, {'board': 'Info'}, interface, None),
    "n": lambda sender_id, interface: handle_bb_steps(sender_id, '2', 1, {'board': 'News'}, interface, None),
    "u": lambda sender_id, interface: handle_bb_steps(sender_id, '3', 1, {'board': 'Urgent'}, interface, None),
    "x": handle_help_command
}


board_action_handlers = {
    "r": lambda sender_id, interface, state: handle_bb_steps(sender_id, 'r', 2, state, interface, None),
    "p": lambda sender_id, interface, state: handle_bb_steps(sender_id, 'p', 2, state, interface, None),
    "x": handle_help_command
}

def process_message(sender_id, message, interface, is_sync_message=False):
    state = get_user_state(sender_id)
    message_lower = message.lower().strip()
    bbs_nodes = interface.bbs_nodes

    # Handle repeated characters for single character commands using a prefix
    if len(message_lower) == 2 and message_lower[1] == 'x':
        message_lower = message_lower[0]

    if is_sync_message:
        if message.startswith("BULLETIN|"):
            parts = message.split("|")
            board, sender_short_name, subject, content, unique_id = parts[1], parts[2], parts[3], parts[4], parts[5]
            add_bulletin(board, sender_short_name, subject, content, [], interface, unique_id=unique_id)

            if board.lower() == "urgent":
                notification_message = f"💥NEW URGENT BULLETIN💥\nFrom: {sender_short_name}\nTitle: {subject}"
                send_message(notification_message, BROADCAST_NUM, interface)
        elif message.startswith("MAIL|"):
            parts = message.split("|")
            sender_id, sender_short_name, recipient_id, subject, content, unique_id = parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
            add_mail(sender_id, sender_short_name, recipient_id, subject, content, [], interface, unique_id=unique_id)
        elif message.startswith("DELETE_BULLETIN|"):
            unique_id = message.split("|")[1]
            delete_bulletin(unique_id, [], interface)
        elif message.startswith("DELETE_MAIL|"):
            unique_id = message.split("|")[1]
            logging.info(f"Processing delete mail with unique_id: {unique_id}")
            recipient_id = get_recipient_id_by_mail(unique_id)
            delete_mail(unique_id, recipient_id, [], interface)
        elif message.startswith("CHANNEL|"):
            parts = message.split("|")
            channel_name, channel_url = parts[1], parts[2]
            add_channel(channel_name, channel_url)
    else:
        if message_lower.startswith("sm,,"):
            handle_send_mail_command(sender_id, message_lower, interface, bbs_nodes)
        elif message_lower.startswith("cm"):
            handle_check_mail_command(sender_id, interface)
        elif message_lower.startswith("pb,,"):
            handle_post_bulletin_command(sender_id, message_lower, interface, bbs_nodes)
        elif message_lower.startswith("cb,,"):
            handle_check_bulletin_command(sender_id, message_lower, interface)
        elif message_lower.startswith("chp,,"):
            handle_post_channel_command(sender_id, message_lower, interface)
        elif message_lower.startswith("chl"):
            handle_list_channels_command(sender_id, interface)
        else:
            if state and state['command'] == 'MENU':
                menu_name = state['menu']
                if menu_name == 'bbs':
                    handlers = bbs_menu_handlers
                elif menu_name == 'utilities':
                    handlers = utilities_menu_handlers
                else:
                    handlers = main_menu_handlers
            elif state and state['command'] == 'BULLETIN_MENU':
                handlers = bulletin_menu_handlers
            elif state and state['command'] == 'BULLETIN_ACTION':
                handlers = board_action_handlers
            elif state and state['command'] == 'JS8CALL_MENU':
                handle_js8call_steps(sender_id, message, state['step'], interface, state)
                return
            elif state and state['command'] == 'GROUP_MESSAGES':
                handle_group_message_selection(sender_id, message, state['step'], state, interface)
                return
            else:
                handlers = main_menu_handlers

            if message_lower == 'x':
                # Reset to main menu state
                handle_help_command(sender_id, interface)
                return

            if message_lower in handlers:
                if state and state['command'] in ['BULLETIN_ACTION', 'BULLETIN_READ', 'BULLETIN_POST', 'BULLETIN_POST_CONTENT']:
                    handlers[message_lower](sender_id, interface, state)
                else:
                    handlers[message_lower](sender_id, interface)
            elif state:
                command = state['command']
                step = state['step']

                if command == 'MAIL':
                    handle_mail_steps(sender_id, message, step, state, interface, bbs_nodes)
                elif command == 'BULLETIN':
                    handle_bb_steps(sender_id, message, step, state, interface, bbs_nodes)
                elif command == 'STATS':
                    handle_stats_steps(sender_id, message, step, interface)
                elif command == 'CHANNEL_DIRECTORY':
                    handle_channel_directory_steps(sender_id, message, step, state, interface)
                elif command == 'CHECK_MAIL':
                    if step == 1:
                        handle_read_mail_command(sender_id, message, state, interface)
                    elif step == 2:
                        handle_delete_mail_confirmation(sender_id, message, state, interface, bbs_nodes)
                elif command == 'CHECK_BULLETIN':
                    if step == 1:
                        handle_read_bulletin_command(sender_id, message, state, interface)
                elif command == 'CHECK_CHANNEL':
                    if step == 1:
                        handle_read_channel_command(sender_id, message, state, interface)
                elif command == 'LIST_CHANNELS':
                    if step == 1:
                        handle_read_channel_command(sender_id, message, state, interface)
                elif command == 'BULLETIN_POST':
                    handle_bb_steps(sender_id, message, 4, state, interface, bbs_nodes)
                elif command == 'BULLETIN_POST_CONTENT':
                    handle_bb_steps(sender_id, message, 5, state, interface, bbs_nodes)
                elif command == 'BULLETIN_READ':
                    handle_bb_steps(sender_id, message, 3, state, interface, bbs_nodes)
                elif command == 'JS8CALL_MENU':
                    handle_js8call_steps(sender_id, message, step, interface, state)
                elif command == 'GROUP_MESSAGES':
                    handle_group_message_selection(sender_id, message, step, state, interface)
                else:
                    handle_help_command(sender_id, interface)
            else:
                handle_help_command(sender_id, interface)


def on_receive(packet, interface):
    # logging.info(f"Received packet \n\n{packet}\n\n --------------------------------------------------")
    try:
        # Use .get() to avoid KeyError if 'decoded' does not exist
        decoded_packet = packet.get('decoded', {})
        if decoded_packet:
            portnum = decoded_packet.get('portnum')
            logging.info(f"-------------- {portnum}")
            sender_node_id = packet.get('fromId')
            to_node_id = packet.get('toId')
            sender_short_name = get_node_short_name(sender_node_id, interface)

            # Handle TEXT_MESSAGE_APP
            if portnum == 'TEXT_MESSAGE_APP':
                message_bytes = decoded_packet.get('payload')
                if message_bytes:
                    message_string = message_bytes.decode('utf-8')
                sender_id = packet.get('fromId')
                to_id = packet.get('toId')
                channel = packet.get('channel', 0)

                receiver_short_name = get_node_short_name(to_id, interface) if to_id and to_id[0] == '!' else f"Channel {channel}"

                logging.info(f"Received message from '{sender_short_name}' to '{receiver_short_name}': {message_string}")

            # Handle TELEMETRY_APP
            elif portnum == 'TELEMETRY_APP':
                telemetry_data = decoded_packet.get('telemetry', {})
                temp = telemetry_data.get('environmentMetrics', {}).get('temperature')
                humidity = telemetry_data.get('environmentMetrics', {}).get('relativeHumidity')
                pressure = telemetry_data.get('environmentMetrics', {}).get('barometricPressure')
                battery = telemetry_data.get('deviceMetrics', {}).get('batteryLevel')
                voltage = telemetry_data.get('deviceMetrics', {}).get('voltage')
                uptime = telemetry_data.get('deviceMetrics', {}).get('uptimeSeconds')

                logging.info(f"Telemetry from '{sender_short_name}' - Temp: {temp}°C, Humidity: {humidity}%, Pressure: {pressure} hPa, "
                             f"Battery: {battery}%, Voltage: {voltage}V, Uptime: {uptime}s")

                # Insert telemetry data into the database
                insert_telemetry_data(sender_node_id=sender_node_id, sender_short_name=sender_short_name, to_node_id=to_node_id,
                                      temperature=temp, humidity=humidity, pressure=pressure,
                                      battery_level=battery, voltage=voltage, uptime_seconds=uptime)

            # Handle POSITION_APP
            elif portnum == 'POSITION_APP':
                position_data = decoded_packet.get('position', {})
                latitude = position_data.get('latitude')
                longitude = position_data.get('longitude')
                altitude = position_data.get('altitude')
                sats_in_view = position_data.get('satsInView')

                logging.info(f"Position from '{sender_short_name}' - Lat: {latitude}, Lon: {longitude}, Alt: {altitude}m, Sats in View: {sats_in_view}")

                # Insert position data into the database
                insert_telemetry_data(sender_node_id=sender_node_id, sender_short_name=sender_short_name, to_node_id=to_node_id,
                                      latitude=latitude, longitude=longitude, altitude=altitude, sats_in_view=sats_in_view)


            # Handle NEIGHBORINFO_APP
            elif portnum == 'NEIGHBORINFO_APP':
                neighbor_info = decoded_packet.get('neighborinfo', {})
                node_id = neighbor_info.get('nodeId')
                neighbors = neighbor_info.get('neighbors', [])
                logging.info(f"Neighbor info from '{sender_short_name}' (Node {node_id}): {[n.get('nodeId') for n in neighbors]}")

                for neighbor in neighbors:
                    neighbor_id = neighbor.get('nodeId')
                    snr = neighbor.get('snr')
                    logging.info(f"Neighbor {neighbor_id} of '{sender_short_name}' with SNR: {snr}")

                    # Insert neighbor info into the database
                    insert_telemetry_data(sender_node_id=sender_node_id, sender_short_name=sender_short_name, to_node_id=to_node_id,
                                          neighbor_node_id=neighbor_id, snr=snr)

            else:
                logging.warning(f"Unhandled portnum '{portnum}' from '{sender_short_name}'")
                
    except Exception as e:
        logging.error(f"Error processing packet: {e}")


    except KeyError as e:
        logging.error(f"Error processing packet from '{sender_short_name}': {e}")


def get_recipient_id_by_mail(unique_id):
    # Fix for Mail Delete sync issue
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT recipient FROM mail WHERE unique_id = ?", (unique_id,))
    result = c.fetchone()
    if result:
        return result[0]
    return None
