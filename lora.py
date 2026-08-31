#!/usr/bin/env /home/andrew/Documents/PROGRAMAS_USO_PROPIO/lora_payload_RAK11720_python/.venv/bin/python

import serial
import time
import os
# import readline
import subprocess as sp
import pandas as pd
import serial.tools.list_ports
import platform

# Importación segura de readline (solo para Linux)
try:
    import readline
except ImportError:
    pass


device = "USB0"
pre_payload = ""
fin_payload = ">"
df = 0

msg_inicial = "&93@"
msg_ack = "&81@"

comando = "cls" if os.name == "nt" else "clear"

def delay(ms): #delay en milisegundos
    time.sleep(ms/1000)


ser = None #Lo inicio vacio
# delay(100)

def search_RAK11720():
    global ser
    ports = list(serial.tools.list_ports.comports())
    count = 0

    for port in ports:
        description = port.description.lower()
        device = port.device # Esto guardará 'COMx' en Windows o '/dev/ttyxxx' en Linux

        count = 0
  
        if "/dev/ttyUSB" in device and platform.system() == "Linux":
            print(f"Puerto: {device}")
            ser = serial.Serial(f'{device}', 115200, timeout = 1)
            while count < 1: #Sacando RX
                response = Send_AT("AT+VER=?", timeout_espera = 1)
                # print(response)

                find_str = response[0].find("RAK11720")
                if find_str != -1:
                    print(f"RAK11720 CONECTADO! {device}")
                    return True
                count += 1

        if "COM" in device and platform.system() == "Windows":
            print(f"Puerto: {device}")
            ser = serial.Serial(f'{device}', 115200, timeout = 1)

            while count < 1: #Sacando RX
                response = Send_AT("AT+VER=?", timeout_espera = 1)
                print(response)

                find_str = response[0].find("RAK11720")
                if find_str != -1:
                    print(f"RAK11720 CONECTADO! {device}")
                    return True
                count += 1

    print("ERROR: No se detectó ningún módulo RAK11720 conectado.")
    return False
        

def Psend(command):
    print(command)
    Psend_AT = f"AT+PSEND={command}\r\n"

    
    ser.write(Psend_AT.encode())

    return True

def Send_AT(comando, timeout_espera = 2): 
    global ser

    ser.reset_input_buffer()
    ser.reset_output_buffer()

    comando_full = comando + "\r\n"
    ser.write(comando_full.encode("utf-8"))

    respuesta = []
    tiempo_inicio = time.time()

    while True:

        try:
  
            linea = ser.readline().decode("utf-8", errors="ignore").strip()
            delay(10)

            if linea:
                respuesta.append(linea)

                if linea in ["OK", "ERROR", "AT_COMMAND_NOT_FOUND"]:
                    break

            if time.time() - tiempo_inicio > timeout_espera:
                respuesta.append("TIMEOUT_SIN_RESPUESTA")
                break
        except serial.serialutil.SerialException:
            print("Tiene otro monitor serie abierto cierrelo para reintentar!")

    return respuesta

def modbuscrc(msg: str) -> int:
    # Convertimos el string de texto plano a bytes reales (ej: "HOLA" -> b'HOLA')
    msg_bytes = msg.encode('ascii') 
    
    crc = 0xFFFF
    for byte in msg_bytes:
        # Ahora 'byte' es el valor numérico de la letra (ej: 'H' es 72)
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def opcion_1():
    global ser, pre_payload
    try:
        while True:
            comando = input("Ingrese el comando a enviar: ")

            sp.run([comando], shell=True) 

            crc_num = modbuscrc(f"{comando}#")
            crc_ascii = f"{crc_num:04X}"

            print(f"CRC: {crc_ascii}")

            #PAYLOAD PARA ENVIAR LORA
            payload = f"{pre_payload}{comando}#{crc_ascii}{fin_payload}"
            payload_hex = payload.encode('ascii').hex().upper() #codifica en ascii, convierte en hex y convierte todo a mayusculas

            print(f"Enviando Payload: {payload}")
            print(f"payload HEX: {payload_hex}")
            print("...................................................................\r\n")

            Psend(payload_hex) #Envio mensaje LoRa

    except KeyboardInterrupt:
        print("Programa terminado por el usuario")

