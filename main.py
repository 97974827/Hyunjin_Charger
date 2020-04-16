from tkinter import *
from inc import admin
from inc import master


class Application:
    '''UI Control Variable'''
    # 메인
    window = ""
    frame_array = ""
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

    # Card Charge
    charge_frame = ""
    charge1_frame = ""
    charge2_frame = ""
    charge_back = ""
    charge1_back = ""
    charge2_back = ""

    # Card Issued
    issued_frame = ""
    issued_back = ""

    # Card Lookup
    lookup_frame = ""
    lookup_back = ""

    # Class Initialize
    # admin_class = admin.Admin()
    # master_class = master.Master()

    def showFrame(self, frame):
        frame.tkraise()

    # UI Initialize
    def __init__(self):
        self.window = Tk()                        # 윈도우창 생성
        self.window.title("kang hyun jin")        # 윈도우이름.title("제목")
        self.window.geometry("1024x768+50+50")    # 윈도우이름.geometry("너비x높이+xpos+ypos")
        self.window.resizable(False, False)       # 윈도우이름.resizeable(상하,좌우) : 인자 상수를 입력해도 적용가능

        admin_class = admin.Admin()
        master_class = master.Master()

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

        # 테스트 메인이미지
        # main_image = PhotoImage(file="./images/test_back.png")
        # self.main_back = Label(self.window, image=main_image)
        # self.main_back.pack()

        self.frame_array = [self.main_frame, self.charge_frame, self.charge1_frame, self.charge2_frame,
                       self.issued_frame, self.lookup_frame, admin_class.login_frame, admin_class.admin_frame,
                       master_class.master_frame, admin_class.init_frame]

        for frame in self.frame_array:
            frame.grid(row=0, column=0, sticky='news')

        # TODO: 이미지 변수는 그때그때 선언해서 처리해놓았음
        main_frame_image = PhotoImage(file="./images/main_back.png")
        charge_frame_image = PhotoImage(file="./images/new_charge_back.png")
        charge1_frame_image = PhotoImage(file="./images/charge1_back.png")
        charge2_frame_image = PhotoImage(file="./images/charge2_back.png")
        issued_frame_image = PhotoImage(file="./images/new_issued_back.png")
        lookup_frame_image = PhotoImage(file="./images/lookup_back.png")

        self.main_back = Label(self.main_frame, image=main_frame_image, bg="#a8c4b9").pack()
        self.charge_back = Label(self.charge_frame, image=charge_frame_image).pack()
        self.charge1_back = Label(self.charge1_frame, image=charge1_frame_image).pack()
        self.charge2_back = Label(self.charge2_frame, image=charge2_frame_image).pack()
        self.issued_back = Label(self.issued_frame, image=issued_frame_image).pack()
        self.lookup_back = Label(self.lookup_frame, image=lookup_frame_image).pack()

        # TODO : 하드웨어 테스트 할 때 ON, OFF 처리해야함
        charge_btn_image = PhotoImage(file="./images/charge_on_btn.png")
        issued_btn_image = PhotoImage(file="./images/issued_on_btn.png")
        lookup_btn_image = PhotoImage(file="./images/lookup_on_btn.png")
        main_use_image = PhotoImage(file="./images/main_use_label.png")

        self.charge_on_btn = Button(self.main_back, image=charge_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.charge_frame))
        self.charge_on_btn.place(x=90, y=240)

        self.issued_on_btn = Button(self.main_back, image=issued_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.issued_frame))
        self.issued_on_btn.place(x=390, y=240)

        self.lookup_on_btn = Button(self.main_back, image=lookup_btn_image, bd=0, bg="#a8c4b9",
                                    command=lambda:self.showFrame(self.lookup_frame))
        self.lookup_on_btn.place(x=690, y=240)

        main_hello_label = Label(self.main_back, text="저희 세차장을 이용해주셔서 감사합니다.", font=("Corier", 20), bg="#a8c4b9")
        main_hello_label.place(x=60, y=70)

        self.main_use_label = Label(self.main_back, image=main_use_image, bd=0)  # bd=테두리 두께(default:2)
        self.main_use_label.place(x=280, y=532)

        self.main_money_label = Label(self.main_back, text="투입금액       0 원", font=("Corier", 30, "bold"), bg="#a8c4b9")
        self.main_money_label.place(x=330, y=705)

        # Card Charge Page

        self.window.mainloop()  # 윈도우가 종료될 때까지 실행


if __name__ == '__main__':
    app = Application()
