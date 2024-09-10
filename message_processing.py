from utils import get_node_short_name, get_node_id_from_num, send_message, log_text_to_file, get_node_info, get_node_names
import logging
import time

def on_receive(packet, interface):
    # try:
    # Use .get() to avoid KeyError if 'decoded' does not exist
    
    decoded_packet = packet.get('decoded', {})
    if decoded_packet:
        portnum = decoded_packet.get('portnum')
        logging.info(f"-------------- {portnum}")
        # Handle TEXT_MESSAGE_APP
        # if portnum == 'TEXT_MESSAGE_APP':
        #     try:
        #         pass
        #     except Exception as e:
        #         logging.error(f"Error processing TEXT_MESSAGE_APP: {e}")

        # # Handle TELEMETRY_APP
        # elif portnum == 'TELEMETRY_APP':
        #     try:
        #         pass
        #     except Exception as e:
        #         logging.error(f"Error processing TELEMETRY_APP: {e}")

        # # Handle POSITION_APP
        # elif portnum == 'POSITION_APP':
        #     try:
        #         pass
        #     except Exception as e:
        #         logging.error(f"Error processing POSITION_APP: {e}")

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

        # # Handle NODEINFO_APP
        # elif portnum == 'NODEINFO_APP':
        #     try:
        #         pass
        #     except Exception as e:
        #         logging.error(f"Error processing NODEINFO_APP: {e}")
                    
    # except Exception as e:
    #     logging.error(f"General error processing packet: {e}")