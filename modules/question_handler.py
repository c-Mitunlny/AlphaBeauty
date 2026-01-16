from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.choice_question_handler import handle_choice_question
from modules.question_type_detector import QuestionTypeDetector
from modules.fill_blank_handler import FillBlankHandler
from modules.programming_handler import ProgrammingHandler
import time

def print_notice_message(title, message):
    """在终端显示醒目的提示消息"""
    print(f"\n{'='*60}")
    print(f"\033[93m⚠️ {title}\033[0m")  # 黄色标题
    print(f"{message}")
    print(f"{'='*60}\n")

def complete_all_questions_smart(driver, max_attempts=3):
    """智能完成所有题目，根据题目类型选择对应的处理模块"""
    try:
        while True:
            question_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
            
            if not question_buttons:
                print("没有找到题目按钮")
                return False
            
            # 检查是否所有题目都已完成
            all_passed = all('status-pass' in btn.get_attribute('class') for btn in question_buttons)
            
            if all_passed:
                print("🎉 所有题目已完成！")
                print("正在返回任务页面...")
                try:
                    # 导航回任务页面
                    driver.get("https://tyutr.alphacoding.cn/task")
                    time.sleep(1)  # 等待页面加载
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
            print(f"\n{'='*60}")
            print(f"开始处理第 {question_number} 题...")
            
            try:
                # 确保点击当前题目
                if 'current' not in current_question.get_attribute('class'):
                    current_question.click()
                    time.sleep(1.5)
                
                # 检测题目类型
                question_type = QuestionTypeDetector.detect_question_type(driver)
                type_name = QuestionTypeDetector.get_question_type_name(question_type)
                
                print(f"📝 检测到题目类型: {type_name}")
                
                success = False
                
                # 根据题目类型选择对应的处理模块
                if question_type == QuestionTypeDetector.QUESTION_TYPE_CHOICE:
                    print("🔄 使用选择题处理模块")
                    success = handle_choice_question(driver)
                    
                elif question_type == QuestionTypeDetector.QUESTION_TYPE_FILL_BLANK:
                    print("🔄 使用填空题处理模块")
                    success = FillBlankHandler.handle_fill_blank_question(driver)
                    
                elif question_type == QuestionTypeDetector.QUESTION_TYPE_PROGRAMMING:
                    print("🔄 使用编程题处理模块")
                    success = ProgrammingHandler.handle_programming_question(driver)
                    
                else:
                    # 未知题型，提示用户手动处理
                    print(f"❓ 未知题目类型: {type_name}")
                    question_info = get_question_info(driver, question_number)
                    
                    # 在终端显示醒目的提示信息
                    title = f"检测到{type_name}"
                    message = f"""
第 {question_number} 题是{type_name}，需要手动完成！

题目信息：{question_info}

请手动完成该题目后，程序会自动检测状态并继续。

手动完成步骤：
1. 在浏览器中完成该题目
2. 点击提交/确认按钮
3. 程序会自动检测完成状态
"""
                    print_notice_message(title, message)
                    
                    # 等待用户手动处理
                    success = wait_for_manual_completion(driver, question_number)
                
                if success:
                    print(f"✅ 第 {question_number} 题处理完成")
                    
                    # 检查状态是否更新为pass
                    time.sleep(0.5)  # 等待状态更新
                    
                    # 重新获取题目按钮状态
                    updated_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
                    for btn in updated_buttons:
                        if btn.text == question_number:
                            btn_class = btn.get_attribute('class')
                            if 'status-pass' in btn_class:
                                print(f"✅ 确认第 {question_number} 题状态已更新为pass")
                                break
                            else:
                                print(f"⚠️ 第 {question_number} 题状态未更新为pass，尝试重新检查")
                                time.sleep(1)
                    
                else:
                    print(f"❌ 第 {question_number} 题处理失败")
                    
                    # 如果是选择题失败，可能是选项都尝试过了但仍然错误
                    # 这里可以添加逻辑：跳过此题或重试
                    if question_type == QuestionTypeDetector.QUESTION_TYPE_CHOICE:
                        print("❌ 选择题尝试所有选项均失败，可能题目有误，尝试跳过此题...")
                        
                        # 尝试点击下一题按钮
                        try:
                            next_buttons = driver.find_elements(By.XPATH, 
                                "//button[contains(text(), '下一题') or contains(text(), '下一道')]")
                            if next_buttons and next_buttons[0].is_displayed():
                                next_buttons[0].click()
                                time.sleep(0.5)
                        except:
                            pass
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n 用户中断操作")
                print("是否继续处理其他题目？(y/n)")
                choice = input().lower()
                if choice not in ['y', 'yes']:
                    return False
                    
            except Exception as e:
                print(f"处理第 {question_number} 题时出错: {e}")
                time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n用户中断程序")
        return False
    except Exception as e:
        print(f"自动完成所有题目失败: {e}")
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
    
def wait_for_manual_completion(driver, question_number):
    """等待用户手动完成题目"""
    print(f"等待用户手动处理第 {question_number} 题...")
    
    while True:
        time.sleep(1)
        
        # 检查题目是否已完成
        if check_question_completed(driver, question_number):
            print(f"✅ 检测到第 {question_number} 题已完成")
            return True
        
        print(f"⏳ 第 {question_number} 题仍在处理中...")

def wait_for_manual_completion(driver, question_number):
    """等待用户手动完成题目"""
    print(f"⏳ 等待用户手动处理第 {question_number} 题...")
    print("提示：完成题目后请确保点击提交/确认按钮")
    
    wait_start_time = time.time()
    max_wait_time = 300  # 最长等待5分钟
    
    while time.time() - wait_start_time < max_wait_time:
        time.sleep(1)
        
        # 检查题目是否已完成
        if check_question_completed(driver, question_number):
            print(f"✅ 检测到第 {question_number} 题已完成")
            return True
        
        # 每10秒打印一次提示
        elapsed = int(time.time() - wait_start_time)
        if elapsed % 10 == 0:
            print(f"⏳ 第 {question_number} 题仍在处理中... 已等待 {elapsed} 秒")
    
    print(f"⚠️ 等待超时 ({max_wait_time} 秒)，第 {question_number} 题未完成")
    return False

def check_question_completed(driver, question_number):
    """检查指定题目是否已完成"""
    try:
        question_buttons = driver.find_elements(By.CLASS_NAME, "exercise-nav-btn")
        
        for btn in question_buttons:
            if btn.text == question_number:
                btn_class = btn.get_attribute('class')
                is_passed = 'status-pass' in btn_class
                if is_passed:
                    print(f"🎯 检测到题目 {question_number} 状态: PASS")
                return is_passed
        
        return False
    except Exception as e:
        print(f"检查题目状态时出错: {e}")
        return False