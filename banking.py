# Write your code here
import random, sqlite3
from math import ceil

IIN = 400000  #  Issuer Identification Number
# CHK_SUM = 0  # check sum digit
acc_len = 10  # number of digits in account number
pin_len = 4  # number of digits in pin

main_menu = ['1. Create an account', '2. Log into account',
             '0. Exit']

# initialize database
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
conn.commit()
# all_cards = {}  # detailed information about all cards
# cur.execute('INSERT INTO card (number) VALUES (111112)')
# conn.commit()
# for row in cur.execute('SELECT * FROM card'):
#     print(row)
# cur.execute('DROP TABLE card');
# cur.execute('DELETE FROM card WHERE id = 112')
# for row in cur.execute('SELECT * FROM card'):
#     print(row)

def menu(menu_items):
    _ = [print(item) for item in menu_items]
    n = int(input('> ' ))
    print('')
    return n


def convert(n, l):  # convert int number n into string with l digits
    s = str(n)
    if len(s) < l:
        s = '0' * (l - len(s)) + s
    return s


class Card:
    def __init__(self, new):
        if new:
            self.create()
        else:
            number = input('Enter your card number:\n')
            pin = input('Enter your PIN:\n')
            if self.validate(number, pin):
                self.balance_request()

    def create(self):  # create a new card
        self.number = self.generate_number()
        self.pin = self.generate_pin()
        self.balance = 0
        cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", (self.number, self.pin))
        conn.commit()
        print('Your card has been created\nYour card number:\n{0}\nYour card PIN:\n{1}\n'
              .format(self.number, self.pin))

    def generate_number(self):  # generate a new card number
        number = str(IIN) + convert(random.randint(0, int('9' * acc_len)), acc_len)
        number = number[:-1] + str(self.generate_last_digit(number))
        cur.execute('SELECT number FROM card WHERE number = ?;', (number,))
        while cur.fetchone() is not None:
            number = str(IIN) + convert(random.randint(0, int('9' * acc_len)), acc_len)
            number = number[:-1] + str(self.generate_last_digit(number))
            cur.execute('SELECT number FROM card WHERE number = ?;', (number,))
        return number

    def generate_last_digit(self, number):  # generate the last digit of card number
        s  = self.check_sum(number)
        return ceil(s/10) * 10 - s

    def check_sum(self, number):  # return the check sum using the Luhn algorithm
        num = number[:-1]
        chk_sum = 0
        for i in range(1, len(num) + 1):
            s = int(num[i - 1])
            if i % 2 == 1:
                s *= 2
                d = s if s <= 9 else s - 9
                chk_sum += d
            else:
                chk_sum += s
        return chk_sum

    def generate_pin(self):
        return convert(random.randint(0, int('9' * pin_len)), pin_len)

    def get_pin(self):
        cur.execute('SELECT number, pin, balance FROM card WHERE number = ?;', (self.number,))
        resp = cur.fetchone()
        return resp[1]

    def get_balance(self):
        cur.execute('SELECT number, pin, balance FROM card WHERE number = ?;', (self.number,))
        resp = cur.fetchone()
        return resp[2]

    def validate(self, number, pin):
        cur.execute('SELECT number, pin, balance FROM card WHERE number = ?;', (number,))
        resp = cur.fetchone()
        if resp is not None and pin == resp[1]:
            self.number = number
            self.pin = pin
            self.balance = resp[2]
            print('\nYou have successfully logged in!\n')
            return True
        else:
            print('\nWrong card number or PIN!\n')
            return False

    def balance_request(self):
        global finish
        balance_menu = ['1. Balance', '2. Add income', '3. Do transfer',
                        '4. Close account', '5. Log out', '0. Exit']
        while True:
            n = menu(balance_menu)
            if n == 0:
                finish = True
                return
            if n == 1:
                self.show_balance()
            elif n == 2:
                self.add_income()
            elif n == 3:
                self.transfer()
            elif n == 4:
                self.close_account()
                return
            elif n == 5:
                print('\nYou have successfully logged out!\n')
                return

    def show_balance(self):
        print('Balance:', self.get_balance(), '\n')

    def add_income(self):
        income = int(input('Enter income:\n'))
        self.balance += income
        cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.balance, self.number))
        conn.commit()
        print('Income was added!\n')

    def transfer(self):
        number = input('Transfer\nEnter card number:\n')
        if number == self.number:
            print('You can\'t transfer money to the same account!\n')
            return
        if ((int(number[-1]) + int(self.check_sum(number))) % 10) != 0:
            print('Probably you made a mistake in the card number. Please try again!\n')
            return
        cur.execute('SELECT number, balance FROM card WHERE number = ?;', (number,))
        resp = cur.fetchone()
        if resp is None:
            print('Such a card does not exist.\n')
            return
        amount = int(input('Enter how much money you want to transfer:\n'))
        if amount > self.balance:
            print('Not enough money!\n')
            return
        # update both balances
        self.balance -= amount
        cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.balance, self.number))
        new_balance2 = resp[1] + amount
        cur.execute("UPDATE card SET balance = ? WHERE number = ?", (new_balance2, number))
        conn.commit()
        print('Success!\n')

    def close_account(self):
        cur.execute("DELETE FROM card WHERE number = ?", (self.number,))
        conn.commit()
        print('The account has been closed!\n')


# Main loop
finish = False
while not finish:
    n = menu(main_menu)
    if n == 0:
        break
    if n == 1:
        new_card = Card(True)
    elif n == 2:
        card = Card(False)

conn.close()
print('Bye !')

