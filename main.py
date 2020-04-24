from tkinter import *
from smartcard.CardMonitoring import CardMonitor
from inc import admin, master, bill, ejector, RFreader, sound, common, AnimatedGif
import threading
import sys
import platform
import time


class Application:

    # 메인 UI 제어 스레드 변수
    thread_main_ui_control_view = ""

    # 충전 음성 스레드
    thread_sound_bill_input = ""          # 지폐 투입 스레드
    count_thread_sound_bill_input = 0     # 지폐 투입 스레드 카운트
    bool_thread_sound_bill_input = False  # 지폐 투입 스레드 플래그



    main_input_money = 0             # 현재 투입금액
    main_input_bonus = 0             # 투입금액에 따른 보너스
    main_total_money = 0             # 투입금액 + 보너스

    main_min_issued_money = 1000

    count_bill_input_sound = 0       # 지폐를 투입하여 주세요 음성 카운트

    '''UI Control Variable'''
    # Main View
    tk_window = ""
    background_main = ""
    frame_main = ""

    # Main Label
    lbl_main_hello = ""
    lbl_main_use = ""
    lbl_main_use_place = ""
    lbl_main_money = ""

    # Main button
    btn_charge_off = ""
    btn_charge_on = ""
    btn_issued_off = ""
    btn_issued_on = ""
    btn_lookup_off = ""
    btn_lookup_on = ""

    # Card Charge View
    frame_charge = ""
    frame_charge_page_1 = ""
    frame_charge_page_2 = ""
    background_charge = ""
    background_charge_page_1 = ""
    background_charge_page_2 = ""

    gif_charge_image = ""
    btn_charge_next_off = ""
    btn_charge_next_on = ""
    btn_charge_next_gif = ""
    btn_charge_back = ""
    btn_charge_page_1_back = ""
    lbl_charge_money = ""
    lbl_charge_page_1_money = ""
    lbl_charge_page_1_bonus = ""
    lbl_charge_page_2_money = ""

    # 추후 삭제해야함
    temp_charge1_next_btn = ""
    temp_charge2_next_btn = ""

    # Card Issued View
    frame_issued = ""
    background_issued = ""

    gif_issued_image = ""
    btn_issued_next_off = ""
    btn_issued_next_on = ""
    btn_issued_next_gif = ""
    btn_issued_back = ""
    lbl_issued_money = ""
    lbl_issued_card_issued_money = ""

    # Card Lookup View
    frame_lookup = ""
    background_lookup = ""
    btn_lookup_back = ""
    lbl_lookup_money = ""

    # Class module Declaration
    admin_class = None
    master_class = None
    bill_class = None
    ejector_class = None
    reader_class = None
    sound_class = None
    common_class = None

    # TODO : 임시 방편 admin, master / 추후 모듈 나눠서 수정
    # Card Init Page
    background_card_init = ""
    btn_hide_login = ""          # 히등 로그인 버튼
    frame_login = ""
    btn_login_config = ""
    btn_login_cancel = ""
    frame_card_init = ""

    lbl_init_use = ""       # 매장 ID 입력상태 (성공, 실패)
    lbl_init_shop_id = ""   # 저장될 매장 ID : 0000
    btn_init_start = ""
    btn_enable_start = ""
    btn_init_cancel = ""

    # Admin Page
    frame_admin = ""
    lbl_admin_bonus1 = ""
    lbl_admin_bonus2 = ""
    lbl_admin_bonus3 = ""
    lbl_admin_bonus4 = ""
    lbl_admin_bonus5 = ""
    lbl_admin_bonus6 = ""
    lbl_admin_bonus7 = ""
    lbl_admin_bonus8 = ""
    lbl_admin_bonus9 = ""
    lbl_admin_bonus10 = ""

    lbl_admin_use = ""       # 관리자 환경설정 라벨
    lbl_admin_version = ""

    lbl_admin_password = ""
    lbl_admin_card_issued_money = ""
    lbl_admin_min_card_issued_money = ""
    lbl_admin_shop_id = ""

    # Entry
    entry_login = ""
    entry_admin_bonus1 = ""
    entry_admin_bonus2 = ""
    entry_admin_bonus3 = ""
    entry_admin_bonus4 = ""
    entry_admin_bonus5 = ""
    entry_admin_bonus6 = ""
    entry_admin_bonus7 = ""
    entry_admin_bonus8 = ""
    entry_admin_bonus9 = ""
    entry_admin_bonus10 = ""

    entry_admin_password = ""
    entry_admin_card_issued_money = ""
    entry_admin_min_card_issued_money = ""
    entry_admin_shop_id = ""

    # Button
    btn_admin_init_shop_id = ""
    btn_admin_save = ""
    btn_admin_cancel = ""
    btn_admin_exit = ""

    # Master Page
    frame_master_frame = ""
    background_master = ""
    lbl_master_use = ""

    lbl_master_bonus1 = ""
    lbl_master_bonus2 = ""
    lbl_master_bonus3 = ""
    lbl_master_bonus4 = ""
    lbl_master_bonus5 = ""
    lbl_master_bonus6 = ""
    lbl_master_bonus7 = ""
    lbl_master_bonus8 = ""
    lbl_master_bonus9 = ""
    lbl_master_bonus10 = ""

    lbl_master_password = ""
    lbl_master_card_issued_money = ""
    lbl_master_min_card_issued_money = ""
    lbl_master_shop_id = ""
    lbl_master_manager_info = ""
    lbl_master_card_address = ""

    # Entry
    entry_master_bonus1 = ""
    entry_master_bonus2 = ""
    entry_master_bonus3 = ""
    entry_master_bonus4 = ""
    entry_master_bonus5 = ""
    entry_master_bonus6 = ""
    entry_master_bonus7 = ""
    entry_master_bonus8 = ""
    entry_master_bonus9 = ""
    entry_master_bonus10 = ""

    entry_master_password = ""
    entry_master_card_issued_money = ""
    entry_master_min_card_issued_money = ""
    entry_master_shop_id = ""

    # Listbox
    listbox_master_manager_info = ""
    listbox_master_card_address = ""

    # Button
    btn_master_db_comfirm = ""
    btn_master_db_init = ""
    btn_master_save = ""
    btn_master_cancel = ""
    btn_master_exit = ""
    # TODO : admin, master 끝

    def mainLabelVisible(self, second=3.0):
        self.common_class.toggleLabel(self.lbl_main_use, self.lbl_main_use_place)

        if self.main_input_money > 0:
            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.sound_class.playSound("./msgs/msg025.wav")

        main_label_thread = threading.Timer(second, self.mainLabelVisible)
        main_label_thread.daemon = True
        main_label_thread.start()

    # 인사말 음성제어
    def soundMain(self, event):
        if not self.sound_class.getBusySound():
            self.sound_class.playSound("./msgs/msg003.wav")

    def adminAuthSuccess(self, password):
        if password == "1234":
            self.showFrame(self.frame_admin)
        elif password == "gls12q23w":
            self.showFrame(self.frame_master)
        else:
            msg = "잘못된 비밀번호 입니다."
            self.common_class.showMsgInfo(msg)

    # 프레임 전환
    def showFrame(self, frame):
        frame.tkraise()

    # 전체 프로그램 종료
    def exitProgram(self):
        print("프로그램 종료")
        sys.exit()

    # 메인으로 돌아갈때 설정 초기화
    def resetMainView(self):
        self.btn_charge.config(state="active")
        self.btn_issued.config(state="active")
        self.btn_lookup.config(state="active")

        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True
        self.reader_class.INIT_STATE = False

        self.showFrame(self.frame_main)

    # 메인 버튼 이미지 변경
    def getMainButtonImage(self, value):
        button_image = ""
        if value == 1:
            self.bill_class.billSendData("hi")
            if self.bill_class.BILL_CONNECT:
                button_image = "./images/charge_on_btn.png"
            else:
                button_image = "./images/charge_off_btn.png"

        elif value == 2:
            self.ejector_class.ejectorSendData("hi")
            if self.ejector_class.EJECTOR_CONNECT:
                button_image = "./images/issued_on_btn.png"
            else:
                button_image = "./images/issued_off_btn.png"

        elif value == 3:
            button_image = "./images/lookup_on_btn.png"

        result = PhotoImage(file=button_image)
        return result

    # 충전 버튼 눌렀을때 이벤트
    def startChargeButton(self):
        self.btn_charge.config(state="disabled")
        self.btn_issued.config(state="disabled")
        self.btn_lookup.config(state="disabled")

        # 음성 재생중 일때 중지
        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        self.sound_class.playSound("./msgs/msg005.wav")

        # Flag State Init
        self.reader_class.CHARGE_STATE = True
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True

        self.bool_thread_sound_bill_input = False  # 지폐 투입 음성스레드 ON

        self.showFrame(self.frame_charge)
        self.viewInputMoneySoundThread(3)

    # 충전 페이지 진입 후 - "지폐를 투입하여 주세요" 음성 스레드
    def viewInputMoneySoundThread(self, second=3):
        # ON 상태일때 종료
        if self.bool_thread_sound_bill_input:
            print("지폐 투입 음성 스레드 : ", self.bool_thread_sound_bill_input)
            return

        # 음성 재생중이 아니라면
        if not self.sound_class.getBusySound():
            if self.reader_class.input_money > 0:  # 투입금액이 있을 때
                self.sound_class.playSound("./msgs/msg009.wav")  # 지폐를 더 투입하거나 다음 버튼을 눌러주세요
            else:
                self.sound_class.playSound("./msgs/msg008.wav")  # 지폐를 투입하여 주세요


        # sound_count += 1
        self.count_bill_input_sound += 1
        print(self.count_bill_input_sound)
        if self.count_bill_input_sound >= 5:
            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.bool_thread_sound_bill_input = True
            self.sound_class.playSound("./msgs/msg020.wav")      # 일정 시간동안 지폐투입 하지않아 메인화면 이동합니다

            self.showFrame(self.frame_main)
            self.resetMainView()

            self.count_bill_input_sound = 0         # 스레드 카운트 초기화
            self.thread_sound_bill_input.cancel()   # 지폐 투입 스레드 취소

        self.thread_sound_bill_input = threading.Timer(second, self.viewInputMoneySoundThread)
        self.thread_sound_bill_input.daemon = True
        self.thread_sound_bill_input.start()

    # 충전 종료
    def chargeQuit(self):
        self.btn_charge.config(state="active")
        self.btn_issued.config(state="active")
        self.btn_lookup.config(state="active")

        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True
        self.reader_class.INIT_STATE = False

        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        self.showFrame(self.frame_main)

        self.thread_sound_bill_input.cancel()

    # 발급 버튼 눌렀을때 이벤트
    def startIssuedButton(self):
        self.btn_charge.config(state="disabled")
        self.btn_issued.config(state="disabled")
        self.btn_lookup.config(state="disabled")

        if self.sound_class.getBusySound():
            self.sound_class.stopSound()
        self.sound_class.playSound("./msgs/msg006.wav")

        # Flag State Init
        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = True
        self.reader_class.LOOKUP_STATE = False

        self.showFrame(self.frame_issued)

    # 조회 버튼 눌렀을때 이벤트
    def startLookupButton(self):
        self.btn_charge.config(state="disabled")
        self.btn_issued.config(state="disabled")
        self.btn_lookup.config(state="disabled")

        if self.sound_class.getBusySound():
            self.sound_class.stopSound()
        self.sound_class.playSound("./msgs/msg007.wav")

        # Flag State Init
        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True

        self.bool_thread_lookup_sound_state = True

        self.showFrame(self.frame_lookup)

    # 잔액조회 종료
    def endLookup(self):

        # 음성 스레드 살아있으면 종료
        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        # 잔액조회 스레드 살아있으면 종료
        # if self.bool_thread_lookup_sound_state:
        #     self.thread_main_ui_control_view.cancel()

        self.resetMainView()

    # 한 사이클 수행 후 금액 초기화
    def initViewMoney(self):
        self.main_input_money = 0
        self.main_input_bonus = 0
        self.main_total_money = 0

        self.reader_class.remain_money = 0
        self.reader_class.input_money = 0
        self.reader_class.input_bonus = 0
        self.reader_class.total_money = 0

    # 메인 UI 제어 스레드 - 충전, 발급, 조회, 초기화 모두 해당
    # Main UI control thread - for charge, issue, lookup, initialization
    def threadUIMainView(self, second=1.0):
        # 초기화 여부 검사
        if self.reader_class.INIT_STATE:
            pass

        # 충전 여부 검사
        if self.reader_class.flag_charge:
            self.reader_class.CHARGE_STATE = False
            self.reader_class.ISSUED_STATE = False

            self.lbl_charge_page_2_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.reader_class.total_money))))
            self.lbl_charge_page_2_money.place(x=570, y=223)

            self.showFrame(self.frame_charge_page_2)

            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.sound_class.playSound("./msgs/msg013.wav")  # 충전 완료 음성
            self.reader_class.flag_charge = False  # 충전 플래그 OFF

            time.sleep(2.5)
            self.initViewMoney()
            self.resetMainView()

        # 조회 여부 검사
        elif self.reader_class.flag_lookup:

            self.reader_class.CHARGE_STATE = False
            self.reader_class.ISSUED_STATE = False
            self.reader_class.INIT_STATE = False

            self.lbl_lookup_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.reader_class.remain_money))))
            self.lbl_lookup_money.place(x=570, y=223)
            self.showFrame(self.frame_lookup)

            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.sound_class.playSound("./msgs/msg018.wav")  # 잔액 조회 완료 음성
            self.reader_class.flag_lookup = False   # 잔액 플래그 OFF

            time.sleep(2.5)
            self.initViewMoney()
            self.endLookup()  # 뒤로가기 버튼이벤트와 카드 터치 이후 이벤트

        self.thread_main_ui_control_view = threading.Timer(second, self.threadUIMainView)
        self.thread_main_ui_control_view.daemon = True
        self.thread_main_ui_control_view.start()

    # 모든 뷰 금액 변경
    def threadChangeMoneyView(self, second=1.0):
        try:
            if self.main_input_money > 0:
                self.lbl_charge_money.config(text="{:,} 원".format(self.main_input_money))
                self.lbl_charge_page_1_money.config(text="{:,} 원".format(self.main_input_money))
                self.lbl_charge_page_2_money.config(text="{:,} 원".format(self.main_input_money))
                self.lbl_issued_money.config(text="{:,} 원".format(self.main_input_money))
                self.lbl_issued_card_issued_money.config(text="{:,} 원".format(self.main_min_issued_money))

                self.lbl_charge_money.place(x=570, y=223)
                self.lbl_charge_page_1_money.place(x=570, y=223)
                self.lbl_charge_page_2_money.place(x=570, y=223)
                self.lbl_issued_money.place(x=570, y=223)
                self.lbl_issued_card_issued_money.place(x=765, y=298)

                if self.main_input_money > 0:
                    lbl_font_color = "red"
                else:
                    lbl_font_color = "black"
                self.lbl_main_money.config(text="투입금액       {} 원".format(str(self.main_input_money)), fg=lbl_font_color)
                self.lbl_main_money.place(x=330, y=705)

        except Exception as error:
            print("threadChangeMoneyView Error : " + str(error))

        ui_money_thread = threading.Timer(second, self.threadChangeMoneyView)
        ui_money_thread.daemon = True
        ui_money_thread.start()

    # second is defalut config -> not typeError
    # 지폐인식 스레드
    def threadBillReader(self, second=1.0):
        bill_status = self.bill_class.billSendData("getActiveStatus")
        if bill_status == 1 or bill_status == 11:
            bill_data = self.bill_class.billSendData("billdata")

            if type(bill_data) == int and bill_data > 0:
                self.main_input_money += bill_data
                self.reader_class.input_money += bill_data
                # print("현재 투입금액 : ", self.main_input_money)
            self.bill_class.billSendData("insertE")

        bill_thread = threading.Timer(second, self.threadBillReader)
        bill_thread.daemon = True
        bill_thread.start()

    # 지폐 들어왔나 확인 음성 스레드
    def threadConfirmBillSound(self):
        pass

    def initialiZation(self):
        # Init Bill Start
        self.bill_class.billSendData("insertE")
        self.mainLabelVisible(3.0)

        # BILL Thread Start
        # if 'Linux' in platform.system():
        self.threadBillReader(1.0)

        # RF reader Thread Start
        cardmonitor = CardMonitor()
        self.reader_class = RFreader.Reader()
        cardmonitor.addObserver(self.reader_class)
        self.reader_class.LOOKUP_STATE = True

        # 메인 금액 뷰 실시간 조회 스레드
        self.threadChangeMoneyView(1)   # 화면 금액 변경 스레드
        self.threadUIMainView(1)        # 충전, 조회 플래그 검사 후

    # UI Initialize
    def __init__(self):
        self.tk_window = Tk()  # 윈도우창 생성

        # Class Initialize
        self.admin_class = admin.Admin(self, self.tk_window)
        self.master_class = master.Master(self, self.tk_window)
        self.bill_class = bill.Bill()
        self.ejector_class = ejector.Ejector()
        self.sound_class = sound.Sound()
        self.common_class = common.Common()

        if 'Linux' in platform.system():
            self.tk_window.title("Touch Charger")
            self.tk_window.attributes('-fullscreen', True)

        self.tk_window.title("kang hyun jin")        # 윈도우이름.title("제목")
        self.tk_window.geometry("1024x768+0+0")      # 윈도우이름.geometry("너비x높이+xpos+ypos")
        self.tk_window.resizable(False, False)       # 윈도우이름.resizeable(상하,좌우) : 인자 상수를 입력해도 적용가능

        self.frame_main = Frame(self.tk_window)
        self.frame_charge = Frame(self.tk_window)
        self.frame_charge_page_1 = Frame(self.tk_window)
        self.frame_charge_page_2 = Frame(self.tk_window)
        self.frame_issued = Frame(self.tk_window)
        self.frame_lookup = Frame(self.tk_window)

        self.frame_login = Frame(self.tk_window)
        self.frame_admin = Frame(self.tk_window)
        self.frame_card_init = Frame(self.tk_window)
        self.frame_master = Frame(self.tk_window)

        frame_array = [self.frame_main, self.frame_charge, self.frame_charge_page_1, self.frame_charge_page_2,
                       self.frame_issued, self.frame_lookup, self.frame_login, self.frame_admin,
                       self.frame_master, self.frame_card_init]

        for frame in frame_array:
            frame.grid(row=0, column=0, sticky='news')

        # TODO: 이미지 변수는 그때그때 선언해서 처리해놓았음
        main_frame_image = PhotoImage(file="./images/main_back.png")
        charge_frame_image = PhotoImage(file="./images/new_charge_back.png")
        charge1_frame_image = PhotoImage(file="./images/charge1_back.png")
        charge2_frame_image = PhotoImage(file="./images/charge2_back.png")
        issued_frame_image = PhotoImage(file="./images/new_issued_back.png")
        lookup_frame_image = PhotoImage(file="./images/lookup_back.png")

        charge_back_btn_image = PhotoImage(file="./images/back_btn.png")
        charge_next_btn_on_image = PhotoImage(file="./images/next_btn_on.png")

        # Main Button Image Config
        charge_btn_image = self.getMainButtonImage(1)
        issued_btn_image = self.getMainButtonImage(2)
        lookup_btn_image = self.getMainButtonImage(3)

        main_use_image = PhotoImage(file="./images/main_use_label.png")

        btn_init_start_image = PhotoImage(file="./images/init_start_btn.png")
        btn_init_enable_image = PhotoImage(file="./images/init_start_btn_enable.png")
        btn_init_quit_image = PhotoImage(file="./images/init_quit_btn.png")

        # 테스트
        # main_image = PhotoImage(file="./images/test_back.png")
        # self.main_back = Label(self.main_frame, image=main_image).pack()
        # charge1_frame_image = PhotoImage(file="./images/charge1_frame.png")
        # charge_frame_image = PhotoImage(file="./images/issued_frame.png")
        # login_image = PhotoImage(file="./images/login.png")
        # admin_class_class.login_back = Label(admin_class_class.login_frame, image=login_image).pack()
        # admin_image = PhotoImage(file="./images/admin_frame.png")
        # admin_back = Label(self.frame_admin, image=admin_image).pack()

        # Background Image config
        self.background_main = Label(self.frame_main, image=main_frame_image)
        self.background_main.bind('<Button-1>', self.soundMain)
        self.background_main.pack()

        self.background_charge = Label(self.frame_charge, image=charge_frame_image).pack()
        self.background_charge_page_1 = Label(self.frame_charge_page_1, image=charge1_frame_image).pack()
        self.background_charge_page_2 = Label(self.frame_charge_page_2, image=charge2_frame_image).pack()
        self.background_issued = Label(self.frame_issued, image=issued_frame_image).pack()
        self.background_lookup = Label(self.frame_lookup, image=lookup_frame_image).pack()
        self.background_card_init = Label(self.frame_card_init, image=main_frame_image).pack()

        # Admin Login Page
        self.btn_hide_login = Button(self.frame_main, bd=0, bg="#a8c4b9", width=30, height=4, activebackground='#a8c4b9'
                                     , command=lambda: self.showFrame(self.frame_login))
        self.btn_hide_login.place(x=20, y=0)

        self.entry_login = Entry(self.frame_login, show="*")
        self.entry_login.delete(0, END)  # 기입창 내용지우기
        self.entry_login.place(x=387, y=407)
        self.btn_login_config = Button(self.frame_login, text="확인", width=6,
                                       command=lambda: self.adminAuthSuccess(self.entry_login.get()))
        self.btn_login_config.place(x=540, y=403)
        self.btn_login_cancel = Button(self.frame_login, text="취소", width=6,
                                       command=lambda: self.showFrame(self.frame_main))
        self.btn_login_cancel.place(x=600, y=403)

        # Admin Page
        self.lbl_admin_use = Label(self.frame_admin, text="관리자 환경설정", font=("", 40, "bold"), anchor="e")
        self.lbl_admin_use.place(x=290, y=40)
        self.lbl_admin_version = Label(self.frame_admin, text="버전 : 1.3.0", font=("", 20, "bold"), anchor="e")
        self.lbl_admin_version.place(x=750, y=50)

        self.lbl_admin_bonus1 = Label(self.frame_admin, text="10,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus1.place(x=50, y=160)
        self.entry_admin_bonus1 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus1.place(x=240, y=150)

        self.lbl_admin_bonus2 = Label(self.frame_admin, text="20,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus2.place(x=50, y=210)
        self.entry_admin_bonus2 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus2.place(x=240, y=200)

        self.lbl_admin_bonus3 = Label(self.frame_admin, text="30,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus3.place(x=50, y=260)
        self.entry_admin_bonus3 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus3.place(x=240, y=250)

        self.lbl_admin_bonus4 = Label(self.frame_admin, text="40,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus4.place(x=50, y=310)
        self.entry_admin_bonus4 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus4.place(x=240, y=300)

        self.lbl_admin_bonus5 = Label(self.frame_admin, text="50,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus5.place(x=50, y=360)
        self.entry_admin_bonus5 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus5.place(x=240, y=350)

        self.lbl_admin_bonus6 = Label(self.frame_admin, text="60,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus6.place(x=50, y=410)
        self.entry_admin_bonus6 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus6.place(x=240, y=400)

        self.lbl_admin_bonus7 = Label(self.frame_admin, text="70,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus7.place(x=50, y=460)
        self.entry_admin_bonus7 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus7.place(x=240, y=450)

        self.lbl_admin_bonus8 = Label(self.frame_admin, text="80,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus8.place(x=50, y=510)
        self.entry_admin_bonus8 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus8.place(x=240, y=500)

        self.lbl_admin_bonus9 = Label(self.frame_admin, text="90,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus9.place(x=50, y=560)
        self.entry_admin_bonus9 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus9.place(x=240, y=550)

        self.lbl_admin_bonus10 = Label(self.frame_admin, text="100,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_admin_bonus10.place(x=50, y=610)
        self.entry_admin_bonus10 = Entry(self.frame_admin, width=7, font=("", 25))
        self.entry_admin_bonus10.place(x=240, y=600)

        self.lbl_admin_password = Label(self.frame_admin, text="관리자비밀번호", font=("", 12, "bold"))
        self.lbl_admin_password.place(x=500, y=160)
        self.entry_admin_password = Entry(self.frame_admin, width=12, font=("", 25))
        self.entry_admin_password.place(x=700, y=150)

        self.lbl_admin_card_issued_money = Label(self.frame_admin, text="카드 발급 금액", font=("", 12, "bold"))
        self.lbl_admin_card_issued_money.place(x=500, y=260)
        self.entry_admin_card_issued_money = Entry(self.frame_admin, width=10, font=("", 25))
        self.entry_admin_card_issued_money.place(x=700, y=250)

        self.lbl_admin_min_card_issued_money = Label(self.frame_admin, text="카드 발급 최소 투입금액", font=("", 12, "bold"))
        self.lbl_admin_min_card_issued_money.place(x=500, y=360)
        self.entry_admin_min_card_issued_money = Entry(self.frame_admin, width=10, font=("", 25))
        self.entry_admin_min_card_issued_money.place(x=700, y=350)

        self.lbl_admin_shop_id = Label(self.frame_admin, text="매장 번호", font=("", 12, "bold"))
        self.lbl_admin_shop_id.place(x=500, y=460)
        self.entry_admin_shop_id = Entry(self.frame_admin, width=10, font=("", 25))
        self.entry_admin_shop_id.place(x=700, y=450)

        self.btn_admin_init_shop_id = Button(self.frame_admin, text="매장 ID 등록 모드 진입", activebackground="blue",
                                             command=lambda: self.showFrame(self.frame_card_init),
                                             font=("", 13, "bold"), width=20, height=2)
        self.btn_admin_init_shop_id.place(x=700, y=550)

        self.btn_admin_save = Button(self.frame_admin, text="저    장", width=20, height=2, font=("", 15, "bold")
                                     )
        self.btn_admin_save.place(x=250, y=650)
        self.btn_admin_cancel = Button(self.frame_admin, text="취    소", width=20, height=2, font=("", 15, "bold"),
                                       command=lambda: self.showFrame(self.frame_main))
        self.btn_admin_cancel.place(x=500, y=650)
        self.btn_admin_exit = Button(self.frame_admin, text="프로그램\n종료", width=10, height=2, font=("", 15, "bold"),
                                     command=lambda: self.exitProgram())
        self.btn_admin_exit.place(x=850, y=650)

        # Card_Init_Page
        self.lbl_init_use = Label(self.frame_card_init, text="매장 ID 입력 상태 : X", font=("", 30, "bold"), anchor="e",
                                  bg="#a8c4b9")
        self.lbl_init_use.place(x=355, y=50)
        self.lbl_init_shop_id = Label(self.frame_card_init, text="저장될 매장 ID : 0000", font=("", 30, "bold"), anchor="e",
                                      bg="#a8c4b9")
        self.lbl_init_shop_id.place(x=340, y=155)
        self.btn_init_start = Button(self.frame_card_init, image=btn_init_start_image, bd=0, bg="#a8c4b9",
                                     activebackground='#a8c4b9')
        self.btn_init_start.place(x=250, y=235)
        self.btn_init_cancel = Button(self.frame_card_init, image=btn_init_quit_image, bd=0, bg="#a8c4b9",
                                      activebackground='#a8c4b9',
                                      command=lambda: self.showFrame(self.frame_main))
        self.btn_init_cancel.place(x=550, y=235)

        # Master Page
        self.lbl_master_use = Label(self.frame_master, text="마스터 환경설정", font=("", 40, "bold"), anchor="e")
        self.lbl_master_use.place(x=290, y=40)

        self.lbl_master_bonus1 = Label(self.frame_master, text="10,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus1.place(x=50, y=160)
        self.entry_master_bonus1 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus1.place(x=240, y=150)

        self.lbl_master_bonus2 = Label(self.frame_master, text="20,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus2.place(x=50, y=210)
        self.entry_master_bonus2 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus2.place(x=240, y=200)

        self.lbl_master_bonus3 = Label(self.frame_master, text="30,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus3.place(x=50, y=260)
        self.entry_master_bonus3 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus3.place(x=240, y=250)

        self.lbl_master_bonus4 = Label(self.frame_master, text="40,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus4.place(x=50, y=310)
        self.entry_master_bonus4 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus4.place(x=240, y=300)

        self.lbl_master_bonus5 = Label(self.frame_master, text="50,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus5.place(x=50, y=360)
        self.entry_master_bonus5 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus5.place(x=240, y=350)

        self.lbl_master_bonus6 = Label(self.frame_master, text="60,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus6.place(x=50, y=410)
        self.entry_master_bonus6 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus6.place(x=240, y=400)

        self.lbl_master_bonus7 = Label(self.frame_master, text="70,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus7.place(x=50, y=460)
        self.entry_master_bonus7 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus7.place(x=240, y=450)

        self.lbl_master_bonus8 = Label(self.frame_master, text="80,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus8.place(x=50, y=510)
        self.entry_master_bonus8 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus8.place(x=240, y=500)

        self.lbl_master_bonus9 = Label(self.frame_master, text="90,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus9.place(x=50, y=560)
        self.entry_master_bonus9 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus9.place(x=240, y=550)

        self.lbl_master_bonus10 = Label(self.frame_master, text="100,000원 보너스금액", font=("", 12, "bold"))
        self.lbl_master_bonus10.place(x=50, y=610)
        self.entry_master_bonus10 = Entry(self.frame_master, width=7, font=("", 25))
        self.entry_master_bonus10.place(x=240, y=600)

        self.lbl_master_password = Label(self.frame_master, text="관리자비밀번호", font=("", 12, "bold"))
        self.lbl_master_password.place(x=500, y=160)
        self.entry_master_password = Entry(self.frame_master, width=12, font=("", 25))
        self.entry_master_password.place(x=700, y=150)

        self.lbl_master_card_issued_money = Label(self.frame_master, text="카드 발급 금액", font=("", 12, "bold"))
        self.lbl_master_card_issued_money.place(x=500, y=210)
        self.entry_master_card_issued_money = Entry(self.frame_master, width=10, font=("", 25))
        self.entry_master_card_issued_money.place(x=700, y=200)

        self.lbl_master_min_card_issued_money = Label(self.frame_master, text="카드 발급 최소 투입금액", font=("", 12, "bold"))
        self.lbl_master_min_card_issued_money.place(x=500, y=260)
        self.entry_master_min_card_issued_money = Entry(self.frame_master, width=10, font=("", 25))
        self.entry_master_min_card_issued_money.place(x=700, y=250)

        self.lbl_master_shop_id = Label(self.frame_master, text="매장 번호", font=("", 12, "bold"))
        self.lbl_master_shop_id.place(x=500, y=310)
        self.entry_master_shop_id = Entry(self.frame_master, width=10, font=("", 25))
        self.entry_master_shop_id.place(x=700, y=300)

        '''+ str(데이터베이스 업체등록)'''
        self.lbl_master_manager_info = Label(self.frame_master, text="현재 업체 상태 : "
                                             , font=("", 15, "bold"))
        self.lbl_master_manager_info.place(x=550, y=360)
        '''+str(현재카드 저장번지)'''
        self.lbl_master_card_address = Label(self.frame_master, text="현재 저장 번지 : "
                                             , font=("", 15, "bold"))
        self.lbl_master_card_address.place(x=550, y=450)

        self.btn_master_db_comfirm = Button(self.frame_master, text="데이터베이스 확인")
        self.btn_master_db_comfirm.place(x=850, y=550)
        self.btn_master_db_init = Button(self.frame_master, text="데이터베이스 초기화")
        self.btn_master_db_init.place(x=850, y=600)

        self.btn_master_save = Button(self.frame_master, text="저    장", width=20, height=2, font=("", 15, "bold"))
        self.btn_master_save.place(x=250, y=650)
        self.btn_master_cancel = Button(self.frame_master, text="취    소", width=20, height=2, font=("", 15, "bold"),
                                        command=lambda: self.showFrame(self.frame_main))
        self.btn_master_cancel.place(x=500, y=650)
        self.btn_master_exit = Button(self.frame_master, text="프로그램\n종료", width=10, height=2, font=("", 15, "bold"),
                                      command=lambda: self.exitProgram())
        self.btn_master_exit.place(x=850, y=650)

        # Main Button
        self.btn_charge = Button(self.frame_main, image=charge_btn_image, bd=0, bg="#a8c4b9", activebackground='#a8c4b9')
        self.btn_issued = Button(self.frame_main, image=issued_btn_image, bd=0, bg="#a8c4b9", activebackground='#a8c4b9')
        self.btn_lookup = Button(self.frame_main, image=lookup_btn_image, bd=0, bg="#a8c4b9", activebackground='#a8c4b9')

        # H/W Module Verification
        if self.bill_class.BILL_CONNECT:
            self.btn_charge.config(command=lambda:self.startChargeButton())
        else:
            self.btn_charge.config(command=lambda:self.common_class.showMsgInfo("지폐인식기를 연결해 주세요."))

        if self.ejector_class.EJECTOR_CONNECT:
            self.btn_issued.config(command=lambda:self.startIssuedButton())
        else:
            self.btn_issued.config(command=lambda:self.common_class.showMsgInfo("카드배출기를 연결해 주세요."))

        self.btn_lookup.config(command=lambda:self.startLookupButton())

        self.btn_charge.place(x=90, y=240)
        self.btn_issued.place(x=390, y=240)
        self.btn_lookup.place(x=690, y=240)

        self.lbl_main_hello = Label(self.frame_main, text="저희 세차장을 이용해주셔서 감사합니다.", font=("Corier", 20), bg="#a8c4b9")
        self.lbl_main_hello.place(x=60, y=70)

        self.lbl_main_use = Label(self.frame_main, image=main_use_image, bd=0)  # bd=테두리 두께(default:2)
        self.lbl_main_use.visible = True
        self.lbl_main_use.place(x=280, y=532)
        self.lbl_main_use_place = self.lbl_main_use.place_info()

        self.lbl_main_money = Label(self.frame_main, text="투입금액      0 원", font=("Corier", 30, "bold"), bg="#a8c4b9", anchor="e")
        self.lbl_main_money.place(x=330, y=705)

        # Charge Card Page
        self.gif_charge_image = AnimatedGif.AnimatedGif(self.frame_charge, './images/bill-1.gif', 0.7)
        self.gif_charge_image.config(bg="#a8c4b9")
        self.gif_charge_image.place(x=360, y=360)
        self.gif_charge_image.start()

        self.btn_charge_back = Button(self.frame_charge, image=charge_back_btn_image, bd=0, bg="#a8c4b9",
                                      activebackground='#a8c4b9', command=lambda:self.chargeQuit())
        self.btn_charge_back.place(x=57, y=657)
        self.btn_charge_next_on = Button(self.frame_charge, image=charge_next_btn_on_image, bd=0, bg="#a8c4b9",
                                    activebackground='#a8c4b9', command=lambda:self.showFrame(self.frame_charge_page_1))
        self.btn_charge_next_on.place(x=833, y=657)    # hidden state 다음 버튼위치
        # self.btn_charge_next_gif.place(x=777, y=630)  # gif 다음 버튼위치

        # self.btn_charge_next_gif = AnimatedGif.AnimatedGif(self.frame_charge, './images/next_btn_ani.gif', 0.8)
        # self.btn_charge_next_gif.config(bg="#a8c4b9", activebackground='#a8c4b9')
        # self.btn_charge_next_gif.place(x=777, y=630)
        # self.btn_charge_next_gif.start()

        self.lbl_charge_money = Label(self.frame_charge, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_charge_money.place(x=740, y=223)
        self.lbl_charge_page_1_money = Label(self.frame_charge_page_1, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_charge_page_1_money.place(x=740, y=223)
        self.lbl_charge_page_1_bonus = Label(self.frame_charge_page_1, text="0 원", fg="#ffffff", bg="#464646", font=("Corier", 12), anchor="e")
        self.lbl_charge_page_1_bonus.place(x=795, y=298)
        self.lbl_charge_page_2_money = Label(self.frame_charge_page_2, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_charge_page_2_money.place(x=740, y=223)

        # TODO : 하드웨어 테스트 이후 지워야할 화면처리
        self.btn_charge_page1_back = Button(self.frame_charge_page_1, image=charge_back_btn_image, bd=0, bg="#a8c4b9",
                                    activebackground='#a8c4b9', command=lambda:self.chargeQuit())
        self.btn_charge_page1_back.place(x=57, y=657)

        self.temp_charge1_next_btn = Button(self.frame_charge_page_1, image=charge_next_btn_on_image, bd=0, bg="#a8c4b9",
                                    activebackground='#a8c4b9', command=lambda: self.showFrame(self.frame_charge_page_2))
        self.temp_charge1_next_btn.place(x=833, y=657)
        self.temp_charge2_next_btn = Button(self.frame_charge_page_2, image=charge_next_btn_on_image, bd=0, bg="#a8c4b9",
                                            activebackground='#a8c4b9', command=lambda: self.showFrame(self.frame_main))
        self.temp_charge2_next_btn.place(x=833, y=657)
        # TODO : 끝

        # Issued Card Page
        self.gif_issued_image = AnimatedGif.AnimatedGif(self.frame_issued, './images/bill-1.gif', 0.7)
        self.gif_issued_image.config(bg="#a8c4b9")
        self.gif_issued_image.place(x=360, y=360)
        self.gif_issued_image.start()

        self.btn_issued_back = Button(self.frame_issued, image=charge_back_btn_image, bd=0, bg="#a8c4b9",
                                    activebackground='#a8c4b9', command=lambda:self.resetMainView())
        self.btn_issued_back.place(x=57, y=657)
        self.btn_issued_next_on = Button(self.frame_issued, image=charge_next_btn_on_image, bd=0, bg="#a8c4b9",
                                      activebackground='#a8c4b9', command=lambda: self.showFrame(self.frame_main))
        self.btn_issued_next_on.place(x=833, y=657)

        self.lbl_issued_money = Label(self.frame_issued, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_issued_money.place(x=740, y=223)
        self.lbl_issued_card_issued_money = Label(self.frame_issued, text="0 원", fg="#ffffff", bg="#464646", font=("Corier", 12), anchor="e")
        self.lbl_issued_card_issued_money.place(x=795, y=298)

        # Lookup Card Page
        self.btn_lookup_back = Button(self.frame_lookup, image=charge_back_btn_image, bd=0, bg="#a8c4b9",
                                    activebackground='#a8c4b9', command=lambda:self.endLookup())
        self.btn_lookup_back.place(x=57, y=657)
        self.lbl_lookup_money = Label(self.frame_lookup, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_lookup_money.place(x=740, y=223)

        # 시작전 메인 프레임 이미지초기화
        self.showFrame(self.frame_main)

        # 프로그램 시작
        self.initialiZation()
        self.tk_window.mainloop()  # 윈도우가 종료될 때까지 실행


if __name__ == '__main__':
    main = Application()