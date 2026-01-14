from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(driver):
    driver.get("https://tyutr.alphacoding.cn/login")

    username_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
    )
    password_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )

    username = input("请输入账号: ")
    password = input("请输入密码: ")
    username_box.send_keys(username)
    password_box.send_keys(password)

    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'n-button--primary-type')]"))
    )
    login_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_changes("https://tyutr.alphacoding.cn/login")
    )