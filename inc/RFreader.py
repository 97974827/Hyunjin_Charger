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

    lookup_flag = "0"

    input_money = 0
    bonus = 0
    total_money = 0
    remain_money = 0

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

    # xor byte
    def getInvertBit(self, arg):
        result = arg ^ 0xFF
        res = hex(result).upper()
        return res

    # (신)길광 체크섬 구해서 인자와 비교하는 방식 : 금액 crc, 매장 ID crc
    # TODO : DB에서 encrypt 필드값 검색 후 초기 조건 등록하기 / 1: 신버전
    def getCheckSum(self, serial, money, shop, money_crc, shop_crc):
        money = int(money, 16) / 1000
        compare_money_index = int(int(serial, 16) + money) % 100

        shop_total = int(serial, 16) + int(shop, 16)
        compare_shop_index = int(shop_total % 100)

        compare_money_crc = self.CRC[compare_money_index]
        compare_shop_crc = self.CRC[compare_shop_index]
        # print(compare_money_crc)
        # print(compare_shop_crc)
        # print(money_crc)
        # print(shop_crc)

        if money_crc == compare_money_crc and shop_crc == compare_shop_crc:
            return True
        else:
            return False

    def getMasterCrcValue(self, serial):
        master_index = (int(serial, 16) + 11) % 100
        response = self.CRC[master_index]
        # return int(response, 16)
        return response

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

    # TODO : 금액 10진수 변환 안함
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

    # TODO : 초기에 DB에서 키값 암호화 여부 값을 가져와서 구/신버전 판단 , DB에서 공급업체번호 가져와서 update
    # Return Card Update Binary Block
    def setMoneyUpdateBinaryBlock(self, serial, money, shop):
        # 신버전
        int_serial = int(serial, 16)
        div_money = int(money / 1000)

        crc_money = (int_serial + div_money) % 100
        crc_shop = (int_serial + shop) % 100

        hex_money = hex(money)[2:].rjust(8, "0")
        hex_shop = hex(shop)[2:].rjust(4, "0")

        arg1 = int(hex_money[4:6], 16)
        arg2 = int(hex_money[6:8], 16)
        arg3 = int(hex_money[2:4], 16)
        arg4 = int(hex_money[0:2], 16)
        arg5 = self.CRC[crc_money]
        arg13 = self.CRC[crc_shop]
        manager_no = 1
        arg14 = int(hex_shop[0:2], 16)
        arg15 = int(hex_shop[2:4], 16)

        update_binary_block = [arg1, arg2, arg3, arg4, arg5, 0x00, 0x00, 0x00, 0xAA, 0x55, manager_no, 0x00, 0x00, arg13, arg14, arg15]

        # 구버전
        # hex_money = hex(money)[2:].rjust(8, "0")
        # hex_shop = hex(shop)[2:].rjust(4, "0")
        #
        # arg1 = int(hex_money[4:6], 16)
        # arg2 = int(hex_money[6:8], 16)
        # arg3 = int(hex_money[2:4], 16)
        # arg4 = int(hex_money[0:2], 16)
        # arg1_invert = self.getInvertBit(arg1)
        # arg2_invert = self.getInvertBit(arg2)
        # arg3_invert = self.getInvertBit(arg3)
        # arg4_invert = self.getInvertBit(arg4)
        #
        # arg5 = int(arg1_invert, 16)
        # arg6 = int(arg2_invert, 16)
        # arg7 = int(arg3_invert, 16)
        # arg8 = int(arg4_invert, 16)
        #
        # arg14 = int(hex_shop[0:2], 16)
        # arg15 = int(hex_shop[2:4], 16)
        # arg14_invert = self.getInvertBit(arg14)
        # arg15_invert = self.getInvertBit(arg15)
        #
        # arg12 = int(arg14_invert, 16)
        # arg13 = int(arg15_invert, 16)
        #
        # update_binary_block = [arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 0xAA, 0x55, 0x00, 0x00, arg12, arg13, arg14, arg15]

        return update_binary_block

    # TODO : 초기에 DB에서 키값 암호화 여부 값을 가져와서 구/신버전 판단 , DB에서 공급업체번호 가져와서 update
    # Return Card Initialize Binary Block
    def setInitUpdateBinaryBlock(self, serial, int_money, int_shop):
        int_money = 0

        # 신버전
        int_serial = int(serial, 16)
        crc_index_money = (int_serial + int_money) % 100
        crc_index_shop = (int_serial + int_shop) % 100

        str_hex_money = hex(int_money)[2:].rjust(8, "0")
        str_hex_shop = hex(int_shop)[2:].rjust(4, "0")

        arg1 = int(str_hex_money[4:6], 16)
        arg2 = int(str_hex_money[6:8], 16)
        arg3 = int(str_hex_money[0:2], 16)
        arg4 = int(str_hex_money[2:4], 16)
        arg5 = self.CRC[crc_index_money]
        manager_no = 1
        arg13 = self.CRC[crc_index_shop]
        arg14 = int(str_hex_shop[0:2], 16)
        arg15 = int(str_hex_shop[2:4], 16)

        init_binary_block = [arg1, arg2, arg3, arg4, arg5, 0x00, 0x00, 0x00, 0x00, 0x00, manager_no, 0x00, 0x00, arg13, arg14, arg15]

        # 구버전
        # str_hex_money = hex(int_money)[2:].rjust(8, "0")
        # str_hex_shop = hex(int_shop)[2:].rjust(4, "0")
        # arg1 = int(str_hex_money[4:6], 16)
        # arg2 = int(str_hex_money[6:8], 16)
        # arg3 = int(str_hex_money[0:2], 16)
        # arg4 = int(str_hex_money[2:4], 16)
        # arg1_invert = self.getInvertBit(arg1)
        # arg2_invert = self.getInvertBit(arg2)
        # arg3_invert = self.getInvertBit(arg3)
        # arg4_invert = self.getInvertBit(arg4)
        #
        # arg5 = int(arg1_invert, 16)
        # arg6 = int(arg2_invert, 16)
        # arg7 = int(arg3_invert, 16)
        # arg8 = int(arg4_invert, 16)
        # arg9 = 0xAA
        # arg10 = 0x55
        # arg14 = int(str_hex_shop[0:2], 16)
        # arg15 = int(str_hex_shop[2:4], 16)
        # arg12 = self.getInvertBit(arg14)
        # arg13 = self.getInvertBit(arg15)
        #
        # init_binary_block = [arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 0xAA, 0x55, 0x00, 0x00, arg12, arg13, arg14, arg15]

        return init_binary_block

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

                    # Charge / Lookup State Reading Card
                    if card.reader == str(r[0]):
                        # print("+ Inserted r[0]: ", toHexString(card.atr))
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
                                    # TODO : DB에서 카드 저장번지에 맞춰 바이너리 블록 read / 바이너리 블록값은 16진수 상태?
                                    binary_block_number_1, is_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS2)
                                    print("Binary Block 1 : ", binary_block_number_1)
                                    binary_block_number_2, is_backup_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS1)
                                    print("Binary Block 2 : ", binary_block_number_2)

                                    # Read Binary Block Success
                                    # TODO : 바이너리 블록 목록값은 10진수  2020 04.23
                                    if binary_block_number_1 and is_read_block_number == 144:
                                        remain_money = self.remainMoneyCalculate(binary_block_number_1)
                                        backup_remain_money = self.remainMoneyCalculate(binary_block_number_2)

                                        shop_id = self.getShopId(binary_block_number_1)
                                        backup_shop_id = self.getShopId(binary_block_number_2)

                                        master_block_value = binary_block_number_1[11]
                                        master_block_crc = binary_block_number_1[12]

                                        master_backup_block_value = binary_block_number_2[11]
                                        master_backup_block_crc = binary_block_number_2[12]

                                        is_check_sum = self.getCheckSum(serial_number, remain_money, shop_id, binary_block_number_1[4], binary_block_number_1[13])

                                        # checksum 맞지 않을 경우 다른 카드저장번지 검증
                                        if not is_check_sum:
                                            remain_money = backup_remain_money
                                            shop_id = backup_shop_id
                                            master_block_value = master_backup_block_value
                                            master_block_crc = master_backup_block_crc

                                            is_check_sum = self.getCheckSum(serial_number, remain_money, shop_id, binary_block_number_2[4], binary_block_number_2[13])

                                            # 백업저장 번지도 맞지않으면 마스터 검증
                                            compare_master_crc = self.getMasterCrcValue(serial_number)
                                            if master_block_value == 11 and compare_master_crc == master_block_crc:
                                                print("This is a master card")
                                                is_check_sum = True

                                        # Nothing Verification Window Test
                                        if 'Windows' in platform.system():
                                            is_check_sum = True

                                        # Checksum Verification Success
                                        if is_check_sum:
                                            remain_money = remain_money.upper()
                                            int_remain_money = int(remain_money, 16)

                                            shop_id = shop_id.upper()
                                            int_shop_id = int(shop_id, 16)
                                            # self.INIT_STATE = True  # 초기화 테스트용
                                            # Card Initialize
                                            if self.INIT_STATE:
                                                self.CHARGE_STATE = False
                                                self.ISSUED_STATE = False
                                                self.LOOKUP_STATE = False

                                                init_binary_block = self.setInitUpdateBinaryBlock(serial_number, int_remain_money, int_shop_id)
                                                init, set_init_1, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS1 + init_binary_block)
                                                init, set_init_2, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + init_binary_block)

                                                if set_init_2 == 144:
                                                    time.sleep(0.25)
                                                    print("Card Initialize 2 Address Success")
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                else:
                                                    print("Card Initialize 2 Address Failed")

                                                    if set_init_1 == 144:
                                                        time.sleep(0.25)
                                                        print("Card Initialize 2 Address Success")
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    else:
                                                        print("Card Initialize 2 Address Failed")
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                            else:
                                                # TODO : DB에서 매장ID 조회 하여 일치 여부 검사하기
                                                if shop_id:
                                                    # self.CHARGE_STATE = True  # 충전 테스트중
                                                    if self.CHARGE_STATE:
                                                        print("충전")
                                                        self.LOOKUP_STATE = False
                                                        self.ISSUED_STATE = False

                                                        if self.input_money > 0:
                                                            self.total_money = self.input_money + self.bonus + int_remain_money
                                                            update_binary_block = self.setMoneyUpdateBinaryBlock(serial_number, self.total_money, int_shop_id)

                                                            # TODO : DB에서 구/신버전 비교값 가져와서 업데이트 블록 설정하기
                                                            update_block_1, set_update_block1, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS1 + update_binary_block)
                                                            update_block_2, set_update_block2, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + update_binary_block)

                                                            if set_update_block2 == 144:
                                                                time.sleep(0.25)
                                                                print("2번지 업데이트 블록 : ", update_binary_block)
                                                                # self.input_money = 0  # 투입금액 테스트용
                                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                            else:
                                                                # TODO : print문 Error log처리
                                                                print("2번지 충전 실패함")

                                                                if set_update_block1 == 144:
                                                                    time.sleep(0.25)
                                                                    print("1번지 업데이트 블록 : ", update_binary_block)
                                                                    self.input_money = 0
                                                                    card.connection.control(SCARD_CTL_CODE(3500),self.BUZZER_BYTE)

                                                                else:
                                                                    print("1번지 충전 실패함")
                                                                    card.connection.control(SCARD_CTL_CODE(3500),self.BUZZER_BYTE)
                                                                    card.connection.control(SCARD_CTL_CODE(3500),self.BUZZER_BYTE)
                                                        else:
                                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                                    elif self.LOOKUP_STATE:
                                                        print("조회")
                                                        # is_check_sum = self.getCheckSum(serial_number, remain_money,
                                                        #             shop_id, binary_block_number_1[4], binary_block_number_1[13])

                                                        # if is_check_sum:
                                                        self.remain_money = int_remain_money
                                                        print("잔액 : ", self.remain_money)
                                                        self.lookup_flag = "1"
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        # else:
                                                        #     time.sleep(0.25)
                                                        #     update_binary_block = self.setMoneyUpdateBinaryBlock(serial_number, int_remain_money, int_shop_id)
                                                        #     update, set_update, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + update_binary_block)
                                                        #
                                                        #     # Card 2 Address Update Success
                                                        #     if set_update == 144:
                                                        #         self.remain_money = int_remain_money
                                                        #         print("업데이트 잔액 : ", self.remain_money)
                                                        #         card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        #
                                                        #     else:
                                                        #         print("업데이트 실패")
                                                        #         card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        #         card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
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
                        else:
                            print("Serial Card Number Failed!")
                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                    # Issued State Reading Card
                    elif card.reader == str(r[1]):
                        # print("+ Inserted r[1]: ", toHexString(card.atr))
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
                                    # TODO : DB에서 카드 저장번지에 맞춰 바이너리 블록 read / 바이너리 블록값은 16진수 상태
                                    binary_block_number_1, is_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS1)
                                    print("Binary Block 1 : ", binary_block_number_1)
                                    binary_block_number_2, is_backup_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS2)
                                    print("Binary Block 2 : ", binary_block_number_2)

                                    # Read Binary Block Success
                                    if binary_block_number_1 and is_read_block_number == 144:
                                        remain_money = self.remainMoneyCalculate(binary_block_number_1)
                                        backup_remain_money = self.remainMoneyCalculate(binary_block_number_2)

                                        shop_id = self.getShopId(binary_block_number_1)
                                        backup_shop_id = self.getShopId(binary_block_number_2)

                                        master_block_value = binary_block_number_1[11]
                                        master_block_crc = binary_block_number_1[12]

                                        master_backup_block_value = binary_block_number_2[11]
                                        master_backup_block_crc = binary_block_number_2[12]

                                        is_check_sum = self.getCheckSum(serial_number, remain_money, shop_id,
                                                                binary_block_number_1[4], binary_block_number_1[13])

                                        # checksum 맞지 않을 경우 다른 카드저장번지 검증
                                        if not is_check_sum:
                                            remain_money = backup_remain_money
                                            shop_id = backup_shop_id
                                            master_block_value = master_backup_block_value
                                            master_block_crc = master_backup_block_crc

                                            is_check_sum = self.getCheckSum(serial_number, remain_money, shop_id,
                                                                    binary_block_number_2[4], binary_block_number_2[13])

                                            # 백업저장 번지도 맞지않으면 마스터 검증
                                            compare_master_crc = self.getMasterCrcValue(serial_number)
                                            if compare_master_crc == master_block_crc and master_block_value == 11:
                                                print("This is a master card")
                                                is_check_sum = True

                                        # Nothing Verification Window Test
                                        if 'Windows' in platform.system():
                                            is_check_sum = True

                                        # Checksum Verification Success
                                        if is_check_sum:
                                            remain_money = remain_money.upper()
                                            int_remain_money = int(remain_money, 16)

                                            shop_id = shop_id.upper()
                                            int_shop_id = int(shop_id, 16)

                                            # TODO : DB에서 매장ID 조회 하여 일치 여부 검사하기
                                            if shop_id:
                                                # self.CHARGE_STATE = True  # 충전 테스트중
                                                if self.CHARGE_STATE:
                                                    print("발급충전")
                                                    self.LOOKUP_STATE = False
                                                    self.ISSUED_STATE = False

                                                    if self.input_money > 0:
                                                        self.total_money = self.input_money + self.bonus + int_remain_money
                                                        update_binary_block = self.setMoneyUpdateBinaryBlock(serial_number, self.total_money, int_shop_id)

                                                        # TODO : DB에서 구/신버전 비교값 가져와서 업데이트 블록 설정하기
                                                        update_block_1, set_update_block1, sw2 = card.connection.transmit(
                                                            self.UPDATE_BINARY_SELECT_ADDRESS1 + update_binary_block)
                                                        update_block_2, set_update_block2, sw2 = card.connection.transmit(
                                                            self.UPDATE_BINARY_SELECT_ADDRESS2 + update_binary_block)

                                                        if set_update_block2 == 144:
                                                            time.sleep(0.25)
                                                            print("2번지 업데이트 블록 : ", update_binary_block)
                                                            self.input_money = 0
                                                            card.connection.control(SCARD_CTL_CODE(3500),self.BUZZER_BYTE)
                                                        else:
                                                            # TODO : print문 Error log처리
                                                            print("2번지 충전 실패함")

                                                            if set_update_block1 == 144:
                                                                time.sleep(0.25)
                                                                print("1번지 업데이트 블록 : ", update_binary_block)
                                                                self.input_money = 0
                                                                card.connection.control(SCARD_CTL_CODE(3500),self.BUZZER_BYTE)

                                                            else:
                                                                print("1번지 충전 실패함")
                                                                card.connection.control(SCARD_CTL_CODE(3500),self.BUZZER_BYTE)
                                                                card.connection.control(SCARD_CTL_CODE(3500),self.BUZZER_BYTE)

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
                        else:
                            print("Serial Card Number Failed!")
                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                except Exception as error:
                    print("RF Card Reader Exception : " + str(error))
                finally:
                    card.connection.disconnect()

        for card in removedcards:
            # print("- Removed: ", toHexString(card.atr))
            if card in self.cards:
                self.cards.remove(card)


# TODO : RFreader Test Code
if __name__ == '__main__':
    pass
    # cardmonitor = CardMonitor()
    # RFreader_class = Reader()
    # cardmonitor.addObserver(RFreader_class)
    # RFreader_class.LOOKUP_STATE = True
    # time.sleep(100)
