from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from page_element_explorer import *
from choice_question_handler import *

# 设置浏览器驱动
driver = webdriver.Chrome()
def printbanners():
    print(r"""
          Welcome to use Mitunlny's Alpha Homework Helper - AlphaBeauty v1.0
          ==================================================================
              ___  _       _            ______                  _         
             / _ \| |     | |           | ___ \                | |        
            / /_\ \ |_ __ | |__   __ _  | |_/ / ___  __ _ _   _| |_ _   _ 
            |  _  | | '_ \| '_ \ / _` | | ___ \/ _ \/ _` | | | | __| | | |
            | | | | | |_) | | | | (_| | | |_/ /  __/ (_| | |_| | |_| |_| |
            \_| |_/_| .__/|_| |_|\__,_| \____/ \___|\__,_|\__,_|\__|\__, |
                    | |                                              __/ |
                    |_|                                             |___/        
          ==================================================================
                   Everything will be fine! Believe in yourself!
                       目前仅支持选择题，遇到非选择题会寄掉....
          """)



def login():
# 登录函数
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

def navigate_to_task():
# 进入作业页面
    task_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.nav-link[href='/task']"))
    )
    task_link.click()

def locate_answer_button(driver, index=0):
# 定位所有的“去作答”按钮，从第一个开始点击

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='去作答']"))
        )
        
        buttons = driver.find_elements(By.XPATH, "//button[text()='去作答']")
        
        if buttons:
            return buttons[index]
        else:
            raise Exception("未找到'去作答'按钮")
            
    except Exception as e:
        print(f"没有在/task界面找到“去做答”按钮，观察题目是否已经作答完毕或程序发生错误: {e}")
        return None



def click_do_homework_button(driver, index=0):
# 定位所有“做作业”按钮，点击第一个
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                f"button.bg-primary-600:nth-of-type({index + 1})"
            ))
        )
        button.click()
        print(f"成功点击第{index+1}个做作业按钮")
        return True
        
    except Exception as e:
        print(f"点击失败: {e}")
        return False



def complete_all_questions_smart(driver, max_attempts=3):
# 完成所有题目的智能函数
    try:
        while True:
            question_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
            
            if not question_buttons:
                print("没有找到题目按钮")
                return False
            
            all_passed = all('status-pass' in btn.get_attribute('class') for btn in question_buttons)
            
            if all_passed:
                print("🎉所有题目已完成！")
                return True
            
            current_question = None
            for btn in question_buttons:
                btn_class = btn.get_attribute('class')
                if 'status-pass' not in btn_class:
                    current_question = btn
                    break
            
            if not current_question:
                print("未找到未完成的题目")
                return True
            

            question_number = current_question.text
            print(f"\n{'='*50}")
            print(f"开始处理第 {question_number} 题...")
            
            try:

                if 'current' not in current_question.get_attribute('class'):
                    current_question.click()
                    time.sleep(1.5)
                
                # 判断题目类型并处理
                if is_choice_question_page_simple(driver):
                    print("检测到选择题页面")
                    success = handle_choice_question(driver)
                    
                    if success:
                        print(f"✅ 第 {question_number} 题已通过")
                        

                        time.sleep(1)
                        
                        # 检查是否通过
                        current_btn_class = current_question.get_attribute('class')
                        if 'status-pass' in current_btn_class:
                            print(f"✅ 确认第 {question_number} 题状态已更新为pass")
                            
                            # 自动点击下一个未完成的题目
                            if not click_next_unfinished_question(driver, question_number):
                                print("已经是最后一题或找不到下一题")
                                break
                        else:
                            print(f"⚠️ 第 {question_number} 题状态未更新为pass，继续当前题目")
                    else:
                        print(f"❌ 第 {question_number} 题处理失败")
                        # 如果失败，停留当前题目继续尝试
                else:
                    print("检测到非选择题页面")
                    success = handle_non_choice_question(driver) # 这个还没写。。。
                    if success:
                        print(f"✅ 第 {question_number} 题已通过")
                        
                        # 等待状态更新
                        time.sleep(1)
                        
                        # 检查是否真的通过了
                        current_btn_class = current_question.get_attribute('class')
                        if 'status-pass' in current_btn_class:
                            print(f"✅ 确认第 {question_number} 题状态已更新为pass")
                            
                            # 自动点击下一个未完成的题目
                            if not click_next_unfinished_question(driver, question_number):
                                print("已经是最后一题或找不到下一题")
                                break
                        else:
                            print(f"⚠️ 第 {question_number} 题状态未更新为pass，继续当前题目")
                    else:
                        print(f"❌ 第 {question_number} 题处理失败")
                

                time.sleep(0.3)
                
            except Exception as e:
                print(f"处理第 {question_number} 题时出错: {e}")
                time.sleep(2)
            
    except KeyboardInterrupt:
        print("用户中断操作")
        return False
    except Exception as e:
        print(f"自动完成失败: {e}")
        return False

def click_next_unfinished_question(driver, current_question_num):
# 查找下一题
    try:
        question_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
        
        if not question_buttons:
            return False
        
        question_dict = {}
        for btn in question_buttons:
            try:
                num = int(btn.text.strip())
                question_dict[num] = btn
            except:
                continue
        
        sorted_nums = sorted(question_dict.keys())
        
        current_num = int(current_question_num)
        
        for num in sorted_nums:
            if num > current_num:  # 找编号更大的题目
                btn = question_dict[num]
                btn_class = btn.get_attribute('class')
                
                if 'status-pass' not in btn_class:  # 未通过的题目
                    print(f"📝 自动跳转到第 {num} 题")
                    btn.click()
                    time.sleep(1.5)  # 等待页面加载
                    return True
        
        # 如果没有找到后面的未完成题目，找第一个未完成的题目
        for num in sorted_nums:
            btn = question_dict[num]
            btn_class = btn.get_attribute('class')
            
            if 'status-pass' not in btn_class:
                print(f"📝 跳转到第 {num} 题（重新开始）")
                btn.click()
                time.sleep(1.5)
                return True
        
        print("所有题目都已通过")
        return False
        
    except Exception as e:
        print(f"点击下一题失败: {e}")
        return False



def is_choice_question_page_simple(driver, timeout=3):
# 判断页面是否为选择题
    try:
        # 等待页面基本加载
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # 快速检查是否有足够的选项
        radio_count = len(driver.find_elements(By.CSS_SELECTOR, "input[type='radio']"))
        checkbox_count = len(driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"))
        
        return (radio_count + checkbox_count) >= 2
        
    except:
        return False






def main():
    printbanners()
    login()

    while True:
        navigate_to_task()

        answer_button = locate_answer_button(driver, 0)
        
        if answer_button is None:
            print("未找到任务，可能已全部完成或发生错误，程序结束。")
            break
        
        answer_button.click()

        time.sleep(1)
        
        click_do_homework_button(driver, 0)
        
        complete_all_questions_smart(driver)

    print("100s后自动关闭浏览器...")
    time.sleep(100)
    driver.quit()

if __name__ == "__main__":
    main()
