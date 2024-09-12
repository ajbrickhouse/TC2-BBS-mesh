import time
import logging
from pubsub import pub
import meshtastic.tcp_interface
from utils import display_banner
from message_processing import on_receive
from config_init import initialize_config, get_interface, init_cli_parser, merge_config
from db_operations import initialize_database, process_and_insert_telemetry_data, get_db_connection, sync_data_to_server
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE,SIG_DFL) 

logger = logging.getLogger(__name__)
# Use the variable in the logging configuration
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

    log_level = getattr(logging, system_config['log_level'].upper(), logging.INFO)  # Convert string to logging level

    logger.setLevel(log_level) 
    
    merge_config(system_config, args)

    interface = get_interface(system_config)

    initialize_database()

    # Start the database connection here so we can close it on KeyboardInterrupt
    conn = get_db_connection()

    # Prime the database with data contained in the interface
    process_and_insert_telemetry_data(conn, logger, interface)
    # sync with the online server
    # sync_data_to_server(conn, 'https://testbench.cc/meshmap2/sync')

    display_banner()
    logger.info(f"Testbench Mesh Logger is running on {system_config['interface_type']} interface...")

    def receive_packet(packet, interface):
        on_receive(conn, logger, system_config, packet, interface)

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
        sync_data_to_server(conn, logger, 'https://testbench.cc/meshmap2/sync')
        logger.info("Shutting down the server and DB...")

        conn.close()
        interface.close()

if __name__ == "__main__":
    main()