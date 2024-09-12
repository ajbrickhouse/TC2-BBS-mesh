import logging
import time


def send_message(message, destination, interface):
    max_payload_size = 200
    for i in range(0, len(message), max_payload_size):
        chunk = message[i:i + max_payload_size]
        try:
            d = interface.sendText(
                text=chunk,
                destinationId=destination,
                wantAck=False,
                wantResponse=False
            )
            logging.info(f"REPLY SEND ID={d.id}")
        except Exception as e:
            logging.info(f"REPLY SEND ERROR {e.message}")

        time.sleep(2)

def get_node_info(interface, short_name):
    nodes = [{'num': node_id, 'shortName': node['user']['shortName'], 'longName': node['user']['longName']}
             for node_id, node in interface.nodes.items()
             if node['user']['shortName'].lower() == short_name]
    return nodes

def get_node_names(interface, node_id):
    node = interface.nodes.get(node_id)
    if node and 'user' in node:
        return node['user']['shortName'], node['user']['longName']
    else:
        return None, None  # Return None or an appropriate response if the node_id is not found

def get_node_id_from_num(node_num, interface):
    for node_id, node in interface.nodes.items():
        if node['num'] == node_num:
            return node_id
    return None


def get_node_short_name(node_id, interface):
    node_info = interface.nodes.get(node_id)
    if node_info:
        return node_info['user']['shortName']
    return None

def log_text_to_file(data, file_path='log.txt'):
    with open(file_path, 'w') as log_file:
        log_file.write(f"{str(data)}")  # Convert the data to a string and write it to the file

# def log_text_to_file(data, file_path='log.txt'):
#     with open(file_path, 'a') as log_file:
#         log_file.write('\n\n' + '-'*100 + '\n\n')  # Add separator line
#         log_file.write(f"{str(data)}")  # Convert the data to a string and write it to the file

def display_banner():
    # clear the console
    print("\033[H\033[J")
    banner = """
 ********** ********  ******** ********** ******   ******** ****     **   ******  **      **      ******    ****** 
/////**/// /**/////  **////// /////**/// /*////** /**///// /**/**   /**  **////**/**     /**     **////**  **////**
    /**    /**      /**           /**    /*   /** /**      /**//**  /** **    // /**     /**    **    //  **    // 
    /**    /******* /*********    /**    /******  /******* /** //** /**/**       /**********   /**       /**       
    /**    /**////  ////////**    /**    /*//// **/**////  /**  //**/**/**       /**//////**   /**       /**       
    /**    /**             /**    /**    /*    /**/**      /**   //****//**    **/**     /** **//**    **//**    **
    /**    /******** ********     /**    /******* /********/**    //*** //****** /**     /**/** //******  //****** 
    //     //////// ////////      //     ///////  //////// //      ///   //////  //      // //   //////    //////  
 ****     **** ********  ******** **      **       **         *******     ********    ********  ******** *******   
/**/**   **/**/**/////  **////// /**     /**      /**        **/////**   **//////**  **//////**/**///// /**////**  
/**//** ** /**/**      /**       /**     /**      /**       **     //** **      //  **      // /**      /**   /**  
/** //***  /**/******* /*********/**********      /**      /**      /**/**         /**         /******* /*******   
/**  //*   /**/**////  ////////**/**//////**      /**      /**      /**/**    *****/**    *****/**////  /**///**   
/**   /    /**/**             /**/**     /**      /**      //**     ** //**  ////**//**  ////**/**      /**  //**  
/**        /**/******** ******** /**     /**      /******** //*******   //********  //******** /********/**   //** 
//         // //////// ////////  //      //       ////////   ///////     ////////    ////////  //////// //     //  
Meshtastic Version
"""
    print(banner)

def format_real_number(value, precision=2):
    if value is None:
        return None

    real_value = float(value)
    return f"{real_value:.{precision}f}"