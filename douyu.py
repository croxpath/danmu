
import socket
import uuid
import time
import hashlib
import re

class DouyuProto():
    """"douyu message protocol"""
    def __init__(self,data):
        self.sendmagic = 0x02b1
        self.devid = str(uuid.uuid4()).replace("-", "")
        self.data = data
        self.length = len(data) + 9 #len + magic + 0x00 + 0x00 + data + 0x00

    def gen_msg(self):
        length_bytes = self.length.to_bytes(4, byteorder='little')
        msg = length_bytes + length_bytes + self.sendmagic.to_bytes(2,'little') + (0).to_bytes(2,'little') \
            + bytes(self.data,encoding="utf8") + (0).to_bytes(1,'little')
        return msg


class douyu():
    def __init__(self,host,port,roomid):
        self.host = host
        self.port = port
        self.roomid = roomid

    def start(self):
        self.auth = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.auth.connect((self.host, self.port))
        login_reps = self.auth_login()
        #print(login_reps)

        self.login_keep_alive()
        self.danmu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.danmu_socket.connect(("danmu.douyutv.com", 12602))
        self.username = self.get_username(login_reps)
        self.gid = self.get_gid(login_reps)
        self.danmu_login(self.username,self.roomid)
        self.join_group(self.roomid,self.gid)
        while True:
            msg = self.danmu_socket.recv(4000)
            print(self.get_danmu(msg))







    def auth_login(self):
        devid = str(uuid.uuid4()).replace("-", "")
        timestrap = str(int(time.time()))
        vk = hashlib.md5(bytes(timestrap + "7oE9nPEG9xXV69phU31FYCLUagKeYtsF" + devid, 'utf-8')).hexdigest()
        data = "type@=loginreq/username@=/ct@=0/password@=/roomid@=" + self.roomid + "/devid@=" + devid \
               + "/rt@=" + timestrap +"/vk@=" + vk +  "/ver@=20150929" + "/ltkid@=/biz@=/stk@=/"
        #payload =  length_bytes + length_bytes + magic.to_bytes(2,'little') + (0).to_bytes(2,'little') \
        #        + bytes(data,encoding="utf8") + (0).to_bytes(1,'little')
        #print(payload)
        msg = DouyuProto(data).gen_msg()
        self.auth.sendall(msg)
        time.sleep(1)
        rev = self.auth.recv(4000)
        #print(rev)
        return  rev

    def send_qrl(self):
        data = "type@=qrl/rid@=" + self.roomid + "/et@=0/"
        msg = DouyuProto(data).gen_msg()
        self.auth.sendall(msg)


    def login_keep_alive(self):
        timestrap = str(int(time.time()))
        data = "type@=keeplive/tick@=" + timestrap + "/vbw@=0/k@=19beba41da8ac2b4c7895a66cab81e23/"
        msg = DouyuProto(data).gen_msg()
        self.auth.sendall(msg)
        rev = self.auth.recv(4000)
        print(rev)

    def danmu_login(self,username,roomid):
        data = "type@=loginreq/uername@=" + username + "/password@=1234567890123456/roomid@=" + roomid + "/"
        msg = DouyuProto(data).gen_msg()
        self.danmu_socket.sendall(msg)
        rev = self.danmu_socket.recv(4000)
        return  rev

    def join_group(self,roomid,gid):
        data = "type@=joingroup/rid@=" + roomid + "/gid@=" + gid + "/"
        msg = DouyuProto(data).gen_msg()
        self.danmu_socket.sendall(msg)
        #rev = self.danmu_socket.recv(4000)
        #return rev

    def danmu_keep_alive(self):
        data = "type@=mrkl/"
        msg = DouyuProto(data).gen_msg()
        self.danmu_socket.sendall(msg)
        rev = self.danmu_socket.recv(4000)
        return rev


    def get_username(self,res):
        username = re.search('\/username@=(.+)\/nickname', res.decode('utf-8','ignore')).group(1)
        return username

    def get_gid(self,res):
        gid = re.search('\/gid@=(\d+)\/', res.decode('utf-8','ignore')).group(1)
        return gid

    def get_danmu(self,msg):
        content = (msg[4:-1]).decode('utf8','ignore')
        content.replace('@S','/').replace("@A",'@')
        print(content)
        if "type@=chatmsg" in content:
            name = re.search('\/nn@=(.+?)\/', content).group(1)
            txt = re.search('\/txt@=(.+?)\/', content).group(1)
            return name + ": " + txt
        else:
            return None


if __name__ == "__main__":
    douyu("119.90.49.92",8057,"319721").start()
