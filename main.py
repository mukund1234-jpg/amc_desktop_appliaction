from PyQt5.QtWidgets import QApplication
from ui.login_ui import LoginUI
from ui.admin_dashboard import AdminDashboard
from ui.app_ui import OfficeWorkerDashboard
from ui.register_ui import RegistrationUI
from database import init_db

window = None  # ✅ Declare global window reference

def handle_login_success(user):
    if user.role == 'admin':
        open_admin_dashboard(user)
    elif user.role == 'office_worker':
        open_office_worker_dashboard(user)
    else:
        print("Unknown role!")

def open_admin_dashboard(user):
    global window
    window.close()
    window = AdminDashboard(user, logout_callback=show_login)
    window.show()

def open_office_worker_dashboard(user):
    global window
    window.close()
    window = OfficeWorkerDashboard(user, logout_callback=show_login)
    window.show()

def show_registration():
    global window
    window.close()
    window = RegistrationUI(show_login)
    window.show()

def show_login():
    global window
    window.close()
    window = LoginUI(
        on_login_success=handle_login_success,
        on_register_clicked=show_registration
    )
    window.show()



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    init_db()

    window = LoginUI(
        on_login_success=handle_login_success,
        on_register_clicked=show_registration
    )
    window.show()

    sys.exit(app.exec_())
