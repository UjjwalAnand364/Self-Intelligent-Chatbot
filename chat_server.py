import socket
import select 
import time
import os
from random import randint, randrange
import smtplib
from pathlib import Path
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

HEADER_LENGTH=10
IP="127.0.0.1"
PORT=1234
i=0

server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) # allows to reconnect, just in case a port is already in use

server_socket.bind((IP,PORT))
server_socket.listen(100)

sockets_list=[server_socket]
clients = {} 
signups={"Ujjwal":["whatdoweknow8604@gmail.com","nopes2"],"Parth":['hi@gmail.com','yess2']}

def receive_msg(client_socket):
    try:
        message_header=client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length= int(message_header.decode("utf-8").strip())
        return{"header":message_header,"data":client_socket.recv(message_length)}
    except:
        return False

def process_credentials(client_socket,user):
    error='You are not registered yet! Please sign up to chat or re-enter credentials!'

    print('Unregistered login attempt by',user['data'].decode("utf-8"))
    error=bytes(f"{error}","utf-8")
    error_header=f"{len(error):<{HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(error_header+error)

    msg=str(signups).encode("utf-8")
    msg_header=f'{len(msg):<{HEADER_LENGTH}}'.encode("utf-8")
    client_socket.send(msg_header+msg)
    email=receive_msg(client_socket)
    try:
        if email['data'].decode('utf-8')=='EXIT!!!':
            return
    except:
        pass
    password=receive_msg(client_socket)
    new_user=receive_msg(client_socket)
    try:
        signups[new_user['data'].decode('utf-8')]=[email['data'].decode('utf-8'),password['data'].decode('utf-8')]
        print(signups)
    except:
        pass
    return

def send_mail(send_from, send_to, subject, message, path,password,
            server='smtp.gmail.com', port=465):

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(message))

    context=ssl.create_default_context()
    with smtplib.SMTP_SSL(server,port,context=context) as smtp:
        smtp.login(send_from, password)
        smtp.sendmail(send_from, send_to, msg.as_string())

def forgot_password(client_socket):
    key_list=signups.keys()
    true=0
    gmail=receive_msg(client_socket)

    for item in key_list:
        if gmail['data'].decode('utf-8')==signups[item][0]:
            reply='Accepted'.encode('utf-8')
            reply_header=f'{len(reply):<{HEADER_LENGTH}}'.encode('utf-8')
            client_socket.send(reply_header+reply)

            true+=1
            os.chdir('C:\\Users\\dell\\OneDrive\\Documents')
            f=open('password.txt','r')
            password=f.readline()
            os.chdir('C:\\Users\\dell\\OneDrive\\Documents\\Python\\Socket programming')
            code=randint(1000, 9999)

            try:
                send_mail('ujjwalanand8604@gmail.com',signups[item][0],'Please find the reset code.',f'Your requested code for resetting the password: {code}.\n If not requested by you, you can safely ignore this mail.','attendance_report_consolidated.csv',password)
            except:
                print('Cannot connect to the internet!')
                break

            iteration=1
            enter_code(client_socket,item,code,iteration)
            break
    if true==0:
        reply='Rejected'.encode('utf-8')
        reply_header=f'{len(reply):<{HEADER_LENGTH}}'.encode('utf-8')
        client_socket.send(reply_header+reply)

def enter_code(client_socket,item,code,iteration):
        activation_code=receive_msg(client_socket)
        new_pass=receive_msg(client_socket)
        
        if activation_code['data'].decode('utf-8')==str(code):
            signups[item][1]=new_pass['data'].decode('utf-8')

            success='Password changed successfully!'.encode('utf-8')
            success_header=f"{len(success):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(success_header+success)
        else:
            iteration+=1
            if iteration <4:
                failure='Wrong activation code input.'.encode('utf-8')
                failure_header=f"{len(failure):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(failure_header+failure)
                enter_code(client_socket,item,code,iteration)
            else:
                failure='Critical iterations reached.'.encode('utf-8')
                failure_header=f"{len(failure):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(failure_header+failure)
                return

