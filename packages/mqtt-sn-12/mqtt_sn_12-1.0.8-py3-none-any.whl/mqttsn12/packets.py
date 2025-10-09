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
import struct
from typing import Optional

from mqttsn12.MqttSnConstants import MqttSnConstants
from mqttsn12.client.MqttSnClientException import MqttSnClientException

class AdvertisePacket:
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_ADVERTISE
        self.gwID = 0
        self.duration = 0

    def decode(self, value: bytes):
        # Decodifica i campi nell'ordine: byte, byte, byte, short (2 byte)
        if len(value) < 5:
            raise ValueError("Packet is too short!")
        
        self.length, self.type, self.gwID, self.duration = struct.unpack('>BBBH', value)

    def get_length(self):
        return self.length

    def get_type(self):
        return self.type

    def get_gateway_id(self):
        return self.gwID

    def get_duration(self):
        return self.duration

class ConnackPacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_CONNACK
        self.return_code = 0
    
    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
        self.return_code = value[2]

    def encode(self):
        self.length = 3
        buffer = bytearray()            
        buffer.append(self.length)
        buffer.append(self.type)
        buffer.append(self.return_code)            
        return bytes(buffer)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_return_code(self):
        return self.return_code 
      
    def set_return_code(self, value):
        self.return_code = value

class ConnectPacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_CONNECT
        self.flags = 0
        self.protocol_id = 0
        self.duration = 0
        self.client_id = ""
    
    def encode(self):
        try:
            self.length = 6 + len(self.client_id)
            buffer = bytearray()
            
            buffer.append(self.length)
            buffer.append(self.type)
            buffer.append(self.flags)
            buffer.append(self.protocol_id)
            buffer.extend(struct.pack('>H', self.duration))
            buffer.extend(self.client_id)
            
            return bytes(buffer)
            
        except Exception as e:
            raise MqttSnClientException(e)

    def decode(self, value: bytes):
        self.length = value[0]
        self.type = value[1]
        self.flags = value[2]
        self.protocol_id = value[3]
        self.duration = struct.unpack('>H', value[4:6])[0]
        self.client_id = value[6:].decode('utf-8', errors='ignore')
            
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_flags(self) -> int:
        return self.flags
    
    def set_flags(self, flags):
        self.flags = flags
    
    def get_protocol_id(self):
        return self.protocolID
    
    def set_protocol_id(self, protocol_id):
        self.protocol_id = protocol_id
    
    def get_duration(self):
        return self.duration
    
    def set_duration(self, duration):
        self.duration = duration
    
    def get_client_id(self):
        return self.client_id
    
    def set_client_id(self, value):
        if value is None:
            self.client_id = ""
        else:
            if len(value.strip()) > MqttSnConstants.MAX_CLIENT_ID_LENGTH:
                raise MqttSnClientException(f"Client ID '{value}' is too long (max {MqttSnConstants.MAX_CLIENT_ID_LENGTH})")        
            self.client_id = value.strip().encode('utf-8')
        
    def get_dup(self) -> bool:
        return bool(self.flags & MqttSnConstants.FLAG_DUP)

    def get_qos(self) -> int:
        return (self.flags & MqttSnConstants.FLAG_QOS_MASK) >> 5

    def get_retain(self) -> bool:
        return bool(self.flags & MqttSnConstants.FLAG_RETAIN)

    def get_will(self) -> bool:
        return bool(self.flags & MqttSnConstants.FLAG_WILL)

    def get_clean_session(self) -> bool:
        return bool(self.flags & MqttSnConstants.FLAG_CLEAN)
        
class DisconnectReqPacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_DISCONNECT 
        self.duration = 0
    
    def encode(self):
        try:
            if self.duration == 0:
                self.length = 0x02
            else:
                self.length = 0x04
            
            if self.duration > 0:
                return struct.pack('>BBH', self.length, self.type, self.duration)
            else:
                return struct.pack('>BB', self.length, self.type)
        except Exception as e:
            raise Exception(str(e))
    
    def decode(self, value):
        self.length = struct.unpack('>B', value[0:1])[0]
        self.type = struct.unpack('>B', value[1:2])[0]
        if self.length == 4:
            self.duration = struct.unpack('>H', value[2:4])[0]
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_duration(self):
        return self.duration
    
    def set_duration(self, duration):
        self.duration = duration

class DisconnectResPacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_DISCONNECT 
        self.duration = 0
    
    def encode(self):
        try:
            if self.duration == 0:
                self.length = 0x02
            else:
                self.length = 0x04
            
            if self.duration > 0:
                return struct.pack('>BBH', self.length, self.type, self.duration)
            else:
                return struct.pack('>BB', self.length, self.type)
        except Exception as e:
            raise Exception(str(e))
    
    def decode(self, value):
        self.length = struct.unpack_from('>B', value, 0)[0]
        self.type = struct.unpack_from('>B', value, 1)[0]
        if self.length == 4:
            self.duration = struct.unpack_from('>H', value, 2)[0]
    
    def get_length(self):
        return self.length
       
    def get_type(self):
        return self.type
       
    def get_duration(self):
        return self.duration
    
    def set_duration(self, duration):
        self.duration = duration

class GatewayInfoPacket:
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_GWINFO
        self.gw_id = 0
        self.gw_address = bytearray()
    
    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
        self.gw_id = value[2]
        
        self.gw_address = bytearray(self.length - 3)
        
        for i in range(self.length - 3):
            self.gw_address[i] = value[3 + i]
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_gateway_id(self):
        return self.gw_id
    
    def get_gateway_address(self):
        return self.gw_address.decode('utf-8')

class PingReqPacket:
    
    def __init__(self, client_id=None):
        self.type = MqttSnConstants.TYPE_PINGREQ
        self.client_id = ""
        self.length = 0
    
    def encode(self):
        # length = 2 (header) + len(client_id) se presente
        self.length = 2 + len(self.client_id.encode("utf-8"))       
        try:
            buffer = struct.pack('BB', self.length, self.type)
            if self.client_id:
                buffer += self.client_id.encode("utf-8")
            return buffer
        except Exception as e:
            raise MqttSnClientException(e)

    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
        if self.length > 2:
            self.client_id = value[2:].decode("utf-8")
        else:
            self.client_id = ""
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_client_id(self):
        return self.client_id

    def set_client_id(self, value):
        if value is None:
            self.client_id = ""
        else:
            if len(value.strip()) > MqttSnConstants.MAX_CLIENT_ID_LENGTH:
                raise MqttSnClientException(f"Client ID '{value}' is too long (max {MqttSnConstants.MAX_CLIENT_ID_LENGTH})")        
            self.client_id = value.strip().encode('utf-8')

class PingResPacket:
    
    def __init__(self):
        self.length = 2
        self.type = MqttSnConstants.TYPE_PINGRESP
    
    def encode(self):
        try:
            buffer = struct.pack('BB', self.length, self.type)
            return buffer
        except Exception as e:
            raise MqttSnClientException(e)

    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
            
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
        
class PubAckPacket:
    def __init__(self):
        self.length = 7
        self.type = MqttSnConstants.TYPE_PUBACK
        self.topic_id = 0
        self.message_id = 0
        self.return_code = 0
    
    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
        self.topic_id = struct.unpack('>H', value[2:4])[0]
        self.message_id = struct.unpack('>H', value[4:6])[0]
        self.return_code = value[6]
    
    def encode(self):
        try:
            data = struct.pack('>BBHHB', 
                             self.length,
                             self.type,
                             self.topic_id,
                             self.message_id,
                             self.return_code)
            return data
        except Exception as e:
            raise MqttSnClientException(e)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_topic_id(self):
        return self.topic_id
    
    def set_topic_id(self, topic_id):
        self.topic_id = topic_id
    
    def get_message_id(self):
        return self.message_id
    
    def set_message_id(self, message_id):
        self.message_id = message_id
    
    def get_return_code(self):
        return self.return_code
    
    def set_return_code(self, return_code):
        self.return_code = return_code

class PubCompPacket:
    
    def __init__(self):
        self.length = 6
        self.type = MqttSnConstants.TYPE_PUBCOMP
        self.topic_id = 0
        self.message_id = 0
    
    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
        self.topic_id = struct.unpack('>H', value[2:4])[0]
        self.message_id = struct.unpack('>H', value[4:6])[0]
    
    def encode(self):
        try:
            buffer = bytearray(self.length)
            buffer[0] = self.length
            buffer[1] = self.type
            struct.pack_into('>H', buffer, 2, self.topic_id)
            struct.pack_into('>H', buffer, 4, self.message_id)
            return bytes(buffer)
        except Exception as e:
            raise MqttSnClientException(str(e))
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_topic_id(self):
        return self.topic_id
    
    def set_topic_id(self, topic_id):
        self.topic_id = topic_id
    
    def get_message_id(self):
        return self.message_id
    
    def set_message_id(self, message_id):
        self.message_id = message_id

class PublishPacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_PUBLISH
        self.flags = 0
        self.topic_id = 0
        self.message_id = 0
        self.data = None
        self.extended = False
        self.length_extended = 0
    
    def encode(self):            
        try:
            if self.extended:
                self.length = 1
                self.length_extended = 0x09 + len(self.data)
                buffer_size = self.length_extended
            else:
                self.length = 0x07 + len(self.data)
                buffer_size = self.length
            
            buffer = bytearray()
            buffer.append(self.length)
            
            if self.extended:
                buffer.extend(struct.pack('>H', self.length_extended))
            
            buffer.append(self.type)
            buffer.append(self.flags)
            buffer.extend(struct.pack('>H', self.topic_id))
            buffer.extend(struct.pack('>H', self.message_id))
            buffer.extend(self.data)
            
            return bytes(buffer)
            
        except Exception as e:
            raise MqttSnClientException(e)
    
    def decode(self, value):
        offset = 0
        
        self.length = value[offset]
        offset += 1
        
        if self.length == 1:
            self.extended = True
            self.length_extended = struct.unpack('>H', value[offset:offset+2])[0]
            offset += 2
        
        self.type = value[offset]
        offset += 1
        
        self.flags = value[offset]
        offset += 1
        
        self.topic_id = struct.unpack('>H', value[offset:offset+2])[0]
        offset += 2
        
        self.message_id = struct.unpack('>H', value[offset:offset+2])[0]
        offset += 2
        
        if self.extended:
            data_length = self.length_extended - 9
        else:
            data_length = self.length - 7
        
        self.data = bytearray()
        for i in range(data_length):
            self.data.append(value[offset + i])
        
        self.data = bytes(self.data)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_flags(self):
        return self.flags
    
    def set_flags(self, flags):
        self.flags = flags
    
    def get_topic_id(self):
        return self.topic_id
    
    def set_topic_id(self, value):
        self.topic_id = value
    
    def get_message_id(self):
        return self.message_id
    
    def set_message_id(self, value):
        self.message_id = value
    
    def get_data(self):
        return self.data
        
    def get_dup(self) -> bool:
        return bool(self.flags & MqttSnConstants.FLAG_DUP)

    def get_qos(self) -> int:
        return (self.flags & MqttSnConstants.FLAG_QOS_MASK) >> 5

    def get_topic_type_id(self) -> int:
        return (self.flags & 0x3)

    def get_retain(self) -> bool:
        return bool(self.flags & MqttSnConstants.FLAG_RETAIN)

    def set_retain(self, value: bool):
        if value:
            # accende il bit RETAIN
            self.flags |= MqttSnConstants.FLAG_RETAIN
        else:
            # spegne il bit RETAIN
            self.flags &= ~MqttSnConstants.FLAG_RETAIN

    def set_dup(self, value: bool):
        if value:
            # accende il bit RETAIN
            self.flags |= MqttSnConstants.FLAG_DUP
        else:
            # spegne il bit RETAIN
            self.flags &= ~MqttSnConstants.FLAG_DUP

    def set_qos(self, value: int):
        if value not in (MqttSnConstants.QOS_0,
                       MqttSnConstants.QOS_1,
                       MqttSnConstants.QOS_2,
                       MqttSnConstants.QOS_N1):
            raise MqttSnClientException("QoS deve essere -1, 0, 1 o 2 per MQTT-SN")

        # Azzeriamo i bit QoS
        self.flags &= ~MqttSnConstants.FLAG_QOS_MASK

        # Impostiamo il QoS corretto usando le costanti
        if value == MqttSnConstants.QOS_0:
            self.flags |= MqttSnConstants.FLAG_QOS_0
        elif value == MqttSnConstants.QOS_1:
            self.flags |= MqttSnConstants.FLAG_QOS_1
        elif value == MqttSnConstants.QOS_2:
            self.flags |= MqttSnConstants.FLAG_QOS_1
        elif value == MqttSnConstants.QOS_N1:
            self.flags |= MqttSnConstants.FLAG_QOS_N1
                        
    def set_data(self, value):
        if isinstance(value, str):
            if value is not None and len(value.strip()) > MqttSnConstants.MAX_PAYLOAD_LENGTH_EXTENDED:
                raise MqttSnClientException(f"Payload '{value}' is too long (max {MqttSnConstants.MAX_PAYLOAD_LENGTH_EXTENDED})")
            if value is not None and len(value.strip()) > MqttSnConstants.MAX_PAYLOAD_LENGTH:
                self.extended = True
            self.data = value.encode('utf-8')
        else:
            if value is not None and len(value) > MqttSnConstants.MAX_PAYLOAD_LENGTH_EXTENDED:
                raise MqttSnClientException(f"Payload '{value}' is too long (max {MqttSnConstants.MAX_PAYLOAD_LENGTH_EXTENDED})")
            if value is not None and len(value) > MqttSnConstants.MAX_PAYLOAD_LENGTH:
                self.extended = True
            self.data = bytes(value) if value is not None else None

