from smartcard.CardMonitoring import CardObserver, CardMonitor
from smartcard.System import readers
from smartcard.scard import SCARD_CTL_CODE
from smartcard.util import toHexString
import time
import platform


class Reader(CardObserver):
    # State Flag
    INIT_STATE = False
    CHARGE_STATE = False
    ISSUED_STATE = False
    LOOKUP_STATE = False

    UID_BYTE = [0xFF, 0xCA, 0x00, 0x00, 0x04]         # 시리얼 번호 바이트
    LOAD_KEY_SELECT = [0xFF, 0x82, 0x00, 0x00, 0x06]  # 로드 키 셀렉트

    AUTH_SELECT = [0xFF, 0x86, 0x00, 0x00, 0x05]  # 인증 셀렉트
    AUTH_DF = [0x01, 0x00, 0x00, 0x60, 0x00]      # 인증 데이터

    READ_BINARY_SELECT_ADDRESS1 = [0xFF, 0xB0, 0x00, 0x01, 0x10]    # 1번 바이너리 블록 셀렉트
    READ_BINARY_SELECT_ADDRESS2 = [0xFF, 0xB0, 0x00, 0x02, 0x10]    # 2번 바이너리 블록 셀렉트

    UPDATE_BINARY_SELECT_ADDRESS1 = [0xFF, 0xD6, 0x00, 0x01, 0x10]    # 1번 업데이트 바이너리 블록 셀렉트
    UPDATE_BINARY_SELECT_ADDRESS2 = [0xFF, 0xD6, 0x00, 0x02, 0x10]    # 2번 업데이트 바이너리 블록 셀렉트

    BUZZER_BYTE = [0xE0, 0x00, 0x00, 0x28, 0x01, 0x0A]  # 부저 바이트

    CRC = [
        0x05, 0x0F, 0x0A, 0x1B, 0x1E, 0x14, 0x11, 0x33, 0x36, 0x3C,
        0x39, 0x28, 0x2D, 0x27, 0x22, 0x63, 0x66, 0x6C, 0x69, 0x78,
        0x7D, 0x77, 0x72, 0x50, 0x55, 0x5F, 0x5A, 0x4B, 0x4E, 0x44,
        0x41, 0xC3, 0xC6, 0xCC, 0xC9, 0xD8, 0xDD, 0xD7, 0xD2, 0xF0,
        0xF5, 0xFF, 0xFA, 0xEB, 0xEE, 0xE4, 0xE1, 0xA0, 0xA5, 0xAF,
        0xAA, 0xBB, 0xBE, 0xB4, 0xB1, 0x93, 0x96, 0x9C, 0x99, 0x88,
        0x8D, 0x87, 0x82, 0x83, 0x86, 0x8C, 0x89, 0x98, 0x9D, 0x97,
        0x92, 0xB0, 0xB5, 0xBF, 0xBA, 0xAB, 0xAE, 0xA4, 0xA1, 0xE0,
        0xE5, 0xEF, 0xEA, 0xFB, 0xFE, 0xF4, 0xF1, 0xD3, 0xD6, 0xDC,
        0xD9, 0xC8, 0xCD, 0xC7, 0xC2, 0x40, 0x45, 0x4F, 0x4A, 0x5B
    ]
    # 05D355B94FEE 길광
    # 0000000021B0 구길광
    # 0350870E930E 대진

    # (신)길광 체크섬 구해서 인자와 비교하는 방식 : 금액 crc, 매장 ID crc
    # TODO : DB에서 encrypt 필드값 검색 후 초기 조건 등록하기 / 1: 신버전
    def getCheckSum(self, serial, money, shop, money_crc, shop_crc):
        money = int(money, 16) / 1000
        compare_money_index = int(int(serial, 16) + money) % 100

        shop_total = int(serial, 16) + int(shop, 16)
        compare_shop_index = int(shop_total % 100)

        compare_money_crc = self.CRC[compare_money_index]
        compare_shop_crc = self.CRC[compare_shop_index]
        print(compare_money_crc)
        print(compare_shop_crc)

        if money_crc == compare_money_crc and shop_crc == compare_shop_crc:
            return True
        else:
            return False

    def getMasterCheckSumValue(self, serial):
        master_index = (int(serial, 16) + 0x0b) % 100
        response = self.CRC[master_index]
        return int(response, 16)

    def changeListSerialNumber(self, serial_number):
        response = hex(serial_number[3])[2:].rjust(2, "0")
        response += hex(serial_number[2])[2:].rjust(2, "0")
        response += hex(serial_number[1])[2:].rjust(2, "0")
        response += hex(serial_number[0])[2:].rjust(2, "0")
        response = response.upper()
        return response

    def getShopId(self, block):
        shop_id = hex(block[14])[2:].rjust(2, "0")
        shop_id += hex(block[15])[2:].rjust(2, "0")
        return shop_id

    # TODO : 금액 10진수 변환 아직 안함
    def remainMoneyCalculate(self, binary_block):
        remain_money = hex(binary_block[3])[2:].rjust(2, "0")
        remain_money += hex(binary_block[2])[2:].rjust(2, "0")
        remain_money += hex(binary_block[0])[2:].rjust(2, "0")
        remain_money += hex(binary_block[1])[2:].rjust(2, "0")

        index = 0
        for r in remain_money:
            if r != "0": break
            index += 1
        # print("index : ", index)

        # remain_money = remain_money[index:]
        # remain_money = int(remain_money, 16)
        # print(remain_money)
        # print(type(remain_money))

        return remain_money

    def __init__(self):
        self.cards = []

    def update(self, observable, actions):
        # TODO : DB처리 할때 매장번호 다시 가져오기
        gookil_loay_key = [0x00, 0x00, 0x00, 0x00, 0x21, 0xB0]
        kil_load_key = [0x05, 0xD3, 0x55, 0xB9, 0x4F, 0xEE]
        dae_load_key = [0x03, 0x50, 0x87, 0x0E, 0x93, 0x0E]

        (addedcards, removedcards) = actions

        for card in addedcards:
            if card not in self.cards:
                self.cards += [card]

                try:
                    r = readers()

                    # Charge / Lookup Card Reader
                    if card.reader == str(r[0]):
                        print("+ Inserted r[0]: ", toHexString(card.atr))
                        card.connection = card.createConnection()
                        card.connection.connect()

                        # Serial Number Get
                        serial_number, is_serial, sw2 = card.connection.transmit(self.UID_BYTE)

                        if serial_number and len(serial_number) > 2 and is_serial == 144:
                            serial_number = self.changeListSerialNumber(serial_number)
                            load_key, is_load_key, sw2 = card.connection.transmit(self.LOAD_KEY_SELECT + kil_load_key)

                            # Load Key Success
                            if is_load_key == 144:
                                auth, is_authentication, sw2 = card.connection.transmit(self.AUTH_SELECT + self.AUTH_DF)

                                # Authentication Success
                                if is_authentication == 144:
                                    # TODO : DB에서 카드 저장번지에 맞춰 바이너리 블록 read
                                    binary_block_number, is_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS1)
                                    print("Binary Block 1 : ", binary_block_number)
                                    backup_binary_block_number, is_backup_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS2)
                                    print("Binary Block 2 : ", backup_binary_block_number)

                                    # Read Binary Block Success
                                    if binary_block_number and is_read_block_number == 144:
                                        remain_money = self.remainMoneyCalculate(binary_block_number)
                                        backup_remain_money = self.remainMoneyCalculate(backup_binary_block_number)

                                        print("카드 번호 : ", serial_number)
                                        print("카드 잔액 : ", remain_money)
                                        print("백업 카드잔액 : ", backup_remain_money)

                                        shop_id = self.getShopId(binary_block_number)
                                        backup_shop_id = self.getShopId(backup_binary_block_number)
                                        print("상점ID : ", shop_id)
                                        print("백업상점ID : ", backup_shop_id)

                                        master_byte_value = str(binary_block_number[11])
                                        master_byte_crc = str(binary_block_number[12])

                                        backup_master_byte_value = str(backup_binary_block_number[11])
                                        backup_master_byte_crc = str(backup_binary_block_number[12])
                                        print("마스터 블록 : ", master_byte_value, master_byte_crc)
                                        print("백업 마스터블록 : ", backup_master_byte_value, backup_master_byte_crc)

                                        is_check_sum = self.getCheckSum(serial_number, remain_money, shop_id, binary_block_number[4], binary_block_number[13])

                                        # checksum 맞지 않을 경우 다른 번지 검증
                                        if not is_check_sum:
                                            remain_money = backup_remain_money
                                            shop_id = backup_shop_id
                                            master_byte_value = backup_master_byte_value
                                            master_byte_crc = backup_master_byte_crc

                                            is_check_sum = self.getCheckSum(serial_number, remain_money, shop_id,
                                                            backup_binary_block_number[4], backup_binary_block_number[13])

                                            compare_master_byte_value = self.getMasterCheckSumValue(serial_number)


                                        if 'Windows' in platform.system():
                                            is_check_sum = True

                                        if is_check_sum:
                                            remain_money = remain_money.upper()
                                            money = int(remain_money, 16)

                                            shop_id = shop_id.upper()


                                        # card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                    else:
                                        print("Read Binary block Failed!")
                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                else:
                                    print("Authentication Failed!")
                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                            else:
                                print("Load Key Failed!")
                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)


                    # Issued Card Reader
                    elif card.reader == str(r[1]):
                        print("+ Inserted r[1]: ", toHexString(card.atr))
                        card.connection = card.createConnection()
                        card.connection.connect()

                except Exception as error:
                    print("RF reader Exception : " + str(error))
                finally:
                    card.connection.disconnect()

        for card in removedcards:
            print("- Removed: ", toHexString(card.atr))
            if card in self.cards:
                self.cards.remove(card)


# TODO : RFreader Test Code
if __name__ == '__main__':
    cardmonitor = CardMonitor()
    RFreader_class = Reader()
    cardmonitor.addObserver(RFreader_class)
    RFreader_class.LOOKUP_STATE = True
    time.sleep(100)
