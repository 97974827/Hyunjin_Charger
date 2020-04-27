import serial
import platform


class Bill:
    bill_serial = None
    BILL_CONNECT = False
    BILL_STATE = False

    BILL_PORT = "COM5"
    if 'Linux' in platform.system():
        #BILL_PORT = "/dev/ttyS0"
        BILL_PORT = "/dev/ttyUSB1"
    BILL_BAUD = "9600"

    bill_receive_data = ""

    input_money = 0
    bonus = 0
    total_money = 0

    # Bill class Serial connection
    # trans_str : argument from main
    def billSendData(self, trans_str):
        try:
            # self.billConnectSerial()
            self.bill_serial = serial.Serial(self.BILL_PORT, self.BILL_BAUD, timeout=1)

            if trans_str == "hi":
                check_sum = 0x48 + 0x69 + 0x3f
                trans_data = bytearray([0x24, 0x48, 0x69, 0x3f, check_sum])
                self.bill_receive_data = self.bill_serial.read(self.bill_serial.write(bytes(trans_data)))
                receive_str = "".join(map(chr, self.bill_receive_data))

                # connection success
                if "$me" in receive_str:
                    self.BILL_CONNECT = True
                    check_sum = 0x65 + 0x73 + 0x21
                    trans_data = bytearray([0x24, 0x65, 0x73, 0x21, check_sum])
                    self.bill_receive_data = self.bill_serial.readline(self.bill_serial.write(trans_data))
                else:
                    self.BILL_CONNECT = False

            # 입수가능
            elif trans_str == "insertE":
                check_sum = 0x53 + 0x41 + 0x0D
                trans_data = bytearray([0x24, 0x53, 0x41, 0x0D, check_sum])
                self.bill_receive_data = self.bill_serial.readline(self.bill_serial.write(trans_data))
                receive_str = "".join(map(chr, self.bill_receive_data))

                if "$OKa" in receive_str:
                    self.BILL_STATE = True
                    check_sum = 0x65 + 0x73 + 0x0D
                    trans_data = bytearray([0x24, 0x65, 0x73, 0x0D, check_sum])
                    self.bill_receive_data = self.bill_serial.readline(self.bill_serial.write(trans_data))
                else:
                    self.BILL_STATE = False

            # 입수금지
            elif trans_str == "insertD":
                check_sum = 0x53 + 0x41 + 0x0E
                trans_data = bytearray([0x24, 0x53, 0x41, 0x0E, check_sum])
                self.bill_receive_data = self.bill_serial.readline(self.bill_serial.write(trans_data))
                receive_str = "".join(map(chr, self.bill_receive_data))

                if "$OKa" in receive_str:
                    self.BILL_STATE = False
                    check_sum = 0x65 + 0x73 + 0x0D
                    trans_data = bytearray([0x24, 0x65, 0x73, 0x0D, check_sum])
                    self.bill_receive_data = self.bill_serial.readline(self.bill_serial.write(trans_data))
                else:
                    self.BILL_STATE = True

            # 지폐권종파악 : 그냥 문자열로 바꿔주면 문자식별 어려움 -> 리스트로 변환해서 처리함
            elif trans_str == "billdata":
                check_sum = 0x47 + 0x42 + 0x3f
                trans_data = bytearray([0x24, 0x47, 0x42, 0x3f, check_sum])
                self.bill_receive_data = self.bill_serial.read(self.bill_serial.write(trans_data))
                receive_str = "".join(map(chr, self.bill_receive_data))

                if "$gb" in receive_str:
                    receive_list = list()
                    for data in self.bill_receive_data:
                        receive_list.append(data)

                    if self.bill_receive_data[3] == 1:
                        self.bill_receive_data = 1000
                    elif self.bill_receive_data[3] == 5:
                        self.bill_receive_data = 5000
                    elif self.bill_receive_data[3] == 10:
                        self.bill_receive_data = 10000
                    elif self.bill_receive_data[3] == 50:
                        self.bill_receive_data = 50000
                    else:
                        self.bill_receive_data = 0
                else:
                    self.bill_receive_data = 0

            elif trans_str == "getActiveStatus":
                check_sum = 0x47 + 0x41 + 0x3f
                trans_str = bytearray([0x24, 0x47, 0x41, 0x3f, check_sum])
                self.bill_receive_data = self.bill_serial.read(self.bill_serial.write(trans_str))

                if self.bill_receive_data:
                    receive_str = list()
                    receive_str = "".join(map(chr, self.bill_receive_data))
                    search_idx = receive_str.find("$ga")
                    start_idx = search_idx + 3

                    if search_idx >= 0:
                        if len(self.bill_receive_data):
                            self.bill_receive_data = self.bill_receive_data[start_idx]

                    event_tx_idx = receive_str.find("$ES")

                    if event_tx_idx >= 0:
                        check_sum = 0x65 + 0x73 + self.bill_receive_data[event_tx_idx + 3]
                        trans_str = bytearray([0x24, 0x65, 0x73, self.bill_receive_data[event_tx_idx + 3], check_sum])
                        self.bill_serial.readline(self.bill_serial.write(bytes(trans_str)))

        except FileNotFoundError as error:
            print("지정된 파일을 찾을수 없습니다 :  ", error)
            self.BILL_CONNECT = False
        except UnboundLocalError as error:
            print("액세스 거부 : ", error)
            self.BILL_CONNECT = False
        except UnicodeDecodeError as error:
            print("디코딩 오류 : ", error)
            self.BILL_CONNECT = False
        except serial.serialutil.SerialException as error:
            print("오류 명령어 >> " + trans_str)
            print("시리얼 오류 : ", error)
            self.BILL_CONNECT = False
        except Exception as error:
            print("bill 오류 명령어 >> " + trans_str)
            print("오류를 알 수 없습니다 : ", error)
            self.BILL_CONNECT = False
        finally:
            self.billCloseSerial()
            return self.bill_receive_data

    def billGetActiveStatus(self, number):
        if number == 0:
            return "리셋 후 초기화 동작중"
        elif number == 1:
            return "초기화 후 대기중"
        elif number == 2:
            return "입수가능"
        elif number == 3:
            return "인식작업 중 오류로 인한 반환 작업 중"
        elif number == 4:
            return "인식작업 중"
        elif number == 5:
            return "인식작업 완료 후 대기 중(입수금지상태)"
        elif number == 7:
            return "반환동작 중"
        elif number == 8:
            return "반환동작 완료 후 대기 중(입수 금지상태)"
        elif number == 10:
            return "stack 동작 중"
        elif number == 11:
            return "stack 동작 완료 후 대기 중 (입수금지상태)"
        elif number == 12:
            return "동작 Error로 인한 대기중"
        elif number == 16:
            return "stack이 open된 상태(입수금지상태)"
        elif number == 17:
            return "강제 입수 동작 중"
        elif number == 18:
            return "강제 입수 완료 후 대기중"
        else:
            return number

    def billConnectSerial(self):
        try:
            self.bill_serial = serial.Serial(self.BILL_PORT, self.BILL_BAUD, timeout=1)
        except Exception as error:
            print("Bill Connect Serial Error : ", error)

    def billCloseSerial(self):
        if self.bill_serial:
            if self.bill_serial.isOpen():
                self.bill_serial.close()


# TODO : Test Code
if __name__ == '__main__':
    pass
    # app = Bill()
    # res = app.billSendData("hi")
    # res = app.billSendData("insertE")
    # res = app.billSendData("billdata")
    # print("res : ", res)
    # # app.billSendData("insertD")