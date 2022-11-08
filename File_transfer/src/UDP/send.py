import os, socket, time, locale
from struct import *
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

host = input("Enter the host: ")
port = int(input("Enter the port: "))
file_path = input("Enter the file path: ")
package_size = int(input("Enter the package size: "))
expected_number_of_packages = os.path.getsize(file_path) // package_size + 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)
server_address = (host, port)
sock.connect(server_address)
print (f"Connected to {host} port {port} for sending file")

file_extension = file_path.split('.')[-1]
file_name = file_path.split('\\')[-1].split('.')[0]

first_header = b',' + str(file_name).encode() + b',' + str(file_extension).encode() + b',' + str(package_size).encode() + b',' + str(expected_number_of_packages).encode()

sock.send(first_header.zfill(100))

while True:
    try:
        response = sock.recvfrom(100)
        if response[0] == b'ACK_HEADER':
            sock.sendto(b'OK', server_address)
            break
    except socket.timeout:
        sock.send(first_header.zfill(100))

fp = open(file_path, 'rb')
send_log = open(f"send_log_{file_name}_{package_size}.txt", 'w')
package_number = 0
start_time = time.time()
last_packages = []

while True:

    try:
        msg = sock.recvfrom(100)
        if msg[0] == b'FINISHED':
            print("Finished")
            break
        if msg[0] == b'ACK_HEADER':
            continue
        expected_packages = [int(x) for x in msg[0].split(b',')]
        if expected_packages != [x[0] for x in last_packages]: 
            last_packages = []

        if len(last_packages) == 4:
            for package in last_packages:
                sock.sendto(package[1], server_address)
            continue
        
        for i in expected_packages:
            fp.seek(package_size * i)
            package = fp.read(package_size)
            num_package = pack('i', i)
            last_packages.append([i, num_package + package])
            sock.sendto(num_package + package, server_address)

    except socket.timeout:
        for package in last_packages:
            sock.sendto(package[1], server_address)
        continue

end_time = time.time()

send_log.write(f"File sent in {end_time - start_time} seconds")

fp.close()