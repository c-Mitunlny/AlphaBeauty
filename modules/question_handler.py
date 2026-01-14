from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.choice_question_handler import handle_choice_question
import time

def print_notice_message(title, message):
    """在终端显示醒目的提示消息"""
    print(f"\n{'='*60}")
    print(f"\033[93m⚠️ {title}\033[0m")  # 黄色标题
    print(f"{message}")
    print(f"{'='*60}\n")

def complete_all_questions_smart(driver, max_attempts=3):
    """智能完成所有题目，遇到非选择题时在终端提示"""
    try:
        while True:
            question_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
            
            if not question_buttons:
                print("没有找到题目按钮")
                return False
            
            all_passed = all('status-pass' in btn.get_attribute('class') for btn in question_buttons)
            
            if all_passed:
                print("🎉所有题目已完成！")
                print("正在返回任务页面...")
                try:
                    # 导航回任务页面
                    driver.get("https://tyutr.alphacoding.cn/task")
                    time.sleep(2)  # 等待页面加载
                    print("✅ 已返回任务页面")
                except Exception as nav_error:
                    print(f"返回任务页面时出错: {nav_error}")
                return True
            
            # 找到第一个未完成的题目
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
                # 确保点击当前题目
                if 'current' not in current_question.get_attribute('class'):
                    current_question.click()
                    time.sleep(1.5)
                
                if is_choice_question_page_simple(driver):
                    print("检测到选择题页面")
                    success = handle_choice_question(driver)
                    
                    if success:
                        print(f"✅ 第 {question_number} 题已通过")
                        time.sleep(1)
                        
                        # 检查状态是否更新为pass
                        current_btn_class = current_question.get_attribute('class')
                        if 'status-pass' in current_btn_class:
                            print(f"✅ 确认第 {question_number} 题状态已更新为pass")
                            continue
                        else:
                            print(f"⚠️ 第 {question_number} 题状态未更新为pass，重新检查")
                    else:
                        print(f"❌ 第 {question_number} 题处理失败")
                else:
                    
                    # 获取题目信息
                    question_info = get_question_info(driver, question_number)
                    
                    # 在终端显示提示信息
                    title = "检测到非选择题类型"
                    message = f"""
第 {question_number} 题是非选择题，需要手动完成！

题目信息：{question_info}

请手动完成该题目后，程序会自动检测状态并继续。
"""
                    print_notice_message(title, message)
                    
                    print(f"等待用户手动处理第 {question_number} 题...")
                    
                    # 等待用户手动处理
                    while True:
                        time.sleep(2)
                        
                        # 重新获取题目状态
                        updated_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
                        current_updated = None
                        
                        for btn in updated_buttons:
                            if btn.text == question_number:
                                current_updated = btn
                                break
                        
                        if current_updated:
                            btn_class = current_updated.get_attribute('class')
                            if 'status-pass' in btn_class:
                                print(f"✅ 检测到第 {question_number} 题已完成")
                                break
                            else:
                                print(f"⏳ 第 {question_number} 题仍在处理中...")
                        else:
                            print("⚠️ 未找到当前题目按钮，继续等待...")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"处理第 {question_number} 题时出错: {e}")
                time.sleep(2)
            
    except KeyboardInterrupt:
        print("用户中断操作")
        return False
    except Exception as e:
        print(f"自动完成失败: {e}")
        return False

def get_question_info(driver, question_number):
    """获取题目信息"""
    try:
        info = ""
        
        # 查找题目元素
        selectors = [
            ".exercise-title",
            ".question-text",
            ".stem",
            ".question-stem",
            ".title",
            "h1, h2, h3, h4"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].text.strip()
                    if text and len(text) > 0:
                        info = text[:100] + "..." if len(text) > 100 else text
                        break
            except:
                continue
        
        if not info:
            info = "非选择题（题型识别失败）"
        
        return info
    except:
        return f"第 {question_number} 题（非选择题）"

def is_choice_question_page_simple(driver, timeout=3):
    """简单检测是否为选择题页面"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        radio_count = len(driver.find_elements(By.CSS_SELECTOR, "input[type='radio']"))
        checkbox_count = len(driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"))
        
        return (radio_count + checkbox_count) >= 2
        
    except:
        return False