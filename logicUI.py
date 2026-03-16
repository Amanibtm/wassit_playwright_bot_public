import sqlite3
import threading
from WassitPlaywrightScript import try_logginIn, wassitDatesDetector
from translation import t
import sys , os


def login(id_, numWassit):
    try:
        # Validate inputs
        if id_.strip() == '':
            return False, t("id_field_isEmpty"), None
        elif numWassit.strip() == '':
            return False, t("wassit_field_isEmpty"), None

        if len(id_) < 18:
            return False, t("id_invalid"), None
        if not id_.isdigit() or not numWassit.isdigit():
            return False, t("id_and_wassitnum_not_digital"), None

        # Connect to database
        conn = sqlite3.connect('wassitdata.db')
        cursor = conn.cursor()

        # ✅ Check if combination already exists
        cursor.execute(
            "SELECT * FROM users WHERE user_id = ? AND wassit_number = ? AND is_active = ?",
            (id_, numWassit, True)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            user_data = {
                'id': existing_user[0],
                'user_id': existing_user[1],
                'wassit_number': existing_user[2],
                'is_active': existing_user[3]
            }
            #print(user_data)
            return True, t("successfull_login"), None

        else:
            return False, t("failed_login"), None

    except sqlite3.IntegrityError:
        return False, t("db_issue"), None
    except Exception as e:
        return False, f"{t("cnx_failed_label")} {str(e)}", None


def signin(id_, numWassit):
    """
    Add new user to database only if (user_id OR wassitNum) doesn't exist

    Returns: (success: bool, message: str, user_data: dict)
    """
    try:
        # Validate inputs
        if id_.strip() == '':
            return False, t("id_field_isEmpty"), None
        elif numWassit.strip() == '':
            return False, t("wassit_field_isEmpty"), None

        if len(id_) < 18:
            return False, t("id_invalid"), None
        if not id_.isdigit() or not numWassit.isdigit():
            return False, t("id_and_wassitnum_not_digital"), None


        # Connect to database
        conn = sqlite3.connect('wassitdata.db')
        cursor = conn.cursor()

        # ✅ Check if combination already exists
        cursor.execute(
            "SELECT * FROM users WHERE user_id = ? OR wassit_number = ? AND is_active = ?",
            (id_, numWassit, True)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return False, t("account_existing"), None

        success, message, data = try_logginIn(id_, numWassit)
        if not success:
            return False, message, None
        # ✅ Insert new user
        cursor.execute(
            "INSERT INTO users (user_id, wassit_number,is_active) VALUES (?, ?, ?)",
            (id_, numWassit, True)
        )

        conn.commit()
        #print("account created ! ✅")

        # Get the newly created user
        cursor.execute(
            "SELECT * FROM users WHERE user_id = ? AND wassit_number = ?",
            (id_, numWassit)
        )
        new_user = cursor.fetchone()

        conn.close()

        # Return success with user data
        user_data = {
            'id': new_user[0],
            'user_id': new_user[1],
            'wassit_number': new_user[2],
            'is_active': new_user[3]
        }

        return True, t("successfull_registration"), user_data

    except sqlite3.IntegrityError:
        return False, t("account_existing"), None
    except Exception as e:
        return False, f"{t("failed_registration")}{str(e)}", None


def logout(page):
    page.client_storage.remove("current_user")
    page.go('/')


operation_id = 0
current_timer = None
data_memory = []
success = None
message = None
data = None
success_times = 0
failure_times = 0


def check(userId, userWassitNum, time, is_running):
    global operation_id, current_timer, data_memory, success, message, data, success_times, failure_times

    # New session = new operation ID
    operation_id += 1
    my_id = operation_id

    if is_running:
        # PAUSE logic
        operation_id += 1
        is_running = False
        if current_timer:
            current_timer.cancel()

        # Save memory content if not yet
        if data_memory:
            with sqlite3.connect("wassitdata.db") as conn:
                trace_history(data_memory, conn, userId)

        return is_running, success_times, failure_times, success, message, data

    # START logic
    is_running = True

    def single_check(run_id):
        global success, message, data, success_times, failure_times

        if not is_running:
            return is_running, success_times, failure_times, success, message, data  #  stop the loop immediately # Get one result from your generator
        # STOP if this timer belongs to *old* session
        if run_id != operation_id:
            return is_running, success_times, failure_times, success, message, data
        try:
            success, message, data = wassitDatesDetector(userId, userWassitNum)
            data_memory.append([success, message, str(data) if data else None])

            if len(data_memory) >= 5:
                with sqlite3.connect("wassitdata.db") as conn:
                    trace_history(data_memory, conn, userId)

            # Update UI with the result
            if not success:
                failure_times += 1
            else:
                success_times += 1

            if is_running:
                current_timer = threading.Timer(time * 60, lambda: single_check(run_id))
                current_timer.start()
            return is_running, success_times, failure_times, success, message, data

        except StopIteration:
            # Generator exhausted (shouldn't happen with infinite loop)
            pass

    return single_check(my_id)


def trace_history(data_memory, conn, userId):
    cursor = conn.cursor()
    for each in data_memory[:]:  # [:] means “give me a shallow copy of the entire list”
        mem_success = each[0]
        mem_message = each[1]
        mem_data = each[2]
        cursor.execute("""INSERT INTO history(user_id, success, message, data)VALUES (?, ?, ?, ?)""",
                       (userId, mem_success, mem_message, mem_data))
    conn.commit()
    data_memory.clear()


def show_history(buffer, userId):
    with sqlite3.connect("wassitdata.db") as conn:
        rows = conn.execute("SELECT id, success, message, data, created_at FROM history WHERE user_id=? ORDER BY id", (userId,)).fetchall()
    for id, success, msg, data, created_at in rows:
        buffer.append([id, success, msg, data, created_at])


def delete(id, cards):
    #print(id)
    with sqlite3.connect("wassitdata.db") as conn:
        conn.execute("DELETE FROM history WHERE id=?", (id,))
    for card in list(cards.controls):
        if str(card.key) == str(id):
            cards.controls.remove(card)
            break
    cards.update()


def deactivate_account(page, user_id):
    """Mark the account as inactive"""
    with sqlite3.connect("wassitdata.db") as conn:
        conn.execute("DELETE from users WHERE user_id = ?", (user_id,))
        conn.execute("DELETE from history WHERE user_id = ?", (user_id,))
    logout(page)