class PubRecPacket:
    def __init__(self):
        self.length = 6
        self.type = MqttSnConstants.TYPE_PUBREC
        self.topic_id = 0
        self.message_id = 0
    
    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
        self.topic_id = struct.unpack('>H', value[2:4])[0]
        self.message_id = struct.unpack('>H', value[4:6])[0]
    
    def encode(self):
        try:
            buffer = bytearray()
            buffer.append(self.length)
            buffer.append(self.type)
            buffer.extend(struct.pack('>H', self.topic_id))
            buffer.extend(struct.pack('>H', self.message_id))
            return bytes(buffer)
        except Exception as e:
            raise MqttSnClientException(str(e))
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_topic_id(self):
        return self.topic_id
    
    def set_topic_id(self, topic_id):
        self.topic_id = topic_id
    
    def get_message_id(self):
        return self.message_id
    
    def set_message_id(self, message_id):
        self.message_id = message_id

class PubRelPacket:
    
    def __init__(self):
        self.length = 6
        self.type = MqttSnConstants.TYPE_PUBREL
        self.topic_id = 0
        self.message_id = 0
    
    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
        self.topic_id = struct.unpack('>H', value[2:4])[0]
        self.message_id = struct.unpack('>H', value[4:6])[0]
    
    def encode(self):
        try:
            buffer = bytearray()
            buffer.append(self.length)
            buffer.append(self.type)
            buffer.extend(struct.pack('>H', self.topic_id))
            buffer.extend(struct.pack('>H', self.message_id))
            return bytes(buffer)
        except Exception as e:
            raise MqttSnClientException(str(e))
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_topic_id(self):
        return self.topic_id
    
    def set_topic_id(self, topic_id):
        self.topic_id = topic_id
    
    def get_message_id(self):
        return self.message_id
    
    def setmessage_id(self, message_id):
        self.message_id = message_id

class RegackPacket:
    
    def __init__(self):
        self.length = 7
        self.type = MqttSnConstants.TYPE_REGACK
        self.topic_id = 0
        self.message_id = 0
        self.return_code = 0
    
    def encode(self):
        try:
            return struct.pack('>BBhhB', self.length, self.type, self.topic_id, self.message_id, self.return_code)
        except Exception as e:
            raise MqttSnClientException(e)
    
    def decode(self, value):
        self.length, self.type, self.topic_id, self.message_id, self.return_code = struct.unpack('>BBhhB', value)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_topic_id(self):
        return self.topic_id
    
    def set_topic_id(self, topic_id):
        self.topic_id = topic_id
    
    def get_message_id(self):
        return self.message_id
    
    def set_message_id(self, message_id):
        self.message_id = message_id
    
    def get_return_code(self):
        return self.return_code
    
    def set_return_code(self, value):
        self.return_code = value

