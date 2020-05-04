from smartcard.CardMonitoring import CardObserver, CardMonitor
from smartcard.System import readers
from smartcard.scard import SCARD_CTL_CODE
from smartcard.util import toHexString
from inc import database
from collections import OrderedDict
import time
import requests
import platform


class Reader(CardObserver):
    db_class = None

    # State Flag
    INIT_STATE = False
    CHARGE_STATE = False
    ISSUED_STATE = False
    LOOKUP_STATE = False

    # Success / Failed Flag  1/0
    flag_charge = False
    flag_issued = False
    flag_lookup = False
    flag_init = False

    # TODO : 사용할 금액 변수
    total_money = 0     # 토탈 ( 충전할 금액 + 현재 카드 잔액)
    current_money = 0   # 투입금액
    current_bonus = 0   # 보너스
    charge_money = 0    # 충전할 금액 ( 투입금액 + 보너스)
    before_money = 0    # 충전 전 금액 (현재 카드잔액)
    card_price = 0      # 카드 가격
    min_card_price = 0  # 카드 발급 최소 금액

    # TODO : Total Table 변수
    total = 0           # 토탈 금액
    charge_total = 0    # 총 충전 금액
    bonus_total = 0     # 총 보너스 금액
    card_count = 0      # 카드 갯수 (발급 할때마다 한개씩 +하기위해 지정)

    member_class = ""
    mb_level = ""

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

    # 반전비트 계산
    def getInvertBit(self, arg):
        result = arg ^ 0xFF
        res = hex(result).upper()
        return res

    # (신)길광 체크섬 구해서 인자와 비교하는 방식 : 금액 crc, 매장 ID crc
    def getCheckSum(self, serial, money, shop, money_crc, shop_crc):
        if self.db_class.getConfigArg("encrypt") == "1":
            money = int(money, 16) / 1000
            compare_money_index = int(int(serial, 16) + money) % 100

            shop_total = int(serial, 16) + int(shop, 16)
            compare_shop_index = int(shop_total % 100)

            compare_money_crc = int(self.db_class.crc_table[compare_money_index], 16)
            compare_shop_crc = int(self.db_class.crc_table[compare_shop_index], 16)
            # print("금액 crc 계산값     : ", compare_money_crc)
            # print("바이너리블록 금액crc : ", money_crc)
            # print("매장ID crc계산값    : ", compare_shop_crc)
            # print("바이너리블록 매장crc : ", shop_crc)

            if money_crc == compare_money_crc and shop_crc == compare_shop_crc:
                return True
            else:
                return False
        else:
            return True

    def getMasterCrcValue(self, serial):
        master_index = (int(serial, 16) + 11) % 100
        response = int(self.db_class.crc_table[master_index], 16)
        # return int(response, 16)
        return response

    # Dec -> Hex
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

        # index = 0
        # for r in remain_money:
        #     if r != "0": break
        #     index += 1
        # print("index : ", index)

        # remain_money = remain_money[index:]
        # remain_money = int(remain_money, 16)
        # print(remain_money)
        # print(type(remain_money))
        return remain_money

    # 보너스 가져오기
    def getBonus(self, input_mny):
        temp_money = input_mny
        bonus = 0

        if temp_money >= 100000:
            while temp_money >= 100000:
                bonus += int(self.db_class.getConfigArg(100000))
                temp_money -= 100000

        if temp_money >= 90000:
            while temp_money >= 90000:
                bonus += int(self.db_class.getConfigArg(90000))
                temp_money -= 90000

        if temp_money >= 80000:
            while temp_money >= 80000:
                bonus += int(self.db_class.getConfigArg(80000))
                temp_money -= 80000

        if temp_money >= 70000:
            while temp_money >= 70000:
                bonus += int(self.db_class.getConfigArg(70000))
                temp_money -= 70000

        if temp_money >= 60000:
            while temp_money >= 60000:
                bonus += int(self.db_class.getConfigArg(60000))
                temp_money -= 60000

        if temp_money >= 50000:
            while temp_money >= 50000:
                bonus += int(self.db_class.getConfigArg(50000))
                temp_money -= 50000

        if temp_money >= 40000:
            while temp_money >= 40000:
                bonus += int(self.db_class.getConfigArg(40000))
                temp_money -= 40000

        if temp_money >= 30000:
            while temp_money >= 30000:
                bonus += int(self.db_class.getConfigArg(30000))
                temp_money -= 30000

        if temp_money >= 20000:
            while temp_money >= 20000:
                bonus += int(self.db_class.getConfigArg(20000))
                temp_money -= 20000

        if temp_money >= 10000:
            while temp_money >= 10000:
                bonus += int(self.db_class.getConfigArg(10000))
                temp_money -= 10000

        if temp_money > 0:
            res = self.db_class.getConfigArg(temp_money)
            bonus += int(res)

        return bonus

    # TODO : 초기에 DB에서 키값 암호화 여부 값을 가져와서 구/신버전 판단 , DB에서 공급업체번호 가져와서 update
    # Return Card Update Binary Block
    def setMoneyUpdateBinaryBlock(self, serial, money, shop):
        self.db_class.loadConfigTable()
        # 신버전
        if self.db_class.getConfigArg("encrypt") == "1":  # 암호화 여부 ON
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
            arg5 = int(self.db_class.crc_table[crc_money], 16)
            arg13 = int(self.db_class.crc_table[crc_shop], 16)
            manager_no = int(self.db_class.getConfigArg("manager_no"))
            arg14 = int(hex_shop[0:2], 16)
            arg15 = int(hex_shop[2:4], 16)

            update_binary_block = [arg1, arg2, arg3, arg4, arg5, 0x00, 0x00, 0x00, 0xAA, 0x55, manager_no, 0x00, 0x00, arg13, arg14, arg15]

        # 구버전
        else:
            hex_money = hex(money)[2:].rjust(8, "0")
            hex_shop = hex(shop)[2:].rjust(4, "0")

            arg1 = int(hex_money[4:6], 16)
            arg2 = int(hex_money[6:8], 16)
            arg3 = int(hex_money[2:4], 16)
            arg4 = int(hex_money[0:2], 16)
            arg1_invert = self.getInvertBit(arg1)
            arg2_invert = self.getInvertBit(arg2)
            arg3_invert = self.getInvertBit(arg3)
            arg4_invert = self.getInvertBit(arg4)

            arg5 = int(arg1_invert, 16)
            arg6 = int(arg2_invert, 16)
            arg7 = int(arg3_invert, 16)
            arg8 = int(arg4_invert, 16)
            arg14 = int(hex_shop[0:2], 16)
            arg15 = int(hex_shop[2:4], 16)
            arg14_invert = self.getInvertBit(arg14)
            arg15_invert = self.getInvertBit(arg15)

            arg12 = int(arg14_invert, 16)
            arg13 = int(arg15_invert, 16)

            update_binary_block = [arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 0xAA, 0x55, 0x00, 0x00, arg12, arg13, arg14, arg15]

        return update_binary_block

    # TODO : 초기에 DB에서 키값 암호화 여부 값을 가져와서 구/신버전 판단 , DB에서 공급업체번호 가져와서 update
    # Return Card Initialize Binary Block
    def setInitUpdateBinaryBlock(self, serial, int_money, int_shop, master_byte1, master_byte2):
        self.db_class.loadConfigTable()
        shop_id = self.db_class.getConfigArg("id")
        compare_master_byte = self.getMasterCrcValue(serial)
        int_money = 0

        # 신버전
        if self.db_class.getConfigArg("encrypt") == "1":
            int_serial = int(serial, 16)
            crc_index_money = (int_serial + int_money) % 100
            crc_index_shop = (int_serial + int_shop) % 100

            str_hex_money = hex(int_money)[2:].rjust(8, "0")
            str_hex_shop = hex(int_shop)[2:].rjust(4, "0")

            arg1 = int(str_hex_money[4:6], 16)
            arg2 = int(str_hex_money[6:8], 16)
            arg3 = int(str_hex_money[0:2], 16)
            arg4 = int(str_hex_money[2:4], 16)
            arg5 = int(self.db_class.crc_table[crc_index_money], 16)
            manager_no = int(self.db_class.getConfigArg("manager_no"))
            arg13 = int(self.db_class.crc_table[crc_index_shop], 16)
            arg14 = int(str_hex_shop[0:2], 16)
            arg15 = int(str_hex_shop[2:4], 16)

            if master_byte1 == 11 and master_byte2 == compare_master_byte:
                arg1 = 0
                arg2 = 0
                arg3 = 0
                arg4 = 0
                arg5 = 0

            init_binary_block = [arg1, arg2, arg3, arg4, arg5, 0x00, 0x00, 0x00, 0x00, 0x00, manager_no, 0x00, 0x00, arg13, arg14, arg15]

        # 구버전
        else:
            str_hex_money = hex(int_money)[2:].rjust(8, "0")
            str_hex_shop = hex(int_shop)[2:].rjust(4, "0")
            arg1 = int(str_hex_money[4:6], 16)
            arg2 = int(str_hex_money[6:8], 16)
            arg3 = int(str_hex_money[0:2], 16)
            arg4 = int(str_hex_money[2:4], 16)
            arg1_invert = self.getInvertBit(arg1)
            arg2_invert = self.getInvertBit(arg2)
            arg3_invert = self.getInvertBit(arg3)
            arg4_invert = self.getInvertBit(arg4)

            arg5 = int(arg1_invert, 16)
            arg6 = int(arg2_invert, 16)
            arg7 = int(arg3_invert, 16)
            arg8 = int(arg4_invert, 16)
            arg9 = 0xAA
            arg10 = 0x55
            arg14 = int(str_hex_shop[0:2], 16)
            arg15 = int(str_hex_shop[2:4], 16)
            arg12 = self.getInvertBit(arg14)
            arg13 = self.getInvertBit(arg15)

            init_binary_block = [arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 0xAA, 0x55, 0x00, 0x00, arg12, arg13, arg14, arg15]

        return init_binary_block

    def __init__(self):
        self.cards = []
        self.db_class = database.Database()

    def update(self, observable, actions):
        # TODO : 수기 처리
        # gookil_loay_key = [0x00, 0x00, 0x00, 0x00, 0x21, 0xB0]
        # kil_load_key = [0x05, 0xD3, 0x55, 0xB9, 0x4F, 0xEE]
        # dae_load_key = [0x03, 0x50, 0x87, 0x0E, 0x93, 0x0E]

        self.db_class.loadConfigTable()
        key = self.db_class.getConfigArg("manager_key")
        arg1 = int(key[0:2], 16)
        arg2 = int(key[2:4], 16)
        arg3 = int(key[4:6], 16)
        arg4 = int(key[6:8], 16)
        arg5 = int(key[8:10], 16)
        arg6 = int(key[10:12], 16)

        LOAD_KEY_DF = [arg1, arg2, arg3, arg4, arg5, arg6]  # 로드 키 데이터

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
                            load_key, is_load_key, sw2 = card.connection.transmit(self.LOAD_KEY_SELECT + LOAD_KEY_DF)

                            # Load Key Success
                            if is_load_key == 144:
                                auth, is_authentication, sw2 = card.connection.transmit(self.AUTH_SELECT + self.AUTH_DF)

                                # Authentication Success
                                if is_authentication == 144:
                                    # TODO : 07.08 2번지 읽기로 변경됨 -> 07.16 데이터베이스에서 설정할 수 있도록 변경됨 -> 08.07 2번지가 비어있을 때 1번지의 값을 쓰도록 변경
                                    # TODO : DB에서 카드 저장번지에 맞춰 바이너리 블록 read
                                    binary_block_number_1 = []
                                    binary_block_number_2 = []

                                    # 구형
                                    if self.db_class.getConfigArg("rf_reader_type") == "1":
                                        binary_block_number_1, is_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS1)
                                        print("Binary Block 1 : ", binary_block_number_1)  # 1번지 읽기
                                        binary_block_number_2, is_backup_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS2)
                                        print("Binary Block 2 : ", binary_block_number_2)  # 2번지 읽기
                                    else:
                                        binary_block_number_1, is_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS2)
                                        print("Binary Block 2 : ", binary_block_number_1)  # 2번지 읽기
                                        binary_block_number_2, is_backup_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS1)
                                        print("Binary Block 1 : ", binary_block_number_2)  # 1번지 일기

                                    # Read Binary Block Success
                                    # TODO : 바이너리 블록 목록값은 10진수
                                    if binary_block_number_1 and is_read_block_number == 144:
                                        remain_money = self.remainMoneyCalculate(binary_block_number_1)
                                        backup_remain_money = self.remainMoneyCalculate(binary_block_number_2)
                                        print("카드 잔액 >> ", remain_money)

                                        shop_id = self.getShopId(binary_block_number_1)
                                        backup_shop_id = self.getShopId(binary_block_number_2)

                                        master_block_value = binary_block_number_1[11]
                                        master_block_crc = binary_block_number_1[12]

                                        master_backup_block_value = binary_block_number_2[11]
                                        master_backup_block_crc = binary_block_number_2[12]

                                        serial_number = self.changeListSerialNumber(serial_number)
                                        data = {'card_num': serial_number}

                                        # 회원 보너스 사용중이면
                                        if self.db_class.getConfigArg("data_collect_state") == "1":
                                            try:
                                                member_info = requests.post("http://192.168.0.200:5000/get_vip_bonus", json=[], data=data)
                                                # member_info = requests.post("http://glstest.iptime.org:50000/get_vip_bonus", json=[], data=data)
                                                member_info = member_info.json()
                                                if member_info:
                                                    for x in member_info:
                                                        member_level = x['level_name']
                                                        # 보너스 재설정
                                                        self.mb_level = str(x['level'])
                                                        self.db_class.memberBonusConfig(str(x['level']))
                                                    self.member_class = member_level
                                                else:
                                                    self.db_class.initBonus()
                                                    self.db_class.loadConfigTable()
                                                    self.member_class = "비회원"
                                            except Exception as e:
                                                self.db_class.insertErrorLog(str(e), "회원보너스 에러")
                                                print(e)

                                        # CRC 검사
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
                                            remain_money = remain_money.upper()         # 금액 : 16진수 대문자
                                            int_remain_money = int(remain_money, 16)    # 금액 : 10진수

                                            shop_id = shop_id.upper()                   # 매장ID : 16진수 대문자
                                            int_shop_id = int(shop_id, 16)              # 매장ID : 10진수

                                            db_shop_id = self.db_class.getConfigArg("id")  # 매장ID : DB get 10진수
                                            hex_db_shop_id = hex(db_shop_id)[2:].rjust(4, "0").upper()  # 매장ID : DB get hex

                                            # Card Initialize
                                            if self.INIT_STATE:
                                                print("초기화")
                                                self.CHARGE_STATE = False
                                                self.ISSUED_STATE = False
                                                self.LOOKUP_STATE = False
                                                set_init = ""

                                                init_binary_block = self.setInitUpdateBinaryBlock(serial_number, int_remain_money, int_shop_id, master_block_value, master_block_crc)

                                                if self.db_class.getConfigArg("rf_reader_type") == "1":
                                                    init, set_init, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS1 + init_binary_block)
                                                elif self.db_class.getConfigArg("rf_reader_type") == "2":
                                                    init, set_init, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + init_binary_block)

                                                if set_init == 144:
                                                    time.sleep(0.25)
                                                    if self.db_class.getConfigArg("rf_reader_type") == "1":
                                                        init, set_init, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + init_binary_block)
                                                    elif self.db_class.getConfigArg("rf_reader_type") == "2":
                                                        init, set_init, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS1 + init_binary_block)

                                                    if set_init == 144:
                                                        time.sleep(0.25)
                                                        self.flag_init = True  # 초기화 성공
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    else:
                                                        self.flag_init = False  # 초기화 실패
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                else:
                                                    self.flag_init = False  # 초기화 실패
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                            else:
                                                # 매장 ID 일치하면
                                                if int_shop_id == db_shop_id:
                                                    # self.CHARGE_STATE = True  # 충전 테스트중
                                                    if self.CHARGE_STATE:
                                                        print("충전")
                                                        self.LOOKUP_STATE = False
                                                        self.ISSUED_STATE = False

                                                        if self.current_money > 0:
                                                            self.before_money = int_remain_money  # 충전 전 금액 저장
                                                            self.total_money = self.current_money + self.current_bonus + int_remain_money  # 최종 충전금액 = 투입금액 + 보너스 + 현재잔액
                                                            self.charge_money = self.current_money + self.current_bonus   # 충전 금액 = 투입금액 + 보너스

                                                            # total 테이블에 들어갈 변수
                                                            self.charge_total = self.current_money
                                                            self.bonus_total = self.current_bonus
                                                            self.total = self.charge_total + self.bonus_total

                                                            # 회원 보너스 사용중이면
                                                            if self.db_class.getConfigArg("data_collect_state") == "1":
                                                                try:
                                                                    # 투입금액에 따른 회원 보너스 구하기
                                                                    mb_bonus = self.db_class.memberBonusConfig(self.current_money)

                                                                    if mb_bonus:
                                                                        self.total_money = self.total_money + int(mb_bonus) - self.current_bonus
                                                                        self.current_bonus = int(mb_bonus)
                                                                        charge_money = self.current_money + int(mb_bonus)
                                                                except Exception as e:
                                                                    self.db_class.insertErrorLog(str(e), "회원보너스 에러")
                                                                    print(e)

                                                            # TODO : 19 07.08 2번지 읽기로 변경됨 -> 19 07.16 데이터베이스 설정값으로 변경됨
                                                            # 블록 업데이트
                                                            update_binary_block = self.setMoneyUpdateBinaryBlock(serial_number, self.total_money, int_shop_id)
                                                            set_update_block = ""

                                                            if self.db_class.getConfigArg("rf_reader_type") == "1":
                                                                update_block_1, set_update_block, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS1 + update_binary_block)
                                                            elif self.db_class.getConfigArg("rf_reader_type") == "2":
                                                                update_block_2, set_update_block, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + update_binary_block)

                                                            if set_update_block == 144:
                                                                time.sleep(0.25)
                                                                if self.db_class.getConfigArg("rf_reader_type") == "1":
                                                                    update_block_1, set_update_block, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + update_binary_block)
                                                                elif self.db_class.getConfigArg("rf_reader_type") == "2":
                                                                    update_block_2, set_update_block, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS1 + update_binary_block)

                                                                # 카드 테이블에 추가할 금액 딕셔너리
                                                                dic_card = OrderedDict()
                                                                dic_card['card_num'] = str(serial_number)                             # 카드번호
                                                                dic_card['total_mny'] = str(self.total_money)                         # 충전금액 + 카드잔액 + 보너스
                                                                dic_card['current_mny'] = str(self.current_money)                     # 현재 금액
                                                                dic_card['current_bonus'] = str(self.getBonus(self.current_money))    # 현재 보너스
                                                                dic_card['before_mny'] = str(int_remain_money)                        # 충전 전 금액
                                                                dic_card['charge_money'] = str(self.charge_money)                     # 충전 금액
                                                                dic_card['card_price'] = "0"                                          # 카드 가격
                                                                dic_card['reader_type'] = "1"                                         # 리더기 종류 (의미X)

                                                                # 토탈 테이블에 업데이트 할 금액 딕셔너리
                                                                dic_total = OrderedDict()
                                                                dic_total['total_mny'] = str(self.total)
                                                                dic_total['charge_mny'] = str(self.charge_total)
                                                                dic_total['bonus_mny'] = str(self.bonus_total)
                                                                dic_total['card_count'] = "0"
                                                                dic_total['card_price'] = "0"

                                                                self.db_class.setCardTable(dic_card)          # 카드 테이블 추가
                                                                self.db_class.setUpdateTotalTable(dic_total)  # 토탈 테이블 업데이트

                                                                print("업데이트 블록 : ", update_binary_block)
                                                                print("카드 잔액 : ", self.total_money)
                                                                self.flag_charge = True  # 충전 성공
                                                                # self.card_count = 0  # 카드 카운트 초기화
                                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                            else:
                                                                print("충전 실패함")
                                                                self.flag_charge = False  # 충전 실패
                                                                self.db_class.insertErrorLog(str(update_binary_block), "1번 리더기 충전 실패함")
                                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    elif self.LOOKUP_STATE:
                                                        print("조회")
                                                        # is_check_sum = self.getCheckSum(serial_number, remain_money, shop_id, binary_block_number_1[4], binary_block_number_1[13])
                                                        #
                                                        # if not is_check_sum:
                                                        #     time.sleep(0.25)
                                                        #     set_req_byte = self.setMoneyUpdateBinaryBlock(serial_number, int(remain_money), int_shop_id)
                                                        #     response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + set_req_byte)  # 2번 바이너리 블럭 업데이트
                                                        #
                                                        #     if set1 == 144:
                                                        #         if remain_money:
                                                        #             self.flag_lookup = True  # 조회 여부 ON
                                                        #         else:
                                                        #             self.flag_lookup = False
                                                        #         self.remain_money = int(remain_money, 16)
                                                        #         card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        # else:
                                                        #     card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        #
                                                        #     if remain_money:
                                                        #         self.flag_lookup = True  # 조회 여부 ON
                                                        #     else:
                                                        #         self.flag_lookup = True  # 조회 여부 ON
                                                        #     self.remain_money = int(remain_money, 16)
                                                        self.remain_money = int_remain_money
                                                        print("잔액 : ", self.remain_money)
                                                        print(remain_money)
                                                        self.flag_lookup = True  # 조회 여부 ON
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

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
                            load_key, is_load_key, sw2 = card.connection.transmit(self.LOAD_KEY_SELECT + LOAD_KEY_DF)

                            # Load Key Success
                            if is_load_key == 144:
                                auth, is_authentication, sw2 = card.connection.transmit(self.AUTH_SELECT + self.AUTH_DF)

                                # Authentication Success
                                if is_authentication == 144:
                                    binary_block_number = []
                                    is_read_block_number = ""

                                    # 구형
                                    if self.db_class.getConfigArg("rf_reader_type") == "1":
                                        binary_block_number, is_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS1)
                                        print("Binary Block 1 : ", binary_block_number)  # 1번지
                                    elif self.db_class.getConfigArg("rf_reader_type") == "2":
                                        binary_block_number, is_read_block_number, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_ADDRESS2)
                                        print("Binary Block 2 : ", binary_block_number)  # 2번지

                                    # Read Binary Block Success
                                    if binary_block_number and is_read_block_number == 144:
                                        remain_money = self.remainMoneyCalculate(binary_block_number)
                                        print("카드 잔액 >> " + str(remain_money))

                                        shop_id = self.getShopId(binary_block_number)
                                        serial_number = self.changeListSerialNumber(serial_number)

                                        # Crc 검증
                                        is_check_sum = self.getCheckSum(serial_number, remain_money, shop_id, binary_block_number[4], binary_block_number[13])

                                        # Nothing Verification Window Test
                                        if 'Windows' in platform.system():
                                            is_check_sum = True

                                        # Checksum Verification Success
                                        if is_check_sum:
                                            remain_money = remain_money.upper()
                                            int_remain_money = int(remain_money, 16)

                                            shop_id = shop_id.upper()
                                            int_shop_id = int(shop_id, 16)

                                            db_shop_id = self.db_class.getConfigArg("id")
                                            hex_db_shop_id = hex(db_shop_id)[2:].rjust(4, "0")

                                            # 매장 ID 일치하면
                                            if int_shop_id == db_shop_id:
                                                self.CHARGE_STATE = False
                                                if self.ISSUED_STATE:
                                                    print("발급")

                                                    if self.current_money > 0:
                                                        self.LOOKUP_STATE = False
                                                        print("투입금액 : ", self.current_money)

                                                        self.before_money = int_remain_money  # 충전 전 금액 저장
                                                        self.total_money = self.current_money + self.current_bonus + int_remain_money - self.card_price
                                                        # 최종 충전금액 = 투입금액 + 보너스 + 현재잔액 - 카드 가격

                                                        # total 테이블에 들어갈 변수
                                                        self.charge_total = self.current_money
                                                        self.bonus_total = self.current_bonus
                                                        self.total = self.charge_total + self.bonus_total

                                                        update_binary_block = self.setMoneyUpdateBinaryBlock(serial_number, self.total_money, int_shop_id)
                                                        set_update_block = ""

                                                        if self.db_class.getConfigArg("rf_reader_type") == "1":
                                                            update_block_1, set_update_block, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS1 + update_binary_block)
                                                            self.CHARGE_STATE = False
                                                            self.ISSUED_STATE = False
                                                        elif self.db_class.getConfigArg("rf_reader_type") == "2":
                                                            update_block_2, set_update_block, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + update_binary_block)

                                                        if set_update_block == 144:
                                                            time.sleep(0.25)
                                                            if self.db_class.getConfigArg("rf_reader_type") == "1":
                                                                update_block_1, set_update_block, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS2 + update_binary_block)
                                                            elif self.db_class.getConfigArg("rf_reader_type") == "2":
                                                                update_block_2, set_update_block, sw2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_ADDRESS1 + update_binary_block)

                                                            dic_card = OrderedDict()
                                                            dic_card['card_num'] = str(serial_number)
                                                            dic_card['total_mny'] = str(self.total_money)
                                                            dic_card['current_mny'] = str(self.current_money)
                                                            dic_card['current_bonus'] = str(self.current_bonus)
                                                            dic_card['before_mny'] = str(self.before_money)
                                                            dic_card['charge_money'] = str(self.charge_money)
                                                            dic_card['card_price'] = "0"
                                                            dic_card['reader_type'] = "1"

                                                            # dic_total = OrderedDict()
                                                            # dic_total['total_mny'] = str(self.total_money)
                                                            # dic_total['charge_mny'] = str(self.charge_money)
                                                            # dic_total['bonus_mny'] = str(self.current_bonus)
                                                            # dic_total['card_count'] = str(self.card_count)
                                                            # dic_total['card_price'] = str(self.card_price)

                                                            self.db_class.setCardTable(dic_card)
                                                            # self.db_class.setUpdateTotalTable(dic_total)

                                                            print("업데이트 블록 : ", update_binary_block)
                                                            self.flag_charge = True  # 충전 성공
                                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                                        else:
                                                            print("충전 실패함")
                                                            self.flag_charge = False  # 충전 실패
                                                            self.db_class.insertErrorLog(str(update_binary_block), "2번 리더기 충전 실패함")
                                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    else:
                                                        self.CHARGE_STATE = False
                                                        self.ISSUED_STATE = False
                                                        self.LOOKUP_STATE = True
                                                        self.INIT_STATE = False
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
                    self.db_class.insertErrorLog(str(error), "RF 리더기 스레드 에러")
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
