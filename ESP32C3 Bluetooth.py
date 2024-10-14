
import ubluetooth
from micropython import const
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

class BLE():
    def __init__(self, name):   
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.connHandle = 0
# mark us as not connected     
        self.disconnected()
# This is the interrupt handler   
        self.ble.irq(self.ble_irq)
# register ourselves with UIDs and the URT service
        self.register()
# advertise ourselves to the world
        self.advertise()

    def connected(self,data):
        self.conHandle = data[0]

    def disconnected(self):        
        pass

# Interrupt handler
    def ble_irq(self, event, data):
        
# Someone wants to talk to us       
        if event == _IRQ_CENTRAL_CONNECT:
            self.connected(data)
            
# We've been disconnected, advertise ourselfs again       
        elif event == _IRQ_CENTRAL_DISCONNECT:
            self.advertise()
            self.disconnected()
            
# Echo back the message   
        elif event == _IRQ_GATTS_WRITE:            
            buffer = self.ble.gatts_read(self.rx)
            message = buffer.decode('UTF-8').strip()
            self.send(message)
            
           
    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_write(self.tx, data + '\n',True)

    def advertise(self):
        name = bytes(self.name, 'UTF-8')
        self.ble.gap_advertise(100, bytearray(b'\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name)


ble = BLE("ESP32 Echo")
