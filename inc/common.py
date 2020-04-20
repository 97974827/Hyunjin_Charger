from tkinter import *
import tkinter.messagebox
import re


class Common:
    def toggleLabel(self, label, label_place):
        if label.visible:
            label.place_forget()
        else:
            label.place(label_place)
        label.visible = not label.visible

    def showMsgInfo(self, msg):
        tkinter.messagebox.showinfo("확인", msg)

    def showMsgYesNo(self, msg):
        result = tkinter.messagebox.askyesno("확인", msg)
        return result

    def adminAuthSuccess(self, password):
        if password == "1234":
            self.showFrame(self.frame_admin)
        elif password == "gls12q23w":
            self.showFrame(self.frame_master)
        else:
            msg = "잘못된 비밀번호 입니다."
            self.showMsgInfo(msg)

    def showFrame(self, frame):
        frame.tkraise()


# TODO : Test Code
if __name__ == '__main__':
    pass