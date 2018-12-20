#!/usr/bin/env python

# ASU CES Syringe Pump Programmer
# By Isaac Roll
# 2015

import datetime
import json 
import os
import serial

version = 3.0
header = ('                 Syringe Pump Programmer for ISMA and IS2 v'+str(version)+'\n')

# Default data block used to create the data file if it isn't present
# pump name, pump address, pos per ml, program name, program string
pump = ['NONE',0,0,'Query','/1Q']
# port name, baud rate
com = ['COM1',9600]
pump1 = ['IS2',1,490431,'Query','/1Q\r']
pump2 = ['ISMA',1,490431,'Query','/1Q\r']
pump3 = ['NIU',2,490431,'Query','/1Q\r']
pump4 = ['IS2B',1,490431,'Query','/1Q\r']
data = [com,pump1,pump2,pump3,pump4]

# Attempts to update data from saved file
try:
    file = open('pumper_data.txt', 'r')
    data = json.load(file)
    file.close()
except:
    print(header)
    wait=input('File read error! Default values used. Press ENTER.')

# Replaces default data with that from the saved file
com = data[0]
pump1 = data[1]
pump2 = data[2]
pump3 = data[3]
pump4 = data[4]
    
# Wipes screen between menus
def clearscreen():
    os.system('cls' if os.name=='nt' else 'clear')

# Main Menu
def main_menu():
    clearscreen()
    print(header)
    print('                                   Main Menu\n')
    print('Current Pump:',pump[0],'at address',pump[1],'on',com[0])
    print('\n1. Pump and Communications Settings')
    print('\n2. Check Communication')
    print('\n3. Push-Pull')
    print('\n4. Program Cycle')
    print('\nt. Terminate all commands')
    print('\nq. Quit\n\n\n\n')
    main_menu=input('Select: ')
    if main_menu=='1':
        pumpselect()
    elif main_menu=='2':
        pumpcheck()
    elif main_menu=='3':
        pushpull()
    elif main_menu=='4':
        program()
    elif main_menu=='T' or main_menu=='t':
        terminate()
    elif main_menu=='Q' or main_menu=='q':
        softexit()
    else:
        pass

# Selects pump and edits pump and communications data
def pumpselect():
    clearscreen()
    print(header)
    print('                        Pump and Communications Settings\n')
    print('Current Pump:',pump[0],'at address',pump[1],'on',com[0])
    print('\n1. Pump 1:', pump1[0])
    print('\n2. Pump 2:', pump2[0])
    print('\n3. Pump 3:', pump3[0])
    print('\n4. Pump 4:', pump4[0])
    print('\n5. Communication Settings')
    print('\nENTER to return to Main Menu\n')
    pump_choice=input('Select: ')
    if pump_choice=='5':
        comedit()
    elif pump_choice=='1':
        pumpedit(pump1)
    elif pump_choice=='2':
        pumpedit(pump2)
    elif pump_choice=='3':
        pumpedit(pump3)
    elif pump_choice=='4':
        pumpedit(pump4)
    else:
        pass

def comedit():
    clearscreen()
    print(header)
    print('                         Edit Communications Settings\n')
    print('Current Pump:',pump[0],'at address',pump[1],'on',com[0])
    print('\n1. Serial Port:',com[0])
    print('\n2. Baud Rate:',com[1])
    print('\nENTER to return to Pump Select\n')
    com_edit=input('Select: ')
    if com_edit=='1':
        com[0]=input('\nEnter new port name: ')
    elif com_edit=='2':
        com[1]=int(input('\nEnter new baud rate: '))
    else:
        pass

