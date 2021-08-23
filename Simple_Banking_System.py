import random
import sqlite3
from sqlite3 import Error


WORK = True
LOG_IN = 0
USR_NUMBER = None


class Card:

    def __init__(self):
        self.pin = str(format(random.randint(0000, 9999), '04d'))
        random_number = '400000' + str(format(random.randint(000000000, 999999999), '09d'))
        num_sum = 0
        for index, i in enumerate(reversed(random_number)):
            num = int(i)
            if index % 2 == 0:
                num *= 2
            if num > 9:
                num -= 9
            num_sum += num
        if num_sum % 10 > 0:
            checksum = 10 - num_sum % 10
        else:
            checksum = 0
        self.acc_number = random_number + str(checksum)
        self.id = random.randint(0, 100)


def run_database():
    """ create a database connection to a SQLite database """
    conn = None
    create_table_sql = """ CREATE TABLE IF NOT EXISTS card (
                                        id INTEGER PRIMARY KEY,
                                        number TEXT,
                                        pin TEXT,
                                        balance INTEGER DEFAULT 0 
                                    ); """
    try:
        conn = sqlite3.connect('card.s3db')
        create_table(conn, create_table_sql)
    except Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    global cur

    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
    except Error as e:
        print(e)


def print_menu():

    if LOG_IN == 0:
        print('1. Create an account\n2. Log into account\n0. Exit')
    else:
        print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')


def get_action():
    global WORK, LOG_IN, USR_NUMBER

    print_menu()
    action = input()
    if action == '0':
        WORK = False
        print('Bye!')
        return
    else:
        if LOG_IN == 0:
            if action == '1':
                create_an_account()
            elif action == '2':
                usr_number = log_in()
                if usr_number is None:
                    print('Wrong card number or PIN!\n')
                else:
                    USR_NUMBER = usr_number
        elif LOG_IN == 1 and USR_NUMBER is not None:
            if action == '1':
                print_balance()
            elif action == '2':
                add_income(USR_NUMBER, None)
                print('Income was added!\n')
            elif action == '3':
                do_transfer()
            elif action == '4':
                close_account()
            elif action == '5':
                LOG_IN = 0
                USR_NUMBER = None
                print('You have successfully logged out!\n')


def create_an_account():

    number = Card()
    cur.execute('''INSERT INTO card (id, number, pin) VALUES (?, ?, ?)''',
                (number.id, number.acc_number, number.pin))
    conn.commit()
    print('Your card has been created\n')
    print('Your card number:\n{}\nYour card PIN:\n{}\n'.format(number.acc_number, number.pin))


def log_in():
    global LOG_IN

    usr_number = input('Enter your card number:\n')
    usr_pin = input('Enter your PIN:\n')
    cur.execute("""SELECT number FROM card WHERE number = (?) AND pin = (?) """, (usr_number, usr_pin,))
    result = cur.fetchone()
    if result:
        print('You have successfully logged in!\n')
        LOG_IN = 1
        number = result[0]
    else:
        number = None
    return number


def print_balance():

    cur.execute('''SELECT balance FROM card WHERE number = (?)''', (USR_NUMBER,))
    balance = cur.fetchone()
    print('Balance:', balance[0])


def add_income(usr_number, income):
    if income is None:
        income = int(input('Enter income:\n'))
    cur.execute('''SELECT balance FROM card WHERE number = (?)''', (usr_number,))
    balance = cur.fetchone()[0]
    balance = balance + income
    cur.execute('''UPDATE card SET balance = (?) WHERE number = (?)''',
                (balance, usr_number))
    conn.commit()


def do_transfer():
    transfer_number = input('Transfer\nEnter card number:\n')
    if luhn_check(transfer_number):
        cur.execute("""SELECT number FROM card WHERE number = (?)""", (transfer_number,))
        result = cur.fetchone()
        if result:
            cash_to_transfer = int(input('Enter how much money you want to transfer:\n'))
            cur.execute('''SELECT balance FROM card WHERE number = (?)''', (USR_NUMBER,))
            balance = cur.fetchone()[0]
            if balance < cash_to_transfer:
                print('Not enough money!\n')
            else:
                balance -= cash_to_transfer
                cur.execute('''UPDATE card SET balance = (?) WHERE number = (?)''',
                            (balance, USR_NUMBER,))
                conn.commit()
                add_income(transfer_number, cash_to_transfer)
                print('Success!')
        else:
            print('Such a card does not exist.\n')


def luhn_check(number):

    checksum = int(number[-1])
    num_sum = 0

    for index, i in enumerate(reversed(number[:-1])):
        num = int(i)
        if index % 2 == 0:
            num *= 2
        if num > 9:
            num -= 9
        num_sum += num
    if (num_sum + checksum) % 10 == 0:
        return True
    else:
        print('Probably you made a mistake in the card number. Please try again!\n')
        return False


def close_account():
    global USR_NUMBER, LOG_IN

    cur.execute('''DELETE FROM card WHERE number = (?)''',
                (USR_NUMBER,))
    conn.commit()
    print('The account has been closed!')
    USR_NUMBER = None
    LOG_IN = 0


if __name__ == '__main__':

    conn = run_database()
    while WORK is True:
        get_action()
    if conn:
        conn.close()
