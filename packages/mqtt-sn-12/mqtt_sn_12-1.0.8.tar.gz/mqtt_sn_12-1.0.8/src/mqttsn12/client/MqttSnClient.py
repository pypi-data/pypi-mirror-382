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
import asyncio
import socket
import struct
import threading
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError
from typing import Dict, Optional, Callable

from mqttsn12.MqttSnConstants import MqttSnConstants
from mqttsn12.client.MqttSnClientException import MqttSnClientException
from mqttsn12.packets import (
    AdvertisePacket,
    ConnackPacket,
    ConnectPacket,
    DisconnectReqPacket,
    DisconnectResPacket,
    GatewayInfoPacket,
    PingReqPacket,
    PingResPacket,
    PubAckPacket,
    PubCompPacket,
    PublishPacket,
    PubRecPacket,
    PubRelPacket,
    RegackPacket,
    RegisterPacket,
    SearchGatewayPacket,
    SubAckPacket,
    SubPacket,
    UnsubackPacket,
    UnsubscribePacket,
    WillMessagePacket,
    WillMessageReqPacket,
    WillMessageRespPacket,
    WillMessageUpdatePacket,
    WillTopicPacket,
    WillTopicReqPacket,
    WillTopicResPacket,
    WillTopicUpdateReqPacket
)

#!/usr/bin/env python3

class MqttSnMessage:
    
    def __init__(self, topic_id=0, topic_name="", qos=0, retain=False, payload=b""):
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.qos = qos
        self.retain = retain
        self.payload = payload

    # Getter e Setter per topic_id
    def get_topic_id(self):
        return self.topic_id

    def set_topic_id(self, value):
        self.topic_id = value

    # Getter e Setter per topic_name
    def get_topic_name(self):
        return self.topic_name

    def set_topic_name(self, value):
        self.topic_name = value

    # Getter e Setter per qos
    def get_qos(self):
        return self.qos

    def set_qos(self, value):
        self.qos = value

    # Getter e Setter per retain
    def get_retain(self):
        return self.retain

    def set_retain(self, value: bool):
        self.retain = value

    # Getter e Setter per payload
    def get_payload(self):
        return self.payload

    def set_payload(self, value):
        if not isinstance(value, (bytes, bytearray)):
            raise MqttSnClientException("Payload must to be bytes or bytearray!")
        self.payload = value

    def __str__(self):
        return (f"MqttSnMessage(topic_id={self.topic_id}, "
                f"topic_name='{self.topic_name}', qos={self.qos}, "
                f"retain={self.retain}, payload={self.payload})")

class MqttSnListener:
    def message_arrived(self, msg: MqttSnMessage) -> None:
        """Callback interface for received messages"""
        pass
                
