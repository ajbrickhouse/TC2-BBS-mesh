import time
import meshtastic
import meshtastic.tcp_interface
from pubsub import pub
from message_processing import on_receive
from db_operations import initialize_database, process_and_insert_telemetry_data
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
    display_banner()
    args = init_cli_parser()
    config_file = None
    if args.config is not None:
        config_file = args.config
    system_config = initialize_config(config_file)

    merge_config(system_config, args)

    interface = get_interface(system_config)

    logging.info(f"Testbench Mesh Logger is running on {system_config['interface_type']} interface...")

    initialize_database()

    def receive_packet(packet, interface):
        process_and_insert_telemetry_data(interface)
        # on_receive(packet, interface)

    pub.subscribe(receive_packet, system_config['mqtt_topic'])

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Shutting down the server...")
        interface.close()


if __name__ == "__main__":
    main()