class RegisterPacket:
    
    def __init__(self):
        self.length = 0
        self.length_extended = 0
        self.extended = False
        self.topic_id = 0
        self.type = MqttSnConstants.TYPE_REGISTER
        self.message_id = 0
        self.topic_name = None

    def encode(self):
        try:
            if self.topic_name is None:
                raise MqttSnClientException("Topic name cannot be None")

            total_length = 6 + len(self.topic_name)
            buffer = bytearray()

            # Determina se serve la lunghezza estesa
            if total_length > MqttSnConstants.MAX_TOPIC_LENGTH:
                self.extended = True
                self.length_extended = total_length
                # Lunghezza estesa: 0x01 + 2 byte lunghezza
                buffer.extend(struct.pack('!BH', 0x01, self.length_extended))
            else:
                self.extended = False
                self.length = total_length
                buffer.extend(struct.pack('!B', self.length))

            buffer.extend(struct.pack('!B', self.type))
            buffer.extend(struct.pack('!H', self.topic_id))
            buffer.extend(struct.pack('!H', self.message_id))
            buffer.extend(self.topic_name)

            return bytes(buffer)
        except Exception as e:
            raise MqttSnClientException(f"Error encoding RegisterPacket: {e}")

    def decode(self, value: bytes):
        try:
            if len(value) < 6:
                raise MqttSnClientException("Invalid REGISTER packet: too short")

            # Controlla se è un pacchetto esteso
            if value[0] == 0x01:
                self.extended = True
                self.length_extended = struct.unpack('!H', value[1:3])[0]
                offset = 3
            else:
                self.extended = False
                self.length = struct.unpack('!B', value[0:1])[0]
                offset = 1

            self.type = struct.unpack('!B', value[offset:offset+1])[0]
            self.topic_id = struct.unpack('!H', value[offset+1:offset+3])[0]
            self.message_id = struct.unpack('!H', value[offset+3:offset+5])[0]

            total_length = self.length_extended if self.extended else self.length
            topic_name_length = total_length - (offset + 5)

            if topic_name_length < 0 or (offset + 5 + topic_name_length) > len(value):
                raise MqttSnClientException("Invalid REGISTER packet length")

            self.topic_name = value[offset+5:offset+5+topic_name_length]
        except Exception as e:
            raise MqttSnClientException(f"Error decoding RegisterPacket: {e}")

    def get_length(self) -> int:
        return self.length_extended if self.extended else self.length

    def get_type(self) -> int:
        return self.type

    def get_topic_id(self) -> int:
        return self.topic_id

    def set_topic_id(self, topic_id: int):
        self.topic_id = topic_id

    def get_message_id(self) -> int:
        return self.message_id

    def set_message_id(self, message_id: int):
        self.message_id = message_id

    def get_topic_name(self) -> str:
        if self.topic_name is None:
            return None
        return self.topic_name.decode('utf-8')

    def set_topic_name(self, value):
        if value is None:
            raise MqttSnClientException("Topic name cannot be None")
        
        if isinstance(value, str):
            if value is not None and len(value.strip()) > MqttSnConstants.MAX_TOPIC_LENGTH_EXTENDED:
                raise MqttSnClientException(f"Payload '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH_EXTENDED})")
            if value is not None and len(value.strip()) > MqttSnConstants.MAX_TOPIC_LENGTH:
                self.extended = True
            self.topic_name = value.encode('utf-8')
        else:
            if value is not None and len(value) > MqttSnConstants.MAX_TOPIC_LENGTH_EXTENDED:
                raise MqttSnClientException(f"Payload '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH_EXTENDED})")
            if value is not None and len(value) > MqttSnConstants.MAX_TOPIC_LENGTH:
                self.extended = True
            self.topic_name = bytes(value) if value is not None else None

class SearchGatewayPacket:
    
    def __init__(self):
        self.length = 3
        self.type = MqttSnConstants.TYPE_SEARCHGW
        self.radius = 0
    
    def encode(self):
        try:
            return struct.pack('BBB', self.length, self.type, self.radius)
        except Exception as e:
            raise MqttSnClientException(e)
    
    def decode(self, value):
        self.length, self.type, self.radius = struct.unpack('BBB', value)
    
    def get_length(self):
        return self.length
    
    def get_radius(self):
        return self.radius
    
    def set_radius(self, value):
        self.radius = value

class SubAckPacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_SUBACK
        self.flags = 0
        self.topic_id = 0
        self.message_id = 0
        self.return_code = 0
    
    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
        self.flags = value[2]
        self.topic_id = struct.unpack('>H', value[3:5])[0]
        self.message_id = struct.unpack('>H', value[5:7])[0]
        self.return_code = value[7]

    def encode(self):
        self.length = 8  # SUBACK sempre 8 byte
        return struct.pack(
            '>BBBHHB',
            self.length,
            self.type,
            self.flags,
            self.topic_id,
            self.message_id,
            self.return_code
        )
            
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_flags(self):
        return self.flags
    
    def get_topic_id(self):
        return self.topic_id
    
    def get_message_id(self):
        return self.message_id
    
    def get_return_code(self):
        return self.return_code
    
    def set_message_id(self, value: int):
        self.message_id = value

    def set_topic_id(self, value: int):
        self.topic_id = value

    def set_flags(self, value = int):
        self.flags = value

    def set_return_code(self, value):
        self.return_code = value
                        
class SubPacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_SUBSCRIBE
        self.flags = 0
        self.message_id = 0
        self.topic_name = None
        self.topic_id = 0
    
    def encode(self):
        try:
            if self.topic_name is None:
                self.length = 7
            else:
                self.length = 0x05 + len(self.topic_name)
            
            buffer = bytearray()
            buffer.extend(struct.pack('B', self.length))
            buffer.extend(struct.pack('B', self.type))
            buffer.extend(struct.pack('B', self.flags))
            buffer.extend(struct.pack('>H', self.message_id))
            
            if self.topic_name is None:
                buffer.extend(struct.pack('>H', self.topic_id))
            else:
                buffer.extend(self.topic_name)
                
        except Exception as e:
            raise MqttSnClientException(e)
        
        return bytes(buffer)

    def decode(self, data: bytes):
        try:
            buffer = memoryview(data)

            # lunghezza e tipo
            self.length = buffer[0]
            self.type = buffer[1]

            if self.type != MqttSnConstants.TYPE_SUBSCRIBE:
                raise MqttSnClientException(f"Invalid message type {self.type}, expected SUBSCRIBE")

            # flags
            self.flags = buffer[2]

            # message id
            self.message_id = struct.unpack_from(">H", buffer, 3)[0]

            # calcolo campo rimanente
            remaining = self.length - 5  # già letti: len(1) + type(1) + flags(1) + msgId(2)

            if remaining == 2:
                # topic id
                self.topic_id = struct.unpack_from(">H", buffer, 5)[0]
                self.topic_name = None
            elif remaining > 0:
                # topic name
                self.topic_name = bytes(buffer[5:5 + remaining])
                self.topic_id = 0
            else:
                raise MqttSnClientException("Malformed SUBSCRIBE packet")

        except Exception as e:
            raise MqttSnClientException(e)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_flags(self):
        return self.flags
    
    def set_flags(self, value):
        self.flags = value
    
    def get_message_id(self):
        return self.message_id
    
    def set_message_id(self, message_id):
        self.message_id = message_id
    
    def get_topic_name(self):
        return self.topic_name.decode() if self.topic_name else None
    
    def set_topic_name(self, value):
        if isinstance(value, str):
            if value is not None and len(value.strip()) > MqttSnConstants.MAX_TOPIC_LENGTH:
                raise MqttSnClientException(f"TopicName '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH})")
            self.topic_name = value.encode()
        elif isinstance(value, bytes):
            if value is not None and len(value) > MqttSnConstants.MAX_TOPIC_LENGTH:
                raise MqttSnClientException(f"TopicName '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH})")
            self.topic_name = bytes(value)
        self.topic_id = 0
    
    def get_topic_id(self):
        return self.topic_id
    
    def set_topic_id(self, value):
        self.topicName = None
        self.topic_id = value

    def get_dup(self) -> bool:
        return bool(self.flags & MqttSnConstants.FLAG_DUP)

    def get_qos(self) -> int:
        return (self.flags & MqttSnConstants.FLAG_QOS_MASK) >> 5

    def get_topic_type_id(self) -> int:
        return (self.flags & 0x3)

class UnsubackPacket:
    
    def __init__(self):
        self.length = 4
        self.type = MqttSnConstants.TYPE_UNSUBACK
        self.message_id = 0
    
    def decode(self, value):
        self.length, self.type, self.message_id = struct.unpack('>BBH', value)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
       
    def get_message_id(self):
        return self.message_id
    
    def set_message_id(self, message_id):
        self.message_id = message_id

class UnsubscribePacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_UNSUBSCRIBE
        self.flags = 0
        self.message_id = 0
        self.topicName = None
        self.topic_id = 0
    
    def encode(self):
        try:
            if self.topicName is not None:
                self.length = 0x05 + len(self.topicName)
            else:
                self.length = 7
            
            buffer = bytearray()
            buffer.append(self.length)
            buffer.append(self.type)
            buffer.append(self.flags)
            buffer.extend(struct.pack('>H', self.message_id))
            
            if self.topicName is not None:
                buffer.extend(self.topicName)
            else:
                buffer.extend(struct.pack('>H', self.topic_id))
                
        except Exception as e:
            raise MqttSnClientException(e)
        
        return bytes(buffer)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_flags(self):
        return self.flags
    
    def set_flags(self, flags):
        self.flags = flags
    
    def get_message_id(self):
        return self.message_id
    
    def set_message_id(self, value):
        self.message_id = value
    
    def get_topic_name(self):
        return self.topicName.decode('utf-8')
    
    def set_topic_name(self, value):
        if isinstance(value, str):
            if value is not None and len(value.strip()) > MqttSnConstants.MAX_TOPIC_LENGTH:
                raise MqttSnClientException(f"TopicName '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH})")
            self.topicName = value.encode('utf-8')
        elif isinstance(value, bytes):
            if value is not None and len(value) > MqttSnConstants.MAX_TOPIC_LENGTH:
                raise MqttSnClientException(f"TopicName '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH})")
            self.topicName = bytes(value)
    
    def get_topic_id(self):
        return self.topic_id
    
    def set_topic_id(self, value):
        self.topic_id = value


