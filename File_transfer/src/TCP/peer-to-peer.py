import os, socket, time, locale
from struct import *

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def receive(host, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    conn, addr = sock.accept()

    print("Connection accepted with " + str(addr) + " for receiving file")

    first_header = conn.recv(100)
    file_name, file_extension, package_size, expected_number_of_packages = first_header.split(b',')[1:]
    expected_number_of_packages = int(expected_number_of_packages)
    package_size = int(package_size)
    file_extension = file_extension.decode()
    file_name = file_name.decode()

    fp = open(f"{file_name}_{package_size}.{file_extension}", 'wb')

    total_bytes = 0
    package_number = 0
    receive_log = open(f"receive_log_{file_name}_{package_size}.txt", 'w')

    start_time = time.time()

    while True:
        data = conn.recv(package_size + 4)
        if not data:
            break
        if len(data) < package_size + 4:
            while len(data) < package_size + 4:
                remaining_bytes = conn.recv(package_size + 4 - len(data))
                if not remaining_bytes:
                    break
                data += remaining_bytes
        package_number = int.from_bytes(data[:4], byteorder='little')

        fp.write(data[4:])
        total_bytes += len(data)

    end_time = time.time()

    if package_number == expected_number_of_packages:
        print("Successfully received all packages")

    speed = total_bytes * 8 / (end_time - start_time)
    speed = locale.format_string('%.10f', speed, True)

    receive_log.write(f"\nTime elapsed using {locale.format_string('%.0f', package_size, True)} bytes plus 4 bytes as package number: {locale.format_string('%.10f',(end_time - start_time), True)}s, total bytes received: {locale.format_string('%.0f', total_bytes, True)} bytes\n")
    receive_log.write(f"Expected number of packages: {locale.format_string('%.0f', expected_number_of_packages, True)} packages received : {locale.format_string('%.0f', package_number, True)}\n")
    receive_log.write(f"Speed: {speed} bits/s\n")
    receive_log.close()
    fp.close()
    return

def send(host, port, file_path, package_size):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print("Connection established with " + host + ":" + str(port))

    expected_number_of_packages = os.path.getsize(file_path) // package_size + 1

    file_extension = file_path.split('.')[-1]
    file_name = file_path.split('\\')[-1].split('.')[0]

    send_log = open(f"send_log_{file_name}_{package_size}.txt", 'w')

    fp = open(file_path, 'rb')
    total_bytes = 0

    first_header = b',' + str(file_name).encode() + b',' + str(file_extension).encode() + b',' + str(package_size).encode() + b',' + str(expected_number_of_packages).encode()

    sock.send(first_header.zfill(100))

    send_log.write(f"Expected number of packages: {expected_number_of_packages}\n")

    start_time = time.time()

    for i in range(expected_number_of_packages):

        msg = fp.read(package_size)
        total_bytes += len(msg) + 4
        final_result = pack(f'I{len(msg)}s', i+1, msg)
        sock.send(final_result)

    end_time = time.time()

    speed = (total_bytes * 8 / (end_time - start_time))
    speed = locale.format_string('%.10f', speed, True)


    send_log.write(f"Time elapsed using {locale.format_string('%.0f', package_size, True)} bytes plus 4 bytes as package number: {locale.format_string('%.10f', (end_time - start_time), True)}s, total bytes sent: {locale.format_string('%.0f', total_bytes, True)} bytes\n")
    send_log.write(f"Speed: {speed} bits/s\n")
    send_log.close()
    fp.close()
    return

def main():
    
    while True:
        try:
            host = input("Host: ")
            socket.gethostbyname(host)
            break
        except socket.gaierror:
            print("Invalid host")

    port = int(input("Port: "))

    while True:

        mode = input("Mode (s/r): ")

        if mode == 's':

            while True:
                file_path = input("File path: ")
                if os.path.isfile(file_path):
                    package_size = int(input("Package size: "))
                    send(host, port, file_path, package_size)
                    break
                else:
                    print("File not found")
            
            break

        elif mode == 'r':
            receive(host, port)
            break
        
        else:
            print("Invalid mode")

if __name__ == "__main__":
    main()