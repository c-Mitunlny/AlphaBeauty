from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def navigate_to_task(driver):
    task_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.nav-link[href='/task']"))
    )
    task_link.click()

def locate_answer_button(driver, index=0):
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
        print(f"没有在/task界面找到'去做答'按钮，观察题目是否已经作答完毕或程序发生错误: {e}")
        return None

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import time

def click_do_homework_button(driver, index=0):
    """
    点击做作业按钮
    如果在5秒内未找到做作业按钮，会尝试查找并点击展开按钮
    然后再重新查找做作业按钮
    """
    # 定义做作业按钮的选择器
    homework_button_selector = f"button.bg-primary-600:nth-of-type({index + 1})"
    
    try:
        print(f"开始查找第{index+1}个做作业按钮...")
        
        # 第一次尝试：直接查找做作业按钮
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, homework_button_selector))
            )
            button.click()
            print(f"✓ 成功点击第{index+1}个做作业按钮")
            return True
            
        except TimeoutException:
            print(f"⏱️ 5秒内未找到做作业按钮，尝试展开更多内容...")
            
            # 第二次尝试：查找并点击"显示余下"按钮
            try:
                # 使用多种方式定位"显示余下"按钮
                show_more_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '显示余下')]")
                
                if not show_more_buttons:
                    # 尝试其他可能的选择器
                    show_more_buttons = driver.find_elements(By.CSS_SELECTOR, "button.text-gray-500")
                    show_more_buttons = [btn for btn in show_more_buttons if "显示余下" in btn.text]
                
                if show_more_buttons:
                    show_more_button = show_more_buttons[0]
                    button_text = show_more_button.text
                    
                    # 滚动到按钮位置
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", show_more_button)
                    time.sleep(0.5)
                    
                    # 点击按钮
                    show_more_button.click()
                    print(f"✓ 成功点击'显示余下'按钮: {button_text}")
                    
                    # 等待内容加载
                    time.sleep(1.5)  # 等待动态内容加载
                    
                    # 第三次尝试：再次查找做作业按钮
                    try:
                        button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, homework_button_selector))
                        )
                        button.click()
                        print(f"✓ 成功点击第{index+1}个做作业按钮")
                        return True
                        
                    except TimeoutException:
                        print("❌ 点击展开按钮后，仍然未找到做作业按钮")
                        return False
                else:
                    print("❌ 未找到展开按钮")
                    return False
                    
            except Exception as e:
                print(f"❌ 处理展开按钮时出错: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 函数执行出错: {e}")
        return False