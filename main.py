import base64
from collections import OrderedDict
from tkinter import *
import tkinter.ttk
from smartcard.CardMonitoring import CardMonitor
from inc import admin, master, bill, ejector, RFreader, sound, common, AnimatedGif, database
import pymysql.cursors
import threading
import sys
import platform
import time
import subprocess, os


class Application:
    # 메인 투입금액 관련 음성 플래그
    CHARGE_INIT_FLAG = False
    ISSUED_INIT_FLAG = False
    LOOKUP_INIT_FLAG = False

    # 충전 음성 스레드 (지폐를 투입하여 주세요, 세차 카드를 터치하여 주세요)
    thread_charge_sound_bill_input = ""                # 지폐 투입 스레드 (충전, 발급 공통사용)
    count_charge_thread_sound_bill_input = 0           # 지폐 투입 스레드 카운트
    bool_charge_thread_sound_bill_input_state = False  # 지폐 투입 스레드 플래그

    thread_charge_sound_card_touch = ""                # 세차 카드 터치 스레드
    count_charge_sound_card_touch = 0                  # 세차 카드 터치 스레드 카운트
    bool_charge_sound_card_touch_state = False         # 세차 카드 터치 스레드 플래그

    # 잔액 조회 세차카드 터치 음성 스레드
    thread_lookup_sound_card_touch = ""
    count_lookup_thread_sound_card_touch = 0
    bool_lookup_thread_sound_card_touch_state = False

    # TODO : 사용할 금액 변수
    total_money = 0         # 토탈 ( 충전할 금액 + 현재 카드 잔액)
    current_money = 0       # 투입금액
    current_bonus = 0       # 보너스
    charge_money = 0        # 충전할 금액 ( 투입금액 + 보너스)
    before_money = 0        # 충전 전 금액 (현재 카드잔액)
    card_price = 0          # 카드 가격
    min_card_price = 0      # 카드 발급 최소 금액

    total = 0
    charge_total = 0
    bonus_total = 0

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
    db_class = None

    # TODO : admin, master / 추후 모듈 나눠서 수정
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

    # Combobox
    combobox_master_manager_info = ""
    combobox_master_card_address = ""

    # Button
    btn_master_db_comfirm = ""
    btn_master_db_init = ""
    btn_master_save = ""
    btn_master_cancel = ""
    btn_master_exit = ""

    key_bored_process = ""

    btn_init_start_image=""
    btn_init_enable_image = ""

    # TODO : admin, master 끝

    def mainLabelVisible(self, second=1.0):
        self.common_class.toggleLabel(self.lbl_main_use, self.lbl_main_use_place)
        main_label_thread = threading.Timer(second, self.mainLabelVisible)

        if self.current_money > 0 and not self.CHARGE_INIT_FLAG and not self.LOOKUP_INIT_FLAG and not self.ISSUED_INIT_FLAG:
            if not self.sound_class.getBusySound():
                self.sound_class.playSound("./msgs/msg025.wav")   # 음성 재생중이 아니면 투입금액이 있습니다 재생

        main_label_thread.daemon = True
        main_label_thread.start()

    # 인사말 음성제어
    def soundMain(self, event):
        if not self.sound_class.getBusySound():
            self.sound_class.playSound("./msgs/msg003.wav")

    # 관리자 인증
    def adminAuthSuccess(self, password):
        if password == self.db_class.getConfigArg("password"):
            self.showFrame(self.frame_admin)
        elif password == self.db_class.getConfigArg("gil_password"):
            self.showFrame(self.frame_admin)
        elif password == self.db_class.getConfigArg("master_password"):
            self.showFrame(self.frame_master)
        else:
            msg = "잘못된 비밀번호 입니다."
            self.common_class.showMsgInfo(msg)

    # 관리자 / 마스터 페이지 초기화
    def initAdminMasterPage(self):
        self.db_class.loadConfigTable()
        self.showFrame(self.frame_login)  # 로그인 페이지 이동
        self.db_class.loadConfigTable()   # 활경설정 불러오기
        # self.tk_window.attributes('-fullscreen', False)

        # ADMIN 기입창 내용지우기
        self.entry_login.delete(0, END)
        self.entry_admin_bonus1.delete(0, END)
        self.entry_admin_bonus2.delete(0, END)
        self.entry_admin_bonus3.delete(0, END)
        self.entry_admin_bonus4.delete(0, END)
        self.entry_admin_bonus5.delete(0, END)
        self.entry_admin_bonus6.delete(0, END)
        self.entry_admin_bonus7.delete(0, END)
        self.entry_admin_bonus8.delete(0, END)
        self.entry_admin_bonus9.delete(0, END)
        self.entry_admin_bonus10.delete(0, END)

        self.entry_admin_password.delete(0, END)
        self.entry_admin_card_issued_money.delete(0, END)
        self.entry_admin_min_card_issued_money.delete(0, END)
        self.entry_admin_shop_id.delete(0, END)

        # ADMIN 기입창 내용 삽입
        self.entry_admin_bonus1.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(10000)))
        self.entry_admin_bonus2.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(20000)))
        self.entry_admin_bonus3.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(30000)))
        self.entry_admin_bonus4.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(40000)))
        self.entry_admin_bonus5.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(50000)))
        self.entry_admin_bonus6.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(60000)))
        self.entry_admin_bonus7.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(70000)))
        self.entry_admin_bonus8.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(80000)))
        self.entry_admin_bonus9.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(90000)))
        self.entry_admin_bonus10.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(100000)))

        self.entry_admin_password.insert(0, self.db_class.getConfigArg("password"))
        self.entry_admin_card_issued_money.insert(0, self.db_class.getConfigArg("card_price"))
        self.entry_admin_min_card_issued_money.insert(0, self.db_class.getConfigArg("min_card_price"))
        self.entry_admin_shop_id.insert(0, self.db_class.getConfigArg("shop_id"))

        # MASTER 기입창 내용지우기
        self.entry_master_bonus1.delete(0, END)
        self.entry_master_bonus2.delete(0, END)
        self.entry_master_bonus3.delete(0, END)
        self.entry_master_bonus4.delete(0, END)
        self.entry_master_bonus5.delete(0, END)
        self.entry_master_bonus6.delete(0, END)
        self.entry_master_bonus7.delete(0, END)
        self.entry_master_bonus8.delete(0, END)
        self.entry_master_bonus9.delete(0, END)
        self.entry_master_bonus10.delete(0, END)

        self.entry_master_password.delete(0, END)
        self.entry_master_card_issued_money.delete(0, END)
        self.entry_master_min_card_issued_money.delete(0, END)
        self.entry_master_shop_id.delete(0, END)

        # MASTER 기입창 내용 삽입
        self.entry_master_bonus1.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(10000)))
        self.entry_master_bonus2.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(20000)))
        self.entry_master_bonus3.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(30000)))
        self.entry_master_bonus4.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(40000)))
        self.entry_master_bonus5.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(50000)))
        self.entry_master_bonus6.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(60000)))
        self.entry_master_bonus7.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(70000)))
        self.entry_master_bonus8.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(80000)))
        self.entry_master_bonus9.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(90000)))
        self.entry_master_bonus10.insert(0, self.common_class.stringNumberFormat(self.db_class.getConfigArg(100000)))

        self.entry_master_password.insert(0, self.db_class.getConfigArg("password"))
        self.entry_master_card_issued_money.insert(0, self.db_class.getConfigArg("card_price"))
        self.entry_master_min_card_issued_money.insert(0, self.db_class.getConfigArg("min_card_price"))
        self.entry_master_shop_id.insert(0, self.db_class.getConfigArg("shop_id"))

        manager_title = self.db_class.getConfigArg("manager_name")
        self.lbl_master_manager_info.config(text="현재 업체 상태 : " + manager_title)

        card_address = self.db_class.getConfigArg("rf_reader_type")
        self.lbl_master_card_address.config(text="현재 저장 번지 : " + card_address)

        # 키보드 원본 fcitx , iBus
        self.key_bored_process = subprocess.Popen(['florence show'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if not "" == self.key_bored_process.stderr.readline():
            self.key_bored_process = subprocess.Popen(['florence'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return

    # 관리자 페이지 설정 저장
    def saveAdminPage(self):
        msg = self.common_class.showMsgYesNo("저장 하시겠습니까?")
        if msg:
            dic_save_admin = OrderedDict()
            dic_save_admin["man"] = int(self.entry_admin_bonus1.get().replace(",", ""))
            dic_save_admin["2man"] = int(self.entry_admin_bonus2.get().replace(",", ""))
            dic_save_admin["3man"] = int(self.entry_admin_bonus3.get().replace(",", ""))
            dic_save_admin["4man"] = int(self.entry_admin_bonus4.get().replace(",", ""))
            dic_save_admin["5man"] = int(self.entry_admin_bonus5.get().replace(",", ""))
            dic_save_admin["6man"] = int(self.entry_admin_bonus6.get().replace(",", ""))
            dic_save_admin["7man"] = int(self.entry_admin_bonus7.get().replace(",", ""))
            dic_save_admin["8man"] = int(self.entry_admin_bonus8.get().replace(",", ""))
            dic_save_admin["9man"] = int(self.entry_admin_bonus9.get().replace(",", ""))
            dic_save_admin["10man"] = int(self.entry_admin_bonus10.get().replace(",", ""))
            dic_save_admin["card_price"] = int(self.entry_admin_card_issued_money.get().replace(",", ""))
            dic_save_admin["min_card_price"] = int(self.entry_admin_min_card_issued_money.get().replace(",", ""))
            dic_save_admin["id"] = self.entry_admin_shop_id.get()
            dic_save_admin["admin_password"] = self.entry_admin_password.get()

            self.db_class.setAdminConfig(dic_save_admin)

            # if not self.DEBUG:
            #     if 'Linux' in platform.system():
            #         self.window.attributes('-fullscreen', True)

            if self.key_bored_process:
                self.key_bored_process.kill()

            self.db_class.loadConfigTable()
            self.showFrame(self.frame_main)

    # 마스터 페이지 설정 저장
    def saveMasterPage(self):
        msg = self.common_class.showMsgYesNo("저장 하시겠습니까?")
        if msg:
            dic_save_master = OrderedDict()
            dic_save_master["man"] = int(self.entry_admin_bonus1.get().replace(",", ""))
            dic_save_master["2man"] = int(self.entry_admin_bonus2.get().replace(",", ""))
            dic_save_master["3man"] = int(self.entry_admin_bonus3.get().replace(",", ""))
            dic_save_master["4man"] = int(self.entry_admin_bonus4.get().replace(",", ""))
            dic_save_master["5man"] = int(self.entry_admin_bonus5.get().replace(",", ""))
            dic_save_master["6man"] = int(self.entry_admin_bonus6.get().replace(",", ""))
            dic_save_master["7man"] = int(self.entry_admin_bonus7.get().replace(",", ""))
            dic_save_master["8man"] = int(self.entry_admin_bonus8.get().replace(",", ""))
            dic_save_master["9man"] = int(self.entry_admin_bonus9.get().replace(",", ""))
            dic_save_master["10man"] = int(self.entry_admin_bonus10.get().replace(",", ""))
            dic_save_master["card_price"] = int(self.entry_admin_card_issued_money.get().replace(",", ""))
            dic_save_master["min_card_price"] = int(self.entry_admin_min_card_issued_money.get().replace(",", ""))
            dic_save_master["id"] = self.entry_admin_shop_id.get()
            dic_save_master["admin_password"] = self.entry_admin_password.get()

            dic_save_master["manager_name"] = self.combobox_master_manager_info.get()
            dic_save_master["binary_type"] = self.combobox_master_card_address.get()

            self.db_class.setMasterConfig(dic_save_master)

            # if not self.DEBUG:
            #     if 'Linux' in platform.system():
            #         self.window.attributes('-fullscreen', True)

            if self.key_bored_process:
                self.key_bored_process.kill()

            self.db_class.loadConfigTable()
            self.showFrame(self.frame_main)

    # 마스터 페이지 - 데이터 베이스 초기화
    def masterDBInithandle(self):
        try:
            self.db_class.openConnectDB()
            with self.db_class.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursor:
                delete_card_sql = "DELETE FROM card"  # 카드 테이블 삭제
                db_cursor.execute(delete_card_sql)
                insert_total_query = "INSERT INTO total (`no`, `total`, `charge`, `bonus`, `card`, `card_count`) " \
                                     "VALUE (1, '0', '0', '0', '0', '0') ON DUPLICATE KEY UPDATE " \
                                     "total = '0', charge = '0', bonus = '0', card = '0', card_count = '0'"  # 토탈 테이블 초기화
                db_cursor.execute(insert_total_query)

                init_pw = '1234'
                admin_pw = init_pw.encode('utf-8')
                base_admin_pw = base64.b64encode(admin_pw)
                admin_pw = base_admin_pw.decode('utf-8')

                update_config_sql = "UPDATE config SET admin_password = %s, `device_addr` = '01', card_price = 1000, " \
                                    "bonus1 = '1000', bonus2 = '3000', bonus3 = '5000', bonus4 = '7000', bonus5 = '10000'," \
                                    "bonus6 = '11000', bonus7 = '13000', bonus8 = '15000', bonus9 = '17000', " \
                                    "bonus10 = '20000', id = '0000', shop_name = 'abcd' WHERE no = 1"  # 설정 초기화
                db_cursor.execute(update_config_sql, (admin_pw))
            self.db_class.db_connect.commit()
        except Exception as error:
            print("master Db Init handle Error : " + str(error))
        finally:
            self.db_class.closeConnectDB()
        self.db_class.loadConfigTable()
        self.showFrame(self.frame_main)

    # 마스터 페이지 - 데이터 베이스 초기화 체크 (카드, 토탈 테이블 확인)
    def masterDBInitCheckHandle(self):
        total_mny = 0
        try:
            self.db_class.openConnectDB()
            with self.db_class.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursor:
                card_query = "SELECT * FROM card"  # 카드테이블 초기화
                db_cursor.execute(card_query)

                rows = db_cursor.fetchall()
                card_length = len(rows)
                if int(card_length) > 0:
                    self.common_class.showMsgInfo("카드테이블이 초기화 되지 않았습니다.")
                    return False

                query = "SELECT * FROM total"  # 토탈 테이블 초기화
                db_cursor.execute(query)
                rows = db_cursor.fetchall()
                for row in rows:
                    total_mny += int(row['total'])

                if total_mny > 0:
                    self.common_class.showMsgInfo("토탈테이블이 초기화 되지 않았습니다.")
                    return False
            self.db_class.db_connect.commit()
        finally:
            self.db_class.closeConnectDB()
        self.common_class.showMsgInfo("초기화 상태입니다.")
        return True

    # 매장 ID 등록 모드 진입 - 카드 금액 초기화
    def cardInitMoney(self):
        self.lbl_init_shop_id.config(text="저장될 매장 ID : " + self.db_class.getConfigArg("shop_id"))
        self.btn_init_start.config(image=self.btn_init_start_image)
        # self.btn_init_start.place_forget()
        self.showFrame(self.frame_card_init)

    # 카드 금액 초기화 시작, 매장 ID등록
    def startCardInitMoney(self):
        self.reader_class.INIT_STATE = True
        self.btn_init_start.place_forget()
        self.btn_init_start.config(image=self.btn_init_enable_image)
        self.btn_init_start.place(x=250, y=233)
        self.common_class.showMsgInfo("카드 초기화모드를 시작합니다. 전면 리더기에 카드를 터치해주세요.")

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
        self.btn_init_start.config(image=self.btn_init_start_image)
        self.showFrame(self.frame_main)

        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        if self.key_bored_process:
            self.key_bored_process.kill()

        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True
        self.reader_class.INIT_STATE = False

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
        self.btn_charge_next_gif.config(state="disabled")

        # 음성 재생중 일때 중지
        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        self.sound_class.playSound("./msgs/msg005.wav")

        # Flag State Init
        self.reader_class.CHARGE_STATE = True
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True

        self.CHARGE_INIT_FLAG = True  # 투입금액 관련 음성 플래그 ON

        self.count_charge_thread_sound_bill_input = 0           # 지폐 투입 음성 스레드 카운트 초기화
        self.bool_charge_thread_sound_bill_input_state = False  # 지폐 투입 음성스레드 ON

        self.count_charge_sound_card_touch = 0                  # 세차 카드 터치 음성 스레드 카운트 초기화
        self.bool_charge_sound_card_touch_state = False         # 세차 카드 터치 음성 스레드 ON

        self.showFrame(self.frame_charge)
        self.inputMoneySoundThread(0, 3)

    # 충전 페이지 진입 후 - "지폐를 투입하여 주세요" 음성 스레드
    def inputMoneySoundThread(self, count=0, second=3.0):
        # ON 상태일때 종료
        if self.bool_charge_thread_sound_bill_input_state:
            return

        # 음성 재생중이 아니라면
        if not self.sound_class.getBusySound():
            if self.reader_class.current_money > 0:  # 투입금액이 있을 때
                self.sound_class.playSound("./msgs/msg009.wav")  # 지폐를 더 투입하거나 다음 버튼을 눌러주세요
            else:
                self.sound_class.playSound("./msgs/msg008.wav")  # 지폐를 투입하여 주세요

        count += 1
        self.count_charge_thread_sound_bill_input += 1

        # 일정 시간 지나면
        if self.count_charge_thread_sound_bill_input >= 20:
            # 지폐 투입 플래그 OFF
            self.bool_charge_thread_sound_bill_input_state = True

            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.sound_class.playSound("./msgs/msg020.wav")      # 일정 시간동안 지폐투입 하지않아 메인화면 이동합니다
            self.showFrame(self.frame_main)

            self.btn_charge.config(state="active")
            self.btn_issued.config(state="active")
            self.btn_lookup.config(state="active")

            self.reader_class.CHARGE_STATE = False
            self.reader_class.ISSUED_STATE = False
            self.reader_class.LOOKUP_STATE = True

            self.thread_charge_sound_bill_input.cancel()   # 지폐 투입 스레드 취소

        self.thread_charge_sound_bill_input = threading.Timer(second, self.inputMoneySoundThread, [count])
        self.thread_charge_sound_bill_input.daemon = True
        self.thread_charge_sound_bill_input.start()

    # 충전 페이지 - (다음 gif 버튼에 핸들링)
    def chargeNextOnHanding(self):
        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        # 지폐 투입 스레드 중지 flow
        self.count_charge_thread_sound_bill_input = 0
        self.bool_charge_thread_sound_bill_input_state = True

        if self.thread_charge_sound_bill_input:
            self.thread_charge_sound_bill_input.cancel()

        self.showFrame(self.frame_charge_page_1)    # 세차 카드 터치 프레임 이동
        self.chargeCardTouchSoundThread(0, 3)     # 세차 카드 터치 음성 스레드 시작

    # 충전 페이지 - 세차카드 터치 음성 스레드
    def chargeCardTouchSoundThread(self, count=0, second=3.0):
        # ON 상태일때 종료
        if self.bool_charge_sound_card_touch_state:
            return

        # 음성 재생중이 아니라면
        if not self.sound_class.getBusySound():
            self.sound_class.playSound("./msgs/msg010.wav")

        count += 1
        self.count_charge_sound_card_touch += 1

        # 일정 시간 지나면
        if self.count_charge_sound_card_touch >= 20:
            # 지폐 투입 플래그 OFF
            self.bool_charge_sound_card_touch_state = True
            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.sound_class.playSound("./msgs/msg021.wav")  # 일정 시간동안 다음 단계를 진행하지않아 메인화면 이동합니다
            self.showFrame(self.frame_main)

            self.btn_charge.config(state="active")
            self.btn_issued.config(state="active")
            self.btn_lookup.config(state="active")

            self.reader_class.CHARGE_STATE = False
            self.reader_class.ISSUED_STATE = False
            self.reader_class.LOOKUP_STATE = True

            self.thread_charge_sound_bill_input.cancel()  # 지폐 투입 스레드 취소

        self.thread_lookup_sound_card_touch = threading.Timer(second, self.chargeCardTouchSoundThread, [count])
        self.thread_lookup_sound_card_touch.daemon = True
        self.thread_lookup_sound_card_touch.start()

    # 충전 종료
    def chargeQuit(self):
        self.btn_charge.config(state="active")
        self.btn_issued.config(state="active")
        self.btn_lookup.config(state="active")

        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True
        self.reader_class.INIT_STATE = False

        self.CHARGE_INIT_FLAG = False  # 투입금액 관련 음성 플래그 OFF

        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        self.showFrame(self.frame_main)

        # 충전 스레드 살아있으면 중지
        if self.thread_charge_sound_bill_input:
            self.thread_charge_sound_bill_input.cancel()
        if self.thread_lookup_sound_card_touch:
            self.thread_lookup_sound_card_touch.cancel()

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

        self.ISSUED_INIT_FLAG = True  # 투입금액 관련 음성 플래그 ON

        self.count_charge_thread_sound_bill_input = 0  # 지폐 투입 음성 스레드 카운트 초기화
        self.bool_charge_thread_sound_bill_input_state = False  # 지폐 투입 음성스레드 ON

        self.showFrame(self.frame_issued)
        self.inputMoneySoundThread(0, 3.5)

    # 발급 - 다음 버튼 눌렀을때
    def issuedNextButtonHanding(self):
        # 지폐 투입 음성 스레드 초기화
        self.count_charge_thread_sound_bill_input = 0
        self.bool_charge_thread_sound_bill_input_state = True

        # 다음 버튼 비활성화
        self.btn_issued_next_gif.config(state="disabled")
        self.issuedNextButtonAnimateStop()

        # 지폐 투입 스레드 살아있으면 중지
        if self.thread_charge_sound_bill_input:
            self.thread_charge_sound_bill_input.cancel()

        if not self.ejector_class.EJECTOR_CONNECT:  # 배출기 연결 OFF면 활성화
            self.ejector_class.ejectorSendData("hi")

        # 배출기 연결 ON 이면 활성화
        if self.ejector_class.EJECTOR_CONNECT:
            self.ejector_class.ejectorSendData("enable")

            # 배출기 상태가 활성화 상태면
            if self.ejector_class.EJECTOR_STATE:
                self.ejector_class.ejectorSendData("output")  # 카드 배출
                self.showFrame(self.frame_main)

                # 배출기 상태 검사
                ejector_state = self.ejector_class.ejectorSendData("state")
                print("배출기 상태 : ", ejector_state)
                if ejector_state == 2:  # 배출 동작중일때
                    self.sound_class.playSound("./msgs/msg014.wav")
                elif ejector_state == 5:  # 1장 배출후 비정상 종료상태 or 카드 없음
                    self.sound_class.playSound("./msgs/msg017.wav")
                    self.btn_charge.config(state="active")
                    self.btn_issued.config(state="active")
                    self.btn_lookup.config(state="active")

                    self.ISSUED_INIT_FLAG = False  # 투입금액 관련 플래그 OFF
                    self.reader_class.LOOKUP_STATE = True
                    self.reader_class.ISSUED_STATE = False
                    self.showFrame(self.frame_main)
                    return
                else:
                    self.sound_class.playSound("./msgs/msg017.wav")
                    self.btn_charge.config(state="active")
                    self.btn_issued.config(state="active")
                    self.btn_lookup.config(state="active")
                    self.ejector_class.ejectorSendData("init")  # 배출기 초기화
                    self.ISSUED_INIT_FLAG = False  # 투입금액 관련 플래그 OFF
                    self.reader_class.LOOKUP_STATE = True
                    self.reader_class.ISSUED_STATE = False
                    self.showFrame(self.frame_main)
                    return

                # 카드 배출 중일때 배출기 상태 다시 검사하여 카드가 나온상황이면 남은 금액 카드 충전
                try:
                    ejector_state = self.ejector_class.ejectorSendData("state")
                    print("배출기 상태 : ", ejector_state)
                    if ejector_state == 4 or ejector_state == 5 or ejector_state == 2:

                        # 보너스 계산
                        self.current_bonus = int(self.db_class.calculateMemberBonus(self.current_money))
                        self.reader_class.current_bonus = int(self.reader_class.getBonus(self.current_money))

                        # 카드 가격, 카드 발급 최소금액 계산
                        self.card_price = int(self.db_class.getConfigArg("card_price"))
                        self.reader_class.card_price = int(self.db_class.getConfigArg("card_price"))
                        self.min_card_price = int(self.db_class.getConfigArg("min_card_price"))
                        self.reader_class.min_card_price = int(self.db_class.getConfigArg("min_card_price"))

                        # 총 충전 잔액 구하기
                        self.charge_money = self.current_money + self.current_bonus
                        self.reader_class.charge_money = self.reader_class.current_money + self.reader_class.current_bonus

                        # 총 충전금액 - 카드 가격
                        self.charge_money -= self.card_price
                        self.reader_class.charge_money -= self.reader_class.card_price


                        # (발급 데이터 -> DB) 저장할 딕셔너리
                        dic_issued = OrderedDict()
                        dic_issued['total_mny'] = str(self.charge_money)
                        dic_issued['charge_mny'] = "0"
                        dic_issued['bonus_mny'] = "0"
                        dic_issued['card_price'] = str(self.card_price)
                        dic_issued['card_count'] = "1"

                        self.db_class.setUpdateTotalTable(dic_issued)

                        self.ejector_class.ejectorSendData("disable")
                        self.btn_charge.config(state="active")
                        self.btn_issued.config(state="active")
                        self.btn_lookup.config(state="active")

                        self.changeMoneyView()

                        # 금액에 따른 플래그 처리
                        if self.reader_class.current_money > 0:
                            self.reader_class.ISSUED_STATE = True
                        else:
                            self.reader_class.ISSUED_STATE = False
                            self.reader_class.LOOKUP_STATE = True

                        self.ISSUED_INIT_FLAG = False
                    else:
                        self.sound_class.playSound("./msgs/msg017.wav")
                        self.btn_charge.config(state="active")
                        self.btn_issued.config(state="active")
                        self.btn_lookup.config(state="active")
                        self.ejector_class.ejectorSendData("init")
                        self.showFrame(self.frame_main)
                        return

                except Exception as error:
                    print("Issued Card Error : " + str(error))

            # 배출기 상태 OFF 일때
            else:
                self.sound_class.playSound("./msgs/msg017.wav")
                self.btn_charge.config(state="active")
                self.btn_issued.config(state="active")
                self.btn_lookup.config(state="active")

                self.ISSUED_INIT_FLAG = False  # 투입금액 관련 플래그 OFF
                self.reader_class.LOOKUP_STATE = True
                self.reader_class.ISSUED_STATE = False
                self.showFrame(self.frame_main)
                return

    # 발급 종료
    def issuedQuit(self):
        self.btn_charge.config(state="active")
        self.btn_issued.config(state="active")
        self.btn_lookup.config(state="active")

        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True

        self.ISSUED_INIT_FLAG = False  # 투입금액 관련 음성 플래그 OFF

        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        if self.thread_charge_sound_bill_input:
            self.thread_charge_sound_bill_input.cancel()

        self.showFrame(self.frame_main)

    # 조회 버튼 눌렀을때 이벤트
    def startLookupButton(self):
        self.btn_charge.config(state="disabled")
        self.btn_issued.config(state="disabled")
        self.btn_lookup.config(state="disabled")
        self.showFrame(self.frame_lookup)

        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        self.sound_class.playSound("./msgs/msg007.wav")

        # Flag State Init
        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True

        self.LOOKUP_INIT_FLAG = True  # 투입금액 관련 음성 플래그 ON

        # self.bool_thread_lookup_sound_state = True
        # 잔액 조회 음성 플래그 ON, 카운트 초기화
        self.bool_lookup_thread_sound_card_touch_state = False
        self.count_lookup_thread_sound_card_touch = 0

        # 잔액조회 세차카드 터치 음성스레드
        self.lookupCardTouchSoundThread(0, 3)

    # 잔액조회 세차 카드 터치해주세요 음성 스레드
    def lookupCardTouchSoundThread(self, count=0, second=3.0):
        if self.bool_lookup_thread_sound_card_touch_state:  # 카드 터치 플래그 검사
            return

        # 음성 재생중이 아니면 울리기
        if not self.sound_class.getBusySound():
            self.sound_class.playSound("./msgs/msg010.wav")

        count += 1
        self.count_lookup_thread_sound_card_touch += 1

        # 일정시간 이후 플래그 OFF , 스레드 중지
        if self.count_lookup_thread_sound_card_touch >= 20:
            self.bool_lookup_thread_sound_card_touch_state = True
            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.sound_class.playSound("./msgs/msg021.wav")  # 메인 이동 음성
            self.showFrame(self.frame_main)

            self.btn_charge.config(state="active")
            self.btn_issued.config(state="active")
            self.btn_lookup.config(state="active")

            # 카드 터치 스레드 취소
            self.thread_lookup_sound_card_touch.cancel()

        self.thread_lookup_sound_card_touch = threading.Timer(second, self.lookupCardTouchSoundThread, [count])
        self.thread_lookup_sound_card_touch.daemon = True
        self.thread_lookup_sound_card_touch.start()

    # 잔액조회 종료
    def lookupQuit(self):
        # 잔액조회 금액 뷰 초기화
        self.lbl_lookup_money.config(text="0 원")
        self.btn_charge.config(state="active")
        self.btn_issued.config(state="active")
        self.btn_lookup.config(state="active")
        self.showFrame(self.frame_main)

        self.reader_class.CHARGE_STATE = False
        self.reader_class.ISSUED_STATE = False
        self.reader_class.LOOKUP_STATE = True

        self.LOOKUP_INIT_FLAG = False  # 투입금액 관련 음성 플래그 OFF

        self.bool_lookup_thread_sound_card_touch_state = True  # 잔액 조회 음성 OFF

        # 음성 스레드 살아있으면 종료
        if self.sound_class.getBusySound():
            self.sound_class.stopSound()

        # 잔액조회 음성 세차카드 플래그 OFF 이후 중지
        if self.thread_lookup_sound_card_touch:
            self.thread_lookup_sound_card_touch.cancel()

    # 한 사이클 수행 후 금액 초기화
    def initViewMoney(self):
        self.total_money = 0
        self.current_money = 0
        self.current_bonus = 0
        self.charge_money = 0
        self.before_money = 0

        self.reader_class.total_money = 0
        self.reader_class.current_money = 0
        self.reader_class.current_bonus = 0
        self.reader_class.charge_money = 0
        self.reader_class.before_money = 0

        self.changeMoneyView()

    # 메인 금액 변화 UI 제어 스레드 - 충전, 발급, 조회, 초기화 모두 해당
    # Main UI control thread - for charge, issue, lookup, initialization
    def threadUIMainView(self, second=1.0):
        # 초기화 여부 검사
        if self.reader_class.INIT_STATE:
            if self.reader_class.flag_init:
                self.lbl_init_use.config(text="매장 ID 입력 상태 : 성공", fg="blue")
            else:
                self.lbl_init_use.config(text="매장 ID 입력 상태 : 실패", fg="red")

        # 충전 여부 검사
        if self.reader_class.flag_charge:
            self.reader_class.CHARGE_STATE = False
            self.reader_class.ISSUED_STATE = False

            self.CHARGE_INIT_FLAG = False          # 투입금액 관련 음성 플래그 OFF
            self.reader_class.flag_charge = False  # 충전 여부 플래그 OFF

            self.total_money = self.reader_class.total_money
            self.lbl_charge_page_2_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.reader_class.total_money))))

            # 충전 완료 프레임 이동
            self.showFrame(self.frame_charge_page_2)

            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.sound_class.playSound("./msgs/msg013.wav")  # 충전 완료 음성

            self.bool_charge_sound_card_touch_state = True
            self.bool_charge_thread_sound_bill_input_state = True

            # 충전 음성 스레드 살아있으면 중지 (지폐 투입, 카드 터치)
            if self.thread_charge_sound_bill_input:
                self.thread_charge_sound_bill_input.cancel()
            if self.thread_lookup_sound_card_touch:
                self.thread_lookup_sound_card_touch.cancel()

            time.sleep(2.5)
            self.initViewMoney()
            self.resetMainView()

        # 조회 여부 검사
        elif self.reader_class.flag_lookup:
            self.reader_class.CHARGE_STATE = False
            self.reader_class.ISSUED_STATE = False
            self.reader_class.INIT_STATE = False

            self.LOOKUP_INIT_FLAG = False          # 투입금액 관련 음성 플래그 OFF
            self.reader_class.flag_lookup = False  # 조회 여부 플래그 OFF

            self.lbl_lookup_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.reader_class.remain_money))))
            self.showFrame(self.frame_lookup)

            if self.sound_class.getBusySound():
                self.sound_class.stopSound()

            self.sound_class.playSound("./msgs/msg018.wav")  # 잔액 조회 완료 음성

            # 잔액조회 음성 중지
            if self.thread_lookup_sound_card_touch:
                self.thread_lookup_sound_card_touch.cancel()

            time.sleep(2.5)
            self.initViewMoney()
            self.lookupQuit()  # 뒤로가기 버튼이벤트와 카드 터치 이후 이벤트

        thread_main_ui_control_view = threading.Timer(second, self.threadUIMainView)
        thread_main_ui_control_view.daemon = True
        thread_main_ui_control_view.start()

    # 모든 뷰 금액 변경
    def changeMoneyView(self):
        try:
            self.lbl_charge_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.charge_money))))
            self.lbl_charge_page_1_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.current_money))))
            self.lbl_charge_page_1_bonus.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.current_bonus))))
            self.lbl_charge_page_2_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.charge_money))))
            self.lbl_issued_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.charge_money))))
            self.card_price = int(self.db_class.getConfigArg("card_price"))
            self.reader_class.card_price = int(self.db_class.getConfigArg("card_price"))
            self.lbl_issued_card_issued_money.config(text="{} 원".format(self.common_class.stringNumberFormat(str(self.card_price))))

            if self.charge_money == "0" or self.charge_money == 0:
                lbl_font_color = "black"
            else:
                lbl_font_color = "red"
            self.lbl_main_money.config(text="투입금액       {} 원".format(self.common_class.stringNumberFormat(str(self.charge_money))), fg=lbl_font_color)

        except Exception as error:
            print("threadChangeMoneyView Error : " + str(error))

    # second is defalut config -> not typeError
    # 지폐인식 스레드
    def threadBillReader(self, second=1.0):
        bill_status = self.bill_class.billSendData("getActiveStatus")

        if bill_status == 1 or bill_status == 11:
            bill_data = self.bill_class.billSendData("billdata")

            # 투입금액 있으면
            if type(bill_data) == int and bill_data > 0:
                # 투입금액 처리
                self.current_money += bill_data
                self.reader_class.current_money += bill_data

                # 보너스 처리
                self.current_bonus = int(self.db_class.calculateMemberBonus(self.current_money))
                self.reader_class.current_bonus = int(self.db_class.calculateMemberBonus(self.reader_class.current_money))

                # 총전 전 잔액 = 투입금액 + 보너스
                self.charge_money = self.current_money + self.current_bonus
                self.reader_class.charge_money = self.reader_class.current_money + self.reader_class.current_bonus

                if self.sound_class.getBusySound():
                    self.sound_class.stopSound()
                self.sound_class.playSound("./msgs/msg022.wav")  # 지폐가 투입되었습니다

                self.bill_class.billSendData("insertE")
                self.changeMoneyView()  # 금액 뷰

        bill_thread = threading.Timer(second, self.threadBillReader)
        bill_thread.daemon = True
        bill_thread.start()

    # 충전 다음 버튼 움직이기
    def nextChargeButtonOnAnimate(self):
        self.btn_charge_next_gif.place(x=770, y=625)
        self.btn_charge_next_gif.stop = False
        self.btn_charge_next_gif.start()

    # 충전 다음 버튼 멈추기
    def nextChargeButtonStopAnimate(self):
        self.btn_charge_next_gif.stop = True
        self.btn_charge_next_gif.place_forget()

    # 충전 다음 버튼 움직이는지 확인하기
    def isNextChargeButtonAnimate(self):
        return self.btn_charge_next_gif.stop

    # 발급 다음 버튼 움직이기
    def issuedNextButtonAnimate(self):
        self.btn_issued_next_gif.place(x=770, y=625)
        self.btn_issued_next_gif.stop = False
        self.btn_issued_next_gif.start()

    # 발급 다음 버튼 멈추기
    def issuedNextButtonAnimateStop(self):
        self.btn_issued_next_gif.stop = True
        self.btn_issued_next_gif.place_forget()

    # 발급 다음 버튼 움직이는지 확인하기
    def isNextIssuedButtonAnimate(self):
        return self.btn_issued_next_gif.stop

    # 지폐가 들어오면 다음 버튼 변화 스레드
    def billCheckChangeNextButtonThread(self, second=0.3):
        try:
            # 투입금액이 있다면
            if self.current_money > 0:
                self.btn_charge_next_gif.config(state="active")

                # 충전 버튼 움직이나
                if self.isNextChargeButtonAnimate():
                    self.nextChargeButtonOnAnimate()

                # 투입금액이 카드 발급 최소금액 보다 크면 다음 버튼 활성화
                if self.current_money >= self.db_class.getConfigArg("min_card_price"):
                    if self.isNextIssuedButtonAnimate():
                        self.issuedNextButtonAnimate()
                        self.btn_issued_next_gif.config(state="active")
            else:
                if not self.isNextIssuedButtonAnimate():
                    self.issuedNextButtonAnimateStop()

                # 움직이지 않으면
                if not self.isNextChargeButtonAnimate():
                    self.nextChargeButtonStopAnimate()

                self.changeMoneyView()  # 금액 뷰
        except Exception as error:
            print("billCheck ChangeNextButtonThread Error : " + str(error))

        thread_bill_check_change_button = threading.Timer(second, self.billCheckChangeNextButtonThread)
        thread_bill_check_change_button.daemon = True
        thread_bill_check_change_button.start()

    # 프로그램 시작
    def initialiZation(self):
        # Init Bill Start
        self.bill_class.billSendData("insertE")
        self.mainLabelVisible(4)

        # RF reader Thread Start
        cardmonitor = CardMonitor()
        self.reader_class = RFreader.Reader()
        cardmonitor.addObserver(self.reader_class)
        self.reader_class.LOOKUP_STATE = True

        # BILL Thread Start
        # if 'Linux' in platform.system():
        self.threadBillReader(1.0)
        self.billCheckChangeNextButtonThread(0.5)

        # 메인 금액 뷰 실시간 스레드
        self.threadUIMainView(1.0)        # 충전, 조회 플래그 검사 후

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
        self.db_class = database.Database()

        self.tk_window.title("kang hyun jin")    # 윈도우이름.title("제목")
        self.tk_window.geometry("1024x768+0+0")  # 윈도우이름.geometry("너비x높이+xpos+ypos")
        self.tk_window.resizable(False, False)   # 윈도우이름.resizeable(상하,좌우) : 인자 상수를 입력해도 적용가능

        if 'Linux' in platform.system():
            self.tk_window.title("Touch Charger")
            self.tk_window.attributes('-fullscreen', True)

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

        self.btn_init_start_image = PhotoImage(file="./images/init_start_btn.png")
        self.btn_init_enable_image = PhotoImage(file="./images/init_start_btn_enable.png")
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
        self.btn_hide_login = Button(self.frame_main, relief="solid", bd="0", bg="#a8c4b9", width=30, height=4,
                                     activebackground='#a8c4b9', highlightthickness=4, highlightcolor="#a8c4b9",
                                     highlightbackground="#a8c4b9", command=lambda: self.initAdminMasterPage())
        self.btn_hide_login.place(x=20, y=0)

        self.entry_login = Entry(self.frame_login, show="*")
        self.entry_login.place(x=387, y=407)
        self.btn_login_config = Button(self.frame_login, text="확인", width=5,
                                       command=lambda: self.adminAuthSuccess(self.entry_login.get()))
        self.btn_login_config.place(x=560, y=403)
        self.btn_login_cancel = Button(self.frame_login, text="취소", width=5,
                                       command=lambda: self.resetMainView())
        self.btn_login_cancel.place(x=640, y=403)

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
                                 command=lambda: self.cardInitMoney(), font=("", 13, "bold"), width=20, height=2)
        self.btn_admin_init_shop_id.place(x=700, y=550)

        self.btn_admin_save = Button(self.frame_admin, text="저    장", width=20, height=2, font=("", 15, "bold")
                                     ,command=lambda: self.saveAdminPage())
        self.btn_admin_save.place(x=250, y=650)
        self.btn_admin_cancel = Button(self.frame_admin, text="취    소", width=20, height=2, font=("", 15, "bold"),
                                       command=lambda: self.resetMainView())
        self.btn_admin_cancel.place(x=500, y=650)
        self.btn_admin_exit = Button(self.frame_admin, text="프로그램\n종료", width=10, height=2, font=("", 15, "bold"),
                                     command=lambda: self.exitProgram())
        self.btn_admin_exit.place(x=850, y=650)

        # Card_Init_Page
        self.lbl_init_use = Label(self.frame_card_init, text="매장 ID 입력 상태 : X", font=("", 30, "bold"), anchor="e",
                                  width=30, bg="#a8c4b9")
        self.lbl_init_use.place(x=0, y=50)
        self.lbl_init_shop_id = Label(self.frame_card_init, text="저장될 매장 ID : 0000", font=("", 30, "bold"), anchor="e",
                                      width=30, bg="#a8c4b9")
        self.lbl_init_shop_id.place(x=0, y=160)
        self.btn_init_start = Button(self.frame_card_init, image=self.btn_init_start_image, bd="0", bg="#a8c4b9",
                                     command=lambda:self.startCardInitMoney(), activebackground='#a8c4b9')
        self.btn_init_start.place(x=250, y=235)
        self.btn_init_cancel = Button(self.frame_card_init, image=btn_init_quit_image, bd="0", bg="#a8c4b9",
                                  activebackground='#a8c4b9', command=lambda: self.resetMainView())
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

        # 현재 업체, 카드 저장번지 셀렉트
        manager_name = self.db_class.getConfigArg("manager_name")
        card_address = self.db_class.getConfigArg("rf_reader_type")

        manager_list = self.db_class.getManagerList()  # 공급업체 리스트 가져오기
        manager_value = []       # 콤보박스 인자값 : 공급업체 이름
        card_address_value = []  # 콤보박스 인자값 : 카드 저장번지

        for manager in manager_list:
            manager_value.append(manager['manager_name'])

        card_address_value.append("1")
        card_address_value.append("2")

        self.lbl_master_manager_info = Label(self.frame_master, text="현재 업체 상태 : " + manager_name, anchor="e", font=("", 15, "bold"))
        self.lbl_master_manager_info.place(x=550, y=360)

        self.lbl_master_card_address = Label(self.frame_master, text="현재 저장 번지 : " + card_address, anchor="e", font=("", 15, "bold"))
        self.lbl_master_card_address.place(x=550, y=450)

        self.combobox_master_manager_info = tkinter.ttk.Combobox(self.frame_master, values=manager_value, height=15, font=("", 15, 'bold'))
        self.combobox_master_manager_info.set(self.db_class.getConfigArg("manager_name"))
        self.combobox_master_manager_info.place(x=550, y=410)

        self.combobox_master_card_address = tkinter.ttk.Combobox(self.frame_master, values=card_address_value, height=15, font=("", 15, 'bold'))
        self.combobox_master_card_address.set(self.db_class.getConfigArg("rf_reader_type"))
        self.combobox_master_card_address.place(x=550, y=500)

        self.btn_master_db_comfirm = Button(self.frame_master, text="데이터베이스 확인", command=lambda:self.masterDBInitCheckHandle())
        self.btn_master_db_comfirm.place(x=850, y=550)

        self.btn_master_db_init = Button(self.frame_master, text="데이터베이스 초기화", command=lambda:self.masterDBInithandle())
        self.btn_master_db_init.place(x=850, y=600)

        self.btn_master_save = Button(self.frame_master, text="저    장", width=20, height=2, font=("", 15, "bold")
                                      ,command=lambda:self.saveMasterPage())
        self.btn_master_save.place(x=250, y=650)
        self.btn_master_cancel = Button(self.frame_master, text="취    소", width=20, height=2, font=("", 15, "bold"),
                                        command=lambda: self.resetMainView())
        self.btn_master_cancel.place(x=500, y=650)
        self.btn_master_exit = Button(self.frame_master, text="프로그램\n종료", width=10, height=2, font=("", 15, "bold"),
                                      command=lambda: self.exitProgram())
        self.btn_master_exit.place(x=850, y=650)

        # Main Button
        self.btn_charge = Button(self.frame_main, image=charge_btn_image, bd="0", bg="#a8c4b9",
                                 activebackground='#a8c4b9', highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")
        self.btn_issued = Button(self.frame_main, image=issued_btn_image, bd="0", bg="#a8c4b9",
                                 activebackground='#a8c4b9', highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")
        self.btn_lookup = Button(self.frame_main, image=lookup_btn_image, bd="0", bg="#a8c4b9",
                                 activebackground='#a8c4b9', highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")

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

        self.lbl_main_use = Label(self.frame_main, image=main_use_image, bd="0")  # bd=테두리 두께(default:2)
        self.lbl_main_use.visible = True
        self.lbl_main_use.place(x=280, y=532)
        self.lbl_main_use_place = self.lbl_main_use.place_info()

        self.lbl_main_money = Label(self.frame_main, text="투입금액      0 원", font=("Corier", 30, "bold"), width=27, bg="#a8c4b9", anchor="e")
        self.lbl_main_money.place(x=0, y=700)

        # Charge Card Page
        self.gif_charge_image = AnimatedGif.AnimatedGif(self.frame_charge, './images/bill-1.gif', 0.7)
        self.gif_charge_image.config(bg="#a8c4b9")
        self.gif_charge_image.place(x=360, y=360)
        self.gif_charge_image.start()

        self.btn_charge_back = Button(self.frame_charge, image=charge_back_btn_image, bd="0", bg="#a8c4b9",
                                      activebackground='#a8c4b9', highlightthickness=4, highlightcolor="#a8c4b9",
                                      highlightbackground="#a8c4b9", command=lambda:self.chargeQuit())
        self.btn_charge_back.place(x=57, y=657)
        self.btn_charge_next_on = Button(self.frame_charge, image=charge_next_btn_on_image, bd="0", bg="#a8c4b9", state="disabled",
                                        relief="solid", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")
        self.btn_charge_next_on.place(x=825, y=650)    # hidden state 다음 버튼위치

        # 충전 다음 GIF 버튼
        self.btn_charge_next_gif = AnimatedGif.AnimatedButtonGif(self.frame_charge, './images/next_btn_ani2.gif', 0.7)
        self.btn_charge_next_gif.config(bg="#a8c4b9", relief="solid", bd="0", activebackground="#a8c4b9", highlightthickness=4,
                highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", command=lambda: self.chargeNextOnHanding())

        self.lbl_charge_money = Label(self.frame_charge, text="0 원", fg="#33ffcc", width=11, bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_charge_money.place(x=490, y=215)
        self.lbl_charge_page_1_money = Label(self.frame_charge_page_1, text="0 원", width=11, fg="#33ffcc", bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_charge_page_1_money.place(x=490, y=215)
        self.lbl_charge_page_1_bonus = Label(self.frame_charge_page_1, text="0 원", width=8, fg="#ffffff", bg="#464646", font=("Corier", 12), anchor="e")
        self.lbl_charge_page_1_bonus.place(x=744, y=295)
        self.lbl_charge_page_2_money = Label(self.frame_charge_page_2, text="0 원", width=11, fg="#33ffcc", bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_charge_page_2_money.place(x=490, y=215)

        self.btn_charge_page1_back = Button(self.frame_charge_page_1, image=charge_back_btn_image, bd="0", bg="#a8c4b9",
                                        activebackground='#a8c4b9', highlightthickness=4,
                                        highlightcolor="#a8c4b9", highlightbackground="#a8c4b9", command=lambda:self.chargeQuit())
        self.btn_charge_page1_back.place(x=57, y=657)

        # Issued Card Page
        self.gif_issued_image = AnimatedGif.AnimatedGif(self.frame_issued, './images/bill-1.gif', 0.7)
        self.gif_issued_image.config(bg="#a8c4b9")
        self.gif_issued_image.place(x=360, y=360)
        self.gif_issued_image.start()

        self.btn_issued_back = Button(self.frame_issued, image=charge_back_btn_image, bd="0", bg="#a8c4b9",
                                    activebackground='#a8c4b9', highlightthickness=4, highlightcolor="#a8c4b9",
                                      highlightbackground="#a8c4b9", command=lambda:self.issuedQuit())
        self.btn_issued_back.place(x=57, y=657)
        self.btn_issued_next_on = Button(self.frame_issued, image=charge_next_btn_on_image, bd="0", bg="#a8c4b9",
                                       activebackground='#a8c4b9', highlightthickness=4, highlightcolor="#a8c4b9",
                                       highlightbackground="#a8c4b9", state="disabled")
        self.btn_issued_next_on.place(x=825, y=650)

        # 발급 다음 GIF 버튼
        self.btn_issued_next_gif = AnimatedGif.AnimatedButtonGif(self.frame_issued, './images/next_btn_ani2.gif', 0.7)
        self.btn_issued_next_gif.config(bg="#a8c4b9", relief="solid", bd="0", activebackground="#a8c4b9",
                                        highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9",
                                        command=lambda: self.issuedNextButtonHanding())

        self.lbl_issued_money = Label(self.frame_issued, text="0 원", width=11, fg="#33ffcc", bg="#454f49", font=("Corier", 40), anchor="e")
        self.lbl_issued_money.place(x=490, y=215)
        self.lbl_issued_card_issued_money = Label(self.frame_issued, width=8, text="0 원", fg="#ffffff", bg="#464646", font=("Corier", 12), anchor="e")
        self.lbl_issued_card_issued_money.place(x=744, y=295)

        # Lookup Card Page
        self.btn_lookup_back = Button(self.frame_lookup, image=charge_back_btn_image, bd="0", bg="#a8c4b9",
                                      activebackground='#a8c4b9', highlightthickness=4, highlightcolor="#a8c4b9",
                                      highlightbackground="#a8c4b9", command=lambda:self.lookupQuit())
        self.btn_lookup_back.place(x=57, y=657)
        self.lbl_lookup_money = Label(self.frame_lookup, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40), width=11, anchor="e")
        self.lbl_lookup_money.place(x=490, y=215)

        # 시작전 메인 프레임 이미지초기화
        self.showFrame(self.frame_main)

        # 프로그램 시작
        self.initialiZation()
        self.tk_window.mainloop()  # 윈도우가 종료될 때까지 실행


if __name__ == '__main__':
    main = Application()