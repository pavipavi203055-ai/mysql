import streamlit as st
import mysql.connector


# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="Banking System",
    layout="centered"
)


# ==========================================
# MYSQL CONNECTION
# ==========================================

def get_db():

    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Pavi@2050",
        database="sbi"
    )


# ==========================================
# SESSION STATE
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "account_id" not in st.session_state:
    st.session_state.account_id = None

if "name" not in st.session_state:
    st.session_state.name = ""


# ==========================================
# DATABASE CONNECTION TEST
# ==========================================

try:

    db = get_db()
    cursor = db.cursor()

except mysql.connector.Error as e:

    st.error("Database connection failed")
    st.error(str(e))
    st.stop()


# ==========================================
# CHECK TRANSACTION TIME COLUMN
# ==========================================

try:

    cursor.execute("""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'sbi'
        AND TABLE_NAME = 'bank'
        AND COLUMN_NAME = 'transaction_time'
    """)

    column_exists = cursor.fetchone()[0]

    if column_exists == 0:  #sql execute

        cursor.execute("""
            ALTER TABLE bank
            ADD COLUMN transaction_time
            DATETIME NOT NULL
            DEFAULT CURRENT_TIMESTAMP
        """)

        db.commit()

except mysql.connector.Error as e:

    st.error("Database table error")
    st.error(str(e))

    cursor.close()
    db.close()

    st.stop()


cursor.close()
db.close()


# ==========================================
# LOGIN PAGE
# ==========================================

if not st.session_state.logged_in:

    st.title(" 🏦Banking System")

    st.subheader("Login")

    login_type = st.radio(
        "Login Type",
        [
            "👤 User Login",
            "🛡️ Admin Login"
        ],
        horizontal=True
    )


    # ======================================
    # USER LOGIN
    # ======================================

    if login_type == "👤 User Login":

        st.subheader("User Login")

        account_number = st.number_input(
            "Account Number",
            min_value=1,
            step=1
        )

        password = st.text_input(
            "Login Password",
            type="password"
        )

        if st.button("User Login"):

            if password.strip() == "":

                st.error("Enter login password")

            else:

                try:

                    db = get_db()
                    cursor = db.cursor()

                    cursor.execute("""
                        SELECT name
                        FROM bank
                        WHERE account_id = %s
                        AND login_password = %s
                        ORDER BY id DESC
                        LIMIT 1
                    """, (
                        account_number,
                        password
                    ))

                    result = cursor.fetchone()

                    cursor.close()
                    db.close()

                    if result:

                        st.session_state.logged_in = True
                        st.session_state.role = "user"
                        st.session_state.account_id = account_number
                        st.session_state.name = result[0]

                        st.rerun()

                    else:

                        st.error(
                            "Invalid Account Number or Password"
                        )

                except mysql.connector.Error as e:

                    st.error(
                        "Database Error: " + str(e)
                    )


    # ======================================
    # ADMIN LOGIN
    # ======================================

    else:

        st.subheader("Admin Login")

        username = st.text_input(
            "Admin Username"
        )

        password = st.text_input(
            "Admin Password",
            type="password"
        )

        if st.button("Admin Login"):

            if username == "admin" and password == "admin123":

                st.session_state.logged_in = True
                st.session_state.role = "admin"

                st.rerun()

            else:

                st.error(
                    "Invalid Admin Username or Password"
                )

    st.stop()


# ==========================================
# USER DASHBOARD
# ==========================================

