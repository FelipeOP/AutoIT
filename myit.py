import logging
import time

import pandas as pd
import whatsapp as whatsapp
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EXPECTED_CONDITIONS
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager

service = Service(EdgeChromiumDriverManager().install())
BROWSER = webdriver.Edge(service=service)


URL_HOMEPAGE = 'https://myitfull.claro.com.co:8443/arsys/shared/login.jsp?/arsys/home'
WO_HEADERS = ['ID', 'Resumen', 'Servicio', 'Prioridad', 'Estado',
              'Motivo del estado', 'Usuario asignado', 'Fecha inicio', 'Fecha envio', 'Nombre producto']
INC_HEADERS = ['ID', 'Resumen', 'Servicio', 'Prioridad', 'Estado',
               'Usuario asignado', 'Fecha deseada', 'Fecha de envío', 'Nombre producto']

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def open_myit():
    BROWSER.maximize_window()
    BROWSER.get(URL_HOMEPAGE)


def login_myit(user, password):
    username_input = BROWSER.find_element(By.XPATH, '//*[@id="username-id"]')
    password_input = BROWSER.find_element(By.XPATH, '//*[@id="pwd-id"]')
    login_button = BROWSER.find_element(By.XPATH, '//*[@id="login"]')

    username_input.send_keys(user)
    password_input.send_keys(password)
    login_button.click()


def is_user_logged():
    try:
        WebDriverWait(BROWSER, 5).until(EXPECTED_CONDITIONS.alert_is_present(),
                                        message='No se encuentra el alert')
        logging.info('Handled alert')
        return True
    except TimeoutException:
        logging.info('User not loged, proceeding normally')
        return False


def handle_promp(action):
    alert = BROWSER.switch_to.alert
    if action == 'accept':
        alert.accept()
    elif action == 'dismiss':
        alert.dismiss()
        go_to_home()


def go_to_home():
    link_home = BROWSER.find_element(
        By.XPATH, '//*[@id="logoutmsg"]/tbody/tr[4]/td[2]/a')
    link_home.click()


def give_support():
    while True:
        try:
            wos_table = get_table_rows('T302847900')
            inc_table = get_table_rows('T302087200')
            WOS = parse_html_to_dataframe(wos_table, WO_HEADERS)
            INCS = parse_html_to_dataframe(inc_table, INC_HEADERS)
            verify_news(WOS, INCS)
            wait(300)
        except Exception as e:
            logging.error(f"Error: {e.args[0]}")

    log_out()
    whatsapp.send_message("Se ha cerrado la sesión")


def get_table_rows(table_id):
    table = WebDriverWait(BROWSER, 5).until(
        EXPECTED_CONDITIONS.presence_of_element_located((By.ID, table_id)),
        message='No se encuentra la tabla'
    )
    rows = table.find_elements(By.TAG_NAME, 'tr')
    return rows


def parse_html_to_dataframe(rows, headers):
    cells = []
    for tr in rows:
        row = []
        for td in tr.find_elements(By.TAG_NAME, 'td'):
            row.append(td.text)
        cells.append(row)

    return pd.DataFrame(cells, columns=headers).dropna(subset=headers)


def verify_news(work_orders, incidents):
    column_to_filter = 'Usuario asignado'
    assigned_wo = len(work_orders[work_orders[column_to_filter] != ''])
    assigned_inc = len(incidents[incidents[column_to_filter] != ''])
    unassigned_wo = len(work_orders[work_orders[column_to_filter] == ''])
    unassigned_inc = len(incidents[incidents[column_to_filter] == ''])

    if (unassigned_wo == 0 and unassigned_inc == 0):
        logging.info(
            f'No hay novedades. WO Asignados: {assigned_wo} INC Asignados: {assigned_inc}'
        )
        return

    message = f'Hay {unassigned_wo} orden(es) de trabajo y {unassigned_inc} incidente(s) pendientes'
    logging.critical(message)
    whatsapp.send_message(message)


def wait(seconds=300):
    time.sleep(seconds)
    BROWSER.refresh()


def log_out():
    log_out_button = BROWSER.find_element(
        By.XPATH, '//*[@id="WIN_0_300000044"]/div/div')
    log_out_button.click()


# TODO: Handle popup with error 9084 when session expires
def is_error_9084():
    try:
        WebDriverWait(BROWSER, 5).until(EXPECTED_CONDITIONS.presence_of_element_located((
            By.XPATH, '//*[@id="PopupMsgFooter"]/a')),
            message='No se encuentra el popup')
        logging.info('Handled error 9084')
        return False
    except TimeoutException as e:
        logging.exception(msg='ARERR 9084', exc_info=e)
        return True


# TODO: Use this to solve overlap when there are 2 users logged in
def handle_user_connected():
    pop_up_button = BROWSER.find_element(
        By.XPATH, '//*[@id="PopupMsgFooter"]/a')
    pop_up_button.click()
    log_out()


def main():
    # whatsapp.init_sandbox()
    open_myit()
    login_myit('user', 'password')
    if is_user_logged():
        handle_promp('accept')
    give_support()


if __name__ == '__main__':
    main()