def pumpedit(this_pump):
    clearscreen()
    global pump
    print(header)
    print('                      Select Pump or Edit Pump Settings\n')
    print('Current Pump:',pump[0],'at address',pump[1],'on',com[0])
    print('\n1. Select this pump (',this_pump[0],')')
    print('\n2. Calibrate pump with dispense data')
    print('\n3. Change calibration constant')
    print('\n4. Change pump name')
    print('\n5. Change pump address')
    print('\nENTER to return to Pump Select\n')
    pump_edit=input('Select: ')
    if pump_edit=='1':
        pump=this_pump
    if pump_edit=='2':
        try:
            v_prog=float(input('\nEnter Programmed Volume (mL): '))
            v_disp=float(input('\nEnter Dispensed Volume (mL): '))
            cal_ratio = v_prog / v_disp
            old_ratio = this_pump[2]
            this_pump[2] = int(old_ratio * cal_ratio)
            wait=input('\nCalibration updated!')
        except:
            pass
    if pump_edit=='3':
        try:
            print('\nCurrent Constant:',this_pump[2],'pos per mL )')
            new_constant=abs(int(input('\nEnter new constant or ENTER to cancel: ')))
            if new_constant != 0 and new_constant != '':
                this_pump[2]=new_constant
            else:
                pass
        except:
            pumpedit(this_pump)
    if pump_edit=='4':
        try:
            this_pump[0]=input('\nEnter new pump name: ')
        except:
            pass
    if pump_edit=='5':
        try:
            this_pump[1]=int(input('\nEnter new pump address: '))
        except:
            pass
    else:
        pass

# Queries the pump; basically testing if the connection is good and the pump is healthy
def pumpcheck():
    clearscreen()
    print(header)
    print('                     Pump Communications and Function Tests\n')
    writecommand('/'+str(pump[1])+'Q\r')
    wait=input('\nENTER to continue')

# Sends a terminate signal to current pump
def terminate():
    clearscreen()
    print(header)
    writecommand('/'+str(pump[1])+'T\r')
    wait=input('\nENTER to continue')

# Push and Pull operation, for advancing the syringe without a loop
def pushpull():
    clearscreen()
    print(header)
    print('                              Push-Pull Operation\n')
    print('Current Pump:',pump[0],'at address',pump[1],'on',com[0])
    print('\n1. Push-Pull Operation')
    print('\nENTER to return to Main Menu')
    push_pull=input('\nSelect: ')
    if push_pull=='1':
        clearscreen()
        try:
            print(header)
            print('                        Pump and Communications Settings\n')
            print('Current Pump:',pump[0],'at address',pump[1],'on',com[0])
            input_vol = float(input('\nEnter Push (+) or Pull (-) Volume (mL): '))
            output_vol = int(abs(input_vol * pump[2]))
            time = abs(float(input('\nEnter Stroke Time (s): ')))
            velocity = int(output_vol / time)
            if input_vol > 0:
                # clockwise = Draw = D; counterclockwise = Push = P
                direction = 'P'
            else:
                direction = 'D'
            zero = ('/'+str(pump[1])+'z1000000000R\r')
            writecommand(zero)
            wait=input('\nMotor Zeroed!')
            writecommand('/'+str(pump[1])+'V'+str(velocity)+str(direction)+str(output_vol)+'R\r')
            wait=input('\nENTER to continue')
        except:
            pass
    else:
        pass

# Program operation, sets up loops
def program():
    clearscreen()
    print(header)
    print('                                Program Operation\n')
    print('Current Pump:',pump[0],'at address',pump[1],'on',com[0])
    print('\nSaved Program Name:',pump[3])
    print('\n1. Execute Saved Program')
    print('\n2. Create New Program')
    print('\nENTER to return to Main Menu')
    prog_select=input('\nSelect: ')
    if prog_select=='1':
        zero = ('/'+str(pump[1])+'z1000000000R\r')
        writecommand(zero)
        wait=input('\nMotor Zeroed!')
        writecommand(pump[4])
        wait=input('\nENTER to continue')
        program()
    elif prog_select=='2':
        programedit()
    else:
        pass
    
