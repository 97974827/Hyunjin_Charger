import pymysql.cursors
import platform
from collections import OrderedDict
import base64


class Database:
    MYSQL_HOST = "192.168.0.224"
    MYSQL_PORT = 3306
    MYSQL_USER = "pi"
    MYSQL_PW = "1234"
    MYSQL_DB = "glstech"
    MYSQL_CHARSET = "utf8mb4"

    db_connect = ""   # DB 연결 변수

    if 'Linux' in platform.system():
        MYSQL_HOST = "localhost"
        MYSQL_PORT = 3306

    program_update_version = "1.3.0"  # 업데이트 버전 : 업데이트 시 수정해야함

    # 회원 보너스
    member_bonus1 = ""
    member_bonus2 = ""
    member_bonus3 = ""
    member_bonus4 = ""
    member_bonus5 = ""
    member_bonus6 = ""
    member_bonus7 = ""
    member_bonus8 = ""
    member_bonus9 = ""
    member_bonus10 = ""

    crc_table = [] * 100

    card_price = ""         # 카드 가격
    min_card_price = ""     # 카드 가격 최소 금액

    shop_name = ""          # 매장 이름
    shop_id = ""            # 매장 ID
    admin_pw = ""
    master_pw = ""
    gil_pw = ""

    version = ""            # 현재 버전
    rf_reader_type = ""     # (구)리더기 타입 -> 카드 저장 번지

    manager_no = ""    # 매장 번호
    manager_name = ""  # 매장 이름
    manager_key = ""   # 공급업체 키

    encrypt = ""       # 암호화 여부  1 / 0
    data_collect_state = ""  # 회원 보너스 사용여부

    # 초기에 불러와야 할것들 - 환경설정, crc 정보저장, 프로그램 버전 업데이트, 공급업체 정보 넣기
    def __init__(self):
        try:
            self.openConnectDB()

            with self.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursors:  # 커서 가져오기
                # 환경설정
                config_query = "SELECT * FROM config AS `con` INNER JOIN manager AS `mg` ON `con`.`manager_no` = `mg`.`no`"
                db_cursors.execute(config_query)     # SQL 실행
                config_rows = db_cursors.fetchall()  # 데이터 가져옴

                # DB get -> 변수 데이터 저장
                for row in config_rows:
                    self.member_bonus1 = row['bonus1']
                    self.member_bonus2 = row['bonus2']
                    self.member_bonus3 = row['bonus3']
                    self.member_bonus4 = row['bonus4']
                    self.member_bonus5 = row['bonus5']
                    self.member_bonus6 = row['bonus6']
                    self.member_bonus7 = row['bonus7']
                    self.member_bonus8 = row['bonus8']
                    self.member_bonus9 = row['bonus9']
                    self.member_bonus10 = row['bonus10']

                    self.version = row['version']
                    self.card_price = row['card_price']
                    self.min_card_price = row['min_card_price']
                    self.shop_id = row['id']
                    self.admin_pw = base64.b64decode(row['admin_password'])
                    self.admin_pw = self.admin_pw.decode('utf-8')
                    self.gil_pw = base64.b64decode(row['gil_password'])
                    self.gil_pw = self.gil_pw.decode('utf-8')
                    self.master_pw = base64.b64decode(row['master_password'])
                    self.master_pw = self.master_pw.decode('utf-8')
                    self.rf_reader_type = row['rf_reader_type']
                    self.manager_name = row['manager_name']
                    self.manager_no = row['manager_no']
                    self.encrypt = row['encrypt']
                    self.data_collect_state = row['data_collect_state']

                # Crc 데이터 가져오기
                crc_query = "SELECT * FROM crc ORDER BY no ASC"
                db_cursors.execute(crc_query)     # SQL 실행
                crc_rows = db_cursors.fetchall()  # 데이터 가져옴

                for row in crc_rows:
                    self.crc_table.append(row['crc'])

                # 버전 업그레이드
                if self.program_update_version != self.version:  # 업데이트 버전 != 현재 버전 (버전 업그레이드)
                    update_version_query = "UPDATE config SET version = %s"
                    db_cursors.execute(update_version_query, self.program_update_version)

                # 공급업체 정보 넣기
                manager_query = "SELECT * FROM manager ORDER BY no ASC"
                db_cursors.execute(manager_query)
                manager_rows = db_cursors.fetchall()

                for row in manager_rows:
                    if row['no'] == 1 and row['manager_name'] != "길광":
                        manager_delete_query = "DELETE FROM manager"
                        db_cursors.execute(manager_delete_query)

                        manager_insert_query = "INSERT INTO manager(no, manager_name, manager_id, encrypt) VALUES(%s, %s, %s, %s)"
                        db_cursors.execute(manager_insert_query, ("1", "길광", "05D355B94FEE", "1"))

                        manager_insert_query = "INSERT INTO manager(no, manager_name, manager_id, encrypt) VALUES(%s, %s, %s, %s)"
                        db_cursors.execute(manager_insert_query, ("2", "주일", "000040BC840C", "0"))

                        manager_insert_query = "INSERT INTO manager(no, manager_name, manager_id, encrypt) VALUES(%s, %s, %s, %s)"
                        db_cursors.execute(manager_insert_query, ("3", "대진", "0350870E930E", "1"))

                        manager_insert_query = "INSERT INTO manager(no, manager_name, manager_id, encrypt) VALUES(%s, %s, %s, %s)"
                        db_cursors.execute(manager_insert_query, ("(구)길광", "0000000021B0", "0"))

                        if self.manager_no == 1:
                            manager_no = "4"
                        elif self.manager_no == 2:
                            manager_no = "1"
                        elif self.manager_no == 3:
                            manager_no = "2"
                        else:
                            manager_no = "3"

                        manager_sql = "UPDATE config SET manager_no = %s"
                        db_cursors.execute(manager_sql, (manager_no))
                        break
            self.db_connect.commit()
        except Exception as error:
            print("DB Init Error : " + str(error))
        finally:
            self.closeConnectDB()

    def openConnectDB(self):
        try:
            self.db_connect = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user=self.MYSQL_USER, password=self.MYSQL_PW, charset=self.MYSQL_CHARSET, db=self.MYSQL_DB)
        except Exception as error:
            print("openConnectDB Error : " + str(error))

    def closeConnectDB(self):
        try:
            self.db_connect.close()
            print("DB Close")
        except Exception as error:
            print("closeConnectDB Error : " + str(error))

    # 환경설정 테이블 인자값 가져오기
    def getConfigArg(self, arg):
        if arg == 10000:
            return self.member_bonus1
        elif arg == 20000:
            return self.member_bonus2
        elif arg == 30000:
            return self.member_bonus3
        elif arg == 40000:
            return self.member_bonus4
        elif arg == 50000:
            return self.member_bonus5
        elif arg == 60000:
            return self.member_bonus6
        elif arg == 70000:
            return self.member_bonus7
        elif arg == 80000:
            return self.member_bonus8
        elif arg == 90000:
            return self.member_bonus9
        elif arg == 100000:
            return self.member_bonus10
        elif arg == "card_price":
            return self.card_price
        elif arg == "min_card_price":
            return self.min_card_price
        elif arg == "shop_name":
            return self.shop_name
        elif arg == "shop_id":
            return self.shop_id
        elif arg == "password":
            return self.admin_pw
        elif arg == "gil_password":
            return self.gil_pw
        elif arg == "master_password":
            return self.master_pw
        elif arg == "rf_reader_type":
            return self.rf_reader_type
        elif arg == "manager_key":
            return self.manager_key
        elif arg == "version":
            return self.version
        elif arg == "manager_name":
            return self.manager_name
        elif arg == "manager_key":
            return self.manager_key
        elif arg == "manager_no":
            return self.manager_no
        elif arg == "encrypt":
            return self.encrypt
        elif arg == "data_collect_state":
            return self.data_collect_state
        else:
            return 0

    # 환경설정 테이블 불러오기
    def loadConfigTable(self):
        try:
            self.openConnectDB()

            with self.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursors:  # 커서 가져오기
                # 환경설정
                config_query = "SELECT * FROM config AS `con` INNER JOIN manager AS `mg` ON `con`.`manager_no` = `mg`.`no`"
                db_cursors.execute(config_query)  # SQL 실행
                config_rows = db_cursors.fetchall()  # 데이터 가져옴

                # DB get -> 변수 데이터 저장
                for row in config_rows:
                    self.member_bonus1 = row['bonus1']
                    self.member_bonus2 = row['bonus2']
                    self.member_bonus3 = row['bonus3']
                    self.member_bonus4 = row['bonus4']
                    self.member_bonus5 = row['bonus5']
                    self.member_bonus6 = row['bonus6']
                    self.member_bonus7 = row['bonus7']
                    self.member_bonus8 = row['bonus8']
                    self.member_bonus9 = row['bonus9']
                    self.member_bonus10 = row['bonus10']

                    self.version = row['version']
                    self.card_price = row['card_price']
                    self.min_card_price = row['min_card_price']
                    self.shop_id = row['id']
                    self.admin_pw = base64.b64decode(row['admin_password'])
                    self.admin_pw = self.admin_pw.decode('utf-8')
                    self.gil_pw = base64.b64decode(row['gil_password'])
                    self.gil_pw = self.gil_pw.decode('utf-8')
                    self.master_pw = base64.b64decode(row['master_password'])
                    self.master_pw = self.master_pw.decode('utf-8')
                    self.rf_reader_type = row['rf_reader_type']
                    self.manager_name = row['manager_name']
                    self.manager_no = row['manager_no']
                    self.encrypt = row['encrypt']
                    self.data_collect_state = row['data_collect_state']
            self.db_connect.commit()
        except Exception as error:
            print("Load Config Table Error : " + str(error))
        finally:
            self.closeConnectDB()

    # 관리자 설정 저장하기
    def setAdminConfig(self):
        pass

    # 마스터 설정 저장하기
    def setMasterConfig(self):
        pass

    # 충전 데이터 저장
    def setCardTable(self, dic):
        try:
            self.openConnectDB()

            with self.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursors:
                card_num = dic['card_num']
                total_money = dic['total_mny']           # 카드 잔액
                current_money = dic['current_mny']       # 투입 금액
                current_bonus = dic['current_bonus']     # 현재 보너스
                charge_money = dic['charge_money']       # 총 충전금액
                before_money = dic['before_mny']         # 충전 전 카드 잔액
                reader_type = dic['reader_type']         # 충전된 리더기 종류
                card_price = dic['card_price']           # 카드 가격
                # ex) 1만원 투입 시
                # 투입금액 : 만원
                # 현재 보너스 : 천원
                # 총 충전금액 : 만천원

                # 카드 발급 여부 확인 :
                # 투입금액 + 현재 보너스 != 총 충전금액 -> 카드 발급
                # 투입금액 + 현재 보너스 == 총 충전금액 -> 카드 충전

                if int(current_money) + int(current_bonus) != int(charge_money):
                    kind = 0  # 충전
                    card_price = self.getConfigArg("card_price")
                else:
                    kind = 1  # 발급
                    card_price = "0"

                card_query = "INSERT INTO card " \
                             "(`card_num`, `total_mny`, `current_mny`, " \
                             "`current_bonus`, `datetime`, `state`, `charge_money`, " \
                             "`card_price`, `kind`, `before_mny`, `reader_type`) " \
                             "VALUE (%s, %s, %s, %s, now(), '0', %s, %s, %s, %s, %s)"
                db_cursors.execute(card_query, (card_num, total_money, current_money, current_bonus, charge_money, card_price, kind, before_money, reader_type))

            self.db_connect.commit()
        except Exception as error:
            print("Set Card Table Error : " + str(error))
        finally:
            self.closeConnectDB()

    # 누적 금액 저장
    def setTotalTable(self):
        pass

    # 공급업체 리스트 불러오기
    def getManagerList(self):
        try:
            self.openConnectDB()
            with self.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursor:
                manager_list_query = "SELECT * FROM manager"
                db_cursor.execute(manager_list_query)

                manager_list = db_cursor.fetchall()
            self.db_connect.commit()
        except Exception as error:
            print("Get List Manager Error : " + str(error))
        finally:
            self.closeConnectDB()
            return manager_list

    # 공급업체 불러오기
    def getManager(self, name):
        dic_manager = OrderedDict()  # 공급업체 저장할 딕셔너리
        try:
            self.openConnectDB()
            with self.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursor:
                manager_query = "SELECT * FROM manager WHERE `manager_name` = %s LIMIT 1"
                db_cursor.execute(manager_query, name)
                rows = db_cursor.fetchall()

                for row in rows:
                    dic_manager['no'] = row['no']
                    dic_manager['manager_id'] = row['manager_id']
            self.db_connect.commit()
        except Exception as error:
            print("Get Manager Error : " + str(error))
        finally:
            self.closeConnectDB()

    # 에러로그 저장
    def insertErrorLog(self, err_log, place):
        try:
            self.openConnectDB()
            with self.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursor:
                insert_errlog = "INSERT INTO error(error, place, input_date) VALUEs (%s, %s, now())"
                db_cursor.execute(insert_errlog, (err_log, place))
            self.db_connect.commit()
        except Exception as error:
            print("Insert Log Error : " + str(error))
        finally:
            self.closeConnectDB()

    # 회원 보너스 적용
    def memberBonusConfig(self, mb_level):
        dic_member_bonus = OrderedDict()  # 반활할 회원 보너스
        try:
            self.openConnectDB()
            with self.db_connect.cursor(pymysql.cursors.DictCursor) as db_cursor:
                member_bonus_query = "SELECT * FROM member_bonus WHERE mb_level = %s LIMIT 1"
                db_cursor.execute(member_bonus_query, (mb_level))
                rows = db_cursor.fetchall()

                for row in rows:
                    self.member_bonus1 = row['bonus1']
                    self.member_bonus2 = row['bonus2']
                    self.member_bonus3 = row['bonus3']
                    self.member_bonus4 = row['bonus4']
                    self.member_bonus5 = row['bonus5']
                    self.member_bonus6 = row['bonus6']
                    self.member_bonus7 = row['bonus7']
                    self.member_bonus8 = row['bonus8']
                    self.member_bonus9 = row['bonus9']
                    self.member_bonus10 = row['bonus10']
            self.db_connect.commit()
        except Exception as error:
            print("Memeber Bonus Config Error : " + str(error))
        finally:
            self.closeConnectDB()
            return dic_member_bonus

    # (int -> str) Return
    def getStrMemberBonus(self, money):
        if money == 10000:
            return self.member_bonus1
        elif money == 20000:
            return self.member_bonus2
        elif money == 30000:
            return self.member_bonus3
        elif money == 40000:
            return self.member_bonus4
        elif money == 50000:
            return self.member_bonus5
        elif money == 60000:
            return self.member_bonus6
        elif money == 70000:
            return self.member_bonus7
        elif money == 80000:
            return self.member_bonus8
        elif money == 90000:
            return self.member_bonus9
        elif money == 100000:
            return self.member_bonus10
        else:
            return 0

    # 보너스 계산 하기
    def calculateMemberBonus(self):
        pass

    # 보너스 초기화
    def initBonus(self):
        self.member_bonus1 = 0
        self.member_bonus2 = 0
        self.member_bonus3 = 0
        self.member_bonus4 = 0
        self.member_bonus5 = 0
        self.member_bonus6 = 0
        self.member_bonus7 = 0
        self.member_bonus8 = 0
        self.member_bonus9 = 0
        self.member_bonus10 = 0


if __name__ == '__main__':
    app = Database()
    # app.loadConfigTable()
    # print("실행설공")