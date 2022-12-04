import os
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import Tk,Frame, Scrollbar,filedialog, Label, END, Entry, Text, VERTICAL, Button
import socket
import select
import errno
import sys
import threading
from threading import Thread
from threading import Event
import re
import ast
import errno
from functools import partial
import time
from pathlib import Path

HEADER_LENGTH=10
IP="127.0.0.1"
PORT=1234

class FirstScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry(f"800x600+370+100")
        self.title("Log-in Page")
        
        self.maxsize(600,500)
        self.minsize(600,500)

        self.user = None
        self.image_extension = None
        self.image_path = None

        self.first_frame = tk.Frame(self, bg="sky blue")
        self.first_frame.pack(fill="both", expand=True)

        background = Image.open("images/login_bg_ca.png")
        background = background.resize((1800, 1200),)
        background = ImageTk.PhotoImage(background)

        tk.Label(self.first_frame, image=background).place(x=-2, y=-2)

        head = tk.Label(self.first_frame, text="Login", font="lucida 17 bold", bg="black", borderwidth=4,relief="sunken" ,fg = "white")
        head.place(relwidth=1, y=24)


        self.username = tk.Label(self.first_frame, text="Username", font="lucida 12 bold", bg="black",fg = "white",relief="solid")
        self.username.place(x=180, y=150)
        
        self.password = tk.Label(self.first_frame, text="Password", font="lucida 12 bold", bg="black",fg = "white",relief="solid")
        self.password.place(x=180, y=180)

        self.username_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=15,highlightcolor="blue", highlightthickness=1)
        self.username_entry.place(x=295, y=150)
        
        self.password_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=15,highlightcolor="blue", highlightthickness=1)
        self.password_entry.place(x=295, y=180)

        self.username_entry.focus_set()
        
        new_user_image = Image.open("images/new_user2.png")
        new_user_image = new_user_image.resize((35, 25))
        new_user_image = ImageTk.PhotoImage(new_user_image)

        new_user_button = tk.Button(self.first_frame,image = new_user_image, compound="left", text="New User", font="lucida 12 bold", padx=4, cursor="hand2", bg="#16cade", relief="solid", bd=2,command = self.immediate_signup)
        new_user_button.place(x=250, y=315)
        
        submit_button_image = Image.open("images/white_tick.png")
        submit_button_image = submit_button_image.resize((25, 25))
        submit_button_image = ImageTk.PhotoImage(submit_button_image)
        submit_button = tk.Button(self.first_frame,image = submit_button_image, compound="left", text="Connect", font="lucida 12 bold", padx=10, cursor="hand2", bg="#16cade", relief="solid", bd=2,command=self.open_user)
        submit_button.place(x=250, y=275)

        reset_button_image = Image.open("images/forgot_button.jpeg")
        reset_button_image=reset_button_image.resize((35,35))
        photo = ImageTk.PhotoImage(reset_button_image)
        reset_button = tk.Button(self.first_frame,image = photo, compound="left", text="Forgot Password",width=180,height=28, font="lucida 12 bold", padx=5, cursor="hand2", bg="#16cade", relief="solid", bd=2,command=self.call_win)
        reset_button.place(x=218, y=355)
        
        self.mainloop() 
    
    def open_user(self):
        try:
            client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client_socket.connect((IP,PORT))
            client_socket.setblocking(False)
        except:
            client_socket.close()
            messagebox.showinfo(title="Unable to connect !", message="Server didn't respond! Please connect to the server!")

        my_username=self.username_entry.get()
        my_password=self.password_entry.get()
        if my_username!='' and my_password!='':
            my_username=self.username_entry.get()
            my_password=self.password_entry.get()
            
            username=my_username.encode("utf-8")
            username_header=f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(username_header+username)
            
            password=my_password.encode("utf-8")
            password_header=f"{len(password):<{HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(password_header+password)
            error='You are not registered yet! Please sign up to chat or re-enter credentials!'
            while True:
                try:
                    while True:
                        username_header=client_socket.recv(HEADER_LENGTH)
                        username_length=int(username_header.decode("utf-8").strip())
                        username=client_socket.recv(username_length).decode("utf-8")
                        if username==error:
                            messagebox.showinfo(title="Username not found!", message=error)
                            msg_header=client_socket.recv(HEADER_LENGTH)
                            msg_length=int(msg_header.decode("utf-8").strip())
                            msg=client_socket.recv(msg_length).decode("utf-8")

                            signups=ast.literal_eval(msg)

                            new_User=new_user(self,client_socket,signups)
                            new_User.grab_set()
                            break
                        else:
                            pass_error_msg='Wrong password!'
                            pass_verify='Verified'
                            time.sleep(0.2)
                            pass_check_header=client_socket.recv(HEADER_LENGTH)
                            pass_check_length=int(pass_check_header.decode("utf-8").strip())
                            pass_check=client_socket.recv(pass_check_length).decode("utf-8")
                            print(pass_check)
                            if pass_check==pass_error_msg:
                                messagebox.showinfo(title="Wrong password!", message='Please recheck your password and try again!')
                                break
                            # messagebox.showinfo(title="Success!", message='You are successfully logged in!')
                            call_gui(self,client_socket,username)
                            break
                    break
                except IOError as e:
                    if e.errno!=errno.EAGAIN and e.errno!=errno.EWOULDBLOCK:
                        print('Reading error',str(e))
                        sys.exit()
                    continue

                except Exception as e:
                    print('General error',str(e))
                    sys.exit()
    def immediate_signup(self):
        try:
            client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client_socket.connect((IP,PORT))
            client_socket.setblocking(False)
        except:
            client_socket.close()
            messagebox.showinfo(title="Unable to connect !", message="Server didn't respond! Please connect to the server!")
        username='RESERVED EMAIL'.encode("utf-8")
        username_header=f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(username_header+username)
        
        password='RESERVED PASSWORD'.encode("utf-8")
        password_header=f"{len(password):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(password_header+password)
        
        error='You are not registered yet! Please sign up to chat or re-enter credentials!'
        print('###')
        while True:
            try:
                while True:
                    username_header=client_socket.recv(HEADER_LENGTH)
                    username_length=int(username_header.decode("utf-8"))
                    print(username_length,'a',username_header)
                    username=client_socket.recv(username_length).decode("utf-8")
                    print(username,username==error)
                    if username==error:
                        msg_header=client_socket.recv(HEADER_LENGTH)
                        msg_length=int(msg_header.decode("utf-8").strip())
                        msg=client_socket.recv(msg_length).decode("utf-8")
                        
                        signups=ast.literal_eval(msg)
                        new_User=new_user(self,client_socket,signups)
                        new_User.grab_set()
                        
                        break
                break
            except IOError as e:
                    if e.errno!=errno.EAGAIN and e.errno!=errno.EWOULDBLOCK:
                        print('Reading error',str(e))
                        sys.exit()
                    else:
                        time.sleep(2)
            except Exception as e:
                print('General error',str(e))
                sys.exit()
    
    def call_win(self):
            win = forgot_user_win()
            win.grab_set()

            
