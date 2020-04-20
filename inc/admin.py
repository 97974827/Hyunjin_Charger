from tkinter import *
import tkinter.messagebox


class Admin:
    # # Card Init Page
    # background_card_init = ""
    # btn_hide_login = ""          # 히등 로그인 버튼
    # frame_login = ""
    # btn_login_config = ""
    # btn_login_cancel = ""
    # frame_card_init = ""
    #
    # lbl_init_use = ""       # 매장 ID 입력상태 (성공, 실패)
    # lbl_init_shop_id = ""   # 저장될 매장 ID : 0000
    # btn_init_start = ""
    # btn_init_enabel = ""
    # btn_init_cancel = ""
    #
    # # Admin Page
    # frame_admin = ""
    # lbl_admin_bonus1 = ""
    # lbl_admin_bonus2 = ""
    # lbl_admin_bonus3 = ""
    # lbl_admin_bonus4 = ""
    # lbl_admin_bonus5 = ""
    # lbl_admin_bonus6 = ""
    # lbl_admin_bonus7 = ""
    # lbl_admin_bonus8 = ""
    # lbl_admin_bonus9 = ""
    # lbl_admin_bonus10 = ""
    #
    # lbl_admin_use = ""       # 관리자 환경설정 라벨
    # lbl_admin_version = ""
    #
    # lbl_admin_password = ""
    # lbl_admin_card_issued_money = ""
    # lbl_admin_min_card_issued_money = ""
    # lbl_admin_shop_id = ""
    #
    # # Entry
    # entry_login = ""
    # entry_admin_bonus1 = ""
    # entry_admin_bonus2 = ""
    # entry_admin_bonus3 = ""
    # entry_admin_bonus4 = ""
    # entry_admin_bonus5 = ""
    # entry_admin_bonus6 = ""
    # entry_admin_bonus7 = ""
    # entry_admin_bonus8 = ""
    # entry_admin_bonus9 = ""
    # entry_admin_bonus10 = ""
    #
    # entry_admin_password = ""
    # entry_admin_card_issued_money = ""
    # entry_admin_min_card_issued_money = ""
    # entry_admin_shop_id = ""
    #
    # # Button
    # btn_admin_init_shop_id = ""
    # btn_admin_save = ""
    # btn_admin_cancel = ""
    # btn_admin_exit = ""
    #
    # print("init 보다 먼저시작함")
    #
    # def showMsgInfo(self, msg):
    #     tkinter.messagebox.showinfo("확인", msg)
    #
    # def showMsgYesNo(self, msg):
    #     result = tkinter.messagebox.askyesno("확인", msg)
    #     return result
    #
    # def adminAuthSuccess(self, password):
    #     if password == "1234":
    #         self.showFrame(self, self.frame_admin)
    #     elif password == "gls12q23w":
    #         self.showFrame(self, self.master.frame_master)
    #     else:
    #         msg = "잘못된 비밀번호 입니다."
    #         self.showMsgInfo(msg)


    # 관리자 페이지, 카드 초기화 페이지 UI 초기화
    def __init__(self, frame, tk_window):
        print("admin init")
        self.frame_login = Frame(tk_window)
        self.entry_login = Entry(self.frame_login, show="*")

        # Application.test(self)
        # Admin Login Page
        # self.hide_login_btn = Button(Application.main_frame, bd=0, bg="#a8c4b9", width=30, height=4,
        #                                     command=lambda: Application.showFrame(self.login_frame))
        # self.hide_login_btn.place(x=20, y=0)
        # # admin_class.login_lbl.bind('<Button-1>', self.showFrame(admin_class.login_frame))
        #
        # self.login_entry = Entry(self.login_frame, show="*")
        # self.login_entry.place(x=387, y=407)
        # self.login_config_btn = Button(self.login_frame, text="확인", width=6,
        #                                       command=lambda: self.adminAuthSuccess(self.login_entry.get()))
        # self.login_config_btn.place(x=540, y=403)
        # self.login_cancel_btn = Button(self.login_frame, text="취소", width=6,
        #                                command=lambda: Application.showFrame(Application.main_frame))
        # self.login_cancel_btn.place(x=600, y=403)