class WillMessagePacket:
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_WILLMSG
        self.message = b''
        self.extended = False
        self.length_extended = 0

    def set_message(self, value: str):
        value = value.strip()
        encoded = value.encode()
        if len(encoded) > MqttSnConstants.MAX_PAYLOAD_LENGTH_EXTENDED:
            raise MqttSnClientException(
                f"Will Message '{value}' is too long "
                f"(max {MqttSnConstants.MAX_PAYLOAD_LENGTH_EXTENDED})"
            )
        self.message = encoded
        # Decide se usare formato esteso
        self.extended = (len(encoded) + 2) > 255  # Length + Type + Msg

    def encode(self) -> bytes:
        if not self.message:
            raise MqttSnClientException("Message not set")

        buffer = bytearray()

        if self.extended:
            # formato esteso: [0x01][len_hi][len_lo][type][message...]
            total_len = 3 + 1 + len(self.message)  # 3-byte length + type + message
            buffer.append(0x01)
            buffer.extend(struct.pack(">H", total_len))
        else:
            # formato corto: [len][type][message...]
            total_len = 2 + len(self.message)
            buffer.append(total_len)

        buffer.append(self.type)
        buffer.extend(self.message)

        return bytes(buffer)

    def decode(self, data: bytes):
        if len(data) < 2:
            raise MqttSnClientException("Invalid WILLMSG packet: too short")

        offset = 0
        self.extended = (data[0] == 0x01)

        if self.extended:
            if len(data) < 4:
                raise MqttSnClientException("Invalid extended WILLMSG packet: too short")

            self.length = 1
            self.length_extended = struct.unpack(">H", data[1:3])[0]
            self.type = data[3]
            offset = 4

            if self.length_extended != len(data):
                raise MqttSnClientException(
                    f"Invalid extended length: expected {self.length_extended}, got {len(data)}"
                )
        else:
            self.length = data[0]
            self.type = data[1]
            offset = 2

            if self.length != len(data):
                raise MqttSnClientException(
                    f"Invalid length: expected {self.length}, got {len(data)}"
                )

        self.message = data[offset:]

    def get_message(self) -> str:
        return self.message.decode()

    def get_length(self):
        return self.length_extended if self.extended else self.length

    def get_type(self):
        return self.type

class WillMessageReqPacket:
    
    def __init__(self):
        self.type = MqttSnConstants.TYPE_WILLMSGREQ
        self.length = 2
    
    def decode(self, value):
        self.length = value[0]
        self.type = value[1]
    
    def encode(self):
        try:
            buffer = bytearray(self.length)
            buffer[0] = self.length
            buffer[1] = self.type
            return bytes(buffer)
        except Exception as e:
            raise MqttSnClientException(str(e))
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type

class WillMessageRespPacket:
    
    def __init__(self):
        self.length = 4
        self.type = MqttSnConstants.TYPE_WILLMSGRESP
        self.return_code = 0
    
    def decode(self, value):
        self.length, self.type, self.return_code = struct.unpack('BBB', value[:3])
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_return_code(self):
        return self.return_code

class WillMessageUpdatePacket:
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_WILLMSGUPD
        self.message = None
    
    def encode(self):
        try:
            self.length = 2 + len(self.message)
            buffer = bytearray()
            buffer.append(self.length)
            buffer.append(self.type)
            buffer.extend(self.message)
            return bytes(buffer)
        except Exception as e:
            raise MqttSnClientException(e)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_message(self):
        return self.message.decode('utf-8')
    
    def set_message(self, value):
        if isinstance(value, str):
            if value is not None and len(value.strip()) > MqttSnConstants.MAX_PAYLOAD_LENGTH:
                raise MqttSnClientException(f"Will Message '{value}' is too long (max {MqttSnConstants.MAX_PAYLOAD_LENGTH})")
            self.message = value.strip().encode('utf-8')
        elif isinstance(value, bytes):
            if value is not None and len(value) > MqttSnConstants.MAX_PAYLOAD_LENGTH:
                raise MqttSnClientException(f"Will Message '{value}' is too long (max {MqttSnConstants.MAX_PAYLOAD_LENGTH})")
            self.message = bytes(value)