class new_user(tk.Toplevel):
    def __init__(self,parent,client_socket,signups):
        super().__init__(parent)
        self.client_socket=client_socket
        self.signups=signups

        self.geometry(f"800x600+370+100")
        self.title("Sign-Up Page")
        
        self.maxsize(600,500)
        self.minsize(600,500)

        self.user = None
        self.image_extension = None
        self.image_path = None

        self.first_frame = tk.Frame(self, bg="sky blue")
        self.first_frame.pack(fill="both", expand=True)
        
        head = tk.Label(self.first_frame, text="Sign-up", font="lucida 17 bold", bg="black", borderwidth=4,relief="sunken" ,fg = "white")
        head.place(relwidth=1, y=24)
        
        self.email = tk.Label(self.first_frame, text="Set G-Mail", font="lucida 12 bold", bg="black",fg = "white",relief="solid",width=10,anchor='w')
        self.email.place(x=170, y=120)
        
        self.username = tk.Label(self.first_frame, text="Set Username", font="lucida 12 bold", bg="black",fg = "white",relief="solid")
        self.username.place(x=170, y=150)
        
        self.password = tk.Label(self.first_frame, text="Set Password", font="lucida 12 bold", bg="black",fg = "white",relief="solid")
        self.password.place(x=170, y=180)

        self.email_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=15,highlightcolor="blue", highlightthickness=1)
        self.email_entry.place(x=295, y=120)
        
        self.username_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=15,highlightcolor="blue", highlightthickness=1)
        self.username_entry.place(x=295, y=150)
        
        self.password_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=15,highlightcolor="blue", highlightthickness=1)
        self.password_entry.place(x=295, y=180)
        
        submit_button = tk.Button(self.first_frame, text="Submit", font="lucida 12 bold", padx=10, cursor="hand2",bg="#16cade",command=partial(self.signup_credentials,(client_socket,signups)), relief="solid", bd=2)
        submit_button.place(x=255, y=275)

        quit_button = tk.Button(self.first_frame, text="Quit", font="lucida 12 bold", padx=10, cursor="hand2",bg="#16cade",command=partial(self.end_op,client_socket), relief="solid", bd=2)
        quit_button.place(x=267, y=315)
        
        self.protocol('WM_DELETE_WINDOW',partial(self.cancel_button,client_socket))

    def cancel_button(self,*args):
        if messagebox.askokcancel("Quit", "Do you want to quit the signup?"):
            exit='EXIT!!!'.encode('utf-8')
            exit_header=f"{len(exit):<{HEADER_LENGTH}}".encode('utf-8')
            args[0].send(exit_header+exit)

            args[0].close()
            self.destroy()

    def end_op(self,*args):
        exit='EXIT!!!'.encode('utf-8')
        exit_header=f"{len(exit):<{HEADER_LENGTH}}".encode('utf-8')
        args[0].send(exit_header+exit)

        args[0].close()
        self.destroy()

    def signup_credentials(self,*args):
        my_email=self.email_entry.get()
        my_password=self.password_entry.get()
        my_new_username=self.username_entry.get()
        check_email=0
        if (my_email!='' and my_password!='' and my_new_username!=''):
            while True:
                pattern=re.compile(r'[a-zA-Z0-9.]+@gmail.com')
                matches=pattern.findall(my_email)
                signups=args[0][1]
                key_list=signups.keys()
                if len(matches)!=1:
                    messagebox.showinfo(title="Input Error", message='Please enter a valid gmail address!')
                    break
                for item in key_list:
                    if signups[item][0]==my_email:
                        check_email+=1
                        messagebox.showinfo(title="Input Error", message='Email already in use! Please try a new one!')
                        break
                if check_email==1:
                    break

                if my_new_username in args[0][1]:
                    messagebox.showinfo(title="Input Error", message='Username already exists! Please choose a new one.')
                    break
                if my_new_username=='RESERVED EMAIL' or my_new_username=='EXIT!!!':
                    messagebox.showinfo(title="Input Error", message='Username denied! Please choose a new one.')
                    break

                email=my_email.encode("utf-8")
                email_header=f"{len(email):<{HEADER_LENGTH}}".encode("utf-8")
                args[0][0].send(email_header+email)

                password=my_password.encode("utf-8")
                password_header=f"{len(password):<{HEADER_LENGTH}}".encode("utf-8")
                args[0][0].send(password_header+password)

                my_new_user=my_new_username.encode("utf-8")
                my_new_header=f"{len(my_new_user):<{HEADER_LENGTH}}".encode("utf-8")
                args[0][0].send(my_new_header+my_new_user)
                args[0][0].close()

                messagebox.showinfo(title="Signed up", message='You are now registered. Please enter the credentials in the login window to continue!')
                self.destroy()
                break


