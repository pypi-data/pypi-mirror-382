# mqttsn12-python3-client
Python3 Client implementation of the Protocol MQTT-SN 1.2 (https://mqtt.org/mqtt-specification/ or https://groups.oasis-open.org/higherlogic/ws/public/document?document_id=66091).

The library was tested with EMQX (https://www.emqx.com/en) and Hive MQ Edge (https://www.hivemq.com/products/hivemq-edge/).

Start from this url http://www.steves-internet-guide.com/mqtt-sn/ for understanding more about the protocol MQTT-SN.

The whole project is available on https://github.com/marcoratto/mqttsn12-python3-client

## Use

Along with the library, two command-line tools are provided: **mqtt_sn_pub** and **mqtt_sn_sub**

Create a Python environment
`python -m venv env`

Enable the new Python environment
`source env/bin/activate`

Install the library
`pip install mqtt-sn-12`

Execute the publisher client tool
`mqtt_sn_pub`

Execute the subscriber client tool
`mqtt_sn_sub`

## mqtt_sn_pub 

```
usage: mqtt_sn_pub [opts] -t <topic> -m <message>

MQTT-SN publisher in Python

options:
  -t, --topic TOPIC     MQTT-SN topic name to publish to
  -d, --enable-debug    Enable debug messages
  -c, --disable-clean-session
                        Disable clean session / enable persistent client mode
  -h, --host HOST       MQTT-SN host to connect to (default: 127.0.0.1)
  -i, --clientid CLIENTID
                        Client ID to use. Defaults to 'mqtt-sn-python-' + pid
  -I, --id-prefix       Define client id as prefix + pid (useful with broker clientid_prefixes)
  -k, --keepalive KEEPALIVE
                        Keep alive in seconds (default: 30)
  -e, --sleep SLEEP     Sleep duration in seconds when disconnecting (default: 0)
  -p, --port PORT       Network port (default: 2442)
  -C, --msg-count MSG_COUNT
                        disconnect and exit after receiving the 'msg_count' messages.
  -1, --one             exit after receiving a single message.
  -q, --qos {0,1}       Quality of Service (0, 1). Default: 0
  -s, --stdin-message   Read one whole message from STDIN
  -T, --topicid TOPICID
                        Pre-defined MQTT-SN topic ID to publish to
  --timeout TIMEOUT     Timeout (default: 60)
  --will-payload WILL_PAYLOAD
                        Payload for the client Will
  --will-payload-file WILL_PAYLOAD_FILE
                        Payload for the client Will loaded from a file
  --will-qos {0,1}      QoS level for the client Will. Default: 0
  --will-retain         Make the client Will retained
  --will-topic WILL_TOPIC
                        The topic on which to publish the client Will
``` 

## mqtt_sn_sub

```
usage: mqtt_sn_pub [opts] -t <topic> -m <message>

MQTT-SN publisher in Python

options:
  -t, --topic TOPIC     MQTT-SN topic name to publish to
  -m, --message MESSAGE
                        Message payload to send
  -d, --enable-debug    Enable debug messages
  -c, --disable-clean-session
                        Disable clean session / enable persistent client mode
  -f, --file FILE       A file to send as the message payload
  -h, --host HOST       MQTT-SN host to connect to (default: 127.0.0.1)
  -i, --clientid CLIENTID
                        Client ID to use. Defaults to 'mqtt-sn-python-' + pid
  -I, --id-prefix       Define client id as prefix + pid (useful with broker clientid_prefixes)
  -k, --keepalive KEEPALIVE
                        Keep alive in seconds (default: 30)
  -e, --sleep SLEEP     Sleep duration in seconds when disconnecting (default: 0)
  -l, --line-mode       Read messages from stdin, sending a separate message for each line
  -n, --null-message    Send a null (zero length) message
  -p, --port PORT       Network port (default: 2442)
  -q, --qos {-1,0,1}    Quality of Service (-1, 0, 1). Default: 0
  -r, --retain          Mark the message as retained
  -s, --stdin-message   Read one whole message from STDIN
  -T, --topicid TOPICID
                        Pre-defined MQTT-SN topic ID to publish to
  --timeout TIMEOUT     Timeout (default: 60)
  --will-payload WILL_PAYLOAD
                        Payload for the client Will
  --will-payload-file WILL_PAYLOAD_FILE
                        Payload for the client Will loaded from a file
  --will-qos {0,1}      QoS level for the client Will. Default: 0
  --will-retain         Make the client Will retained
  --will-topic WILL_TOPIC
                        The topic on which to publish the client Will
  --repeat REPEAT       Repeat publish N times (default: 1)
  --repeat-delay REPEAT_DELAY
                        Delay in seconds between repeats (default: 0)
``` 

## Code Coverage

The following table summarizes the code coverage of the library:

| Name                                         |    Stmts |     Miss |   Cover |
|--------------------------------------------- | -------: | -------: | ------: |
| src/mqttsn12/MqttSnConstants.py              |       61 |        0 |    100% |
| src/mqttsn12/\_\_init\_\_.py                 |        0 |        0 |    100% |
| src/mqttsn12/client/MqttSnClient.py          |      708 |      126 |     82% |
| src/mqttsn12/client/MqttSnClientException.py |       12 |        8 |     33% |
| src/mqttsn12/client/\_\_init\_\_.py          |        0 |        0 |    100% |
| src/mqttsn12/packets.py                      |     1013 |      363 |     64% |
| tests/unit\_test\_publisher.py               |      120 |        1 |     99% |
| tests/unit\_test\_subscriber.py              |      293 |       20 |     93% |
|                                    **TOTAL** | **2207** |  **518** | **77%** |

## Message Types

Below you can find the list of the Message Type implemented:

|MsgType|Field|Status|Note|
|-|-|-|-|
|0x00|ADVERTISE|NA||
|0x01|SEARCHGW|Implemented||
|0x02|GWINFO|Implemented||
|0x03|reserved|NA||
|0x04|CONNECT|Implemented||
|0x05|CONNACK|Implemented||
|0x06|WILLTOPICREQ|Implemented||
|0x07|WILLTOPIC|Implemented||
|0x08|WILLMSGREQ|Implemented||
|0x09|WILLMSG|Implemented||
|0x0A|REGISTER|Implemented||
|0x0B|REGACK|Implemented||
|0x0C|PUBLISH|Implemented||
|0x0D|PUBACK|Implemented||
|0x0E|PUBCOMP|NA||
|0x0F|PUBREC|NA||
|0x10|PUBREL|NA||
|0x11|reserved|NA||
|0x12|SUBSCRIBE|Implemented||
|0x13|SUBACK|Implemented||
|0x14|UNSUBSCRIBE|Implemented||
|0x15|UNSUBACK|Implemented||
|0x16|PINGREQ|Implemented||
|0x17|PINGRESP|Implemented||
|0x18|DISCONNECT|Implemented||
|0x19|reserved|NA||
|0x1A|WILLTOPICUPD|Implemented||
|0x1B|WILLTOPICRESP|Implemented||
|0x1C|WILLMSGUPD|Implemented||
|0x1D|WILLMSGRESP|Implemented||
|0x1E-0xFD|reserved|NA||
|0xFE|Encapsulated message|NA||
|0xFF|reserved|NA||
