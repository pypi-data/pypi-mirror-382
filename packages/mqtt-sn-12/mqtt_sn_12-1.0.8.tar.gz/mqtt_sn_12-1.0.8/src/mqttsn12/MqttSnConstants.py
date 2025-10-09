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
class MqttSnConstants:
    
    DEFAULT_PORT = 2442
    DEFAULT_TIMEOUT = 60
    DEFAULT_KEEP_ALIVE = 30
    
    MAX_PACKET_LENGTH = 255
    MAX_PAYLOAD_LENGTH = MAX_PACKET_LENGTH - 7
    MAX_TOPIC_LENGTH = MAX_PACKET_LENGTH - 6
    MAX_CLIENT_ID_LENGTH = 23
    MAX_WIRELESS_NODE_ID_LENGTH = 252
    
    # The byte buffer (the byte array) is the data that is to be sent in the UDP datagram.
    # The length of the above buffer, 65508 bytes, is the maximum amount of data you can send in a single UDP packet.
    MAX_PACKET_LENGTH_EXTENDED = 63 * 1024
    MAX_PAYLOAD_LENGTH_EXTENDED = MAX_PACKET_LENGTH_EXTENDED - 7
    MAX_TOPIC_LENGTH_EXTENDED = MAX_PACKET_LENGTH_EXTENDED - 6
    
    TYPE_ADVERTISE = 0x00
    TYPE_SEARCHGW = 0x01
    TYPE_GWINFO = 0x02
    TYPE_CONNECT = 0x04
    TYPE_CONNACK = 0x05
    TYPE_WILLTOPICREQ = 0x06
    TYPE_WILLTOPIC = 0x07
    TYPE_WILLMSGREQ = 0x08
    TYPE_WILLMSG = 0x09
    TYPE_REGISTER = 0x0A
    TYPE_REGACK = 0x0B
    TYPE_PUBLISH = 0x0C
    TYPE_PUBACK = 0x0D
    TYPE_PUBCOMP = 0x0E
    TYPE_PUBREC = 0x0F
    TYPE_PUBREL = 0x10
    TYPE_SUBSCRIBE = 0x12
    TYPE_SUBACK = 0x13
    TYPE_UNSUBSCRIBE = 0x14
    TYPE_UNSUBACK = 0x15
    TYPE_PINGREQ = 0x16
    TYPE_PINGRESP = 0x17
    TYPE_DISCONNECT = 0x18
    TYPE_WILLTOPICUPD = 0x1A
    TYPE_WILLTOPICRESP = 0x1B
    TYPE_WILLMSGUPD = 0x1C
    TYPE_WILLMSGRESP = 0x1D
    TYPE_FRWDENCAP = 0xFE
    
    ACCEPTED = 0x00
    REJECTED_CONGESTION = 0x01
    REJECTED_INVALID = 0x02
    REJECTED_NOT_SUPPORTED = 0x03
    
    TOPIC_TYPE_NORMAL = 0x00
    TOPIC_TYPE_PREDEFINED = 0x01
    TOPIC_TYPE_SHORT = 0x02
    
    FLAG_DUP = 0x1 << 7
    FLAG_QOS_0 = 0x0 << 5
    FLAG_QOS_1 = 0x1 << 5
    FLAG_QOS_2 = 0x2 << 5
    FLAG_QOS_N1 = 0x3 << 5
    FLAG_QOS_MASK = 0x3 << 5
    FLAG_RETAIN = 0x1 << 4
    FLAG_WILL = 0x1 << 3
    FLAG_CLEAN = 0x1 << 2
    
    PROTOCOL_ID = 0x01
    
    QOS_0 = 0
    QOS_1 = 1
    QOS_2 = 2
    QOS_N1 = -1