if st.session_state.role == "user":

    st.title("User Dashboard")

    st.sidebar.subheader("User Menu")

    st.sidebar.write(
        "Account Number: "
        + str(st.session_state.account_id)
    )

    st.sidebar.write(
        "Name: "
        + st.session_state.name
    )

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "My Account",
            "Deposit",
            "Withdraw",
            "Balance",
            "Transaction Details"
        ]
    )


    # ======================================
    # MY ACCOUNT
    # ======================================

    if menu == "My Account":

        st.subheader("My Account")

        try:

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                SELECT
                    account_id,
                    name,
                    balance,
                    transaction_time
                FROM bank
                WHERE account_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (
                st.session_state.account_id,
            ))

            result = cursor.fetchone()

            cursor.close()
            db.close()

            if result:

                st.write(
                    "Account Number:",
                    result[0]
                )

                st.write(
                    "Account Holder:",
                    result[1]
                )

                st.success(
                    "Current Balance: "
                    + f"{float(result[2]):.2f}"
                )

                st.write(
                    "Last Transaction:",
                    result[3].strftime(
                        "%d-%m-%Y %I:%M:%S %p"
                    )
                )

            else:

                st.error(
                    "Account not found"
                )

        except mysql.connector.Error as e:

            st.error(str(e))


    # ======================================
    # DEPOSIT
    # ======================================

    elif menu == "Deposit":

        st.subheader("Deposit Money")

        amount = st.number_input(
            "Deposit Amount",
            min_value=0.0,
            step=100.0
        )

        pin = st.text_input(
            "Deposit PIN",
            type="password"
        )

        if st.button("Deposit"):

            if amount <= 0:

                st.error(
                    "Enter valid amount"
                )

            elif len(pin) != 4 or not pin.isdigit():

                st.error(
                    "Deposit PIN must be 4 digits"
                )

            else:

                try:

                    db = get_db()
                    cursor = db.cursor()

                    cursor.execute("""
                        SELECT
                            name,
                            login_password,
                            deposit_pin,
                            balance
                        FROM bank
                        WHERE account_id = %s
                        ORDER BY id DESC
                        LIMIT 1
                    """, (
                        st.session_state.account_id,
                    ))

                    result = cursor.fetchone()

                    if not result:

                        st.error(
                            "Account not found"
                        )

                    else:

                        name = result[0]
                        login_password = result[1]
                        saved_pin = result[2]
                        current_balance = float(result[3])

                        if str(saved_pin) != str(pin):

                            st.error(
                                "Invalid Deposit PIN"
                            )

                        else:

                            new_balance = (
                                current_balance + amount
                            )

                            cursor.execute("""
                                INSERT INTO bank
                                (
                                    account_id,
                                    name,
                                    login_password,
                                    deposit_pin,
                                    transaction_type,
                                    amount,
                                    balance,
                                    transaction_time
                                )
                                VALUES
                                (
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    NOW()
                                )
                            """, (
                                st.session_state.account_id,
                                name,
                                login_password,
                                saved_pin,
                                "Deposit",
                                amount,
                                new_balance
                            ))

                            db.commit()

                            st.success(
                                "Deposit Successful"
                            )

                            st.write(
                                "Account Number:",
                                st.session_state.account_id
                            )

                            st.write(
                                "Deposited:",
                                f"{amount:.2f}"
                            )

                            st.write(
                                "Current Balance:",
                                f"{new_balance:.2f}"
                            )

                    cursor.close()
                    db.close()

                except mysql.connector.Error as e:

                    st.error(str(e))


    # ======================================
    # WITHDRAW
    # ======================================

    elif menu == "Withdraw":

        st.subheader("Withdraw Money")

        amount = st.number_input(
            "Withdraw Amount",
            min_value=0.0,
            step=100.0
        )

        pin = st.text_input(
            "Deposit PIN",
            type="password"
        )

        if st.button("Withdraw"):

            if amount <= 0:

                st.error(
                    "Enter valid amount"
                )

            elif len(pin) != 4 or not pin.isdigit():

                st.error(
                    "Deposit PIN must be 4 digits"
                )

            else:

                try:

                    db = get_db()
                    cursor = db.cursor()

                    cursor.execute("""
                        SELECT
                            name,
                            login_password,
                            deposit_pin,
                            balance
                        FROM bank
                        WHERE account_id = %s
                        ORDER BY id DESC
                        LIMIT 1
                    """, (
                        st.session_state.account_id,
                    ))

                    result = cursor.fetchone()

                    if not result:

                        st.error(
                            "Account not found"
                        )

                    else:

                        name = result[0]
                        login_password = result[1]
                        saved_pin = result[2]
                        current_balance = float(result[3])

                        if str(saved_pin) != str(pin):

                            st.error(
                                "Invalid Deposit PIN"
                            )

                        elif amount > current_balance:

                            st.error(
                                "Insufficient Balance"
                            )

                        else:

                            new_balance = (
                                current_balance - amount
                            )

                            cursor.execute("""
                                INSERT INTO bank
                                (
                                    account_id,
                                    name,
                                    login_password,
                                    deposit_pin,
                                    transaction_type,
                                    amount,
                                    balance,
                                    transaction_time
                                )
                                VALUES
                                (
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    NOW()
                                )
                            """, (
                                st.session_state.account_id,
                                name,
                                login_password,
                                saved_pin,
                                "Withdraw",
                                amount,
                                new_balance
                            ))

                            db.commit()

                            st.success(
                                "Withdrawal Successful"
                            )

                            st.write(
                                "Account Number:",
                                st.session_state.account_id
                            )

                            st.write(
                                "Withdrawn:",
                                f"{amount:.2f}"
                            )

                            st.write(
                                "Current Balance:",
                                f"{new_balance:.2f}"
                            )

                    cursor.close()
                    db.close()

                except mysql.connector.Error as e:

                    st.error(str(e))


    # ======================================
    # BALANCE
    # ======================================

    elif menu == "Balance":

        st.subheader("Balance")

        try:

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                SELECT
                    account_id,
                    name,
                    balance,
                    transaction_time
                FROM bank
                WHERE account_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (
                st.session_state.account_id,
            ))

            result = cursor.fetchone()

            cursor.close()
            db.close()

            if result:

                st.write(
                    "Account Number:",
                    result[0]
                )

                st.write(
                    "Account Holder:",
                    result[1]
                )

                st.success(
                    "Current Balance: "
                    + f"{float(result[2]):.2f}"
                )

                st.write(
                    "Last Updated:",
                    result[3].strftime(
                        "%d-%m-%Y %I:%M:%S %p"
                    )
                )

            else:

                st.error(
                    "Account not found"
                )

        except mysql.connector.Error as e:

            st.error(str(e))


    # ======================================
    # TRANSACTION DETAILS
    # ======================================

    elif menu == "Transaction Details":

        st.subheader("Transaction Details")

        try:

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                SELECT
                    id,
                    account_id,
                    transaction_type,
                    amount,
                    balance,
                    transaction_time
                FROM bank
                WHERE account_id = %s
                ORDER BY id DESC
            """, (
                st.session_state.account_id,
            ))

            rows = cursor.fetchall()

            cursor.close()
            db.close()

            if rows:

                data = []

                for row in rows:

                    data.append({
                        "ID": row[0],
                        "Account Number": row[1],
                        "Transaction": row[2],
                        "Amount": f"{float(row[3]):.2f}",
                        "Balance": f"{float(row[4]):.2f}",
                        "Date & Time": row[5].strftime(
                            "%d-%m-%Y %I:%M:%S %p"
                        )
                    })

                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No transactions found"
                )

        except mysql.connector.Error as e:

            st.error(str(e))


    # ======================================
    # USER LOGOUT
    # ======================================

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.account_id = None
        st.session_state.name = ""

        st.rerun()


# ==========================================
# ADMIN DASHBOARD
# ==========================================

elif st.session_state.role == "admin":

    st.title("Admin Dashboard")

    st.sidebar.subheader("Admin Menu")

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Create Account",
            "All Bank Accounts",
            "Edit Account",
            "All Transactions",
            "Delete Account"
        ]
    )


    # ======================================
    # CREATE ACCOUNT
    # ======================================

    if menu == "Create Account":

        st.subheader("Create Account")

        name = st.text_input(
            "Account Holder Name"
        )

        password = st.text_input(
            "Login Password",
            type="password"
        )

        pin = st.text_input(
            "Deposit PIN",
            type="password"
        )

        st.info(
            "Initial Balance: 1000"
        )

        if st.button("Create Account"):

            name = name.strip()

            if name == "":

                st.error(
                    "Enter account holder name"
                )

            elif password.strip() == "":

                st.error(
                    "Enter login password"
                )

            elif len(pin) != 4 or not pin.isdigit():

                st.error(
                    "Deposit PIN must be 4 digits"
                )

            else:

                try:

                    db = get_db()
                    cursor = db.cursor()

                    cursor.execute("""
                        SELECT MAX(account_id)
                        FROM bank
                    """)

                    result = cursor.fetchone()

                    if result[0] is None:

                        account_id = 1

                    else:

                        account_id = int(result[0]) + 1

                    opening_balance = 1000.00

                    cursor.execute("""
                        INSERT INTO bank
                        (
                            account_id,
                            name,
                            login_password,
                            deposit_pin,
                            transaction_type,
                            amount,
                            balance,
                            transaction_time
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            NOW()
                        )
                    """, (
                        account_id,
                        name,
                        password,
                        pin,
                        "Opening",
                        opening_balance,
                        opening_balance
                    ))

                    db.commit()

                    cursor.close()
                    db.close()

                    st.success(
                        "Account Created Successfully"
                    )

                    st.write(
                        "Account Number:",
                        account_id
                    )

                    st.write(
                        "Account Holder:",
                        name
                    )

                    st.write(
                        "Login Password:",
                        password
                    )

                    st.write(
                        "Deposit PIN:",
                        pin
                    )

                    st.write(
                        "Initial Balance:",
                        "1000.00"
                    )

                except mysql.connector.Error as e:

                    st.error(str(e))


    # ======================================
    # ALL BANK ACCOUNTS
    # ======================================

    elif menu == "All Bank Accounts":

        st.subheader("All Bank Accounts")

        try:

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                SELECT
                    account_id,
                    name,
                    balance,
                    transaction_time
                FROM bank
                WHERE id IN
                (
                    SELECT MAX(id)
                    FROM bank
                    GROUP BY account_id
                )
                ORDER BY account_id
            """)

            rows = cursor.fetchall()

            cursor.close()
            db.close()

            if rows:

                data = []

                for row in rows:

                    data.append({
                        "Account Number": row[0],
                        "Name": row[1],
                        "Balance": f"{float(row[2]):.2f}",
                        "Last Transaction":
                            row[3].strftime(
                                "%d-%m-%Y %I:%M:%S %p"
                            )
                    })

                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No accounts found"
                )

        except mysql.connector.Error as e:

            st.error(str(e))


    # ======================================
    # EDIT ACCOUNT
    # ======================================

    elif menu == "Edit Account":

        st.subheader("Edit Account")

        account_id = st.number_input(
            "Account Number",
            min_value=1,
            step=1
        )

        new_name = st.text_input(
            "New Name"
        )

        new_password = st.text_input(
            "New Login Password",
            type="password"
        )

        new_pin = st.text_input(
            "New Deposit PIN",
            type="password"
        )

        if st.button("Update Account"):

            if new_name.strip() == "":

                st.error(
                    "Enter name"
                )

            elif new_password.strip() == "":

                st.error(
                    "Enter password"
                )

            elif len(new_pin) != 4 or not new_pin.isdigit():

                st.error(
                    "PIN must be 4 digits"
                )

            else:

                try:

                    db = get_db()
                    cursor = db.cursor()

                    cursor.execute("""
                        SELECT id
                        FROM bank
                        WHERE account_id = %s
                        ORDER BY id DESC
                        LIMIT 1
                    """, (
                        account_id,
                    ))

                    result = cursor.fetchone()

                    if not result:

                        st.error(
                            "Account not found"
                        )

                    else:

                        latest_id = result[0]

                        cursor.execute("""
                            UPDATE bank
                            SET
                                name = %s,
                                login_password = %s,
                                deposit_pin = %s
                            WHERE id = %s
                        """, (
                            new_name.strip(),
                            new_password,
                            new_pin,
                            latest_id
                        ))

                        db.commit()

                        st.success(
                            "Account Updated Successfully"
                        )

                    cursor.close()
                    db.close()

                except mysql.connector.Error as e:

                    st.error(str(e))


    # ======================================
    # ALL TRANSACTIONS
    # ======================================

    elif menu == "All Transactions":

        st.subheader("All Transactions")

        try:

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                SELECT
                    id,
                    account_id,
                    name,
                    transaction_type,
                    amount,
                    balance,
                    transaction_time
                FROM bank
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

            cursor.close()
            db.close()

            if rows:

                data = []

                for row in rows:

                    data.append({
                        "ID": row[0],
                        "Account Number": row[1],
                        "Name": row[2],
                        "Transaction": row[3],
                        "Amount": f"{float(row[4]):.2f}",
                        "Balance": f"{float(row[5]):.2f}",
                        "Date & Time":
                            row[6].strftime(
                                "%d-%m-%Y %I:%M:%S %p"
                            )
                    })

                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No transactions found"
                )

        except mysql.connector.Error as e:

            st.error(str(e))


    # ======================================
    # DELETE ACCOUNT
    # ======================================

    elif menu == "Delete Account":

        st.subheader("Delete Account")

        account_id = st.number_input(
            "Account Number",
            min_value=1,
            step=1
        )

        confirm = st.checkbox(
            "Confirm Delete Account"
        )

        if st.button("Delete Account"):

            if not confirm:

                st.warning(
                    "Please confirm deletion"
                )

            else:

                try:

                    db = get_db()
                    cursor = db.cursor()

                    cursor.execute("""
                        DELETE FROM bank
                        WHERE account_id = %s
                    """, (
                        account_id,
                    ))

                    db.commit()

                    if cursor.rowcount > 0:

                        st.success(
                            "Account Deleted Successfully"
                        )

                    else:

                        st.error(
                            "Account not found"
                        )

                    cursor.close()
                    db.close()

                except mysql.connector.Error as e:

                    st.error(str(e))


    # ======================================
    # ADMIN LOGOUT
    # ======================================

    if st.sidebar.button("Log out"):

        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.account_id = None
        st.session_state.name = ""

        st.rerun()
