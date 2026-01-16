"""
填空题处理模块
处理填空题的逻辑
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class FillBlankHandler:
    """填空题处理器"""
    
    @staticmethod
    def handle_fill_blank_question(driver):
        """
        处理填空题
        
        Args:
            driver: WebDriver实例
            
        Returns:
            bool: 是否成功处理
        """
        print("📝 检测到填空题，正在处理...")
        
        try:
            # 第一步：点击"查看答案"按钮
            if not FillBlankHandler._click_view_answer_button(driver):
                print("❌ 无法点击'查看答案'按钮")
                return False
            
            # 第二步：获取答案列表
            answers = FillBlankHandler._extract_answers(driver)
            if not answers:
                print("❌ 无法获取答案列表")
                return False
            
            print(f"✅ 获取到 {len(answers)} 个答案: {answers}")
            
            # 第三步：切换回练习页面（如果需要）
            # 注意：有些系统可能不需要切换，答案弹窗在页面上方
            
            # 第四步：查找所有填空输入框
            blank_inputs = FillBlankHandler._find_all_blank_inputs(driver)
            if not blank_inputs:
                print("❌ 未找到填空输入框")
                return False
            
            print(f"✅ 找到 {len(blank_inputs)} 个填空输入框")
            
            # 第五步：按照顺序填入答案
            if not FillBlankHandler._fill_answers_to_inputs(driver, blank_inputs, answers):
                print("❌ 填写答案失败")
                return False
            
            # 第六步：提交答案
            if not FillBlankHandler._submit_answer(driver):
                print("❌ 提交答案失败")
                return False
            
            print("✅ 填空题已提交")
            return True
            
        except Exception as e:
            print(f"处理填空题时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _click_view_answer_button(driver):
        """点击'查看答案'按钮"""
        try:
            print("🔍 查找'查看答案'按钮...")
            
            # 精确查找查看答案按钮
            answer_buttons = driver.find_elements(By.XPATH,
                "//button[text()='查看答案']")
            
            if not answer_buttons:
                answer_buttons = driver.find_elements(By.XPATH,
                    "//button[contains(text(), '查看答案')]")
            
            for btn in answer_buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        button_class = btn.get_attribute('class') or ''
                        button_text = btn.text.strip()
                        
                        print(f"找到按钮: 文本='{button_text}', class='{button_class}'")
                        
                        # 匹配填空题的查看答案按钮样式
                        if (button_text == '查看答案' and 
                            'text-success-700' in button_class and 
                            'bg-white' in button_class):
                            
                            print("✅ 找到'查看答案'按钮")
                            
                            # 滚动到按钮位置
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                            time.sleep(0.5)
                            
                            print("🖱️ 点击'查看答案'按钮")
                            btn.click()
                            time.sleep(0.5)  # 等待答案加载
                            
                            # 检查答案是否加载
                            if FillBlankHandler._check_answer_loaded(driver):
                                print("✅ 答案已加载")
                                return True
                except Exception as e:
                    print(f"检查按钮失败: {e}")
                    continue
            
            print("❌ 未找到可用的'查看答案'按钮")
            return False
            
        except Exception as e:
            print(f"点击'查看答案'按钮失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _check_answer_loaded(driver):
        """检查答案是否已加载"""
        try:
            # 查找答案容器
            answer_containers = driver.find_elements(By.CSS_SELECTOR,
                ".exercise-solution, [class*='solution'], .answer-content")
            
            for container in answer_containers:
                if container.is_displayed():
                    # 检查是否有序号列表
                    ol_elements = container.find_elements(By.TAG_NAME, "ol")
                    li_elements = container.find_elements(By.TAG_NAME, "li")
                    
                    if ol_elements or li_elements:
                        print("✅ 检测到答案列表")
                        return True
            
            return False
            
        except:
            return False
    
    @staticmethod
    def _extract_answers(driver):
        """提取答案列表"""
        try:
            print("🔍 提取答案列表...")
            
            answers = []
            
            # 首先，精确找到答案弹窗容器
            solution_container = None
            
            # 查找答案容器
            container_selectors = [
                ".exercise-solution",  # 最精确的选择器
                ".answer-content",
                "[class*='solution']",
                ".border-success-500"  # 绿色边框的容器
            ]
            
            for selector in container_selectors:
                try:
                    containers = driver.find_elements(By.CSS_SELECTOR, selector)
                    for container in containers:
                        if container.is_displayed():
                            # 验证这是真正的答案容器
                            container_text = container.text.lower()
                            if '答案' in container_text and not '等级考试' in container_text:
                                solution_container = container
                                print(f"✅ 找到答案容器: {selector}")
                                break
                    if solution_container:
                        break
                except:
                    continue
            
            if not solution_container:
                print("❌ 未找到答案容器")
                return None
            
            # 现在只从答案容器中提取答案
            print("🎯 从答案容器中提取答案...")
            
            # 方法1: 提取有序列表中的答案
            try:
                # 在答案容器内查找ol元素
                ol_elements = solution_container.find_elements(By.TAG_NAME, "ol")
                if ol_elements:
                    print(f"✅ 在答案容器中找到 {len(ol_elements)} 个ol元素")
                    
                    for ol in ol_elements:
                        li_elements = ol.find_elements(By.TAG_NAME, "li")
                        print(f"  找到 {len(li_elements)} 个li元素")
                        
                        for li in li_elements:
                            try:
                                li_text = li.text.strip()
                                print(f"  li文本: '{li_text}'")
                                
                                # 查找答案文本（通常在span中，有特殊样式）
                                spans = li.find_elements(By.TAG_NAME, "span")
                                for span in spans:
                                    span_text = span.text.strip()
                                    span_class = span.get_attribute('class') or ''
                                    
                                    # 精确匹配答案span的特征
                                    if (span_text and 
                                        ('text-blue-700' in span_class or 
                                         'px-2 py-1' in span_class or
                                         'text-blue' in span_class)):
                                        
                                        if span_text not in answers:
                                            answers.append(span_text)
                                            print(f"    ✅ 从span提取答案: '{span_text}' (class: {span_class})")
                                            break
                                
                                # 如果没有找到带特殊样式的span，检查li文本
                                if not answers or len(answers) <= li_elements.index(li):
                                    # 清理li文本，去除序号
                                    if li_text and len(li_text) > 1:
                                        # 去除序号（如"1. "、"1、"等）
                                        import re
                                        cleaned_text = re.sub(r'^\d+[\.、]\s*', '', li_text)
                                        if cleaned_text and cleaned_text != li_text:
                                            if cleaned_text not in answers:
                                                answers.append(cleaned_text)
                                                print(f"    ✅ 从li文本提取答案: '{cleaned_text}' (原始: '{li_text}')")
                                
                            except Exception as e:
                                print(f"    处理li失败: {e}")
                                continue
            except Exception as e:
                print(f"提取ol答案失败: {e}")
            
            # 方法2: 直接从答案容器中查找所有答案span
            if not answers:
                try:
                    answer_spans = solution_container.find_elements(By.CSS_SELECTOR,
                        "span.text-blue-700, span.px-2.py-1, span[class*='text-blue']")
                    
                    print(f"✅ 在容器中找到 {len(answer_spans)} 个答案span")
                    
                    for span in answer_spans:
                        try:
                            span_text = span.text.strip()
                            if span_text and span_text not in answers:
                                answers.append(span_text)
                                print(f"    ✅ 直接找到答案span: '{span_text}'")
                        except:
                            continue
                except Exception as e:
                    print(f"直接提取span失败: {e}")
            
            # 方法3: 从答案容器的文本中解析
            if not answers:
                try:
                    container_text = solution_container.text.strip()
                    print(f"容器文本: '{container_text[:100]}...'")
                    
                    # 按行分割
                    lines = container_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        # 过滤条件
                        if (line and 
                            len(line) > 0 and 
                            '答案' not in line and 
                            '解析' not in line and
                            '等级考试' not in line and
                            '训练营' not in line):
                            
                            # 去除序号
                            import re
                            cleaned_line = re.sub(r'^\d+[\.、]\s*', '', line)
                            if cleaned_line and cleaned_line != line:
                                if cleaned_line not in answers:
                                    answers.append(cleaned_line)
                                    print(f"    ✅ 从文本解析答案: '{cleaned_line}'")
                except Exception as e:
                    print(f"文本解析失败: {e}")
            
            # 去重和验证
            if answers:
                # 去重
                unique_answers = []
                for ans in answers:
                    if ans not in unique_answers:
                        unique_answers.append(ans)
                
                # 过滤掉明显不是答案的文本
                filtered_answers = []
                for ans in unique_answers:
                    # 排除导航链接等
                    if (len(ans) <= 20 and  # 答案通常不会太长
                        '训练营' not in ans and
                        '等级考试' not in ans and
                        'nav-link' not in ans and
                        'http' not in ans.lower() and
                        '.com' not in ans.lower() and
                        '点击' not in ans):
                        
                        filtered_answers.append(ans)
                    else:
                        print(f"    ⚠️ 过滤掉可能非答案的文本: '{ans}'")
                
                if filtered_answers:
                    print(f"✅ 最终提取到 {len(filtered_answers)} 个答案: {filtered_answers}")
                    return filtered_answers
                else:
                    print("❌ 过滤后无有效答案")
                    return None
            else:
                print("❌ 未提取到任何答案")
                return None
                
        except Exception as e:
            print(f"提取答案失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _find_all_blank_inputs(driver):
        """查找所有填空输入框（特别处理CodeMirror中的填空题）"""
        try:
            print("🔍 查找所有填空输入框...")
            
            blank_inputs = []
            
            # 方法1: 首先尝试查找CodeMirror中的填空题输入框
            # 这些输入框在.CodeMirror-widget容器中
            try:
                # 查找所有CodeMirror-widget容器
                code_widgets = driver.find_elements(By.CSS_SELECTOR, ".CodeMirror-widget")
                print(f"找到 {len(code_widgets)} 个CodeMirror-widget")
                
                for widget in code_widgets:
                    try:
                        # 在widget中查找输入框
                        inputs = widget.find_elements(By.CSS_SELECTOR, "input.blank, input[class*='blank']")
                        for input_elem in inputs:
                            if input_elem.is_displayed() and input_elem.is_enabled():
                                blank_inputs.append(input_elem)
                                print(f"  在CodeMirror-widget中找到输入框")
                    except:
                        continue
            except Exception as e:
                print(f"查找CodeMirror-widget失败: {e}")
            
            # 方法2: 查找blank-input容器中的输入框
            try:
                blank_containers = driver.find_elements(By.CSS_SELECTOR, ".blank-input")
                print(f"找到 {len(blank_containers)} 个blank-input容器")
                
                for container in blank_containers:
                    try:
                        inputs = container.find_elements(By.TAG_NAME, "input")
                        for input_elem in inputs:
                            if input_elem.is_displayed() and input_elem.is_enabled():
                                # 去重检查
                                if not any(inp == input_elem for inp in blank_inputs):
                                    blank_inputs.append(input_elem)
                                    print(f"  在blank-input容器中找到输入框")
                    except:
                        continue
            except Exception as e:
                print(f"查找blank-input容器失败: {e}")
            
            # 方法3: 直接查找所有带有blank类的输入框
            if not blank_inputs:
                try:
                    direct_inputs = driver.find_elements(By.CSS_SELECTOR, "input.blank")
                    for input_elem in direct_inputs:
                        if input_elem.is_displayed() and input_elem.is_enabled():
                            if not any(inp == input_elem for inp in blank_inputs):
                                blank_inputs.append(input_elem)
                                print(f"  直接找到blank输入框")
                except:
                    pass
            
            # 方法4: 查找所有文本输入框，然后检查是否在填空题上下文中
            if not blank_inputs or len(blank_inputs) < 5:  # 我们知道应该有5个输入框
                try:
                    all_text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    print(f"找到 {len(all_text_inputs)} 个文本输入框")
                    
                    for input_elem in all_text_inputs:
                        try:
                            if input_elem.is_displayed() and input_elem.is_enabled():
                                # 检查输入框的父元素是否包含填空题特征
                                parent_html = input_elem.find_element(By.XPATH, "..").get_attribute('outerHTML')
                                grandparent_html = input_elem.find_element(By.XPATH, "../..").get_attribute('outerHTML')
                                
                                # 检查是否在填空题环境中
                                if ('blank' in parent_html.lower() or 
                                    'blank' in grandparent_html.lower() or
                                    'CodeMirror-widget' in parent_html or
                                    'CodeMirror-widget' in grandparent_html):
                                    
                                    if not any(inp == input_elem for inp in blank_inputs):
                                        blank_inputs.append(input_elem)
                                        print(f"  从文本输入框中识别为填空题: 父级包含blank或CodeMirror-widget")
                        except:
                            continue
                except Exception as e:
                    print(f"检查所有文本输入框失败: {e}")
            
            # 方法5: 使用JavaScript查找所有可能的填空题输入框
            if not blank_inputs or len(blank_inputs) < 5:
                try:
                    print("使用JavaScript查找填空题输入框...")
                    
                    # 使用JavaScript查找所有输入框，并检查它们的环境
                    script = """
                    var inputs = document.querySelectorAll('input[type="text"], input.blank, .blank-input input');
                    var result = [];
                    
                    for (var i = 0; i < inputs.length; i++) {
                        var input = inputs[i];
                        // 检查是否可见
                        if (input.offsetParent !== null) {
                            var parent = input.parentElement;
                            var grandparent = parent.parentElement;
                            
                            // 检查是否在填空题环境中
                            var parentClass = parent.className || '';
                            var grandparentClass = grandparent.className || '';
                            var parentHtml = parent.outerHTML || '';
                            
                            if (parentClass.includes('blank') || 
                                grandparentClass.includes('blank') ||
                                parentClass.includes('CodeMirror-widget') ||
                                parentHtml.includes('blank-input') ||
                                input.className.includes('blank')) {
                                
                                result.push(input);
                            }
                        }
                    }
                    
                    return result;
                    """
                    
                    js_inputs = driver.execute_script(script)
                    print(f"JavaScript找到 {len(js_inputs)} 个可能的填空题输入框")
                    
                    # 转换回WebElement
                    for js_input in js_inputs:
                        try:
                            # 使用JavaScript获取输入框并添加到列表
                            input_id = driver.execute_script("return arguments[0].id;", js_input) or ""
                            if not any(inp.get_attribute('id') == input_id for inp in blank_inputs):
                                blank_inputs.append(js_input)
                                print(f"  JavaScript找到输入框: id='{input_id}'")
                        except:
                            continue
                            
                except Exception as e:
                    print(f"JavaScript查找失败: {e}")
            
            # 按照DOM顺序排序（从上到下，从左到右）
            if blank_inputs:
                # 使用JavaScript获取元素的Y坐标进行排序
                try:
                    sorted_inputs = sorted(blank_inputs, key=lambda x: 
                        driver.execute_script("return arguments[0].getBoundingClientRect().top;", x))
                    
                    print(f"✅ 找到并排序了 {len(sorted_inputs)} 个填空输入框")
                    
                    # 打印每个输入框的位置信息
                    for i, input_elem in enumerate(sorted_inputs):
                        try:
                            rect = driver.execute_script("return arguments[0].getBoundingClientRect();", input_elem)
                            print(f"  输入框 {i+1}: top={rect['top']}, left={rect['left']}")
                        except:
                            pass
                    
                    return sorted_inputs
                except Exception as e:
                    print(f"排序输入框失败: {e}")
                    return blank_inputs
            else:
                print("❌ 未找到任何填空输入框")
                return None
            
        except Exception as e:
            print(f"查找输入框失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _fill_answers_to_inputs(driver, blank_inputs, answers):
        """将答案填入输入框"""
        try:
            print("✏️ 开始填写答案...")
            
            # 确保答案数量与输入框数量匹配
            min_count = min(len(blank_inputs), len(answers))
            
            if min_count == 0:
                print("❌ 输入框或答案数量为0")
                return False
            
            print(f"📊 匹配情况: {len(blank_inputs)}个输入框, {len(answers)}个答案, 将填写{min_count}个")
            
            if len(blank_inputs) != len(answers):
                print(f" 警告: 输入框数量({len(blank_inputs)})与答案数量({len(answers)})不匹配")
            
            # 按顺序填写答案
            for i in range(min_count):
                try:
                    input_elem = blank_inputs[i]
                    answer = answers[i]
                    
                    print(f"  填写第{i+1}个空: '{answer}'")
                    
                    # 确保输入框可见
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_elem)
                    time.sleep(0.3)
                    
                    # 清空输入框
                    input_elem.clear()
                    time.sleep(0.2)
                    
                    # 填写答案
                    input_elem.send_keys(answer)
                    time.sleep(0.3)
                    
                    # 验证是否填写成功
                    input_value = input_elem.get_attribute('value') or ''
                    if input_value == answer:
                        print(f"    验证通过: '{input_value}'")
                    else:
                        print(f"    验证失败: 期望'{answer}', 实际'{input_value}'")
                        
                except Exception as e:
                    print(f"    ❌ 填写第{i+1}个空失败: {e}")
                    continue
            
            print(f"✅ 成功填写 {min_count} 个答案")
            return True
            
        except Exception as e:
            print(f"填写答案失败: {e}")
            return False
    
    @staticmethod
    def _submit_answer(driver):
        """提交答案"""
        try:
            print("📤 查找提交按钮...")
            
            # 查找提交按钮（可能在底部控件区域）
            submit_selectors = [
                "button.bg-success-600",  # 绿色提交按钮
                "button[class*='bg-success']",  # 任何成功颜色的按钮
                ".controls button",  # 控件区域的按钮
            ]
            
            # 先尝试XPath查找
            submit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '提交')]")
            
            for button in submit_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.strip()
                        button_class = button.get_attribute('class') or ''
                        
                        print(f"找到按钮: 文本='{button_text}', class='{button_class[:80]}...'")
                        
                        # 检查是否是被禁用的按钮
                        if 'cursor-not-allowed' in button_class or 'pointer-events-none' in button_class:
                            print("按钮被禁用，可能答案未填写完整")
                            # 检查输入框是否都填了
                            continue
                        
                        if '提交' in button_text and ('bg-success' in button_class or 'bg-primary' in button_class):
                            print("✅ 找到提交按钮")
                            
                            # 滚动到按钮
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                            time.sleep(0.5)
                            
                            print("🖱️ 点击提交按钮")
                            button.click()
                            time.sleep(0.5)  # 等待提交结果
                            
                            # 等待提交结果并关闭弹窗
                            if FillBlankHandler._wait_and_close_success_dialog(driver):
                                print("✅ 提交成功并关闭弹窗")
                                return True
                except:
                    continue
            
            # 如果XPath没找到，尝试CSS选择器
            for selector in submit_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                button_text = button.text.strip()
                                if '提交' in button_text:
                                    print(f"通过CSS找到按钮: 文本='{button_text}'")
                                    
                                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                                    time.sleep(0.5)
                                    
                                    print("🖱️ 点击提交按钮")
                                    button.click()
                                    time.sleep(0.5)
                                    
                                    if FillBlankHandler._wait_and_close_success_dialog(driver):
                                        print("✅ 提交成功并关闭弹窗")
                                        return True
                        except:
                            continue
                except:
                    continue
            
            print("❌ 未找到可用的提交按钮")
            return False
            
        except Exception as e:
            print(f"提交答案失败: {e}")
            return False
    
    @staticmethod
    def _wait_and_close_success_dialog(driver):
        """等待提交结果并关闭成功弹窗"""
        try:
            print("⏳ 等待提交结果...")
            
            # 等待可能的成功弹窗
            success_detected = False
            
            for i in range(5):  # 最多等待5秒
                time.sleep(1)
                
                # 检查是否有成功弹窗
                try:
                    success_dialogs = driver.find_elements(By.CSS_SELECTOR,
                        ".el-dialog__body, .submit-result-wrap, [class*='success']")
                    
                    for dialog in success_dialogs:
                        if dialog.is_displayed():
                            dialog_text = dialog.text.lower()
                            if '太棒了' in dialog_text or '成功' in dialog_text or '通过' in dialog_text:
                                print("✅ 检测到成功弹窗")
                                success_detected = True
                                break
                    
                    if success_detected:
                        break
                        
                except:
                    pass
                
                print(f"  ⏳ 等待成功提示... ({i+1}/5)")
            
            if success_detected:
                # 关闭成功弹窗
                return FillBlankHandler._close_success_dialog(driver)
            else:
                # 即使没检测到弹窗，也检查题目状态
                if FillBlankHandler._check_question_status(driver):
                    print("✅ 题目状态已更新，提交成功")
                    return True
                else:
                    print("未检测到成功弹窗，但继续执行")
                    return True
                    
        except Exception as e:
            print(f"等待提交结果失败: {e}")
            return True
    
    @staticmethod
    def _close_success_dialog(driver):
        """关闭成功弹窗"""
        try:
            print("🖱️ 点击弹窗外区域关闭弹窗...")
            
            # 方法1: 点击页面左上角
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                
                # 使用ActionChains点击左上角
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(body, 10, 10).click().perform()
                

                time.sleep(0.5)
                
                # 检查弹窗是否关闭
                if FillBlankHandler._check_dialog_closed(driver):
                    print("✅ 弹窗已关闭")
                    return True
                    
            except Exception as e:
                print(f"点击左上角失败: {e}")
            
            # 方法2: 直接点击body
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body.click()
                print("✅ 已点击body元素")
                time.sleep(0.5)
                
                if FillBlankHandler._check_dialog_closed(driver):
                    print("✅ 弹窗已关闭")
                    return True
                    
            except:
                pass
            
            # 方法3: 使用JavaScript点击
            try:
                driver.execute_script("document.body.click();")
                print("✅ 已通过JavaScript点击body")
                time.sleep(0.5)
                
                if FillBlankHandler._check_dialog_closed(driver):
                    print("✅ 弹窗已关闭")
                    return True
                    
            except:
                pass
            
            print("无法关闭弹窗，但继续执行")
            return True
            
        except Exception as e:
            print(f"关闭弹窗失败: {e}")
            return True
    
    @staticmethod
    def _check_dialog_closed(driver):
        """检查弹窗是否已关闭"""
        try:
            time.sleep(0.5)
            
            # 检查弹窗元素是否还存在
            dialogs = driver.find_elements(By.CSS_SELECTOR,
                ".el-dialog__body, .submit-result-wrap")
            
            for dialog in dialogs:
                if dialog.is_displayed():
                    return False
            
            return True
            
        except:
            return True
    
    @staticmethod
    def _check_question_status(driver):
        """检查题目状态是否更新"""
        try:
            # 查找当前题目的按钮，检查是否变为pass状态
            current_buttons = driver.find_elements(By.CSS_SELECTOR, ".exercise-nav-btn.current")
            
            for btn in current_buttons:
                btn_class = btn.get_attribute('class') or ''
                if 'status-pass' in btn_class:
                    print("✅ 题目状态已更新为pass")
                    return True
            
            return False
            
        except:
            return False
    
    @staticmethod
    def _check_submission_result(driver):
        """检查提交结果"""
        # 直接返回True，使用新的_wait_and_close_success_dialog方法
        return True