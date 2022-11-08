import os, socket, time, locale
from struct import *
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
host = input("Enter the host: ")
port = int(input("Enter the port: "))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (host, port)
sock.bind(server_address)

print (f"Connected to {host} port {port} for receiving file")

while True:
    first_header = sock.recvfrom(100)
    global sender
    sender = (first_header[1][0], first_header[1][1])
    sock.connect(sender)
    first_header = first_header[0]

    global file_name, file_extension, package_size, expected_number_of_packages
    file_name, file_extension, package_size, expected_number_of_packages = first_header.split(b',')[1:]
    expected_number_of_packages = int(expected_number_of_packages)
    package_size = int(package_size)
    file_extension = file_extension.decode()
    file_name = file_name.decode()

    while True:
        sock.sendto(b'ACK_HEADER', sender)
        # Change the socket host to the sender host
        response = sock.recvfrom(100)
        print(response)
        if response[0] == b'OK':
            print("Received confirmation")
            break
    break


fp = open(f"{file_name}.{file_extension}", 'wb')
receive_log = open(f"receive_log_{file_name}_{package_size}.txt", 'w')
package_num = 0

ffp = open(f"receive_log_{file_name}_{package_size}_bruh.txt", 'w')

received_packages = []
wanted_packages = [0,1,2,3]
packages_count = 0
start_time = time.time()

while True:

    sock.sendto(b','.join([str(x).encode() for x in wanted_packages]), sender)
    ffp.write(str(wanted_packages) + ' - ')
    received_packages = []

    for i in range(4):
            
        msg = sock.recvfrom(package_size + 4)
        packages_count += 1
        package_num = unpack('i', msg[0][:4])[0]
        package = msg[0][4:]
        received_packages.append([package_num, package])

    received_packages.sort(key=lambda x: x[0])

    ffp.write(str([x[0] for x in received_packages]) + ' {}\n'.format(wanted_packages == [x[0] for x in received_packages]))

    if [x[0] for x in received_packages] == wanted_packages:

        for package in received_packages:

            fp.write(package[1])
            wanted_packages.append(package[0] + 4)
            wanted_packages = wanted_packages[1:]

    if wanted_packages[0] >= expected_number_of_packages:
        end_time = time.time()
        sock.sendto(b'FINISHED', sender)
        print("Finished")
        break

total_bytes = expected_number_of_packages * package_size
speed = total_bytes * 8 / (end_time - start_time)
speed = locale.format_string('%.10f', speed, True)

receive_log.write(f"\nTime elapsed using {locale.format_string('%.0f', package_size, True)} bytes plus 4 bytes as package number: {locale.format_string('%.10f',(end_time - start_time), True)}s, total bytes received: {locale.format_string('%.0f', total_bytes, True)} bytes\n")
receive_log.write(f"Expected number of packages: {locale.format_string('%.0f', expected_number_of_packages, True)} packages transmitted (including retransmission) : {locale.format_string('%.0f', packages_count, True)} loss percentage : {locale.format_string('%.2f', (1 - (packages_count / expected_number_of_packages)) * -100, True)}%\n")
receive_log.write(f"Speed: {speed} bits/s\n")
receive_log.close()
fp.close()