def opcion_2():
    global msg_inicial
    global msg_ack

    try:
        while True:
            try: 
                line_bytes = ser.readline()
                line_str = line_bytes.decode('utf-8').rstrip() # Decodifica en UTF-8
                # print(f"{line_str}")

                init_msg = line_str.find("&00")
                other_msg = line_str.find("TPK")

                if init_msg != -1:
                    print(f"{line_str}")
                    crc_num = modbuscrc(f"{msg_inicial}#")
                    crc_ascii = f"{crc_num:04X}"
        
                    print(f"CRC: {crc_ascii}")
        
                    #PAYLOAD PARA ENVIAR LORA
                    payload = f"{pre_payload}{msg_inicial}#{crc_ascii}{fin_payload}"
                    payload_hex = payload.encode('ascii').hex().upper() #codifica en ascii, convierte en hex y convierte todo a mayusculas
        
                    print(f"Enviando Payload: {payload}")
                    print(f"payload HEX: {payload_hex}")
                    print("...................................................................\r\n")
        
                    Psend(payload_hex) #Envio mensaje LoRa
                    init_msg = -1

                elif init_msg == -1 and other_msg != -1: 
                    print(f"{line_str}")
                    crc_num = modbuscrc(f"{msg_ack}#")
                    crc_ascii = f"{crc_num:04X}"
        
                    print(f"CRC: {crc_ascii}")
        
                    #PAYLOAD PARA ENVIAR LORA
                    payload = f"{pre_payload}{msg_ack}#{crc_ascii}{fin_payload}"
                    payload_hex = payload.encode('ascii').hex().upper() #codifica en ascii, convierte en hex y convierte todo a mayusculas
        
                    print(f"Enviando Payload: {payload}")
                    print(f"payload HEX: {payload_hex}")
                    print("...................................................................\r\n")
        
                    Psend(payload_hex) #Envio mensaje LoRa
                    other_msg = -1
                
                    

            except ValueError:
                continue

    except KeyboardInterrupt:
        print("Programa terminado por el usuario")

def opcion_3():
    global ser

    try:
        while True:
            try:
                seleccion = float(input("Ingrese nueva frecuencia LoRa en MHz (Ej: 915): "))
                break

            except ValueError:
                print("ERROR debe ingresar un valor Numerico!")
    except KeyboardInterrupt:
        sp.run([comando], shell=True)
        print("Programa interrupido por el usuario")

    frecuencia_hz = int(seleccion * 1e6)
    print(f"Frecuencia seleccionada: {seleccion}Mhz --> {frecuencia_hz} Hz")


    while True: #Sacando RX
        response = Send_AT("AT+PRECV=0")
        print("AT > AT+PRECV=0") 
        print(f"AT < {response}")
        if response[0] == "OK":
            break
        

    while True: #Configurando nueva frecuencia
        response = Send_AT(f"AT+PFREQ={frecuencia_hz}")
        print(f"AT > AT+PFREQ={frecuencia_hz}")
        print(f"AT < {response}")
        if response[0] == "OK":
            break

    while True: #Poniendo RX con posibilidad de TX
        response = Send_AT("AT+PRECV=65535") #Sacando de RX
        print(f"AT > AT+PRECV=65535")
        print(f"AT < {response}")
        if response[0] == "OK":
            break

def opcion_4(): #Agregar mas ADDRS y seleccionar otro dispositivo
    global df, pre_payload

    df = pd.read_csv('addr_lora.csv')

    print("Direcciones LoRa guardadas")
    print(df)

    try:
        while True:
            try:
                seleccion = int(input("Ingrese la direccion que quiera usar: "))

                if(seleccion > len(df) and seleccion < 0):
                    print("Debe elegir una de las direcciones guardadas")
                else: #Crea el nuevo Pre payload
                    addrH = df.iloc[seleccion, 0]
                    addrL = df.iloc[seleccion, 1]

                    print(f"AddrH: {addrH}")
                    print(f"AddrL: {addrL}")

                    pre_payload = f"<TPK:{addrH},{addrL}:"
               
                    break


            except ValueError:
                print("Debe elegir un numero")
    except KeyboardInterrupt:
        sp.run([comando], shell=True)
        print("Programa interrupido por el usuario")

