"""
choice_question_handler.py
选择题处理模块 - 尝试每个选项并提交
"""

from selenium.webdriver.common.by import By
import time

def handle_choice_question(driver):
    """
    处理选择题：尝试每个选项并提交
    
    Args:
        driver: WebDriver实例
    
    Returns:
        bool: 是否成功作答
    """
    try:
        # 1. 获取当前题目的按钮信息
        current_btn = get_current_question_button(driver)
        if not current_btn:
            print("未找到当前题目按钮")
            return False
        
        current_question_num = current_btn.text
        print(f"当前题目: 第{current_question_num}题")
        
        # 2. 获取所有选项
        options = driver.find_elements(By.CSS_SELECTOR, "input[type='radio'], input[type='checkbox']")
        
        if not options:
            print("未找到任何选项")
            return False
        
        print(f"找到 {len(options)} 个选项")
        
        # 3. 记录当前题目的初始状态
        initial_status = current_btn.get_attribute('class')
        print(f"题目初始状态: {initial_status}")
        
        # 4. 尝试每个选项
        for i, option in enumerate(options):
            print(f"\n尝试第 {i+1} 个选项...")
            
            try:
                # 清空之前的选择
                clear_selections(driver, options)
                
                # 点击新选项
                option.click()
                time.sleep(0.3)
                
                # 提交
                if try_submit_question(driver):
                    # 等待状态更新
                    time.sleep(0.3)
                    
                    # 检查题目按钮状态是否变为pass
                    if check_question_passed(driver, current_question_num):
                        print(f"✅ 第 {i+1} 个选项正确！题目状态已更新为pass")
                        return True
                    else:
                        print(f"❌ 第 {i+1} 个选项错误，题目状态未更新")
                else:
                    print(f"❌ 第 {i+1} 个选项提交失败")
                    
            except Exception as e:
                print(f"尝试第 {i+1} 个选项失败: {e}")
                continue
        
        print("\n所有选项都尝试完毕，均未成功")
        return False
        
    except Exception as e:
        print(f"处理选择题失败: {e}")
        return False

def get_current_question_button(driver):
    """
    获取当前题目的按钮元素
    """
    try:
        # 查找包含 current 类的题目按钮
        current_buttons = driver.find_elements(
            By.CSS_SELECTOR, ".exercise-nav-btn.current"
        )
        
        if current_buttons:
            return current_buttons[0]
        
        # 如果找不到current，找所有题目按钮
        all_question_buttons = driver.find_elements(
            By.CLASS_NAME, "exercise-nav-btn"
        )
        
        for btn in all_question_buttons:
            if "current" in btn.get_attribute('class'):
                return btn
        
        return None
        
    except:
        return None

def check_question_passed(driver, question_num):
    """
    检查指定题目的按钮是否变为pass状态
    
    Args:
        driver: WebDriver实例
        question_num: 题目编号
    
    Returns:
        bool: 是否已通过
    """
    try:
        # 找到指定题号的按钮
        question_buttons = driver.find_elements(
            By.CLASS_NAME, "exercise-nav-btn"
        )
        
        for btn in question_buttons:
            if btn.text == question_num:
                btn_class = btn.get_attribute('class')
                is_passed = 'status-pass' in btn_class
                print(f"题目{question_num}状态: {btn_class}, 是否pass: {is_passed}")
                return is_passed
        
        return False
        
    except:
        return False

def clear_selections(driver, all_options):
    """
    清空所有已选中的选项
    """
    try:
        # 对于checkbox，取消所有选中状态
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']:checked")
        for checkbox in checkboxes:
            if checkbox.is_selected():
                checkbox.click()
                time.sleep(0.1)
    except:
        pass

def try_submit_question(driver):
    """
    尝试提交题目
    
    Returns:
        bool: 是否成功提交
    """
    try:
        # 查找提交按钮
        submit_button = find_submit_button(driver)
        
        if not submit_button:
            print("未找到提交按钮")
            return False
        
        # 检查按钮是否可用
        if not is_button_enabled(submit_button):
            print("提交按钮不可用")
            return False
        
        print(f"找到提交按钮: {submit_button.text}")
        
        # 点击提交按钮
        submit_button.click()
        print("已点击提交按钮")
        
        # 等待页面响应
        time.sleep(0.5)
        return True
        
    except Exception as e:
        print(f"提交失败: {e}")
        return False

def is_button_enabled(button):
    """
    检查按钮是否可用
    """
    try:
        class_attr = button.get_attribute('class') or ''
        disabled_keywords = ['cursor-not-allowed', 'pointer-events-none', 'opacity-40', 'disabled']
        
        for keyword in disabled_keywords:
            if keyword in class_attr:
                return False
        
        return button.is_enabled() and button.is_displayed()
    except:
        return False

def find_submit_button(driver):
    """
    查找提交按钮
    """
    # 方法1：按文本查找
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            btn_text = btn.text.strip()
            if btn_text and ("提交" in btn_text or "交卷" in btn_text):
                return btn
    except:
        pass
    
    # 方法2：按class查找
    try:
        submit_selectors = [
            "button.bg-success-600",
            "button[class*='bg-success']",
            "button.font-medium.whitespace-nowrap.shadow-sm.rounded.border",
            "button.text-white"
        ]
        
        for selector in submit_selectors:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for btn in buttons:
                if btn.is_displayed():
                    return btn
    except:
        pass
    
    return None