import re


class test:
    def literal(self):
        text = "에러 1122 : 레퍼런스 오류\n 에러 1033: 아규먼트 오류"
        regex = re.compile("에러 1033")  # 정규식 객체 (re.RegexObject 클래스 객체)를 리턴 = re.compile(검색할문자열)
        mo = regex.search(text)

        if mo != None:
            print(mo.group())

    def strtext(self):
        text = "문의사항이 있으면 032-232-3245 으로 연락주시기 바랍니다."

        regex = re.compile(r'\d\d\d-\d\d\d-\d\d\d\d')
        matchobj = regex.search(text)
        phonenumber = matchobj.group()
        print(phonenumber)

    def money(self):
        str_money = "1000000000000"

        if str_money.find('.') < 0:
            e = re.compile(r"(\d)(\d\d\d)$")
            str_money, cnt = re.subn(e, r"\1,\2", str_money)
            print(str_money)
            print(cnt)

        e = re.compile(r"(\d)(\d\d\d([.,]))")
        while True:
            str_money, cnt = re.subn(e, r"\1,\2", str_money)
            print(str_money)
            print(cnt)
            if not cnt:
                break


if __name__ == '__main__':
    app = test()
    app.money()
