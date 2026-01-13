from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from choice_question_handler import *
from video import *

# 设置浏览器驱动
driver = webdriver.Chrome()
def printbanners():
    print(r"""
            Welcome to use MiTu's Alpha Homework Helper - AlphaBeauty v2.0
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
          """)

def printVideoBanners():
    print(r"""
                    欢迎使用AlphaBeauty视频自动观看模块 - V1.0
          =================================================================
               _   _       _               ___                  _         
              /_\ | |_ __ | |__   __ _    / __\ ___  __ _ _   _| |_ _   _ 
             //_\\| | '_ \| '_ \ / _` |  /__\/// _ \/ _` | | | | __| | | |
            /  _  \ | |_) | | | | (_| | / \/  \  __/ (_| | |_| | |_| |_| |
            \_/ \_/_| .__/|_| |_|\__,_| \_____/\___|\__,_|\__,_|\__|\__, |
                    |_|                                             |___/ 
                   _     _                ___ _                          
            /\   /(_) __| | ___  ___     / _ \ | __ _ _   _  ___ _ __    
            \ \ / / |/ _` |/ _ \/ _ \   / /_)/ |/ _` | | | |/ _ \ '__|   
             \ V /| | (_| |  __/ (_) | / ___/| | (_| | |_| |  __/ |      
              \_/ |_|\__,_|\___|\___/  \/    |_|\__,_|\__, |\___|_|      
                                                      |___/    
          =================================================================          
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
                    success = handle_non_choice_question(driver)
                    if success:
                        print(f"✅ 第 {question_number} 题已跳过")
                        # 等待一下让页面稳定
                        time.sleep(2)
                        
                        # 重新获取题目按钮状态，避免死循环
                        new_question_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
                        current_question = None
                        
                        for btn in new_question_buttons:
                            btn_class = btn.get_attribute('class')
                            if 'current' in btn_class:
                                new_num = btn.text
                                if new_num != question_number:
                                    print(f"已成功切换到第 {new_num} 题")
                                    break
                                else:
                                    # 如果还在同一题，手动标记它为"跳过"
                                    print(f"⚠️ 仍在第 {question_number} 题，强制跳过...")
                                    # 模拟按Tab键或点击下一个按钮
                                    try:
                                        actions = webdriver.ActionChains(driver)
                                        actions.send_keys(Keys.TAB).perform()
                                        time.sleep(1)
                                    except:
                                        pass
                    else:
                        print(f"❌ 第 {question_number} 题跳过失败")

                

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


def handle_non_choice_question(driver):
    """
    适配原有代码的非选择题处理函数
    遇到非选择题时，模拟点击下一个题目并更新状态
    """
    try:
        print("⚠️ 检测到非选择题页面，尝试处理...")
        
        # 获取当前题号
        current_num = None
        current_btn = None
        try:
            question_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
            for btn in question_buttons:
                if 'current' in btn.get_attribute('class'):
                    current_num = btn.text
                    current_btn = btn
                    break
        except:
            pass
        
        # 记录题目信息
        try:
            question_text = "非选择题"
            elements = driver.find_elements(By.CSS_SELECTOR, ".exercise-title, .question-text, .stem")
            if elements:
                question_text = elements[0].text[:50]
            print(f"📝 正在跳过第 {current_num if current_num else '?'} 题: {question_text}...")
        except:
            print(f"📝 正在跳过第 {current_num if current_num else '?'} 题（非选择题）")
        
        # 关键：首先找到下一个未完成的题目
        next_question_num = None
        next_question_btn = None
        
        if current_num and current_btn:
            # 查找下一个未完成的题目
            try:
                question_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
                found_current = False
                for btn in question_buttons:
                    btn_class = btn.get_attribute('class')
                    btn_num = btn.text
                    
                    if found_current and 'status-pass' not in btn_class:
                        next_question_num = btn_num
                        next_question_btn = btn
                        break
                    
                    if btn_num == current_num:
                        found_current = True
            except:
                pass
        
        # 如果有下一个题目，点击它
        if next_question_btn:
            print(f"📝 跳转到第 {next_question_num} 题")
            next_question_btn.click()
            time.sleep(1.5)
            return True
        else:
            # 如果没有下一个未完成的题目，可能已经全部完成
            print("没有找到下一个未完成的题目")
            
            # 尝试点击当前按钮让它失去焦点
            if current_btn:
                # 先点击其他地方
                try:
                    driver.execute_script("arguments[0].blur();", current_btn)
                except:
                    pass
            
            # 返回False，让外层逻辑判断是否需要继续
            return False
        
    except Exception as e:
        print(f"非选择题处理时出错: {e}")
        return True  # 出错时返回True避免卡住


def main():
    printbanners()
    login()
    class_name = input("你想要完成的课程名称:\n(A:软件python科目\tB:软件web科目)\n请选择:")
    if class_name == 'A':
        print("目前python仅支持视频刷课，是否启动？(y/n)")
        choice = input().lower()
        if choice == 'y':
            printVideoBanners()
            url = input("请输入你当前所看到的进度（视频网址）:") # https://tyutr.alphacoding.cn/courses/13415/learn/60067b441b184a51608de9b4
            print("自动观看视频开始...请不要频繁刷新或点击页面，否则程序可能失效！")
            driver.get(url)
            try:
                pages_processed = Vmain(driver, max_pages=50)
                print(f"成功处理了 {pages_processed} 个页面")
            finally:
                print("100s后自动关闭浏览器...")
                time.sleep(100)
                driver.quit()
        elif choice == 'n':
            print("程序结束，未启动刷课模块。")
            driver.quit()
        else:
            print("无效输入，程序结束。")
            driver.quit()           
    elif class_name == 'B':

        choose = input("请输入你想要实现的功能(1/2)\n1.完成所有选择题作业\n2.观看所有视频\n")
        if choose == '1':
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
        elif choose == '2':
            printVideoBanners()
            url = input("请输入你当前所看到的进度（视频网址）:") # https://tyutr.alphacoding.cn/courses/13415/learn/60067b441b184a51608de9b4
            print("自动观看视频开始...请不要频繁刷新或点击页面，否则程序可能失效！")
            driver.get(url)
            try:
                pages_processed = Vmain(driver, max_pages=50)
                print(f"成功处理了 {pages_processed} 个页面")
            finally:
                print("100s后自动关闭浏览器...")
                time.sleep(100)
                driver.quit()
        else:
            print("无效的功能选择，程序结束。")
            driver.quit()
    else:
        print("无效的课程选择，程序结束。")
        driver.quit()    


if __name__ == "__main__":
    main()
