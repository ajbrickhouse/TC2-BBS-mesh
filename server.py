import time
import meshtastic
import meshtastic.tcp_interface
from pubsub import pub
from message_processing import on_receive
from db_operations import initialize_database, process_and_insert_telemetry_data, get_db_connection
import logging
from config_init import initialize_config, get_interface, init_cli_parser, merge_config
from utils import display_banner

# General logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    args = init_cli_parser()
    config_file = None
    if args.config is not None:
        config_file = args.config
    system_config = initialize_config(config_file)

    merge_config(system_config, args)

    interface = get_interface(system_config)

    initialize_database()

    # Start the database connection here so we can close it on KeyboardInterrupt
    conn = get_db_connection()

    # Prime the database with data contained in the interface
    process_and_insert_telemetry_data(conn, interface)

    display_banner()
    logging.info(f"Testbench Mesh Logger is running on {system_config['interface_type']} interface...")

    def receive_packet(packet, interface):
        on_receive(conn, packet, interface)

    pub.subscribe(receive_packet, system_config['mqtt_topic'])

    try:
        while True:
            time.sleep(1)
            try:
                interface.sendHeartbeat()  # Send heartbeat as usual
            except BrokenPipeError:
                logging.error("BrokenPipeError during heartbeat. Reconnecting...")
                interface._reconnect()  # Reconnect on broken pipe

    except KeyboardInterrupt:
        conn.close()
        logging.info("Shutting down the server and DB...")
        interface.close()

if __name__ == "__main__":
    main()