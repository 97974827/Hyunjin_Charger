from tkinter import *
from inc import admin
from inc import master


class Application:
    '''UI Control Variable'''

    # Main View
    window = ""
    main_back = ""
    main_frame = ""

    main_hello_label = ""
    main_use_label = ""
    main_money_label = ""

    charge_off_btn = ""
    charge_on_btn = ""
    issued_off_btn = ""
    issued_on_btn = ""
    lookup_off_btn = ""
    lookup_on_btn = ""

    # Card Charge View
    charge_frame = ""
    charge1_frame = ""
    charge2_frame = ""
    charge_back = ""
    charge1_back = ""
    charge2_back = ""
    charge_next_btn_off = ""
    charge_next_btn_on = ""
    charge_next_btn_ani = ""
    charge_back_btn = ""
    charge1_back_btn = ""
    charge_money_lbl = ""
    charge1_money_lbl = ""
    charge1_bonus_lbl = ""
    charge2_money_lbl = ""

    # 추후 삭제해야함
    temp_charge1_next_btn = ""
    temp_charge2_next_btn = ""

    # Card Issued View
    issued_frame = ""
    issued_back = ""
    issued_next_btn_off = ""
    issued_next_btn_on = ""
    issued_next_btn_ani = ""
    issued_back_btn = ""
    issued_money_lbl = ""
    issued_card_issued_money_lbl = ""

    # Card Lookup View
    lookup_frame = ""
    lookup_back = ""
    lookup_back_btn = ""
    lookup_money_lbl = ""

    # Class Initialize View
    # admin_class = admin.Admin()
    # master_class = master.Master()

    def showFrame(self, frame):
        frame.tkraise()

    def test(self):
        print("main test")

    # UI Initialize
    def __init__(self, admin_class, master_class):
        self.window = Tk()                        # 윈도우창 생성
        self.window.title("kang hyun jin")        # 윈도우이름.title("제목")
        self.window.geometry("1024x768+50+50")    # 윈도우이름.geometry("너비x높이+xpos+ypos")
        self.window.resizable(False, False)       # 윈도우이름.resizeable(상하,좌우) : 인자 상수를 입력해도 적용가능

        self.main_frame = Frame(self.window)
        self.charge_frame = Frame(self.window)
        self.charge1_frame = Frame(self.window)
        self.charge2_frame = Frame(self.window)
        self.issued_frame = Frame(self.window)
        self.lookup_frame = Frame(self.window)

        admin_class.login_frame = Frame(self.window)
        admin_class.admin_frame = Frame(self.window)
        admin_class.init_frame = Frame(self.window)
        master_class.master_frame = Frame(self.window)

        frame_array = [self.main_frame, self.charge_frame, self.charge1_frame, self.charge2_frame,
                       self.issued_frame, self.lookup_frame, admin_class.login_frame, admin_class.admin_frame,
                       master_class.master_frame, admin_class.init_frame]

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
        charge_next_btn_gif_image = PhotoImage(file="./images/next_btn_ani.gif")

        # TODO : 하드웨어 테스트 할 때 ON, OFF 처리해야함
        charge_btn_image = PhotoImage(file="./images/charge_on_btn.png")
        issued_btn_image = PhotoImage(file="./images/issued_on_btn.png")
        lookup_btn_image = PhotoImage(file="./images/lookup_on_btn.png")
        main_use_image = PhotoImage(file="./images/main_use_label.png")

        # 테스트
        # main_image = PhotoImage(file="./images/test_back.png")
        # self.main_back = Label(self.main_frame, image=main_image).pack()
        # charge1_frame_image = PhotoImage(file="./images/charge1_frame.png")
        # charge_frame_image = PhotoImage(file="./images/issued_frame.png")

        # background config
        self.main_back = Label(self.main_frame, image=main_frame_image).pack()
        self.charge_back = Label(self.charge_frame, image=charge_frame_image).pack()
        self.charge1_back = Label(self.charge1_frame, image=charge1_frame_image).pack()
        self.charge2_back = Label(self.charge2_frame, image=charge2_frame_image).pack()
        self.issued_back = Label(self.issued_frame, image=issued_frame_image).pack()
        self.lookup_back = Label(self.lookup_frame, image=lookup_frame_image).pack()

        # Main View
        self.charge_on_btn = Button(self.main_frame, image=charge_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.charge_frame))
        self.charge_on_btn.place(x=90, y=240)

        self.issued_on_btn = Button(self.main_frame, image=issued_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.issued_frame))
        self.issued_on_btn.place(x=390, y=240)

        self.lookup_on_btn = Button(self.main_frame, image=lookup_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.lookup_frame))
        self.lookup_on_btn.place(x=690, y=240)

        main_hello_label = Label(self.main_frame, text="저희 세차장을 이용해주셔서 감사합니다.", font=("Corier", 20), bg="#a8c4b9")
        main_hello_label.place(x=60, y=70)
        self.main_use_label = Label(self.main_frame, image=main_use_image, bd=0)  # bd=테두리 두께(default:2)
        self.main_use_label.place(x=280, y=532)
        self.main_money_label = Label(self.main_frame, text="투입금액      0 원", font=("Corier", 30, "bold"), bg="#a8c4b9")
        self.main_money_label.place(x=330, y=705)

        admin_class.login_lbl = Button(self.main_frame, bd=0, bg="#a8c4b9", width=30, height=3,
                                       command=lambda:self.showFrame(admin_class.login_frame))
        admin_class.login_lbl.place(x=20, y=0)
        admin_class.login_lbl.pack_forget()
        # admin_class.login_lbl.bind('<Button-1>', command=lambda:self.showFrame(admin_class.login_frame))
        admin_class.login_bnt = Button(admin_class.login_frame, text="취소",
                                       command=lambda:self.showFrame(self.main_frame)).place(x=500, y=500)

        # Charge Card Page
        self.charge_back_btn = Button(self.charge_frame, image=charge_back_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.main_frame))
        self.charge_back_btn.place(x=57, y=657)
        self.charge_next_btn_on = Button(self.charge_frame, image=charge_next_btn_on_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.charge1_frame))
        self.charge_next_btn_on.place(x=833, y=657)    # hidden state 다음 버튼위치
        # self.charge_next_btn_on.place(x=777, y=630)  # gif 다음 버튼위치
        self.charge_money_lbl = Label(self.charge_frame, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40),
                                      anchor="e")
        self.charge_money_lbl.place(x=740, y=223)
        self.charge1_money_lbl = Label(self.charge1_frame, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40),
                                      anchor="e")
        self.charge1_money_lbl.place(x=740, y=223)
        self.charge1_bonus_lbl = Label(self.charge1_frame, text="0 원", fg="#ffffff", bg="#464646", font=("Corier", 12),
                                      anchor="e")
        self.charge1_bonus_lbl.place(x=795, y=298)
        self.charge2_money_lbl = Label(self.charge2_frame, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40),
                                       anchor="e")
        self.charge2_money_lbl.place(x=740, y=223)

        # TODO : 하드웨어 테스트 이후 지워야할 화면처리
        self.charge1_back_btn = Button(self.charge1_frame, image=charge_back_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.charge_frame))
        self.charge1_back_btn.place(x=57, y=657)

        self.temp_charge1_next_btn = Button(self.charge1_frame, image=charge_next_btn_on_image, bd=0, bg="#a8c4b9",
                                    command=lambda: self.showFrame(self.charge2_frame))
        self.temp_charge1_next_btn.place(x=833, y=657)
        self.temp_charge2_next_btn = Button(self.charge2_frame, image=charge_next_btn_on_image, bd=0, bg="#a8c4b9",
                                            command=lambda: self.showFrame(self.main_frame))
        self.temp_charge2_next_btn.place(x=833, y=657)
        # TODO : 끝

        # Issued Card Page
        self.issued_back_btn = Button(self.issued_frame, image=charge_back_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.main_frame))
        self.issued_back_btn.place(x=57, y=657)
        self.issued_next_btn_on = Button(self.issued_frame, image=charge_next_btn_on_image, bd=0, bg="#a8c4b9",
                                      command=lambda: self.showFrame(self.main_frame))
        self.issued_next_btn_on.place(x=833, y=657)
        self.issued_money_lbl = Label(self.issued_frame, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40),
                                       anchor="e")
        self.issued_money_lbl.place(x=740, y=223)
        self.issued_card_issued_money_lbl = Label(self.issued_frame, text="0 원", fg="#ffffff", bg="#464646",
                                                  font=("Corier", 12), anchor="e")
        self.issued_card_issued_money_lbl.place(x=795, y=298)

        # Lookup Card Page
        self.lookup_back_btn = Button(self.lookup_frame, image=charge_back_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.main_frame))
        self.lookup_back_btn.place(x=57, y=657)
        self.lookup_money_lbl = Label(self.lookup_frame, text="0 원", fg="#33ffcc", bg="#454f49", font=("Corier", 40),
                                      anchor="e")
        self.lookup_money_lbl.place(x=740, y=223)

        # 시작전 메인 프레임 이미지초기화
        self.showFrame(self.main_frame)
        self.window.mainloop()  # 윈도우가 종료될 때까지 실행


if __name__ == '__main__':
    admin_class = admin.Admin()
    master_class = master.Master()
    main = Application(admin_class, master_class)