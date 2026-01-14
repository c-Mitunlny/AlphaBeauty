"""
题目类型判断模块
功能：根据当前页面元素判断题目类型
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class QuestionTypeDetector:
    """题目类型检测器"""
    
    # 题目类型枚举
    QUESTION_TYPE_CHOICE = "choice"       # 选择题
    QUESTION_TYPE_FILL_BLANK = "fill_blank" # 填空题
    QUESTION_TYPE_PROGRAMMING = "programming" # 编程题
    QUESTION_TYPE_UNKNOWN = "unknown"     # 未知类型
    
    @staticmethod
    def detect_question_type(driver):
        """
        检测当前页面的题目类型
        
        Args:
            driver: WebDriver实例
            
        Returns:
            str: 题目类型（choice/fill_blank/programming/unknown）
        """
        try:
            # 等待页面加载
            WebDriverWait(driver, 3).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 优先级 1: 检测编程题特征（检查"页面预览"）
            if QuestionTypeDetector._has_html_preview_panel(driver):
                return QuestionTypeDetector.QUESTION_TYPE_PROGRAMMING
            
            # 优先级 2: 检测选择题特征
            if QuestionTypeDetector._is_choice_question(driver):
                return QuestionTypeDetector.QUESTION_TYPE_CHOICE
            
            # 优先级 3: 检测填空题特征
            if QuestionTypeDetector._is_fill_blank_question(driver):
                return QuestionTypeDetector.QUESTION_TYPE_FILL_BLANK
            
            # 优先级 4: 再次检测编程题的其他特征
            if QuestionTypeDetector._is_programming_question(driver):
                return QuestionTypeDetector.QUESTION_TYPE_PROGRAMMING
            
            return QuestionTypeDetector.QUESTION_TYPE_UNKNOWN
            
        except Exception as e:
            print(f"检测题目类型时出错: {e}")
            return QuestionTypeDetector.QUESTION_TYPE_UNKNOWN
    
    @staticmethod
    def _has_html_preview_panel(driver):
        """
        检查是否存在"页面预览"部分
        这是判断编程题的首要条件
        
        Args:
            driver: WebDriver实例
            
        Returns:
            bool: 是否存在页面预览
        """
        try:
            # 方法1: 直接查找包含"页面预览"文本的元素
            preview_elements = driver.find_elements(By.XPATH,
                "//*[contains(text(), '页面预览') or contains(text(), 'HTML预览') or contains(text(), '网页预览')]")
            
            # 方法2: 查找特定的class或id
            css_selectors = [
                ".html-preview", "#html-preview", "[class*='preview']",
                ".right-panel", ".preview-panel", ".splitpanes__pane"
            ]
            
            for selector in css_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # 检查元素是否包含iframe或特定内容
                        iframes = element.find_elements(By.TAG_NAME, "iframe")
                        if iframes:
                            return True
                        # 检查元素文本内容
                        text = element.text.lower()
                        if 'preview' in text or '预览' in text:
                            return True
                except:
                    continue
            
            # 方法3: 查找iframe的父元素
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    parent = iframe.find_element(By.XPATH, "..")
                    parent_text = parent.text.lower()
                    if 'preview' in parent_text or '预览' in parent_text:
                        return True
                except:
                    continue
            
            # 方法4: 查找带有预览功能的特定结构
            preview_tabs = driver.find_elements(By.XPATH,
                "//div[contains(@class, 'tab') or contains(@class, 'pane')]")
            for tab in preview_tabs:
                try:
                    text = tab.text.lower()
                    if ('页面预览' in text or 'html' in text) and ('iframe' in tab.get_attribute('outerHTML').lower()):
                        return True
                except:
                    continue
            
            # 如果找到"页面预览"文本元素
            if preview_elements:
                print(f"找到 {len(preview_elements)} 个包含'页面预览'的元素")
                for element in preview_elements:
                    # 检查这个元素是否在可见的tab或panel中
                    try:
                        # 查找父级tab或panel
                        parent = element.find_element(By.XPATH, "..")
                        parent_html = parent.get_attribute('outerHTML').lower()
                        if 'active' in parent_html or not 'hidden' in parent_html:
                            print("发现激活的页面预览标签")
                            return True
                    except:
                        # 如果元素本身可见
                        if element.is_displayed():
                            print("发现可见的页面预览文本")
                            return True
                
                # 检查第一个元素周围的环境
                try:
                    parent_html = preview_elements[0].find_element(By.XPATH, "../..").get_attribute('outerHTML')
                    print("页面预览父级HTML:", parent_html[:200])
                    
                    # 检查父级是否包含iframe或其他预览特征
                    if 'iframe' in parent_html.lower():
                        print("父级包含iframe，判定为编程题")
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"检查页面预览时出错: {e}")
            return False
    
    @staticmethod
    def _is_choice_question(driver):
        """检测是否为选择题"""
        try:
            # 检测单选按钮
            radio_count = len(driver.find_elements(By.CSS_SELECTOR, "input[type='radio']"))
            # 检测多选按钮
            checkbox_count = len(driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"))
            # 检测选择题选项容器
            option_containers = len(driver.find_elements(By.CSS_SELECTOR, ".option-container, .choice-option, [class*='option']"))
            
            choice_found = (radio_count + checkbox_count) >= 2 or option_containers >= 2
            
            if choice_found:
                print(f"找到选择题特征: radio={radio_count}, checkbox={checkbox_count}, options={option_containers}")
            
            return choice_found
        except Exception as e:
            print(f"检测选择题时出错: {e}")
            return False
    
    @staticmethod
    def _is_fill_blank_question(driver):
        """检测是否为填空题"""
        try:
            # 检测输入框（可能是多个）
            text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
            # 检测包含"填空"、"填写"等关键词的元素
            fill_keywords = driver.find_elements(By.XPATH, 
                "//*[contains(text(), '填空') or contains(text(), '填写') or contains(text(), '填写答案')]")
            # 检测下划线形式的填空题
            blanks = driver.find_elements(By.CSS_SELECTOR, ".blank, .fill-blank, [class*='blank']")
            
            fill_found = len(text_inputs) > 0 or len(fill_keywords) > 0 or len(blanks) > 0
            
            if fill_found:
                print(f"找到填空题特征: text_inputs={len(text_inputs)}, fill_keywords={len(fill_keywords)}, blanks={len(blanks)}")
            
            return fill_found
        except Exception as e:
            print(f"检测填空题时出错: {e}")
            return False
    
    @staticmethod
    def _is_programming_question(driver):
        """检测是否为编程题（其他特征）"""
        try:
            # 检测代码编辑器
            code_editors = driver.find_elements(By.CSS_SELECTOR, 
                ".code-editor, .monaco-editor, .ace_editor, textarea[class*='code'], [class*='editor']")
            # 检测编程题关键词
            programming_keywords = driver.find_elements(By.XPATH,
                "//*[contains(text(), '编程') or contains(text(), '代码') or contains(text(), '写程序') or contains(text(), '编写')]")
            # 检测运行/提交代码按钮
            run_buttons = driver.find_elements(By.XPATH,
                "//button[contains(text(), '运行') or contains(text(), '执行') or contains(text(), '提交代码')]")
            
            programming_found = len(code_editors) > 0 or len(programming_keywords) > 0 or len(run_buttons) > 0
            
            if programming_found:
                print(f"找到编程题特征: code_editors={len(code_editors)}, programming_keywords={len(programming_keywords)}, run_buttons={len(run_buttons)}")
            
            return programming_found
        except Exception as e:
            print(f"检测编程题时出错: {e}")
            return False
    
    @staticmethod
    def get_question_type_name(question_type):
        """获取题目类型的中文名称"""
        type_map = {
            QuestionTypeDetector.QUESTION_TYPE_CHOICE: "选择题",
            QuestionTypeDetector.QUESTION_TYPE_FILL_BLANK: "填空题",
            QuestionTypeDetector.QUESTION_TYPE_PROGRAMMING: "编程题",
            QuestionTypeDetector.QUESTION_TYPE_UNKNOWN: "未知题型"
        }
        return type_map.get(question_type, "未知题型")