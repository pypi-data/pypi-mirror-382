#!/usr/bin/env python3
# MIT License
# 
# Copyright (c) 2025 Marco Ratto
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import argparse
import os
import sys
import time
import logging

from mqttsn12.MqttSnConstants import MqttSnConstants
from mqttsn12.client.MqttSnClient import MqttSnClient
from mqttsn12.client.MqttSnClientException import MqttSnClientException
from mqttsn12.packets import *

logging.basicConfig(
    level=logging.CRITICAL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="mqtt_sn_pub",
        usage="mqtt_sn_pub [opts] -t <topic> -m <message>",
        description="MQTT-SN publisher in Python",
        add_help=False  # disabilito l'help automatico
    )
   
    parser.add_argument("-t", "--topic", required=False,
                        help="MQTT-SN topic name to publish to")

    parser.add_argument("-m", "--message", required=False,
                        help="Message payload to send")

    parser.add_argument("-d", "--enable-debug",
                        action="store_true", default=False,
                        help="Enable debug messages")

    parser.add_argument("-c", "--disable-clean-session",
                        action="store_false", default=True,
                        help="Disable clean session / enable persistent client mode")
    parser.add_argument("-f", "--file",
                        help="A file to send as the message payload")
    parser.add_argument("-h", "--host",
                        default="127.0.0.1",
                        help="MQTT-SN host to connect to (default: 127.0.0.1)")
    parser.add_argument("-i", "--clientid", type=str, default="mqtt-sn-python-" + str(os.getpid()),
                        help="Client ID to use. Defaults to 'mqtt-sn-python-' + pid")
    parser.add_argument("-I", "--id-prefix",
                        action="store_true",
                        help="Define client id as prefix + pid (useful with broker clientid_prefixes)")
    parser.add_argument("-k", "--keepalive",
                        type=int, default=30,
                        help="Keep alive in seconds (default: 30)")
    parser.add_argument("-e", "--sleep",
                        type=int, default=0,
                        help="Sleep duration in seconds when disconnecting (default: 0)")
    parser.add_argument("-l", "--line-mode",
                        action="store_true",
                        help="Read messages from stdin, sending a separate message for each line")
    parser.add_argument("-n", "--null-message", default=False,
                        action="store_true",
                        help="Send a null (zero length) message")
    parser.add_argument("-p", "--port", 
                        type=int, default=2442,
                        help="Network port (default: 2442)")
    parser.add_argument("-q", "--qos",
                        type=int, choices=[-1, 0, 1], default=0,
                        help="Quality of Service (-1, 0, 1). Default: 0")
    parser.add_argument("-r", "--retain",
                        action="store_true", default=False,
                        help="Mark the message as retained")
    parser.add_argument("-s", "--stdin-message",
                        action="store_true", default=False,
                        help="Read one whole message from STDIN")
    parser.add_argument("-T", "--topicid",
                        type=int,
                        help="Pre-defined MQTT-SN topic ID to publish to")
    parser.add_argument("--timeout",
                        type=int, default=60,
                        help="Timeout (default: 60)")
    parser.add_argument("--will-payload",
                        help="Payload for the client Will")
    parser.add_argument("--will-payload-file",
                        help="Payload for the client Will loaded from a file")                        
    parser.add_argument("--will-qos",
                        type=int, choices=[0, 1], default=0,
                        help="QoS level for the client Will. Default: 0")
    parser.add_argument("--will-retain",
                        action="store_true", default=False,
                        help="Make the client Will retained")
    parser.add_argument("--will-topic",
                        help="The topic on which to publish the client Will")
    parser.add_argument("--repeat",
                        type=int, default=1,
                        help="Repeat publish N times (default: 1)")
    parser.add_argument("--repeat-delay",
                        type=int, default=0,
                        help="Delay in seconds between repeats (default: 0)")

    # Se nessun argomento → mostra help completo
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    try:
        args = parser.parse_args()
    except SystemExit:
        # Se errore nei parametri obbligatori → mostra help completo
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args

def main():
    mqttsn_client = MqttSnClient()

    args = parse_args()

    if args.enable_debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.clientid:
        mqttsn_client.set_client_id(args.clientid)
    
    if args.disable_clean_session:
        mqttsn_client.set_clean_session(args.disable_clean_session)

    if args.keepalive:
        mqttsn_client.set_keep_alive(args.keepalive)
    if args.timeout:
        mqttsn_client.set_timeout(args.timeout)

    if args.will_topic:
        mqttsn_client.set_will_topic(args.will_topic)
    if args.will_payload:
        mqttsn_client.set_will_message(args.will_payload)
    if args.will_qos:
        mqttsn_client.set_will_qos(args.will_qos)
    if args.will_retain:
        mqttsn_client.set_will_retain(args.will_retain)

    if args.will_payload_file:
        with open(args.will_payload_file, "r", encoding="utf-8") as f:
            will_message = f.read()  
            mqttsn_client.set_will_message(will_message)
    
    message = None
       
    if args.message:
        message = args.message
        
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            message = f.read()  

    if args.stdin_message:
        message = sys.stdin.read()
        
    if args.null_message:
        message = ""
    
    mqttsn_client.open(args.host, args.port)
    
    if args.qos >= 0:
        mqttsn_client.send_connect()

    if args.topicid:
        for i in range(args.repeat):
            mqttsn_client.send_publish_predefined(args.topicid, 
                        message, 
                        args.qos, 
                        args.retain)
            time.sleep(args.repeat_delay)
    else:
        for i in range(args.repeat):
            mqttsn_client.send_publish(args.topic, 
                            message, 
                            args.qos, 
                            args.retain)
            
            time.sleep(args.repeat_delay)
        
    if args.qos >= 0:
        mqttsn_client.send_disconnect(args.sleep)

    mqttsn_client.close()

if __name__ == "__main__":
    main()