def programedit():
    clearscreen()
    print(header)
    print('                                  Program Editor\n')
    print('\nCurrent Program:',pump[3])
    print('\n',pump[4])
    print('\n1. Guided Program Entry')
    #print('\n2. Manual Program Entry')
    print('\nENTER to return to Program Menu')
    prog_edit=input('\nSelect: ')
    if prog_edit=='1':
        try:
            clearscreen()
            print(header)
            print('                                  Program Editor\n')
            new_name=input('\nProgram Name (optional): ')
            stroke_input=abs(float(input('\nStroke Volume (mL): ')))
            drawtime=abs(float(input('\nDraw Time (s): ')))
            filled_wait=abs(int(1000 * float(input('\nFilled Wait Time (s): '))))
            pushtime=abs(float(input('\nPush Time (s): ')))
            empty_wait=abs(int(1000 * float(input('\nEmpty Wait Time (s): '))))
            cycles=abs(int(input('\nNumber of Strokes: ')))
            stroke = int(stroke_input * pump[2])
            draw_velocity = int(stroke / drawtime)
            push_velocity = int(stroke / pushtime)
            if filled_wait>30000:
                filled_loop='gM30000'
                fdiv=filled_wait//30000
                filled_loop+='G'+str(fdiv)
                fmod=int(filled_wait%30000)
                filled_loop+='M'+str(fmod)
            else:
                filled_loop='M'+str(filled_wait)
            if empty_wait>30000:
                empty_loop='gM30000'
                ediv=empty_wait//30000
                empty_loop+='G'+str(ediv)
                emod=int(empty_wait%30000)
                empty_loop+='M'+str(emod)
            else:
                empty_loop='M'+str(empty_wait)
            new_command=('/'+str(pump[1])+'gV'+str(draw_velocity)+'D'+str(stroke)+filled_loop+'V'+str(push_velocity)+'P'+str(stroke)+empty_loop+'G'+str(cycles)+'R\r')
            pump[3]=new_name
            pump[4]=new_command
            wait=input('Program Saved!')
        except:
            pass
    elif prog_edit=='2':
        try:
            clearscreen()
            print(header)
            print('                                  Program Editor\n')
            new_name=input('\nProgram Name (optional):')
            new_command=input('\nCommand:')
            do_this=input('\nAbandon (a), Save without executing (s), Execute without saving (e)\n or Save and Execute (ENTER)')
            if do_this=='a' or do_this=='A':
                pass
            elif do_this=='s' or do_this=='S':
                pump[3]=new_name
                pump[4]=new_command
            elif do_this=='e' or do_this=='E':
                writecommand(new_command)
                wait=input('\nENTER to continue')
            else:
                pump[3]=new_name
                pump[4]=new_command
                writecommand(pump[4])
                wait=input('\nENTER to continue')
        except:
            pass
    else:
        pass    
# Opens serial port, writes command, reads (and prints) response
def writecommand(command):
    try:
        clearscreen()
        print(header)
        print('                                Communicating...\n')
        port = serial.Serial(com[0], com[1], timeout=0.1)
        port.write(bytes(command.encode('ascii')))
        print('\nWrote',command)
        response_bytes = port.read(100)
        port.close()
        try:
            timestamp = datetime.datetime.now()
            timestring = str(timestamp.strftime('%Y/%m/%d %H:%M:%S '))
            logline = (timestring+command+'\n')
            log = open('pumper_log.txt', 'a+')
            log.write(logline)
            log.close()
        except:
            print('Logging Error!')
#        response_hex = [hex(i) for i in response_bytes]
        print('\nRead',list(response_bytes))
        home_address = response_bytes.index(48)
        if response_bytes[home_address + 1] == 96 or response_bytes[home_address+1] == 64:
            print('\nCommand accepted without error!')
        elif response_bytes[home_address + 1] == 98:
            print('\nCommand detected but malformed!')
        else:
            print('\nMotor Error!')
    except:
        print('\nCommunications Error!')

# Saves data to the file and closes gracefully
def softexit():
    global quitter
    data = [com,pump1,pump2,pump3,pump4]
    file = open('pumper_data.txt', 'w')
    json.dump(data, file)
    file.close()
    quit()

def main_loop():
    always_true = 1
    while always_true == 1:
        main_menu()

main_loop()