def opcion_5(): #Agregar mas ADDRS y seleccionar otro dispositivo
    global df, pre_payload

    flag_confirm = False
    df = pd.read_csv('addr_lora.csv')

    print("Direcciones LoRa guardadas")
    print(df)

    try:
        while True:
            try:
                seleccion1 = int(input("Ingrese la nueva AddrH a registrar: "), 16)
                seleccion2 = int(input("Ingrese la nueva AddrL a registrar: "), 16)

                while True:

                    confirmacion = input(f"AddrH: {seleccion1:X}, AddrL: {seleccion2:X} ---> Son correctas? S/n: ")

                    if(confirmacion == "S" or confirmacion == "s"):
                        print("Registrando nuevas Addrs...")

                        with open('addr_lora.csv', 'a', encoding='utf-8') as archivo:
                            archivo.write(f"\n{seleccion1:X},{seleccion2:X}")
                        flag_confirm = True

                        df = pd.read_csv('addr_lora.csv')
                        print("Direcciones LoRa guardadas")
                        print(df)

                        break

                    elif(confirmacion == "N" or confirmacion == "n"):
                        print("Seleccione nuevas..")
                        break
                    else:
                        print("Seleccione una opcion valida S/n!")

                if flag_confirm == True:
                    flag_confirm = False
                    break

            except ValueError:
                print("Debe elegir dato correcto")
    except KeyboardInterrupt:
        sp.run([comando], shell=True)
        print("Programa interrupido por el usuario")
        
def menu():
    try:
        while True:
            print('''   
            -----------------
            Menu de opciones
            -----------------
            1) Modo Manual.
            2) Modo ACK.
            3) Configurar Frecuencia.
            4) Seleccionar Address LoRa.
            5) Registrar Nuevas Address LoRa.
    
            0) Quit
            ''')

            try:
                seleccion = int(input("Ingrese el numero del menu: "))
                if seleccion == 0:
                    print("Saliendo del programa")
                    print("____________________________________________________________\r\n")
                    exit()
                elif seleccion == 1:
                    sp.run([comando], shell=True)
                    print("                     MODO MANUAL ACTIVADO")
                    print("____________________________________________________________\r\n")
                    opcion_1()
                elif seleccion == 2:
                    sp.run([comando], shell=True)
                    print("                     MODO ACK ACTIVADO")
                    print("____________________________________________________________\r\n")
                    opcion_2()
                elif seleccion == 3:
                    sp.run([comando], shell=True)
                    print("                MODO CONFIGURACION FREQ ACTIVADO")
                    print("____________________________________________________________\r\n")
                    opcion_3()
                elif seleccion == 4:
                    sp.run([comando], shell=True)
                    print("                 MODO SELECCION ADDRS ACTIVADO")
                    print("____________________________________________________________\r\n")
                    opcion_4()
                elif seleccion == 5:
                    sp.run([comando], shell=True)
                    print("                 MODO REGISTRO NUEVAS ADDRS")
                    print("____________________________________________________________\r\n")
                    opcion_5()
              
                else:
                    print("Seleccione una opcion valida")
                    print("____________________________________________________________\r\n")

            except ValueError:
                print("Error reintente!")
    except KeyboardInterrupt:
        sp.run([comando], shell=True)
        print("Programa interrupido por el usuario")


def main(): #Funcion principal
    global df, pre_payload

    if search_RAK11720() == False:
        exit()

    #Predefinicion de la primera opcion
    df = pd.read_csv('addr_lora.csv')

    addrH = df.iloc[0, 0]
    addrL = df.iloc[0, 1]

    print(f"AddrH: {addrH}")
    print(f"AddrL: {addrL}")

    pre_payload = f"<TPK:{addrH},{addrL}:"
    print(f"Pre_payload: {pre_payload}")

    sp.run([comando], shell=True)
    menu()


########################################################################################################
#EJECUCION PRINCIPAL


if __name__ == "__main__":
    main()
