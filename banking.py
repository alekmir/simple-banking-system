from random import randint
import sqlite3


# Create connection to DB. If no existing DB - create DB and connect
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS card (
        id INTEGER,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
        );
        ''')


class Card:
    def number_generator(self):
        # This function is for card number generation due to Luhn algorithm.
        # The first part of card number is static due to task description
        bin = "400000"
        # The second part must be generated
        ai = str()
        for _ in range(9):
            ai += str(randint(0, 9))
        bin_ai = bin + ai
        # The third part is the control key number. It is generated due to Luhn algorithm
        luhn_num = str()
        for i in range(len(bin_ai)):
            if i == 0 or i % 2 == 0:
                doubled = int(bin_ai[i]) * 2
                if doubled > 9:
                    doubled -= 9
                luhn_num += str(doubled)
            else:
                luhn_num += bin_ai[i]
        sum_all_number = int()
        for i in luhn_num:
            sum_all_number += int(i)
        if sum_all_number % 10 == 0:
            number = bin_ai + "0"
        else:
            number = bin_ai + str(10 - sum_all_number % 10)
        return number

    def pin_generator(self):
        pin = str()
        for _ in range(4):
            pin += str(randint(0, 9))
        return pin

    def __init__(self):
        global current_max_id

        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute('''
            SELECT
                *
            FROM
                card
            ;
        ''')
        cards_ids = cur.fetchall()
        current_max_id = 0
        for i in range(len(cards_ids)):
            if cards_ids[i][0] > current_max_id:
                current_max_id = cards_ids[i][0]
        id = current_max_id + 1
        number = self.number_generator()
        pin = self.pin_generator()
        balance = 0
        cur.execute(f'''
            INSERT INTO card VALUES (
                {id},
                {number},
                {pin},
                {balance}
                );
                ''')
        conn.commit()
        conn.close()
        print(f"\nYour card has been created\n"
              f"Your card number:\n{number}\n"
              f"Your card PIN:\n{pin}\n")


def main_menu():
    choice = input("1. Create an account\n"
                   "2. Log into account\n"
                   "0. Exit\n")
    if choice == "1":
        Card()
        main_menu()
    elif choice == "2":
        login()
    else:
        print("\nBye!")


def login():
    user_number = input("\nEnter your card number:\n")
    user_pin = input("Enter your card PIN:\n")
    if is_number_exist(user_number) and is_pin_correct(user_number, user_pin):
        print("\nYou have successfully logged in!")
        authorised(user_number)
    else:
        print("Wrong card number or PIN!\n")
        main_menu()


def is_number_exist(number):
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute(f'''
        SELECT
            number
        FROM
            card
        ;
    ''')
    existing_numbers = cur.fetchall()
    conn.commit()
    conn.close()
    for i in range(len(existing_numbers)):
        if existing_numbers[i][0] == number:
            return True
    return False


def is_pin_correct(number, pin):
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute(f'''
        SELECT
            pin
        FROM
            card
        WHERE
            number = {number}
        ;
    ''')
    pin_in_db = cur.fetchone()
    conn.commit()
    conn.close()
    if str(pin) == pin_in_db[0]:
        return True
    else:
        return False


def authorised(card_number):
    choice = input("\n1. Balance\n"
                   "2. Add income\n"
                   "3. Do transfer\n"
                   "4. Close account\n"
                   "5. Log out\n"
                   "0. Exit\n""")
    if choice == "1":
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(f'''
            SELECT
                balance
            FROM
                card
            WHERE
                number = {card_number}
            ;
        ''')
        balance_in_db = cur.fetchone()
        conn.commit()
        conn.close()
        print(f"\nBalance: {balance_in_db[0]}\n")
        authorised(card_number)
    elif choice == "2":
        income = int(input("Enter income:\n"))
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(f'''
            UPDATE
                card
            SET
                balance = balance + {income}
            WHERE
                number = {card_number}
            ;
        ''')
        conn.commit()
        conn.close()
        print("Income was added!\n")
        authorised(card_number)
    elif choice == "3":
        target_card = input("\nTransfer\nEnter card number:\n")
        if is_card_valid(target_card) is False:
            print("Probably you made a mistake in the card number. Please try again!\n")
            authorised(card_number)
        elif is_number_exist(target_card) is False:
            print("Such a card does not exist.\n")
            authorised(card_number)
        else:
            conn = sqlite3.connect('card.s3db')
            cur = conn.cursor()
            cur.execute(f'''
                        SELECT
                            balance
                        FROM
                            card
                        WHERE
                            number = {card_number}
                        ;
                    ''')
            balance_in_db = cur.fetchone()
            conn.commit()
            conn.close()
            transfer_amount = int(input("Enter how much money you want to transfer:\n"))
            if transfer_amount > balance_in_db[0]:
                print("Not enough money!\n")
                authorised(card_number)
            else:
                conn = sqlite3.connect('card.s3db')
                cur = conn.cursor()
                cur.execute(f'''
                    UPDATE
                        card
                    SET
                        balance = balance + {transfer_amount}
                    WHERE
                        number = {target_card}
                    ;
                ''')
                cur.execute(f'''
                    UPDATE
                        card
                    SET
                        balance = balance - {transfer_amount}
                    WHERE
                        number = {card_number}
                    ;
                ''')
                conn.commit()
                conn.close()
                print("Income was added!")
                print("Success!\n")
                authorised(card_number)
    elif choice == "4":
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(f'''
            DELETE FROM
                card
            WHERE
                number = {card_number}
            ;
        ''')
        conn.commit()
        conn.close()
        print("\nThe account has been closed!\n")
        main_menu()
    elif choice == "5":
        print("\nYou have successfully logged out!\n")
        main_menu()
    else:
        print("\nBye!")


def is_card_valid(card_number):
    # Cut check number
    check_num = card_number[-1]
    # Rest numbers going to processing
    numbers = card_number[:-1]
    # Preparing empty variable for Luhn numbers
    luhn_num = str()
    # Doubling odd numbers. Subtracting 9 from numbers more than 9
    for i in range(len(numbers)):
        if i == 0 or i % 2 == 0:
            doubled = int(numbers[i]) * 2
            if doubled > 9:
                doubled -= 9
            luhn_num += str(doubled)
        else:
            luhn_num += numbers[i]
    # Check is sum of numbers plus check number divisible by 10
    sum_luhn_num = int()
    for i in luhn_num:
        sum_luhn_num += int(i)
    result = (sum_luhn_num + int(check_num)) % 10
    # Return boolean result
    if result == 0:
        return True
    else:
        return False


main_menu()
