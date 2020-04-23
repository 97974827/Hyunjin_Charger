import serial
import platform


class Ejector:
    ejector_serial = None
    EJECTOR_CONNECT = False
    EJECTOR_STATE = False
    EJECTOR_INIT = False

    EJECTOR_PORT = "COM6"
    if 'Linux' in platform.system():
        EJECTOR_PORT = "/dev/ttyS1"
    EJECTOR_BAUD = "9600"

    ejector_receive_data = ""

    # Card Ejector Connection
    def ejectorSendData(self, trans_str):
        try:
            # self.ejectorConnectSerial()
            self.ejector_serial = serial.Serial(self.EJECTOR_PORT, self.EJECTOR_BAUD, timeout=1)

            if trans_str == "hi":
                check_sum = 0x48 + 0x49 + 0x3f
                trans_data = bytearray([0x24, 0x48, 0x49, 0x3f, check_sum])
                self.ejector_receive_data = self.ejector_serial.readline(self.ejector_serial.write(trans_data))
                receive_str = "".join(map(chr, self.ejector_receive_data))

                # connection success
                if "$me" in receive_str:
                    self.EJECTOR_CONNECT = True
                else:
                    self.EJECTOR_CONNECT = False

            elif trans_str == "init":
                check_sum = 0x49 + 0x00 + 0x00
                trans_data = bytearray([0x24, 0x49, 0x00, 0x00, check_sum])
                self.ejector_receive_data = self.ejector_serial.readline(self.ejector_serial.write(trans_data))
                receive_str = "".join(map(chr, self.ejector_receive_data))

                if "$ia" in receive_str:
                    self.EJECTOR_INIT = True
                else:
                    self.EJECTOR_INIT = False

            elif trans_str == "disable":
                check_sum = 0x48 + 0x00 + 0x00
                trans_data = bytearray([0x24, 0x48, 0x00, 0x00, check_sum])
                self.ejector_receive_data = self.ejector_serial.readline(self.ejector_serial.write(trans_data))
                receive_str = "".join(map(chr, self.ejector_receive_data))

                if "$ha" in receive_str:
                    print(receive_str)
                    self.EJECTOR_STATE = False
                else:
                    self.EJECTOR_STATE = True

            elif trans_str == "enable":
                check_sum = 0x48 + 0x43 + 0x3f
                trans_data = bytearray([0x24, 0x48, 0x43, 0x3f, check_sum])
                self.ejector_receive_data = self.ejector_serial.readline(self.ejector_serial.write(trans_data))
                receive_str = "".join(map(chr, self.ejector_receive_data))

                if "$hc" in receive_str:
                    self.EJECTOR_STATE = True
                else:
                    self.EJECTOR_STATE = False

            elif trans_str == "output":
                check_sum = 0x44 + 0x01 + 0x53
                trans_data = bytearray([0x24, 0x44, 0x01, 0x53, check_sum])
                self.ejector_receive_data = self.ejector_serial.readline(self.ejector_serial.write(trans_data))
                receive_str = "".join(map(chr, self.ejector_receive_data))

            elif trans_str == "state":
                check_sum = 0x53 + 0x00 + 0x00
                trans_data = bytearray([0x24, 0x53, 0x00, 0x00, check_sum])
                self.ejector_receive_data = self.ejector_serial.readline(self.ejector_serial.write(trans_data))

                # "대기상태"
                if self.ejector_receive_data == b'$stb':
                    self.ejector_receive_data = 1
                # "배출 동작중"
                elif self.ejector_receive_data == b'$sonP':
                    self.ejector_receive_data = 2
                # "배출기 동작 금지 상태"
                elif self.ejector_receive_data == b'$sth!':
                    self.ejector_receive_data = 3
                # "1장 배출 후 정상종료 상태"
                elif self.ejector_receive_data == b'$s\x01o\xe3':
                    self.ejector_receive_data = 4
                # "1장 배출 후 비정상종료 상태 or 카드 없음"
                elif self.ejector_receive_data == b'$s\x01n\xe2':
                    self.ejector_receive_data = 5
                # "1장 배출 후 도둑 감지상태"
                elif self.ejector_receive_data == b'$s\x01n\xe8':
                    self.ejector_receive_data = 6
                # "알수없는 오류"
                else:
                    self.ejector_receive_data = 7

            elif trans_str == "getErr":
                check_sum = 0x53 + 0x45 + 0x52
                req = bytearray([0x24, 0x53, 0x45, 0x52, check_sum])
                self.ejector_receive_data = self.ejector_serial.readline(self.ejector_serial.write(bytes(req)))

        except FileNotFoundError as error:
            print("지정된 파일을 찾을수 없습니다 :  ", error)
            self.EJECTOR_CONNECT = False
        except UnboundLocalError as error:
            print("액세스 거부 : ", error)
            self.EJECTOR_CONNECT = False
        except UnicodeDecodeError as error:
            print("디코딩 오류 : ", error)
            self.EJECTOR_CONNECT = False
        except Exception as error:
            print("ejector 오류 명령어 >> " + trans_str)
            print("오류를 알 수 없습니다 : ", error)
            self.EJECTOR_CONNECT = False
        finally:
            self.ejectorCloseSerial()
            return self.ejector_receive_data

    def ejectorConnectSerial(self):
        try:
            self.ejector_serial = serial.Serial(self.EJECTOR_PORT, self.EJECTOR_BAUD, timeout=1)
        except Exception as error:
            print("Ejector Serial Connect Error : ", error)

    def ejectorCloseSerial(self):
        if self.ejector_serial:
            if self.ejector_serial.isOpen():
                # print("Ejector Serial Close")
                self.ejector_serial.close()


# TODO : Test Code
if __name__ == '__main__':
    pass
    # app = Ejector()
    # res = app.ejectorSendData("hi")
    # res = app.ejectorSendData("init")
    # # res = app.ejectorSendData("disable")
    # # res = app.ejectorSendData("enable")
    # # res = app.ejectorSendData("output")
    # print("res : ", res)