while True:
    read_sockets, _, exception_sockets=select.select(sockets_list,[],sockets_list)

    for notified_socket in read_sockets:
        if notified_socket==server_socket:
            client_socket,client_address=server_socket.accept()

            user=receive_msg(client_socket)
            password=receive_msg(client_socket)
            
            if user is False: 
                continue
            elif user['data'].decode('utf-8')=='RESERVED EMAIL':
                process_credentials(client_socket,user)
                continue
            elif user['data'].decode('utf-8')=='RESERVED [EMAIL2]':
                forgot_password(client_socket)
                continue
            elif user['data'].decode('utf-8') not in signups:
                process_credentials(client_socket,user)
                continue
            username=user['data']
            username_header=f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(username_header+username)

            key_list=signups.keys()
            pass_err=0
            pass_list=[]
            pass_error_msg='Wrong password!'

            for item in key_list:
                pass_list.append(signups[item][1]+item)

            if password['data'].decode('utf-8')+username.decode('utf-8') not in pass_list:
                pass_error=pass_error_msg.encode('utf-8')
                pass_error_header=f'{len(pass_error):<{HEADER_LENGTH}}'.encode('utf-8')
                client_socket.send(pass_error_header+pass_error)
                continue

            pass_verify='Verified'
            pass_verified=pass_verify.encode('utf-8')
            pass_verified_header=f'{len(pass_verified):<{HEADER_LENGTH}}'.encode('utf-8')
            client_socket.send(pass_verified_header+pass_verified)

            sockets_list.append(client_socket)
            clients[client_socket]=user
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")
            for client in clients:
                if client_socket!=client:
                    user_joined=user['data'].decode('utf-8')+' has joined the chat.'
                    user_joined=user_joined.encode('utf-8')
                    user_joined_header=f'{len(user_joined):<{HEADER_LENGTH}}'.encode('utf-8')
                    client.send(user_joined_header+user_joined)

            clients_list=clients.keys()
            clients_users=''
            for client in clients_list:
                clients_users=clients_users+' '+clients[client]['data'].decode('utf-8')

            clients_users+=' IMPORTANT[SOBREMESSA]MESSAGE[91267]'
            clients_usernames=clients_users.encode('utf-8')
            clients_usernames_header=f'{len(clients_usernames):<{HEADER_LENGTH}}'.encode('utf-8')
            for client_sock in clients:
                client_sock.send(clients_usernames_header+clients_usernames)
            
        else:
            message=receive_msg(notified_socket)
            if message is False:
                print('5')
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                client_left=clients[notified_socket]['data'].decode('utf-8')+' has left the chat.'
                client_left=client_left.encode('utf-8')
                client_left_header=f'{len(client_left):<{HEADER_LENGTH}}'.encode('utf-8')

                sockets_list.remove(notified_socket)
                del clients[notified_socket]

                clients_list=clients.keys()
                clients_left=''
                for client in clients_list:
                    clients_left=clients_left+' '+clients[client]['data'].decode('utf-8')

                clients_left+=' IMPORTANT[ANTIMESSA]MESSAGE[52396]'
                clients_left=clients_left.encode('utf-8')
                clients_left_header=f'{len(clients_left):<{HEADER_LENGTH}}'.encode('utf-8')

                for client_sock in clients:
                    client_sock.send(client_left_header+client_left)
                    client_sock.send(clients_left_header+clients_left)

                continue
            if 'EMPTY[NULLMESSA]OPERATION[27465]' in message['data'].decode('utf-8'):
                continue
            if 'TYPING[GREETMESA]OPERATION[12567]' in message['data'].decode('utf-8'):
                clients_typing=''
                clients_list=clients.keys()
                
                for client in clients_list:
                    if client==notified_socket:
                        clients_typing=clients_typing+' '+clients[client]['data'].decode('utf-8')+'(typing)'
                    else:
                        clients_typing=clients_typing+' '+clients[client]['data'].decode('utf-8')
                clients_typing+=' TYPING[GREETMESA]OPERATION[12567]'
                
                clients_typing=clients_typing.encode('utf-8')
                clients_typing_header=f'{len(clients_typing):<{HEADER_LENGTH}}'.encode('utf-8')

                for client_sock in clients:
                    if client_sock!=notified_socket:
                        client_sock.send(clients_typing_header+clients_typing)
                continue
            
            clients_online=''
            if 'IMPORTANT[ANTIMESSA]MESSAGE[52396]' in message['data'].decode('utf-8'):
                for client in clients_list:
                    clients_online=clients_online+' '+clients[client]['data'].decode('utf-8')
                clients_online+=' IMPORTANT[ANTIMESSA]MESSAGE[52396]'

                clients_online=clients_online.encode('utf-8')
                clients_online_header=f'{len(clients_online):<{HEADER_LENGTH}}'.encode('utf-8')

                for client_soc in clients:
                    if client_soc!=notified_socket:
                        client_soc.send(clients_online_header+clients_online)
            if 'FILEGO[FILEMESSA]OPERATION[83729]' in message['data'].decode('utf-8'):
                filename=receive_msg(notified_socket)
                file_size=receive_msg(notified_socket)
                user=clients[notified_socket]

                list1=filename['data'].decode('utf-8').split('/')
                file_name=list1[-1]
                
                file=open(file_name,'wb')
                chunk=notified_socket.recv(int(file_size['data'].decode('utf-8')))
                file.write(chunk)

                file_info=('FILEGO[FILEMESSA]OPERATION[83729]>'+file_name+'>'+str(file_size['data'].decode('utf-8'))+'>'+user['data'].decode('utf-8')).encode('utf-8')
                file_info_header=f'{len(file_info):<{HEADER_LENGTH}}'.encode('utf-8')
                print(file_info_header.decode('utf-8'))
                for client_socket in clients:
                    if client_socket!=notified_socket:
                        client_socket.send(file_info_header+file_info)
                file.close()

                file2=open(file_name,'rb')
                data=file2.read()
                print(clients,notified_socket)
                for client_socket in clients:
                    if client_socket!=notified_socket:
                        client_socket.send(data)
                file2.close()

                continue
            user=clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}:{message['data'].decode('utf-8')}")

            clients_list=clients.keys()
            clients_online=''
            for client in clients_list:
                clients_online=clients_online+' '+clients[client]['data'].decode('utf-8')
            clients_online+=' IMPORTANT[ANTIMESSA]MESSAGE[52396]'

            clients_online=clients_online.encode('utf-8')
            clients_online_header=f'{len(clients_online):<{HEADER_LENGTH}}'.encode('utf-8')

            user_msg=user['data'].decode('utf-8')+' : '+message['data'].decode('utf-8')
            user_msg=user_msg.encode('utf-8')
            user_msg_header=f'{len(user_msg):<{HEADER_LENGTH}}'.encode('utf-8')
            
            for client_socket in clients:
                if client_socket!=notified_socket:
                    client_socket.send(user_msg_header+user_msg)
                    client_socket.send(clients_online_header+clients_online)
    
    for notified_socket in exception_sockets:
        print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
        client_left=clients[notified_socket]['data'].decode('utf-8')+' has left the chat.'
        client_left=client_left.encode('utf-8')
        client_left_header=f'{len(client_left):<{HEADER_LENGTH}}'.encode('utf-8')

        clients_users+=' IMPORTANT[ANTIMESSA]MESSAGE[52396]'
        clients_usernames=clients_users.encode('utf-8')
        clients_usernames_header=f'{len(clients_usernames):<{HEADER_LENGTH}}'.encode('utf-8')

        sockets_list.remove(notified_socket)
        del clients[notified_socket]
        for client_sock in clients:
            client_sock.send(client_left_header+client_left)
            client_sock.send(clients_usernames_header+clients_usernames)
        