import urllib.parse
import urllib.request
import http.cookiejar
import random
from bs4 import BeautifulSoup


class Login(object):
    login_url = "http://seat.lib.whu.edu.cn/auth/signIn"
    captcha_url = 'http://seat.lib.whu.edu.cn//simpleCaptcha/captcha'
    booking_url_01 = "http://seat.lib.whu.edu.cn/"
    booking_url_02 = "http://seat.lib.whu.edu.cn/map"
    booking_url_03 = "http://seat.lib.whu.edu.cn/freeBook/fav"

    def __init__(self):
        self.username = ''
        self.password = ''
        self.captcha = ''


    def setPostData(self,username,password):
        if username and password:
            self.username = username
            self.password = password
            self.captcha = input('please enter captcha: ')
        else:
            return None

    def downloadCaptcha(self):
        isDownOk = False
        try:
            if Login.captcha_url:
                out_img = open("code.jpg","wb")
                img = urllib.request.urlopen(Login.captcha_url).read()
                out_img.write(img)
                out_img.flush()
                out_img.close()
                isDownOk = True
            else:
                print('ERROR: captcha_url is NULL')
        except:
            isDownOk = False
        return isDownOk


    def login(self,username,password):
        cj = http.cookiejar.LWPCookieJar()
        cookie_support = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(cookie_support,urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)

        if (self.downloadCaptcha()):
            self.setPostData(username,password)
        else:
            print("captcha false")
            return None

        headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0"}
        post_data = {
            'username': self.username,
            'password': self.password,
            'captcha': self.captcha
        }

        post_data = urllib.parse.urlencode(post_data).encode("utf-8")
        request = urllib.request.Request(Login.login_url,post_data,headers)

        response = urllib.request.urlopen(request)
        result = response.read().decode('utf-8')
        soup = BeautifulSoup(result, "html.parser")
        title = soup.title.text
        if (title == "自选座位 :: 图书馆预约系统"):
            return True
        else:
            return False

    '''
    布局选座 直接使用room_id唯一标注一个场馆某个楼层的某个房间,如信部分馆二楼东区,关于参数building(场馆)和floor(楼层)可以暂时不考虑

    '''
    def map_book(self,username,password,room_id,date,start_seat_id,end_seat_id,start_time,end_time):
        #isLogin = self.login(username,password)
        #if(isLogin):
        #get请求 发送room_id和date
        url1 = "http://seat.lib.whu.edu.cn/mapBook/getSeatsByRoom?room="+room_id+"&date="+date
        response= urllib.request.urlopen(url1)
        result = response.read().decode("utf-8")
        soup = BeautifulSoup(result, "html.parser")
        lis = soup.find_all("li")
        isBooked = False
        for li in lis:
            if(li.a):
                #座位id范围
                seat_num = li.a.text
                if(start_seat_id<=int(seat_num)<=end_seat_id):
                    #这里获得到每一个座位id
                    seat_id = li["id"].split("_")[1]
                    post_data = {
                        "seat":seat_id,
                        "date":date,
                        "start":start_time,
                        "end":end_time
                    }
                    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0"}
                    #post请求 请求内容为date和座位id
                    url2 = "http://seat.lib.whu.edu.cn/selfRes"
                    post_data = urllib.parse.urlencode(post_data).encode("utf-8")
                    request = urllib.request.Request(url2, post_data, headers)
                    response = urllib.request.urlopen(request)
                    result = response.read().decode("utf-8")
                    if("预约失败" in result):
                        print("Booking Failed. Seat No."+seat_num)
                    else:
                        isBooked = True
                        print("Booking Success! Date "+date+", Seat No."+seat_num+", room "+room_id+", floor 2, building 1.")
                        break
        return isBooked

    #def freeBook(self):
        ##下面两种使用post
        # url3 = "http://seat.lib.whu.edu.cn/freeBook/ajaxGetRooms"
        # url4 = "http://seat.lib.whu.edu.cn/freeBook/ajaxSearch"


    def randomSeatNum(self,start,end):
        return random.randint(start,end)



if __name__ == '__main__':
    print("-----------------------------------------------------------------------")
    print("Input Rules")
    print("Time Lookup:")
    print("07:30----450   08:00----480\n08:30----510   09:00----540\n09:30----570   10:00----600\n"
          "10:30----630   11:00----660\n11:30----690   12:00----720\n12:30----750   13:00----780\n"
          "13:30----810   14:00----840\n14:30----870   15:00----900\n15:30----930   16:00----960\n"
          "16:30----990   17:00----1020\n17:30----1050  18:00----1080\n18:30----1110  19:00----1140\n"
          "19:30----1170  20:00----1200\n20:30----1230  21:00----1260\n21:30----1290  22:00----1320\n")

    print("Room id Lookup:")
    print("一楼3C创客空间----4                  一楼创新学习讨论区----5\n"
          "3C创客-电子资源阅览区（20台）----13    C创客-双屏电脑（20台）----14\n"
          "创新学习-MAC电脑（12台）----15        创新学习-云桌面（42台）----16\n"
          "二楼自然科学图书借阅区西----6          二楼自然科学图书借阅区东----7\n"
          "三楼社会科学图书借阅区西----8          三楼社会科学图书借阅区西----8\n"
          "四楼图书阅览区西----9                 四楼图书阅览区东----11\n"
          "三楼自主学习区----12 \n")


    print("Seat id Boundary:")
    print("二楼自然科学图书借阅区东:[1-91]  二楼自然科学图书借阅区西:[1-89]\n")

    print("Date Format:\nYYYY-MM-DD(2017-01-18)")
    print("-----------------------------------------------------------------------")

    l = Login()
    print("Login Info:")
    #用户名和密码
    #username = ''
    #password = ''
    username = input("username: ")
    password = input("password: ")
    isLogin = l.login(username,password)

    #room_id = "7"
    #date = "2017-01-23"

    #seat range mode
    #start_seat_id = 1
    #end_seat_id = 24
    #seat random mode
    #start_seat_id = random.randint(1,24)
    #end_seat_id = start_seat_id

    #start_time = "510"
    #end_time = "1290"

    if(isLogin):
        while(True):
            print("Seat Info:")
            date = input("please enter date: ")
            room_id = input("please enter room_id: ")
            start_time = input("please enter time_from: ")
            end_time = input("please enter time_to: ")
            start_seat_id = int(input("please enter start_seat_id: "))
            end_seat_id = int(input("please enter end_seat_id: "))
            if l.map_book(username,password,room_id,date,start_seat_id,end_seat_id,start_time,end_time): break
    else:
        print("Login failed.")