class GUI():
    
    def __init__(self,master,client_socket,username):
        self.client_socket = client_socket
        self.username=username
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        f=open(f"{self.username}.txt","a+")
        global n
        n=len(f.readlines())
        self.initialize_gui(f)
        self.listen_to_server()

    def initialize_gui(self,f): 
        self.f=f
        self.root.title("Chat Window") 
        self.root.resizable(0, 0)
        self.root.configure(background='#00e090')
        self.display_chat_box(f)
        self.online_list()
        self.display_chat_entry_box()
        self.profile_pic()
        f.close()
    
    def listen_to_server(self):
        thread = threading.Thread(target=self.receive_message_from_server)
        thread.start()

    def receive_message_from_server(self):
        while True:
            try:
                message=self.receive_msg()
                f=open(f'{self.username}.txt','a')
                if "has joined the chat" in message['data'].decode('utf-8'):
                    self.chat_transcript_area.insert('end', message['data'].decode('utf-8') + '\n')
                    self.chat_transcript_area.yview(END)
                    f.write( message['data'].decode('utf-8') + '\n')
                elif "IMPORTANT[SOBREMESSA]MESSAGE[91267]" in message['data'].decode('utf-8'):
                    username_list=message['data'].decode('utf-8').split(' ')
                    self.name_widget.delete(1.0,'end')
                    for i in range(1,len(username_list)-1):
                        self.name_widget.insert('end', username_list[i] + '\n')
                        self.name_widget.yview(END)
                elif "has left the chat" in message['data'].decode('utf-8'):
                    self.chat_transcript_area.insert('end',message['data'].decode('utf-8')+'\n')
                    self.chat_transcript_area.yview(END)
                    f.write( message['data'].decode('utf-8') + '\n')
                elif "IMPORTANT[ANTIMESSA]MESSAGE[52396]" in message['data'].decode('utf-8'):
                    left_list=message['data'].decode('utf-8').split(' ')
                    self.name_widget.delete("1.0",'end')
                    for i in range(1,len(left_list)-1):
                        print(left_list[i])
                        self.name_widget.insert('end', left_list[i]+ '\n')
                        self.name_widget.yview(END)
                elif 'TYPING[GREETMESA]OPERATION[12567]' in message['data'].decode('utf-8'):
                    typing_list=message['data'].decode('utf-8').split(' ')
                    self.name_widget.delete("1.0",'end')
                    for i in range(1,len(typing_list)-1):
                        self.name_widget.insert('end',typing_list[i]+'\n')
                        self.name_widget.yview(END)
                elif 'FILEGO[FILEMESSA]OPERATION[83729]' in message['data'].decode('utf-8'):
                    file_info_list=(message['data'].decode('utf-8')).split('>')
                    file_name=file_info_list[1]
                    file_size=file_info_list[2]
                    user=file_info_list[3]

                    socket_dir=os.getcwd()
                    downloads_path = str(Path.home() / "Downloads")
                    os.chdir(downloads_path)
                    if os.path.exists('Chat App')==False:
                        os.mkdir('Chat App')
                    os.chdir('Chat App')
                    file=open(file_name,'wb')
                    time.sleep(0.5)
                    chunk=self.client_socket.recv(int(file_size))
                    file.write(chunk)

                    self.chat_transcript_area.insert('end', f"{user} sent a file: {file_name}. File stored in Downloads.\n")
                    self.chat_transcript_area.yview(END)
                    os.chdir(socket_dir)
                    f.write(f"{user} sent a file: {file_name}. File stored in Downloads.+'\n")
                else:
                    if message['data'].decode('utf-8')[:1]=='\n':
                        self.chat_transcript_area.insert('end', message['data'].decode('utf-8')[1:]+'\n')
                        self.chat_transcript_area.yview(END)
                        f.write( message['data'].decode('utf-8')[1:] + '\n')
                    else:
                        self.chat_transcript_area.insert('end', message['data'].decode('utf-8')+'\n')
                        self.chat_transcript_area.yview(END)
                        f.write( message['data'].decode('utf-8') + '\n')
                f.close()

            except IOError as e:
                if e.errno!=errno.EAGAIN and e.errno!=errno.EWOULDBLOCK:
                    print('Reading error',str(e))
                    sys.exit()
            except Exception as e:
                print('General error',str(e))
                sys.exit()

    def send_msg(self,message):
        message=message.encode("utf-8")
        message_header=f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
        self.client_socket.send(message_header+message)
        return


    def receive_msg(self):
        message_header=self.client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length= int(message_header.decode("utf-8").strip())
        return{"header":message_header,"data":self.client_socket.recv(message_length)}

    def display_chat_box(self,f):
        frame = Frame(self.root,background='#00e090')
        Label(frame, text='Chat Box:', font=("Mosse", 12),background='#00e090').pack(side='top', padx=15,pady=5,anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=15, font=("Mosse", 12),background='#d0dad6')
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL,background='#00e090')
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')

        scrollbar.pack(side='right', fill='y',padx=5)
        self.chat_transcript_area.pack(side='right', padx=15,pady=1)
        frame.pack(side='top',anchor='w')

        self.f=f
        self.f.seek(0)
        lines=self.f.readlines()
        for line in lines:
            self.chat_transcript_area.insert('end',line)
        self.chat_transcript_area.insert('end','You joined the chat.\n')

    def display_chat_entry_box(self):
        frame = Frame(self.root,background='#00e090')
        Label(frame, text='Enter message:', font=("Mosse", 12),background='#00e090').pack(side='top', anchor='w',pady=5,padx=15)
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Mosse", 12),background='#d0dad6')
        self.enter_text_widget.bind('<KeyRelease>', self.on_enter_key_pressed)
        scrollbar = Scrollbar(frame, command=self.enter_text_widget.yview, orient=VERTICAL,troughcolor='#00e090')

        attach_button=Button(frame,text='Attach File',font=("Mosse", 10),width=12,height=1,command=self.attach_file)
        send=Button(frame,text='Send',font=("Mosse", 10),width=5,height=1,command=self.send_file)

        scrollbar.pack(side='right', fill='y',padx=2,pady=10)
        self.enter_text_widget.pack(side='right', pady=10,padx=15)
        frame.pack(side='left',anchor='w')
        attach_button.place(x=150,y=4)
        send.place(x=575,y=4)

    def online_list(self):
        frame=Frame(self.root,background='#00e090')
        Label(frame, text='Online:', font=("Helvetica", 12),background='#00e090').pack(side='top',anchor='w')
        self.name_widget = Text(frame, width=30,height=5, borderwidth=2,background='#d0dad6')
        self.name_widget.bind('<KeyRelease-Return>', self.receive_message_from_server)
        scrollbar = Scrollbar(frame, command=self.name_widget.yview, orient=VERTICAL,background='#00e090')
        self.name_widget.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y',padx=2)
        self.name_widget.pack(side='top')
        frame.pack(side='right', anchor='e',padx=5,pady=15)

    def add_photo(self):
        self.image_path = filedialog.askopenfilename(initialdir=os.getcwd(),title='Select a file',filetypes=(("PNG Files","*.png"),("JPG Files","*.jpg"),('WEBP Files','*.webp')))
        image_name = os.path.basename(self.image_path)
        self.image_extension = image_name[image_name.rfind('.')+1:]

        if self.image_path:
            user_image = Image.open(self.image_path)
            user_image = user_image.resize((150, 140))
            user_image.save('resized'+image_name)
            user_image.close()

            self.image_path = 'resized'+image_name
            user_image = Image.open(self.image_path)

            user_image = ImageTk.PhotoImage(user_image)
            self.profile_label.image = user_image
            self.profile_label.config(image=user_image)
        
    def profile_pic(self):
        upload_image = Image.open('images/upload_ca.png')
        upload_image = upload_image.resize((25, 25),)
        upload_image = ImageTk.PhotoImage(upload_image)

        self.user_image = 'images/user.png'

        self.profile_label = Label(self.root,image=upload_image)
        self.profile_label.place(x=715, y=75, width=150, height=140)

        upload_button = Button(self.root, compound="left", text="Upload Image",cursor="hand2", font="lucida 12 bold" ,padx=2,command = self.add_photo)
        upload_button.place(x=715, y=225,width=150)

    def attach_file(self):
        try:
            self.root.filename=filedialog.askopenfilename(initialdir=os.getcwd(),title='Select a file',filetypes=(("PNG Files","*.png"),("All Files","*.*")))
            if self.root.filename!='':
                self.file_label=Label(self.root,text=self.root.filename,width=35,height=1)
                self.file_label.place(x=260,y=417)

                self.remove_button=Button(self.root,text='Remove',command=self.remove_file)
                self.remove_button.place(x=520,y=417)
        except:
            messagebox.showinfo(title="Invalid File", message="Selected file could not be read!")

    def send_file(self):
        try:
            if self.root.filename!='':
                file=open(self.root.filename,'rb')
                file_size=os.path.getsize(self.root.filename)

                self.send_msg('FILEGO[FILEMESSA]OPERATION[83729]')
                list1=self.root.filename.split('\\')
                file_name=list1[-1]
                file_=file_name.split('.')
                file_name=file_[0]+'.'+file_[1]
                self.send_msg(file_name)
                self.send_msg(str(file_size))

                data=file.read()
                self.client_socket.send(data)

                self.chat_transcript_area.insert(END,f'You sent a file: {file_name}.\n')
                self.chat_transcript_area.yview(END)
                self.file_label.destroy()
                self.remove_button.destroy()
                file.close()
        except:
            messagebox.showinfo(title="Unable to connect !", message="Server didn't respond! Please close the chat window and try logging in again!")

    def remove_file(self):
        self.file_label.destroy()
        self.remove_button.destroy()
        self.root.filename=''

    def on_enter_key_pressed(self, event):
        self.send_chat()

    def clear_text(self):
        self.enter_text_widget.delete("1.0", 'end')

    def send_chat(self):
        data = self.enter_text_widget.get('1.0','end')
        f=open(f'{self.username}.txt','a')
        try:
            if '\n' in data:
                print('b')
                self.send_msg('TYPING[GREETMESA]OPERATION[12567]')
        except:
            pass
            try:
                if '\n\n' in data:
                    print('c')
                    senders_name = self.username + " (You) : "
                    self.send_msg('EMPTY[NULLMESSA]OPERATION[27465]')
                    if senders_name+data.strip()!=senders_name:
                        print('d')
                        self.chat_transcript_area.insert('end', (senders_name+data.strip()) + '\n')
                        self.chat_transcript_area.yview(END)
                        f.write(senders_name+data.strip()+'\n')
                        f.close()

                        self.send_msg(data.strip())
                        self.enter_text_widget.delete("1.0", 'end')
                        return 'break'
            except:
                messagebox.showinfo(title="Unable to connect !", message="Server didn't respond! Please close the chat window and try logging in again!")

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to exit the program?"):
            f=open(f'{self.username}.txt','a+')
            f.seek(0)
            lines=f.readlines()
            n=len(lines)
            if n!=0:
                if lines[n-1]=='You left the chat.\n' or lines[n-1]=='You joined and left the chat.\n':
                    f.write('You joined and left the chat.\n')
                else:
                    f.write('You left the chat.\n')
            else:
                f.write('You joined and left the chat.\n')
   
            self.root.destroy()
            self.client_socket.close()
            exit(0)

