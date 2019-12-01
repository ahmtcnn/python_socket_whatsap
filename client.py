import sys
from PyQt5.QtWidgets import QApplication, QWidget,QMainWindow,QProgressBar,QPushButton,QCheckBox,QHeaderView,QAbstractScrollArea,QMessageBox,QAction,QTableWidgetItem,QTableWidget, QLineEdit, QMessageBox,QGroupBox,QVBoxLayout,QMenuBar,QTabWidget,QLabel,QHBoxLayout,QFrame,QSplitter,QStyleFactory,QListWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot,Qt
import time
import threading
import psutil
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import psutil
import time
import validators
from urllib.parse import urlparse,urljoin

import threading
from socket import AF_INET, socket, SOCK_STREAM

# Protocol
MESSAGE="MESSAGE\n"
QUIT="QUIT\n"


HOST = "127.0.0.1"
PORT = 4444

BUFSIZE = 1024
ADDR = (HOST, PORT)

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Whatsap'
        self.setFixedSize(500  , 300)

        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.window = Window()
        self.setCentralWidget(self.window)
        self.show()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.first_control = True
        self.clients_usernames = []
        self.signals = HelperSignals()
        self.connection_status = False
        self.current_user = None
        self.chat_dictionary = {}

        self.connect_server()
        self.threadpool = QThreadPool()


        self._red = QtGui.QBrush(QtCore.Qt.red)
        self._green = QtGui.QBrush(QtCore.Qt.green)


        
        self.init_ui()
        

        
    def init_ui(self):
        self.hbox = QHBoxLayout(self)
        self.set_frames()
        self.set_label_and_buttons()
        self.set_user_list()
        


        #self.create_chat_list('test')
        self.show()


    def set_label_and_buttons(self):
        self.username_text = QLineEdit(self.top_left_frame)
        self.username_text.setPlaceholderText("Username") 
        self.username_text.move(15, 20)
        self.username_text.resize(100,15)

        self.join_button = QPushButton('Katıl', self.top_left_frame)
        self.join_button.clicked.connect(self.set_username)
        self.join_button.move(120,20)
        self.join_button.resize(50,15)

        # Chat için text
        self.message_text = QLineEdit(self.right_frame)
        self.message_text.setPlaceholderText("type_here") 
        self.message_text.move(10, 220)
        self.message_text.resize(200,40)


        self.send_button = QPushButton('Gonder', self.right_frame)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.move(220,220)
        self.send_button.resize(80,40)

        self.chatlist = QListWidget(self.right_frame)
        self.chatlist.addItem('test')
        self.chatlist.clear()


    def set_user_list(self):
        self.users_list = QListWidget(self.bottom_left_frame)
        self.users_list.setMinimumSize(10,15)
        # self.chat = QListWidget()
        # self.right_frame.addWidget(self.chat)
        self.users_list.itemClicked.connect(self.user_on_click)

    def user_on_click(self):
        
        if self.first_control:
            self.current_user = self.users_list.currentItem().text()
            # print("current",self.current_user)
            
            if self.is_user_recorded(self.current_user):
                print(self.chat_dictionary[self.current_user])

            if not self.is_user_recorded(self.current_user):
                self.create_record(self.current_user)

            for i in self.chat_dictionary[self.current_user]:
                    self.chatlist.addItem(i)
            self.first_control = False
        else:
            messages = [self.chatlist.item(i).text() for i in range(self.chatlist.count())]
            self.chat_dictionary[self.current_user] = messages
            self.current_user = self.users_list.currentItem().text()
            self.chatlist.clear()
            if not self.is_user_recorded(self.current_user):
                self.create_record(self.current_user)

            for i in self.chat_dictionary[self.current_user]:
                    self.chatlist.addItem(i)


        #messages = [self.chatlist.item(i).text() for i in range(self.chatlist.count())]

    def create_record(self,user):
        self.chat_dictionary[user] = []

    def set_frames(self):
        self.top_left_frame    = QFrame()
        self.top_left_frame.setFrameShape(QFrame.StyledPanel)
        
        self.bottom_left_frame = QFrame()
        self.bottom_left_frame.setFrameShape(QFrame.StyledPanel)

        self.right_frame = QFrame()
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        
        self.splitter1 = QSplitter(Qt.Vertical,frameShape=QFrame.StyledPanel)
        self.splitter1.addWidget(self.top_left_frame)
        self.splitter1.addWidget(self.bottom_left_frame)
        self.splitter1.setSizes([125,400])


        self.splitter2 = QSplitter(Qt.Horizontal,frameShape=QFrame.StyledPanel)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.right_frame)
        self.splitter2.setSizes([200,350])

        self.hbox.addWidget(self.splitter2)

    def connect_server(self):

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.client_socket.connect(ADDR)
        except:
            print("Counldn't connect to server")
        else:
            self.connection_status = True
            #status bara yazdırılacak
            msg = self.client_socket.recv(BUFSIZE).decode("utf8")
            print(msg)
    
    def set_username(self):
        username = self.username_text.text()
        # control eklenecek
        if username == "":
            pass
        self.client_socket.send(bytes(username, "utf8"))

        validation = self.client_socket.recv(BUFSIZE).decode("utf8")
        if validation == "True":
            #self.is_username_valid = True
            self.disable_options()
            self.username = username
            self.handler = Handler(self.client_socket)
            self.handler.signals.update_usernames.connect(self.update_username_list)
            self.handler.signals.chat_message.connect(self.write_list)
            self.threadpool.start(self.handler)
        else:
            pass
            #self.is_username_valid = False

    def update_username_list(self,usernames):
        self.users_list.clear()

        for i in usernames:
            if i not in self.clients_usernames:
                self.users_list.addItem(i)

    # def write_list(self,person,message):
    #     self.chatlist.addItem(str(person)+str(message))


    def write_list(self,person,message):
        if self.is_user_recorded(person):
            self.update_record(person,message)
            if self.is_window_active(person):
                self.chatlist.addItem(person+message)
        else:
            self.chat_dictionary[person] = [person + message]


        # users = self.chat_dictionary.keys()
        # if person in users:
        #     chats = self.chat_dictionary[person]
        #     chats.append(message)
        #     self.chat_dictionary[person] = chats
        # else:
        #     self.chat_dictionary[person] = message
        #     print(self.chat_dictionary)
        # self.chatlist.addItem(str(person)+str(message))

    def update_record(self,user,msg):
        value = self.chat_dictionary[user]
        print(type(value),value)
        value.append(user+msg)
        self.chat_dictionary[user] = value

    def is_window_active(self,user):
        return self.current_user == user

    def is_user_recorded(self,user):
        users = self.chat_dictionary.keys()
        if user in users:
            return True
        else:
            return False

    def send_message(self):
        text = self.message_text.text()
        if text != "" and text!= None:
            PROTOCOL=MESSAGE
            FROM=self.username+"\n"
            print(self.username)
            if self.users_list.currentItem() == None:
                print("Please select user to send message")
                return
            TO=self.current_user + "\n"

            TEXT = ": "+text
            packet = PROTOCOL+FROM+TO+TEXT
            print(packet)
            self.client_socket.send(bytes(packet, "utf8"))
            self.chatlist.addItem('You: '+TEXT)
            # burası dictionary'e ekleme şeklinde olmali
            self.message_text.setText('')


    def disable_options(self):
        self.username_text.setDisabled(True)
        self.join_button.setDisabled(True)



class HelperSignals(QObject):
    create_list = pyqtSignal(str)



class HandlerSignals(QObject):
    
    chat_message   = pyqtSignal(str,str)
    update_usernames = pyqtSignal(list)
    #info_box = pyqtSignal(str)


class Handler(QRunnable):
    def __init__(self,connection):
        super(Handler,self).__init__()
        self.connection = connection
        self.signals = HandlerSignals()
        self.chatlist = {}
        self.clients = []
        
    @pyqtSlot()    
    def run(self):
        print("handler works")
        self.recv_messages()

    def recv_messages(self):
        while True:
            print("handler works2")
            received_message = self.connection.recv(BUFSIZE).decode("utf8")
            message = received_message.split("\n")


            if message[0] == "INFO":
                usernames = message[3].split("-")
                self.clients.clear()
                for u in usernames:
                    self.clients.append(u)

                self.signals.update_usernames.emit(self.clients)


            if message[0] == "MESSAGE":

                FROM = message[1]
                TO = message[2]
                MSG = ' '.join(message[3:])
                print(type(MSG),MSG)
                self.signals.chat_message.emit(str(FROM),str(MSG))






if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
