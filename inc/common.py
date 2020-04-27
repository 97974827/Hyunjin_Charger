import tkinter.messagebox


class Common:
    def toggleLabel(self, label, label_place):
        if label.visible:
            label.place_forget()
            label.visible = False
        else:
            label.place(label_place)
            label.visible = True

    def showMsgInfo(self, msg):
        tkinter.messagebox.showinfo("확인", msg)

    def showMsgYesNo(self, msg):
        result = tkinter.messagebox.askyesno("확인", msg)
        return result

    def stringNumberFormat(self, str_number):
        mark = ''

        if str_number[0] == '-':
            print("?")
            mark = '-'
            str_number = str_number[1:]

        # 4자리 이하
        if len(str_number) < 4:
            return mark + str_number

        # 콤마 찍는 자릿수 구하기
        digit = (len(str_number) - 1) % 3 + 1
        result_str_number = str_number[0:digit]

        # 세 자릿수 마다 콤마 찍기
        for index in range(digit, len(str_number), 3):
            result_str_number += ',' + str_number[index:(index+3)]
        # print(type(mark + result_str_number))
        return mark + result_str_number


# TODO : Test Code
if __name__ == '__main__':
    pass
    # app = Common()
    # res = app.stringNumberFormat("100000000")
    # print(res)