def call_gui(self,client_socket,username):
    FirstScreen.destroy(self)
    root2 = tk.Tk()
    gui_val = GUI(root2,client_socket,username)

    root2.protocol("WM_DELETE_WINDOW", gui_val.on_close_window)
    root2.mainloop()


class forgot_user_win(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.initialize_win()
        
    def initialize_win(self):
        self.title('Send Activation Code')
        self.geometry('400x300+450+200')
        
        self.first_frame = tk.Frame(self, bg="sky blue")
        self.first_frame.pack(fill="both", expand=True)

        self.mail_id = tk.Label(self, text="Registered Gmail ID", font="lucida 12 bold", bg="black",fg = "white",relief="solid")
        self.mail_id.place(x=20, y=30)
        
        self.Mail_ID_entry = tk.Entry(self,  font="lucida 12 bold", width=20 ,highlightcolor="blue", highlightthickness=1)
        self.Mail_ID_entry.place(x=190, y=30)
        
        self.button = tk.Button(self, text='Generate Activation Code',compound="left", cursor="hand2", font="lucida 12 bold", padx=2,bg="#16cade", relief="solid",command=self.button_clicked)
        self.button.place(x = 20,y = 80)
    
    def send_msg(self,message,client_socket):
        try:
            message=message.encode("utf-8")
            message_header=f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(message_header+message)
            return 
        except:
            pass

    def receive_msg(self,client_socket):
        message_header=client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length= int(message_header.decode("utf-8").strip())
        return{"header":message_header,"data":client_socket.recv(message_length)}

    def button_clicked(self):
            try:
                client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                client_socket.connect((IP,PORT))
                client_socket.setblocking(False)
                print(client_socket,'calling')
            except:
                client_socket.close()
                messagebox.showinfo(title="Unable to connect !", message="Server didn't respond! Please connect to the server!")

            email='RESERVED [EMAIL2]'
            password='RESERVED [PASSWORD2]'
            self.send_msg(email,client_socket)
            self.send_msg(password,client_socket)

            gmail=self.Mail_ID_entry.get()
            self.send_msg(gmail,client_socket)
            time.sleep(0.5)
            reply=self.receive_msg(client_socket)

            if reply['data'].decode('utf-8')=='Accepted':
                messagebox.showinfo(title="Activation Code", message="Activation code has been sent to your G-Mail inbox (or in spam).")
                activ_win = activation_code_win(client_socket)
                activ_win.grab_set()
                forgot_user_win.destroy(self)
            else:
                messagebox.showinfo(title="Wrong Gmail ID", message="Please input the correct Gmail ID associated with your account.")

        
class activation_code_win(tk.Toplevel):
    def __init__(self,client_socket):
        super().__init__()
        self.client_socket=client_socket
        self.activate_win()
    
    def activate_win(self):
        self.title('Reset Password')
        self.geometry('400x300+450+200')
        
        self.first_frame = tk.Frame(self, bg="sky blue")
        self.first_frame.pack(fill="both", expand=True)
        
        self.activation_code = tk.Label(self, text="Activation Code", font="lucida 12 bold", bg="black",fg = "white",relief="solid")
        self.activation_code.place(x=20, y=80)
        
        self.new_password = tk.Label(self, text="New Password", font="lucida 12 bold", bg="black",fg = "white",relief="solid")
        self.new_password.place(x=20, y=120)
        
        self.activation_code_entry = tk.Entry(self,  font="lucida 12 bold", width=10,highlightcolor="blue", highlightthickness=1)
        self.activation_code_entry.place(x=160, y=80)
        
        self.new_password_entry = tk.Entry(self,  font="lucida 12 bold", width=10,highlightcolor="blue", highlightthickness=1)
        self.new_password_entry.place(x=155, y=120)
        
        self.submit_button = tk.Button(self, text='Reset password',compound="left", cursor="hand2", font="lucida 12 bold", padx=2,bg="#16cade", relief="solid",command=self.reset_password)
        self.submit_button.place(x = 20,y = 165)
    
    def send_msg(self,message):
        try:
            message=message.encode("utf-8")
            message_header=f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
            self.client_socket.send(message_header+message)
            return 
        except:
            pass

    def receive_msg(self):
        message_header=self.client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length= int(message_header.decode("utf-8").strip())
        return{"header":message_header,"data":self.client_socket.recv(message_length)}

    def reset_password(self):
        code=self.activation_code_entry.get()
        new_pass=self.new_password_entry.get()

        self.send_msg(code)
        self.send_msg(new_pass)
        
        time.sleep(0.5)
        message=self.receive_msg()
        if message['data'].decode('utf-8')=='Password changed successfully!':
            messagebox.showinfo(title="Success!", message="Password changed successfully! Please login again.")
            self.destroy()
        elif message['data'].decode('utf-8')=='Critical iterations reached.':
            messagebox.showinfo(title="Error", message="Maximum no. of attempts reached! Exiting...")
            self.destroy()
        else:
            messagebox.showinfo(title="Error", message="Wrong activation code entered!")

FirstScreen()