class WillTopicPacket:
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_WILLTOPIC
        self.flags = 0
        self.topic_name = b""

    def encode(self) -> bytes:
        if self.topic_name is None:
            raise MqttSnClientException("Topic name not set")
        self.length = 3 + len(self.topic_name)
        try:
            return struct.pack(f'>BBB{len(self.topic_name)}s',
                               self.length,
                               self.type,
                               self.flags,
                               self.topic_name)
        except Exception as e:
            raise MqttSnClientException(e)

    def decode(self, data: bytes):
        try:
            if len(data) < 3:
                raise MqttSnClientException("Invalid WILLTOPIC packet: too short")

            # primi 3 byte: length, type, flags
            self.length, self.type, self.flags = struct.unpack(">BBB", data[:3])

            if self.length != len(data):
                raise MqttSnClientException(
                    f"Invalid length: expected {self.length}, got {len(data)}"
                )

            # resto: topic name
            self.topic_name = data[3:]
        except Exception as e:
            raise MqttSnClientException(e)

    def get_length(self):
        return self.length

    def get_type(self):
        return self.type

    def get_flags(self):
        return self.flags

    def set_flags(self, flags: int):
        self.flags = flags

    def get_topic_name(self) -> str:
        return self.topic_name.decode()

    def set_topic_name(self, value: str):
        value = value.strip()
        if len(value) > MqttSnConstants.MAX_TOPIC_LENGTH:
            raise MqttSnClientException(f"Will Topic Name '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH})")
        self.topic_name = value.encode()

    def get_qos(self) -> int:
        return (self.flags & MqttSnConstants.FLAG_QOS_MASK) >> 5

    def get_retain(self) -> bool:
        return bool(self.flags & MqttSnConstants.FLAG_RETAIN)
        
class WillTopicReqPacket:
    def __init__(self):
        self.length = 2
        self.type = MqttSnConstants.TYPE_WILLTOPICREQ

    def decode(self, value: bytes):
        if len(value) < 2:
            raise MqttSnClientException("Pacchetto troppo corto")
        self.length, self.type = struct.unpack('>BB', value[:2])

    def encode(self) -> bytes:
        try:
            return struct.pack('>BB', self.length, self.type)
        except Exception as e:
            raise MqttSnClientException(e)

    def get_length(self):
        return self.length

    def get_type(self):
        return self.type

class WillTopicResPacket:
    
    def __init__(self):
        self.length = 4
        self.type = MqttSnConstants.TYPE_WILLTOPICRESP
        self.return_code = 0
    
    def decode(self, value):
        self.length, self.type, self.return_code = struct.unpack('BBB', value[:3])
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_return_code(self):
        return self.return_code

class WillTopicUpdateReqPacket:
    
    def __init__(self):
        self.length = 0
        self.type = MqttSnConstants.TYPE_WILLTOPICUPD
        self.flags = 0
        self.topic_name = None
    
    def encode(self):
        try:
            self.length = 3 + len(self.topic_name)
            buffer = bytearray()
            buffer.append(self.length)
            buffer.append(self.type)
            buffer.append(self.flags)
            buffer.extend(self.topic_name)
            return bytes(buffer)
        except Exception as e:
            raise MqttSnClientException(e)
    
    def get_length(self):
        return self.length
    
    def get_type(self):
        return self.type
    
    def get_flags(self):
        return self.flags
    
    def set_flags(self, flags):
        self.flags = flags
    
    def get_topic_name(self):
        return self.topic_name.decode('utf-8')
    
    def set_topic_name(self, value):
        if isinstance(value, str):
            if value is not None and len(value.strip()) > MqttSnConstants.MAX_TOPIC_LENGTH:
                raise MqttSnClientException(f"Will Topic Name '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH})")
            self.topic_name = value.strip().encode('utf-8')
        elif isinstance(value, (bytes, bytearray)):
            if value is not None and len(value) > MqttSnConstants.MAX_TOPIC_LENGTH:
                raise MqttSnClientException(f"Will Topic Name '{value}' is too long (max {MqttSnConstants.MAX_TOPIC_LENGTH})")
            self.topic_name = bytes(value)