class MqttSnClient:
    logger = logging.getLogger(__name__)
    port = MqttSnConstants.DEFAULT_PORT
    timeout = MqttSnConstants.DEFAULT_TIMEOUT
    keep_alive = MqttSnConstants.DEFAULT_KEEP_ALIVE
    client_id = None
    next_message_id = 1
    will_message = None
    will_topic = None
    will_qos = MqttSnConstants.QOS_0
    will_retain = False
    connected = False
    reuse_address = True
    clean_session = True    
    datagram_socket = None
    address = None
    last_transmit = 0
    last_receive = 0
    executor = None
    topic_map: Dict[int, str] = {}
    list_of_mqtt_sn_callback: Dict[str, MqttSnListener] = {}
        
    def __init__(self):
        self.port = MqttSnConstants.DEFAULT_PORT
        self.timeout = MqttSnConstants.DEFAULT_TIMEOUT
        self.keep_alive = MqttSnConstants.DEFAULT_KEEP_ALIVE
        self.client_id = ""
        self.next_message_id = 1
        self.will_message = None
        self.will_topic = None
        self.will_qos = 0
        self.will_retain = False
        self.connected = False
        self.reuse_address = True
        self.clean_session = True
        
        self.datagram_socket = None
        self.address = None
        self.last_transmit = 0
        self.last_receive = 0
        
        self.topic_map: Dict[int, str] = {}
        self.list_of_mqtt_sn_callback: Dict[str, MqttSnListener] = {}
        self.executor = ThreadPoolExecutor(max_workers=1)
        
    def open(self, host: str, port: int) -> None:
        """Open connection to MQTT-SN gateway"""
        try:
            self.address = socket.gethostbyname(host)
            self.open_socket(self.address, port)
        except socket.gaierror as e:
            raise MqttSnClientException(f"Unknown host: {e}")
    
    def open_inet(self, address: str, port: int) -> None:
        """Open connection using IP address"""
        self.open_socket(address, port)
    
    def open_socket(self, address: str, port: int) -> None:
        """Internal method to open UDP socket"""
        try:
            self.port = port
            self.address = address
            self.datagram_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.datagram_socket.settimeout(self.timeout)
            if self.reuse_address:
                self.datagram_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.logger.debug("Socket opened.")
            self.connected = True
        except socket.error as e:
            raise MqttSnClientException(f"Socket error: {e}")
    
    def close(self) -> None:
        """Close the connection"""
        if self.datagram_socket:
            self.logger.debug("Socket closed.")
            self.datagram_socket.close()
            self.datagram_socket = None
        self.connected = False
        if self.executor is not None:
            self.executor.shutdown(wait=True)
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self.connected
    
    def send_subscribe(self, topic_filter: str, qos: int, callback: MqttSnListener) -> None:
        """Subscribe to a topic with callback"""
        topic_len = len(topic_filter)
        sub_packet = SubPacket()
        
        flags = 0x00
        flags += self.get_qos_flag(qos)
        
        if topic_len == 2:
            flags += MqttSnConstants.TOPIC_TYPE_SHORT
            topic_bytes = topic_filter.encode()
            topic_id = (topic_bytes[0] << 8) + topic_bytes[1]
            sub_packet.set_topic_id(topic_id)
        else:
            flags += MqttSnConstants.TOPIC_TYPE_NORMAL
            sub_packet.set_topic_name(topic_filter)
        
        sub_packet.set_flags(flags)
        sub_packet.set_message_id(self.next_message_id)
        self.next_message_id += 1
        
        self.send_packet(sub_packet.encode())
        
        topic_id = self.receive_suback()
        
        if topic_id > 0 and topic_len > 2:
            self.register_topic(topic_id, topic_filter)
            self.add_mqtt_sn_callback(topic_filter, callback)
        elif topic_id == 0 and topic_len == 2:
            topic_bytes = topic_filter.encode()
            topic_id = (topic_bytes[0] << 8) + topic_bytes[1]
            self.add_mqtt_sn_callback(str(topic_id), callback)
        else:
            self.add_mqtt_sn_callback(topic_filter, callback)
    
    def send_subscribe_predefined(self, topic_id: int, qos: int, callback: MqttSnListener) -> None:
        """Subscribe to predefined topic ID"""
        sub_packet = SubPacket()
        
        flags = 0x00
        flags += self.get_qos_flag(qos)
        flags += MqttSnConstants.TOPIC_TYPE_PREDEFINED
        sub_packet.set_flags(flags)
        
        sub_packet.set_message_id(self.next_message_id)
        sub_packet.set_topic_id(topic_id)
        self.next_message_id += 1
        
        self.send_packet(sub_packet.encode())
        self.receive_suback()        
        self.add_mqtt_sn_callback(str(topic_id), callback)
    
    def send_unsubscribe(self, topic_name: str) -> None:
        """Unsubscribe from topic"""
        topic_name_len = len(topic_name)
        unsubscribe_packet = UnsubscribePacket()
        
        flags = 0
        if topic_name_len == 2:
            flags += MqttSnConstants.TOPIC_TYPE_SHORT
        else:
            flags += MqttSnConstants.TOPIC_TYPE_NORMAL
        
        unsubscribe_packet.set_flags(flags)
        unsubscribe_packet.set_message_id(self.next_message_id)
        unsubscribe_packet.set_topic_name(topic_name)
        self.next_message_id += 1
        
        self.send_packet(unsubscribe_packet.encode())
        self.receive_unsuback()
        
        topic_id = self.search_topic_id(topic_name)
        if topic_id is not None:
            self.unregister_topic(topic_id)
    
    def send_unsubscribe_predefined(self, topic_id: int) -> None:
        """Unsubscribe from predefined topic ID"""
        unsubscribe_packet = UnsubscribePacket()
        flags = 0x00
        flags += MqttSnConstants.TOPIC_TYPE_PREDEFINED
        unsubscribe_packet.set_flags(flags)
        
        unsubscribe_packet.set_message_id(self.next_message_id)
        unsubscribe_packet.set_topic_id(topic_id)
        self.next_message_id += 1
        
        self.send_packet(unsubscribe_packet.encode())
        self.receive_unsuback()
        self.unregister_topic(topic_id)
    
    def send_will_message_update(self, will_message: str) -> None:
        """Update will message"""
        self.will_message = will_message
        
        will_message_update_packet = WillMessageUpdatePacket()
        will_message_update_packet.set_message(self.will_message)
        self.send_packet(will_message_update_packet.encode())
        
        response = self.receive_packet(True)
        if response is None:
            raise MqttSnClientException("Failed to connect to MQTT-SN gateway.")
        
        will_message_resp_packet = WillMessageRespPacket()
        will_message_resp_packet.decode(response)
        
        if will_message_resp_packet.get_type() != MqttSnConstants.TYPE_WILLMSGRESP:
            raise MqttSnClientException(f"Was expecting WILLMSGRESP packet but received: {self.decode_type(will_message_resp_packet.get_type())}")
        
        self.logger.debug(f"WILLMSGRESP return code: {self.decode_return_code(will_message_resp_packet.get_return_code())}")
        
        if will_message_resp_packet.get_return_code() > 0:
            raise MqttSnClientException(f"WILLMSGRESP error: {self.decode_return_code(will_message_resp_packet.get_return_code())}")
    
    def send_will_topic_update(self, will_topic) -> None:
        """Update will topic"""
        
        self.will_topic = will_topic
        
        will_topic_update_req_packet = WillTopicUpdateReqPacket()
        
        flags = 0
        if self.will_retain:
            flags += MqttSnConstants.FLAG_RETAIN
        flags |= self.get_qos_flag(self.will_qos)
        
        will_topic_update_req_packet.set_flags(flags)
        will_topic_update_req_packet.set_topic_name(self.will_topic)
        
        self.send_packet(will_topic_update_req_packet.encode())
        
        response = self.receive_packet(True)
        if response is None:
            raise MqttSnClientException("Failed to connect to MQTT-SN gateway.")
        
        will_topic_res_packet = WillTopicResPacket()
        will_topic_res_packet.decode(response)
        
        if will_topic_res_packet.get_type() != MqttSnConstants.TYPE_WILLTOPICRESP:
            raise MqttSnClientException(f"Was expecting WILLTOPICRESP packet but received: {self.decode_type(will_topic_res_packet.get_type())}")
        
        self.logger.debug(f"WILLTOPICRESP return code: {will_topic_res_packet.get_return_code()}")
        
        if will_topic_res_packet.get_return_code() > 0:
            raise MqttSnClientException(f"WILLTOPICRESP error: {self.decode_return_code(will_topic_res_packet.get_return_code())}")
          
    def send_disconnect(self, duration: int = 0) -> None:
        """Send DISCONNECT packet"""
        disconnect_req_packet = DisconnectReqPacket()
        disconnect_req_packet.set_duration(duration)
        
        self.send_packet(disconnect_req_packet.encode())
        
        response = self.wait_for(True, MqttSnConstants.TYPE_DISCONNECT)
        if response is None:
            raise MqttSnClientException("Failed to disconnect from MQTT-SN gateway.")
        
        disconnect_res_packet = DisconnectResPacket()
        disconnect_res_packet.decode(response)
        
        if disconnect_res_packet.get_type() != MqttSnConstants.TYPE_DISCONNECT:
            raise MqttSnClientException(f"Was expecting DISCONNECT packet but received: {self.decode_type(disconnect_res_packet.get_type())}")
        
        if disconnect_res_packet.get_length() == 4:
            self.logger.warning("DISCONNECT warning. Gateway returned duration in disconnect packet.")
    
    def send_search_gateway(self, radius: int) -> None:
        """Send SEARCHGW packet"""
        search_gateway_packet = SearchGatewayPacket()
        search_gateway_packet.set_radius(radius)
        
        self.send_packet(search_gateway_packet.encode())
        
        response = self.wait_for(True, MqttSnConstants.TYPE_GWINFO)
        if response is None:
            raise MqttSnClientException("Failed to find MQTT-SN gateway.")
        
        gateway_info_packet = GatewayInfoPacket()
        gateway_info_packet.decode(response)
        
        if gateway_info_packet.get_type() != MqttSnConstants.TYPE_GWINFO:
            raise MqttSnClientException(f"Was expecting GWINFO packet but received: {self.decode_type(gateway_info_packet.get_type())}")
        
        self.logger.info(f"Gateway ID: {gateway_info_packet.get_gateway_id()}")
        self.logger.info(f"Gateway Address: {gateway_info_packet.get_gateway_address()}")
    
    def send_publish(self, topic_name: str, data: bytes, qos: int, retain: bool = False) -> int:
        """Publish message to topic"""
        topic_id = 0
        if len(topic_name) == 2:
            topic_id = int.from_bytes(topic_name.encode('ascii'), 'big')
            self.send_publish_short(topic_id, data, qos, retain)
        else:
            topic_id = self.send_register(topic_name)
            self.send_publish_with_id(topic_id, MqttSnConstants.TOPIC_TYPE_NORMAL, data, qos, retain)
        
        return topic_id
    
    def send_register(self, topic: str) -> int:
        """Register topic name"""
        topic_name_len = len(topic)
        if topic_name_len > MqttSnConstants.MAX_TOPIC_LENGTH_EXTENDED:
            raise MqttSnClientException("Topic name is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH_EXTENDED} bytes)")
        
        packet = RegisterPacket()
        packet.set_topic_id(0)
        packet.set_message_id(self.next_message_id)
        packet.set_topic_name(topic)
        self.next_message_id += 1
        
        self.send_packet(packet.encode())
        topic_id = self.receive_regack()
        return topic_id
    
    def send_publish_short(self, topic_id: int, data: bytes, qos: int, retain: bool = False) -> None:
        """Publish to short topic"""
        self.send_publish_with_id(topic_id, MqttSnConstants.TOPIC_TYPE_SHORT, data, qos, retain)
    
    def send_publish_predefined(self, topic_id: int, data: bytes, qos: int, retain: bool = False) -> None:
        """Publish to predefined topic"""
        self.send_publish_with_id(topic_id, MqttSnConstants.TOPIC_TYPE_PREDEFINED, data, qos, retain)
    
    def send_publish_with_bytes(self, topic_name: bytes, data: bytes, qos: int, retain: bool = False) -> None:
        """Publish with 2-byte topic name"""
        if len(topic_name) != 2:
            raise MqttSnClientException("Parameter 'topic_name' must be 2 bytes!")
        topic_id = (topic_name[0] << 8) + topic_name[1]
        self.send_publish_with_id(topic_id, MqttSnConstants.TOPIC_TYPE_SHORT, data, qos, retain)
    
    def send_publish_with_id(self, topic_id: int, topic_type: int, data: bytes, qos: int, retain: bool = False) -> None:
        """Publish with topic ID and type"""

        if len(data) > MqttSnConstants.MAX_PAYLOAD_LENGTH_EXTENDED:
            raise MqttSnClientException(f"Data is too big (max {MqttSnConstants.MAX_PAYLOAD_LENGTH_EXTENDED} bytes)!")
            
        flags = 0
        
        if retain:
            flags += MqttSnConstants.FLAG_RETAIN
        
        flags += self.get_qos_flag(qos)
        flags += (topic_type & 0x3)
        
        publish_packet = PublishPacket()
        publish_packet.set_flags(flags)
        publish_packet.set_topic_id(topic_id)
        
        if qos > 0:
            publish_packet.set_message_id(self.next_message_id)
            self.next_message_id += 1
        else:
            publish_packet.set_message_id(0x0000)
        
        publish_packet.set_data(data)
        self.send_packet(publish_packet.encode())
        
        if qos > 0:
            self.receive_puback()
        
    def receive_puback(self) -> int:
        """Receive PUBACK packet"""
        buffer = self.wait_for(True, MqttSnConstants.TYPE_PUBACK)
        if buffer is None:
            raise MqttSnClientException("Failed to receive PUBACK.")
        
        puback_packet = PubAckPacket()
        puback_packet.decode(buffer)
        
        if puback_packet.get_type() != MqttSnConstants.TYPE_PUBACK:
            raise MqttSnClientException(f"Was expecting PUBACK packet but received: {self.decode_type(puback_packet.get_type())}")
        
        self.logger.debug(f"PUBACK return code: {puback_packet.get_return_code()}")
        
        if puback_packet.get_return_code() > 0:
            raise MqttSnClientException(f"PUBLISH error: {self.decode_return_code(puback_packet.get_return_code())}")
        
        received_message_id = puback_packet.get_message_id()
        if received_message_id != self.next_message_id - 1:
            self.logger.warning("Message id in PUBACK does not equal message id sent")
            self.logger.debug(f"Expecting: {self.next_message_id - 1}")
            self.logger.debug(f"Actual: {received_message_id}")
        
        received_topic_id = puback_packet.get_topic_id()
        self.logger.debug(f"PUBACK topic id: {received_topic_id}")
        return received_topic_id
    
    def receive_suback(self) -> int:
        """Receive SUBACK packet"""
        buffer = self.wait_for(True, MqttSnConstants.TYPE_SUBACK)
        if buffer is None:
            raise MqttSnClientException("Failed to subscribe to topic.")
        
        packet = SubAckPacket()
        packet.decode(buffer)
        
        if packet.get_type() != MqttSnConstants.TYPE_SUBACK:
            raise MqttSnClientException(f"Was expecting SUBACK packet but received: {self.decode_type(packet.get_type())}")
        
        self.logger.debug(f"SUBACK return code: {packet.get_return_code()}")
        
        if packet.get_return_code() > 0:
            raise MqttSnClientException(f"SUBSCRIBE error: {self.decode_return_code(packet.get_return_code())}")
        
        received_message_id = packet.get_message_id()
        if received_message_id != self.next_message_id - 1:
            self.logger.warning("Message id in SUBACK does not equal message id sent")
            self.logger.debug(f"Expecting: {self.next_message_id - 1}")
            self.logger.debug(f"Actual: {received_message_id}")
        
        received_topic_id = packet.get_topic_id()
        self.logger.debug(f"SUBACK topic id: {received_topic_id}")
        return received_topic_id
    
    def receive_unsuback(self) -> None:
        """Receive UNSUBACK packet"""
        buffer = self.wait_for(True, MqttSnConstants.TYPE_UNSUBACK)
        if buffer is None:
            raise MqttSnClientException("Failed to unsubscribe from topic.")
        
        unsuback_packet = UnsubackPacket()
        unsuback_packet.decode(buffer)
        
        if unsuback_packet.get_type() != MqttSnConstants.TYPE_UNSUBACK:
            raise MqttSnClientException(f"Was expecting UNSUBACK packet but received: {self.decode_type(unsuback_packet.get_type())}")
        
        received_message_id = unsuback_packet.get_message_id()
        if received_message_id != self.next_message_id - 1:
            self.logger.warning("Message id in UNSUBACK does not equal message id sent")
            self.logger.debug(f"Expecting: {self.next_message_id - 1}")
            self.logger.debug(f"Actual: {received_message_id}")
    
    def send_puback(self, publish: PublishPacket, return_code: int) -> None:
        """Send PUBACK packet"""
        puback = PubAckPacket()
        puback.set_topic_id(publish.get_topic_id())
        puback.set_message_id(publish.get_message_id())
        puback.set_return_code(return_code)
        self.logger.debug("Sending PUBACK packet...")
        self.send_packet(puback.encode())
    
    def receive_regack(self) -> int:
        """Receive REGACK packet"""
        buffer = self.wait_for(True, MqttSnConstants.TYPE_REGACK)
        if buffer is None:
            raise MqttSnClientException("Failed to register topic.")
        
        packet = RegackPacket()
        packet.decode(buffer)
        
        if packet.get_type() != MqttSnConstants.TYPE_REGACK:
            raise MqttSnClientException(f"Was expecting REGACK packet but received: {self.decode_type(packet.get_type())}")
        
        ret_code = packet.get_return_code()
        self.logger.debug(f"REGACK return code: {ret_code}")
        
        if ret_code > 0:
            raise MqttSnClientException(f"REGISTER failed: {self.decode_return_code(packet.get_return_code())}")
        
        received_message_id = packet.get_message_id()
        if received_message_id != self.next_message_id - 1:
            self.logger.warning("Message id in REGACK does not equal message id sent")
        
        received_topic_id = packet.get_topic_id()
        self.logger.debug(f"REGACK topic id: {received_topic_id}")
        return received_topic_id
    
    def process_register(self, packet_data: bytes) -> None:
        """Process incoming REGISTER packet"""
        register_packet = RegisterPacket()
        register_packet.decode(packet_data)
        
        if register_packet.get_type() != MqttSnConstants.TYPE_REGISTER:
            raise MqttSnClientException(f"Was expecting REGISTER packet but received: {self.decode_type(register_packet.get_type())}")
        
        message_id = register_packet.get_message_id()
        topic_id = register_packet.get_topic_id()
        topic_name = register_packet.get_topic_name()
        
        self.register_topic(topic_id, topic_name)
        self.send_regack(topic_id, message_id)
    
    def send_regack(self, topic_id: int, message_id: int) -> None:
        regack_packet = RegackPacket()
        regack_packet.set_message_id(message_id)
        regack_packet.set_return_code(0)
        regack_packet.set_topic_id(topic_id)
        self.send_packet(regack_packet.encode())
        
    def send_connect(self):
        connect_packet = ConnectPacket()
        
        flags = 0
        if self.clean_session:
            self.logger.debug("clean session enabled")
            flags += MqttSnConstants.FLAG_CLEAN
        
        if self.will_topic is not None and self.will_message is not None:
            self.logger.debug("LWT enabled")
            flags += MqttSnConstants.FLAG_WILL
        
        connect_packet.set_flags(flags)
        connect_packet.set_protocol_id(MqttSnConstants.PROTOCOL_ID)
        connect_packet.set_duration(self.keep_alive)
        connect_packet.set_client_id(self.client_id)
        
        self.send_packet(connect_packet.encode())
        
        if self.will_topic is not None and self.will_message is not None:
            self.logger.debug("LWT enabled.")
            response = self.receive_packet(True)
            
            if response is None:
                raise MqttSnClientException("Failed to connect to MQTT-SN gateway.")
            
            will_topic_req_packet = WillTopicReqPacket()
            will_topic_req_packet.decode(response)
            
            if will_topic_req_packet.get_type() != MqttSnConstants.TYPE_WILLTOPICREQ:
                raise MqttSnClientException("Was expecting WILLTOPICREQ packet but received: " + self.decode_type(will_topic_req_packet.get_type()))
            
            will_topic_packet = WillTopicPacket()
            
            flags = 0
            
            if self.will_retain:
                flags += MqttSnConstants.FLAG_RETAIN
            
            flags |= self.get_qos_flag(self.will_qos)
            
            will_topic_packet.set_topic_name(self.will_topic)
            will_topic_packet.set_flags(flags)
            
            self.send_packet(will_topic_packet.encode())
            response = self.receive_packet(True)
            
            if response is None:
                raise MqttSnClientException("Failed to connect to MQTT-SN gateway.")
            
            will_message_req_packet = WillMessageReqPacket()
            will_message_req_packet.decode(response)
            
            if will_message_req_packet.get_type() != MqttSnConstants.TYPE_WILLMSGREQ:
                raise MqttSnClientException("Was expecting WILLMSGREQ packet but received: " + self.decode_type(will_message_req_packet.get_type()))
            
            will_message_packet = WillMessagePacket()
            will_message_packet.set_message(self.will_message)
            
            self.send_packet(will_message_packet.encode())
        
        response = self.receive_packet(True)
        
        if response is None:
            raise MqttSnClientException("Failed to connect to MQTT-SN gateway.")
        
        connack_packet = ConnackPacket()
        connack_packet.decode(response)
        
        if connack_packet.get_type() != MqttSnConstants.TYPE_CONNACK:
            raise MqttSnClientException("Was expecting CONNACK packet but received: " + self.decode_type(connack_packet.get_type()))
        
        self.logger.debug("CONNACK return code:" + self.decode_return_code(connack_packet.get_return_code()))
        
        if connack_packet.get_return_code() > 0:
            raise MqttSnClientException("CONNECT error: " + self.decode_return_code(connack_packet.get_return_code()))

    def send_packet(self, buf):
        if buf[0] == 1:
            self.logger.debug(f"Sending {self.decode_type(buf[3])} packet...")
        else:
            self.logger.debug(f"Sending {self.decode_type(buf[1])} packet...")
        
        self.logger.debug(f"Sending {len(buf)} bytes: {buf.hex()}")
        datagram_packet = (buf, (self.address, self.port))
        try:
            self.datagram_socket.settimeout(self.timeout)
            self.datagram_socket.sendto(buf, (self.address, self.port))
            
            # Store the last time that we sent a packet
            self.last_transmit = int(time.time())
        except IOError as e:
            raise MqttSnClientException(e)

    def decode_type(self, type):
        if type == MqttSnConstants.TYPE_ADVERTISE:
            return "ADVERTISE"
        elif type == MqttSnConstants.TYPE_SEARCHGW:
            return "SEARCHGW"
        elif type == MqttSnConstants.TYPE_GWINFO:
            return "GWINFO"
        elif type == MqttSnConstants.TYPE_CONNECT:
            return "CONNECT"
        elif type == MqttSnConstants.TYPE_CONNACK:
            return "CONNACK"
        elif type == MqttSnConstants.TYPE_WILLTOPICREQ:
            return "WILLTOPICREQ"
        elif type == MqttSnConstants.TYPE_WILLTOPIC:
            return "WILLTOPIC"
        elif type == MqttSnConstants.TYPE_WILLMSGREQ:
            return "WILLMSGREQ"
        elif type == MqttSnConstants.TYPE_WILLMSG:
            return "WILLMSG"
        elif type == MqttSnConstants.TYPE_REGISTER:
            return "REGISTER"
        elif type == MqttSnConstants.TYPE_REGACK:
            return "REGACK"
        elif type == MqttSnConstants.TYPE_PUBLISH:
            return "PUBLISH"
        elif type == MqttSnConstants.TYPE_PUBACK:
            return "PUBACK"
        elif type == MqttSnConstants.TYPE_PUBCOMP:
            return "PUBCOMP"
        elif type == MqttSnConstants.TYPE_PUBREC:
            return "PUBREC"
        elif type == MqttSnConstants.TYPE_PUBREL:
            return "PUBREL"
        elif type == MqttSnConstants.TYPE_SUBSCRIBE:
            return "SUBSCRIBE"
        elif type == MqttSnConstants.TYPE_SUBACK:
            return "SUBACK"
        elif type == MqttSnConstants.TYPE_UNSUBSCRIBE:
            return "UNSUBSCRIBE"
        elif type == MqttSnConstants.TYPE_UNSUBACK:
            return "UNSUBACK"
        elif type == MqttSnConstants.TYPE_PINGREQ:
            return "PINGREQ"
        elif type == MqttSnConstants.TYPE_PINGRESP:
            return "PINGRESP"
        elif type == MqttSnConstants.TYPE_DISCONNECT:
            return "DISCONNECT"
        elif type == MqttSnConstants.TYPE_WILLTOPICUPD:
            return "WILLTOPICUPD"
        elif type == MqttSnConstants.TYPE_WILLTOPICRESP:
            return "WILLTOPICRESP"
        elif type == MqttSnConstants.TYPE_WILLMSGUPD:
            return "WILLMSGUPD"
        elif type == MqttSnConstants.TYPE_WILLMSGRESP:
            return "WILLMSGRESP"
        elif type == MqttSnConstants.TYPE_FRWDENCAP:
            return "FRWDENCAP"
        else:
            return "UNKNOWN"

    def receive_packet(self, blocking):
        received = None
        
        try:
            self.datagram_socket.settimeout(self.timeout)
            self.datagram_socket.setblocking(blocking)
            data, addr = self.datagram_socket.recvfrom(MqttSnConstants.MAX_PACKET_LENGTH_EXTENDED)
            self.last_receive = int(time.time())           
            self.logger.debug(f"Received {len(data)} bytes: {data.hex()}")          
        
        except BlockingIOError:    
            if (blocking == False):
                return None
            else:
                raise MqttSnClientException(e)
        except Exception as e:
            raise MqttSnClientException(e)
        
        return data

    def decode_return_code(self, return_code):
        if return_code == MqttSnConstants.ACCEPTED:
            return "Accepted (" + str(return_code) + ")"
        elif return_code == MqttSnConstants.REJECTED_CONGESTION:
            return "Rejected: congestion (" + str(return_code) + ")"
        elif return_code == MqttSnConstants.REJECTED_INVALID:
            return "Rejected: invalid topic ID (" + str(return_code) + ")"
        elif return_code == MqttSnConstants.REJECTED_NOT_SUPPORTED:
            return "Rejected: not supported (" + str(return_code) + ")"
        else:
            return str(return_code)

    def wait_for(self, blocking, msg_type):
        started_waiting = int(time.time())
        
        running = True
        tmp_msg_type = None
        
        while running:
            now = int(time.time())
            # self.logger.debug(f"Waiting {now}...")
            
            # Time to send a ping?
            if self.keep_alive > 0 and self.last_transmit > 0 and ((now - self.last_transmit) >= self.keep_alive):
                self.logger.debug("Time to send a PING")
                self.send_ping_req()                
                
            buf = self.receive_packet(blocking)
            if buf is None:
                return None
                
            if buf[0] == 1:
                tmp_msg_type = buf[3]
                self.logger.debug(f"Received {self.decode_type(tmp_msg_type)} packet...")
            else:
                tmp_msg_type = buf[1]
                self.logger.debug(f"Received {self.decode_type(tmp_msg_type)} packet...") 
            
            # Did we find what we were looking for?
            if tmp_msg_type == msg_type:
                return buf
            elif tmp_msg_type == MqttSnConstants.TYPE_REGISTER:
                self.process_register(buf)
            elif tmp_msg_type == MqttSnConstants.TYPE_ADVERTISE:
                running = False
            elif tmp_msg_type == MqttSnConstants.TYPE_DISCONNECT:
                self.logger.debug("Received DISCONNECT from gateway.") 
            else:
                if tmp_msg_type != msg_type:
                    self.logger.warning("Was expecting '" + self.decode_type(msg_type) + "' packet but received: " + self.decode_type(msg_type))
            
            # Waiting or not ?            
            if blocking == False:
                running = False
            # Check for receive timeout
            if self.keep_alive > 0 and self.last_receive > 0 and (now - self.last_receive) >= (self.keep_alive * 1.5):
                self.logger.warning("Keep alive error: timed out while waiting for a '" + self.decode_type(msg_type) + "' from gateway.")
                break
            
            # Check if we have timed out waiting for the packet we are looking for
            if (now - started_waiting) >= self.timeout:
                self.logger.warning("Timed out while waiting for a '" + self.decode_type(msg_type) + "' from gateway.")
                break

        if tmp_msg_type == msg_type:
            return buf            
        else:
            return None
        
    def receive_packet_async(self):
        response = None
        try:
            receiver = Receiver(self, self.datagram_socket, 1)
            response = asyncio.run(receiver.call())
        except TimeoutError:
            # Ignore
            pass
        except Exception:
            # Ignore
            pass
        
        return response
        
    def send_ping_req(self):
        ping_req_packet = PingReqPacket()
        self.send_packet(ping_req_packet.encode())
        buf = self.wait_for(True, MqttSnConstants.TYPE_PINGRESP)
        packet = PingResPacket()
        packet.decode(buf)

    def get_qos_flag(self, qos):
        out = 0
        if qos == MqttSnConstants.QOS_N1:
            out = MqttSnConstants.FLAG_QOS_N1
        elif qos == MqttSnConstants.QOS_0:
            out = MqttSnConstants.FLAG_QOS_0
        elif qos == MqttSnConstants.QOS_1:
            out = MqttSnConstants.FLAG_QOS_1
        elif qos == MqttSnConstants.QOS_2:
            raise MqttSnClientException(f"QOS={qos} not supported")
        else:
            raise MqttSnClientException(f"QOS={qos} not valid")
        
        self.logger.debug(f"QOS:{out}")
        return out
    
    def set_client_id(self, value: str):
        if value is None:
            self.client_id = f"mqtt-sn-python-{random.randint(0, 0xffff)}"
        else:
            if len(value) < 1:
                raise MqttSnClientException("client_id not valid. Too short.")      
            if len(value) > MqttSnConstants.MAX_CLIENT_ID_LENGTH:
                raise MqttSnClientException("client_id not valid! Too long.")       
        self.client_id = value

    def set_clean_session(self, value: bool):
        self.clean_session = value

    def set_will(self, topic: str, message: str, qos: int, retain: bool):
        self.will_topic = topic
        self.will_qos = qos
        self.will_retain = retain
        self.will_message = message

    def set_will_topic(self, value: str):
        self.will_topic = value

    def set_will_message(self, value: str):
        self.will_message = value

    def set_will_qos(self, value: int):
        self.will_qos = value

    def set_will_retain(self, value: bool):
        self.will_retain = value

    def set_keep_alive(self, value: int):
        self.keep_alive = value

    def set_timeout(self, value: int):
        self.timeout = value
        
    def polling(self):
        buffer = self.wait_for(False, MqttSnConstants.TYPE_PUBLISH)
        if buffer is not None:
            publish_packet = PublishPacket()
            publish_packet.decode(buffer)
            
            if publish_packet.get_type() != MqttSnConstants.TYPE_PUBLISH:
                raise MqttSnClientException("Was expecting PUBLISH packet but received: " + self.decode_type(publish_packet.get_type()))
            
            packet_retain = publish_packet.get_retain()
            packet_qos = publish_packet.get_qos()
            if packet_qos == MqttSnConstants.FLAG_QOS_1:
                self.send_puback(publish_packet, MqttSnConstants.ACCEPTED)
            
            topic_id = publish_packet.get_topic_id()
            topic_name = self.topic_map.get(publish_packet.get_topic_id())
            payload = publish_packet.get_data()

            self.logger.debug("topic ID is " + str(topic_id))
            self.logger.debug("topic name is " + str(topic_name))
            self.logger.debug(f"Payload is {payload}")
            
            mqtt_sn_callback = None
            if topic_name is not None:
                self.logger.debug("Search listener for Topic Name...")
                mqtt_sn_callback = self.list_of_mqtt_sn_callback.get(topic_name)
            else:
                self.logger.debug("Search listener for Topic ID...")
                mqtt_sn_callback = self.list_of_mqtt_sn_callback.get(str(topic_id))
            
            if mqtt_sn_callback is None:
                self.logger.debug("Listener for topic name not found. Search by Topic ID")
                for filter_name, callback in self.list_of_mqtt_sn_callback.items():
                    if self.is_matched(topic_name, filter_name):
                        self.logger.debug("Found listener for topicID=" + str(topic_id) + ",topic name=" + str(topic_name) + ", topic filter=" + filter_name)
                        msg = MqttSnMessage()
                        msg.set_topic_id(topic_id)
                        msg.set_topic_name(topic_name)
                        msg.set_qos(packet_qos)
                        msg.set_retain(packet_retain)     
                        msg.set_payload(payload)                   
                        callback.message_arrived(msg)
            else:
                self.logger.debug("Callback...")
                msg = MqttSnMessage()
                msg.set_topic_id(topic_id)
                msg.set_topic_name(topic_name)
                msg.set_qos(packet_qos)
                msg.set_retain(packet_retain)       
                msg.set_payload(payload)                  
                mqtt_sn_callback.message_arrived(msg)

    def register_topic(self, topic_id, topic_name):
        
        # Check topic ID is valid
        if topic_id == 0x0000 or topic_id == 0xFFFF:
            raise MqttSnClientException(f"Attempted to register invalid topic id: {topic_id}")

        # Check topic name is valid
        if topic_name is None or len(topic_name) <= 0 or len(topic_name) > MqttSnConstants.MAX_TOPIC_LENGTH:
            raise MqttSnClientException("Attempted to register invalid topic name.")

        self.logger.debug(f"Registering topic {topic_id}={topic_name}")

        self.topic_map[topic_id] = topic_name

    def unregister_topic(self, topic_id):
        
        # Check topic ID is valid
        if topic_id == 0x0000 or topic_id == 0xFFFF:
            raise MqttSnClientException(f"Attempted to register invalid topic id: {topic_id}")
        
        topic_name = self.topic_map.get(topic_id)
        self.logger.debug(f"Unregistering topic ID '{topic_id}': {topic_name}")
        self.topic_map.pop(topic_id, None)

    def search_topic_id(self, topic_name):
        for key, value in self.topic_map.items():
            if topic_name == value:
                return key
        return None
    
    def add_mqtt_sn_callback(self, topic: int, a_mqtt_sn_callback):
        self.logger.debug("Store MqttSnCallback for topic " + topic)
        self.list_of_mqtt_sn_callback[topic] = a_mqtt_sn_callback

    def add_mqtt_sn_callback(self, topic_id: str, a_mqtt_sn_callback):
        self.logger.debug("Store MqttSnCallback for topic ID " + str(topic_id))
        self.list_of_mqtt_sn_callback[str(topic_id)] = a_mqtt_sn_callback
    
    def is_matched(self, topic: str, topic_filter: str) -> bool:
        """
        Check if an MQTT topic matches a topic filter with wildcards (+, #).
        """
        if topic is None:
            raise MqttSnClientException("Parameter 'topic' is None.")

        if topic_filter is None:
            raise MqttSnClientException("Parameter 'topic_filter' is None.")
            
        topic_levels = topic.split('/')
        filter_levels = topic_filter.split('/')

        i = 0
        while i < len(filter_levels):
            f = filter_levels[i]

            # wildcard "#": matches all remaining levels, must be last
            if f == '#':
                return i == len(filter_levels) - 1

            # wildcard "+" matches exactly one level (even empty one)
            if f == '+':
                if len(topic_levels) <= i:
                    return False
            else:
                # normal string, must match exactly
                if len(topic_levels) <= i or topic_levels[i] != f:
                    return False
            i += 1

        return len(topic_levels) == len(filter_levels)
