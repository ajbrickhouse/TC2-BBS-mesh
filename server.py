import time
import meshtastic
import meshtastic.tcp_interface
from pubsub import pub
from message_processing import on_receive
from db_operations import initialize_database, process_and_insert_telemetry_data, get_db_connection, sync_data_to_server
import logging
from config_init import initialize_config, get_interface, init_cli_parser, merge_config
from utils import display_banner
from pubsub import pub
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE,SIG_DFL) 

# General logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(message)s',
    datefmt='%H:%M:%S'
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
    # sync with the online server
    sync_data_to_server(conn, 'https://testbench.cc/meshmap2/sync')

    display_banner()
    logging.info(f"Testbench Mesh Logger is running on {system_config['interface_type']} interface...")

    def receive_packet(packet, interface):
        on_receive(conn, system_config, packet, interface)

    def onConnection(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
        # defaults to broadcast, specify a destination ID if you wish
        # interface.sendText("hello mesh")
        pass

    pub.subscribe(receive_packet, system_config['mqtt_topic'])
    pub.subscribe(onConnection, "meshtastic.connection.established")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        sync_data_to_server(conn, 'https://testbench.cc/meshmap2/sync')
        conn.close()
        logging.info("Shutting down the server and DB...")
        interface.close()

if __name__ == "__main__":
    main()