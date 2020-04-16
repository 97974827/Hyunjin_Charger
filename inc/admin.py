from main import Application
from tkinter import *


class Admin():
    # Card Init Page
    login_lbl = ""          # 로그인 라벨
    login_frame = ""
    init_frame = ""

    init_use_label = ""     # 매장 ID 입력상태 (성공, 실패)
    init_lbl_shop_id = ""   # 저장될 매장 ID : 0000
    init_btn_start = ""
    init_btn_cancel = ""

    # Admin Page
    admin_frame = ""
    admin_lbl_bonus1 = ""
    admin_lbl_bonus2 = ""
    admin_lbl_bonus3 = ""
    admin_lbl_bonus4 = ""
    admin_lbl_bonus5 = ""
    admin_lbl_bonus6 = ""
    admin_lbl_bonus7 = ""
    admin_lbl_bonus8 = ""
    admin_lbl_bonus9 = ""
    admin_lbl_bonus10 = ""

    admin_use_label = ""   # 관리자 환경설정 라벨
    admin_lbl_version = ""

    admin_lbl_password = ""
    admin_lbl_card_issued_money = ""
    admin_lbl_min_card_issued_money = ""
    admin_lbl_shop_id = ""

    # Entry
    admin_entry_bonus1 = ""
    admin_entry_bonus2 = ""
    admin_entry_bonus3 = ""
    admin_entry_bonus4 = ""
    admin_entry_bonus5 = ""
    admin_entry_bonus6 = ""
    admin_entry_bonus7 = ""
    admin_entry_bonus8 = ""
    admin_entry_bonus9 = ""
    admin_entry_bonus10 = ""

    admin_entry_password = ""
    admin_entry_card_issued_money = ""
    admin_entry_min_card_issued_money = ""
    admin_entry_shop_id = ""

    # Button
    admin_btn_init_shop_id = ""
    admin_btn_save = ""
    admin_btn_cancel = ""
    admin_btn_exit = ""

    def admin_test(self):
        print("admin test")

    def admin_page_init(self, frame):
        Application.showFrame(self, frame)

    # 관리자 페이지, 카드 초기화 페이지 UI 초기화
    def __init__(self):
        print("admin init")
        # Application.test(self)
        # self.login_lbl = Label(Application.main_frame(self), bg="#a8c4b9")
        # self.login_lbl.bind("<Button-1>", Application.showFrame(self.login_frame))
        # self.login_lbl.place(x=20, y=0)

