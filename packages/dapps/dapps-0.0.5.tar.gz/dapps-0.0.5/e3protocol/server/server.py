import socket
import asn1tools

SERVER_PORT = 5000
BUFFER_SIZE = 362144
CHUNK_SIZE = 8192

defs = asn1tools.compile_files('../defs/e3.asn', codec='per')

def receive_in_chunks(conn):
    data = bytearray()
    while True:
        chunk = conn.recv(CHUNK_SIZE)
        if not chunk:
            break  # Connection closed
        data.extend(chunk)
        if len(chunk) < CHUNK_SIZE:
            break  # Last chunk received (assuming client sends in fixed chunks)
    return bytes(data)

def handle_client(conn):
    while True:
        data = receive_in_chunks(conn)
        if not data:
            # No more data received, client has closed the connection
            print("Client disconnected")
            break

        print("Received data:")
        pdu = defs.decode('E3-PDU', data)
        if pdu[0] == 'setupRequest':
            e3_setup_request = pdu[1]
            print(f"Received Setup Request: ID = {e3_setup_request.get('id')}, dApp ID = {e3_setup_request['dAppIdentifier']}, RAN Function List = {e3_setup_request['ranFunctionList']}, Type = {e3_setup_request.get('type')}")
            # Create response PDU with proper field names
            setup_response = ('setupResponse', {
                'id': 1,  # Response message ID
                'requestId': e3_setup_request.get('id', 1),  # Original request ID
                'responseCode': 'positive',
                'ranFunctionList': e3_setup_request.get('ranFunctionList', [])
            })
            encoded_response = defs.encode('E3-PDU', setup_response)
            print("Send Response data:", encoded_response.hex())
            conn.sendall(encoded_response)
        elif pdu[0] == 'setupResponse' or pdu[0] == 'controlAction':
            raise ValueError('E3 dApp Termination should not receive this kind of messages ', pdu[0])
        elif pdu[0] == 'subscriptionRequest':
            e3_subscription_request = pdu[1]
            print(f"Received Subscription Request: ID = {e3_subscription_request.get('id')}, Type = {e3_subscription_request.get('type')}, RAN Function ID = {e3_subscription_request.get('ranFunctionIdentifier')}")
            # Create subscription response
            subscription_response = ('subscriptionResponse', {
                'id': 2,  # Response message ID
                'requestId': e3_subscription_request.get('id', 1),
                'responseCode': 'positive'
            })
            encoded_response = defs.encode('E3-PDU', subscription_response)
            print("Send Subscription Response data:", encoded_response.hex())
            conn.sendall(encoded_response)
        elif pdu[0] == 'messageAck':
            e3_message_ack = pdu[1]
            print(f"Received Message ACK: ID = {e3_message_ack.get('id')}, Request ID = {e3_message_ack.get('requestId')}, Response Code = {e3_message_ack.get('responseCode')}")
        elif pdu[0] == 'indicationMessage':
            print('E3-IndicationMessage')
            e3_indication_message = pdu[1]
            print(f"Message ID: {e3_indication_message.get('id')}")
            protocolData = e3_indication_message['protocolData']
            print(len(list(protocolData)))

            # # Only for the test purposes
            # control_message = ('controlAction', {'id': 3, 'actionData': bytes([1,2,3])} )
            # encoded_control = defs.encode('E3-PDU', control_message)
            # print("Send Control data:", encoded_control.hex())
            # conn.sendall(encoded_control)

        else:
            raise ValueError('Unrecognized value ', pdu)

def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SCTP)
    server_socket.bind(('127.0.0.1', SERVER_PORT))
    server_socket.listen(5)
    print('Start server')

    while True:
        conn, addr = server_socket.accept()
        print('Received connection')
        handle_client(conn)
        conn.close()

if __name__ == "__main__":
    main()
