import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor()
print("Connected Successfully")

# CREATE TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS bank (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    balance DECIMAL(10,2) NOT NULL
)
""")

conn.commit()


# ==========================================
# MAIN MENU
# ==========================================

while True:

    print("\n===== BANK MENU =====")
    print("1. Create Account")
    print("2. View Accounts")
    print("3. Deposit Money")
    print("4. Withdraw Money")
    print("5. Transaction Details")
    print("6. Delete Account")
    print("7. Exit")

    choice = input("Enter your choice: ")


    # ======================================
    # CREATE ACCOUNT
    # ======================================

    if choice == "1":

        name = input("Enter name: ")

        if name.strip() == "":
            print("Name cannot be empty")
            continue

        # Account ID
        cursor.execute(
            "SELECT MAX(account_id) FROM bank"
        )

        result = cursor.fetchone()

        if result[0] is None:
            account_id = 1
        else:
            account_id = result[0] + 1

        # Initial balance
        opening_balance = 1000.00

        sql = """
        INSERT INTO bank
        (account_id, name, transaction_type, amount, balance)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            account_id,
            name,
            "Opening",
            opening_balance,
            opening_balance
        )

        cursor.execute(sql, values)
        conn.commit()

        print("\nAccount Created Successfully")
        print("Account ID:", account_id)
        print("Name:", name)
        print("Initial Balance:", opening_balance)


    # ======================================
    # VIEW ACCOUNTS
    # ======================================

    elif choice == "2":

        cursor.execute("""
            SELECT
                account_id,
                name,
                balance
            FROM bank
            WHERE id IN (
                SELECT MAX(id)
                FROM bank
                GROUP BY account_id
            )
            ORDER BY account_id
        """)

        rows = cursor.fetchall()

        if not rows:

            print("\nNo Accounts Found")

        else:

            print("\n===== ACCOUNTS =====")
            print("ID\tNAME\tBALANCE")

            for row in rows:

                print(
                    row[0],
                    "\t",
                    row[1],
                    "\t",
                    row[2]
                )


    # ======================================
    # DEPOSIT MONEY
    # ======================================

    elif choice == "3":

        try:

            account_id = int(
                input("Enter Account ID: ")
            )

            amount = float(
                input("Enter Deposit Amount: ")
            )

        except ValueError:

            print("Please enter valid numbers")
            continue


        if amount <= 0:

            print("Amount must be greater than 0")
            continue


        # Get current account
        cursor.execute("""
            SELECT name, balance
            FROM bank
            WHERE account_id = %s
            ORDER BY id DESC
            LIMIT 1
        """, (account_id,))

        result = cursor.fetchone()


        if result is None:

            print("Account not found")

        else:

            name = result[0]
            current_balance = float(result[1])

            new_balance = (
                current_balance + amount
            )


            # Insert transaction
            cursor.execute("""
                INSERT INTO bank
                (account_id, name, transaction_type,
                 amount, balance)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                account_id,
                name,
                "Deposit",
                amount,
                new_balance
            ))

            conn.commit()


            print("\nAmount Deposited Successfully")
            print("Account ID:", account_id)
            print("Deposited:", amount)
            print("New Balance:", new_balance)


    # ======================================
    # WITHDRAW MONEY
    # ======================================

    elif choice == "4":

        try:

            account_id = int(
                input("Enter Account ID: ")
            )

            amount = float(
                input("Enter Withdraw Amount: ")
            )

        except ValueError:

            print("Please enter valid numbers")
            continue


        if amount <= 0:

            print("Amount must be greater than 0")
            continue


        # Get current balance
        cursor.execute("""
            SELECT name, balance
            FROM bank
            WHERE account_id = %s
            ORDER BY id DESC
            LIMIT 1
        """, (account_id,))

        result = cursor.fetchone()


        if result is None:

            print("Account not found")

        else:

            name = result[0]
            current_balance = float(result[1])


            if amount > current_balance:

                print("Insufficient Balance")

            else:

                new_balance = (
                    current_balance - amount
                )


                # Insert transaction
                cursor.execute("""
                    INSERT INTO bank
                    (account_id, name, transaction_type,
                     amount, balance)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    account_id,
                    name,
                    "Withdraw",
                    amount,
                    new_balance
                ))

                conn.commit()


                print("\nAmount Withdrawn Successfully")
                print("Account ID:", account_id)
                print("Withdrawn:", amount)
                print("New Balance:", new_balance)


    # ======================================
    # TRANSACTION DETAILS
    # ======================================

    elif choice == "5":

        try:

            account_id = int(
                input("Enter Account ID: ")
            )

        except ValueError:

            print("Please enter valid Account ID")
            continue


        cursor.execute("""
            SELECT
                id,
                account_id,
                name,
                transaction_type,
                amount,
                balance
            FROM bank
            WHERE account_id = %s
            ORDER BY id
        """, (account_id,))

        rows = cursor.fetchall()


        if not rows:

            print("No transactions found")

        else:

            print("\n===== TRANSACTION DETAILS =====")

            print(
                "ID\tACCOUNT\tNAME\tTYPE\tAMOUNT\tBALANCE"
            )

            for row in rows:

                print(
                    row[0],
                    "\t",
                    row[1],
                    "\t",
                    row[2],
                    "\t",
                    row[3],
                    "\t",
                    row[4],
                    "\t",
                    row[5]
                )


    # ======================================
    # DELETE ACCOUNT
    # ======================================

    elif choice == "6":

        try:

            account_id = int(
                input("Enter Account ID: ")
            )

        except ValueError:

            print("Please enter valid Account ID")
            continue


        cursor.execute(
            "DELETE FROM bank WHERE account_id = %s",
            (account_id,)
        )

        if cursor.rowcount > 0:

            conn.commit()

            print("Account Deleted Successfully")

        else:

            print("Account not found")


    # ======================================
    # EXIT
    # ======================================

    elif choice == "7":

        print("Thank You!")
        break


    # ======================================
    # INVALID CHOICE
    # ======================================

    else:

        print("Invalid Choice")


# ==========================================
# CLOSE CONNECTION
# ==========================================

cursor.close()
conn.close()

print("Connection Closed")
