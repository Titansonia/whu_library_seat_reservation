import urllib.parse
import urllib.request
import http.cookiejar
import random
import pytesseract
import datetime
from PIL import Image
from bs4 import BeautifulSoup

#本代码的主体部分为Titansonia完成,我只添加了验证码自动识别功能与当前日期获取功能
#向Titansonia学长or学姐表示感谢。。。
class WhuLibrarySeat(object):
    login_url = "http://seat.lib.whu.edu.cn/auth/signIn"
    captcha_url = 'http://seat.lib.whu.edu.cn//simpleCaptcha/captcha'
    booking_url_01 = "http://seat.lib.whu.edu.cn/"
    #布局选座模式
    booking_url_02 = "http://seat.lib.whu.edu.cn/map"
    #常用座位模式
    booking_url_03 = "http://seat.lib.whu.edu.cn/freeBook/fav"

    def __init__(self):
        self.username = ''
        self.password = ''
        self.captcha = ''


    def setPostData(self,username,password):
        if username and password:
            self.username = username
            self.password = password
            image = Image.open('captcha.jpg')
            #转化为灰度图
            imgry = image.convert('L')
            #阈值，自己一个个尝试吧
            threshold = 22  
            table = []  
            for i in range(256):  
                if i < threshold:  
                    table.append(0)  
                else:  
                    table.append(1)
            out = imgry.point(table,'1') 
            code = pytesseract.image_to_string(out)
            self.captcha = code
            print(code)
        else:
            return None

    def downloadCaptcha(self):
        isDownOk = False
        try:
            if WhuLibrarySeat.captcha_url:
                out_img = open("captcha.jpg","wb")
                img = urllib.request.urlopen(WhuLibrarySeat.captcha_url).read()
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
            print("get captcha error!")
            return None

        headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0"}
        post_data = {
            'username': self.username,
            'password': self.password,
            'captcha': self.captcha
        }

        post_data = urllib.parse.urlencode(post_data).encode("utf-8")
        request = urllib.request.Request(WhuLibrarySeat.login_url,post_data,headers)

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
                if(start_seat_id <= int(seat_num) <= end_seat_id):
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
                        print("Booking Failed. Date "+date+", Seat No."+seat_num+", room "+room_id+".")
                        isBooked = False
                    else:
                        isBooked = True
                        print("Booking Success! Date "+date+", Seat No."+seat_num+", room "+room_id+".\n")
                        os._exit()
                        break
        return isBooked


    def randomSeatNum(self,start,end):
        return random.randint(start,end)

    #根据room_id获得当前room中seat_no的边界
    def getSeatIdBoundary(self,room_id):
        url_get_seats_by_room = "http://seat.lib.whu.edu.cn/mapBook/getSeatsByRoom?room=" + room_id
        response = urllib.request.urlopen(url_get_seats_by_room)
        result = response.read().decode("utf-8")
        soup = BeautifulSoup(result, "html.parser")
        lis = soup.find_all("li")
        count = 0
        for li in lis:
            if (li.a):
                count += 1
        return count

if __name__ == '__main__':
    print("-----------------------------------------------------------------------")
    print("Seat Info Input Rules\n")

    print("[Date Format]\nYYYY-MM-DD(e.g.2017-01-18)\n")

    print("[Time Code Lookup]")
    print("07:30----450   08:00----480\n08:30----510   09:00----540\n09:30----570   10:00----600\n"
          "10:30----630   11:00----660\n11:30----690   12:00----720\n12:30----750   13:00----780\n"
          "13:30----810   14:00----840\n14:30----870   15:00----900\n15:30----930   16:00----960\n"
          "16:30----990   17:00----1020\n17:30----1050  18:00----1080\n18:30----1110  19:00----1140\n"
          "19:30----1170  20:00----1200\n20:30----1230  21:00----1260\n21:30----1290  22:00----1320\n")

    print("[Room id Lookup]")
    print("信息科学分馆:")
    print("一层:\n"
          "一楼3C创客空间----4                  一楼创新学习讨论区----5\n"
          "3C创客-电子资源阅览区（20台）----13    C创客-双屏电脑（20台）----14\n"
          "创新学习-MAC电脑（12台）----15        创新学习-云桌面（42台）----16\n"
          "二层:\n"
          "二楼自然科学图书借阅区西----6          二楼自然科学图书借阅区东----7\n"
          "三层:\n"
          "三楼社会科学图书借阅区西----8          三楼社会科学图书借阅区西----8\n"
          "三楼自主学习区----12\n"
          "四层:\n"
          "四楼图书阅览区西----9                 四楼图书阅览区东----11\n")

    print("工学分馆:")
    print("二层:\n"
          "201室+东部自科图书借阅区---19          205室+中部电子图书借阅区----31\n"
          "2楼+中部走廊---29\n"
          "三层:\n"
          "301室+东部自科图书借阅区---32          305室+中部自科图书借阅区----33\n"
          "四层:\n"
          "401室+东部自科图书借阅区---34          405室+中部期刊阅览区----35\n"
          "五层:\n"
          "501室+东部外文图书借阅区---37          505室+中部自科图书借阅区----38\n")
    print("-----------------------------------------------------------------------")


    mode = input("Which mode?(pre/inter)\n")
    #mode='pre'

    #进入预录入式预定
    if mode == "pre":
        ###自定义信息
        username =''
        password = ''
        room_id = '8'
        #获取当前日期，我是打算前一天预定，所以日期加了一天
        date=str(datetime.date.today()+datetime.timedelta(days=1))
        
        #date = "2017-06-01"
        start_seat_id = 25
        end_seat_id = 80
        start_time = "570"
        end_time = "1230"

        while (True):
            l = WhuLibrarySeat()
            print("--------------------Predefined mode-----------------------\n")
            print("[Login Info]")
            print("Username: " + username)
            print("Password: " + password)
            isLogin = l.login(username, password)
            if (isLogin):
                print("[Seat Info]")
                print("Date: " + date)
                print("Room id: " + room_id)
                print("Start time: " + start_time)
                print("End time: " + end_time)
                print("Start seat id: " + str(start_seat_id))
                print("End seat id: " + str(end_seat_id))
                l.map_book(username, password, room_id, date, start_seat_id, end_seat_id, start_time,end_time)
            else:
                print("Login failed.")



    else:
        #进入交互式预定
        if mode == "inter":
            while (True):
                l = WhuLibrarySeat()
                print("--------------------Interactive mode-----------------------\n")
                print("[Login Info]")
                username = 2016301500143
                password = 125051
                isLogin = l.login(username, password)
                if (isLogin):
                    while (True):
                        print("[Seat Info]")
                        date = input("please enter date: \n")
                        room_id = input("please enter room_id: \n")
                        start_time = input("please enter time_from: \n")
                        end_time = input("please enter time_to: \n")
                        seat_id_limit = l.getSeatIdBoundary(room_id)
                        start_seat_id = int(
                            input("please enter start_seat_id:(Less than " + str(seat_id_limit) + ") \n"))
                        end_seat_id = int(input("please enter end_seat_id:(Less than " + str(seat_id_limit) + ") \n"))
                        if l.map_book(username, password, room_id, date, start_seat_id, end_seat_id, start_time,
                                         end_time): break
                else:
                    print("Login failed.")
        
