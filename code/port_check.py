import serial.tools.list_ports

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    if len(ports) == 0:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for port in ports:
            print(port.device)

if __name__ == "__main__":
    list_serial_ports()
