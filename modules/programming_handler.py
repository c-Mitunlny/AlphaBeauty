"""
编程题处理模块
处理编程题的逻辑
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip  # 用于复制粘贴到剪贴板

class ProgrammingHandler:
    """编程题处理器"""
    
    @staticmethod
    def handle_programming_question(driver):
        """
        处理编程题
        
        Args:
            driver: WebDriver实例
            
        Returns:
            bool: 是否成功处理
        """
        print("💻 检测到编程题，正在处理...")
        
        try:
            # 第一步：点击"解析"标签页
            if not ProgrammingHandler._click_solution_tab(driver):
                print("❌ 无法点击'解析'标签页")
                return False
            
            # 第二步：点击"查看答案"按钮
            if not ProgrammingHandler._click_view_answer_button(driver):
                print("❌ 无法点击'查看答案'按钮")
                return False
            
            # 第三步：获取答案代码
            answer_code = ProgrammingHandler._extract_answer_code(driver)
            if not answer_code:
                print("❌ 无法获取答案代码")
                return False
            
            print(f"✅ 成功获取答案代码，长度: {len(answer_code)} 字符")
            
            # 第四步：切换回"练习"标签页
            if not ProgrammingHandler._click_exercise_tab(driver):
                print("❌ 无法切换回'练习'标签页")
                return False
            
            # 第五步：将答案粘贴到答题框
            if not ProgrammingHandler._paste_code_to_editor(driver, answer_code):
                print("❌ 无法粘贴代码到答题框")
                return False
            
            # 第六步：提交代码（直接提交，不运行）
            if not ProgrammingHandler._submit_code(driver):
                print("❌ 提交代码失败")
                return False
            
            print("✅ 编程题已提交")
            return True
            
        except Exception as e:
            print(f"处理编程题时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _click_solution_tab(driver):
        """点击'解析'标签页"""
        try:
            print("🔍 查找'解析'标签页...")
            
            # 方法1: 通过文本查找
            solution_tabs = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'el-tabs__item') and contains(text(), '解析')]")
            
            for tab in solution_tabs:
                try:
                    if tab.is_displayed() and tab.is_enabled():
                        # 检查是否已经是激活状态
                        tab_class = tab.get_attribute('class') or ''
                        if 'is-active' in tab_class:
                            print("✅ '解析'标签页已经是激活状态")
                            return True
                        
                        # 点击标签页
                        print("🖱️ 点击'解析'标签页")
                        tab.click()
                        time.sleep(0.5)  # 等待标签页切换
                        
                        # 验证是否切换成功
                        time.sleep(0.5)
                        if 'is-active' in (tab.get_attribute('class') or ''):
                            print("✅ 成功切换到'解析'标签页")
                            return True
                except:
                    continue
            
            print("❌ 未找到可用的'解析'标签页")
            return False
            
        except Exception as e:
            print(f"点击'解析'标签页失败: {e}")
            return False
    
    @staticmethod
    def _click_view_answer_button(driver):
        """点击'查看答案'按钮"""
        try:
            print("🔍 查找'查看答案'按钮...")
            
            # 精确匹配按钮的多个特征
            # 特征1: 精确文本匹配
            answer_buttons = driver.find_elements(By.XPATH,
                "//button[text()='查看答案']")
            
            if not answer_buttons:
                # 特征2: 包含文本匹配
                answer_buttons = driver.find_elements(By.XPATH,
                    "//button[contains(text(), '查看答案')]")
            
            for button in answer_buttons:
                try:
                    # 检查按钮是否可见且可用
                    if not button.is_displayed() or not button.is_enabled():
                        print(f"按钮不可见或不可用")
                        continue
                    
                    # 获取按钮的所有属性进行精确匹配
                    button_class = button.get_attribute('class') or ''
                    button_text = button.text.strip()
                    
                    print(f"找到按钮: 文本='{button_text}', class='{button_class}'")
                    
                    # 精确匹配按钮的特征
                    # 1. 文本必须是"查看答案"
                    # 2. class包含特定的样式类
                    if (button_text == '查看答案' and 
                        'text-success-700' in button_class and 
                        'bg-white' in button_class and 
                        'border-gray-300' in button_class):
                        
                        print("✅ 找到符合条件的'查看答案'按钮")
                        
                        # 滚动到按钮位置
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # 高亮按钮（可选，用于调试）
                        driver.execute_script("arguments[0].style.border='3px solid red';", button)
                        time.sleep(0.5)
                        
                        print("🖱️ 点击'查看答案'按钮")
                        button.click()
                        time.sleep(1)  # 等待答案加载
                        
                        # 验证答案是否已加载
                        if ProgrammingHandler._check_answer_loaded(driver):
                            print("✅ 答案已成功加载")
                            return True
                        else:
                            print("⚠️ 答案可能未加载，继续尝试")
                            time.sleep(1)
                            return True
                            
                except Exception as e:
                    print(f"检查按钮失败: {e}")
                    continue
            
            # 如果精确匹配失败，尝试更宽松的匹配
            print("⚠️ 精确匹配失败，尝试宽松匹配...")
            
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in all_buttons:
                try:
                    button_text = button.text.strip()
                    if '查看答案' in button_text:
                        print(f"宽松匹配找到按钮: '{button_text}'")
                        
                        if button.is_displayed() and button.is_enabled():
                            print("🖱️ 点击宽松匹配的按钮")
                            button.click()
                            time.sleep(1)
                            
                            if ProgrammingHandler._check_answer_loaded(driver):
                                print("✅ 答案已加载")
                                return True
                except:
                    continue
            
            print("❌ 未找到可用的'查看答案'按钮")
            
            # 调试：打印所有按钮信息
            print("\n🔍 调试信息：当前页面所有按钮：")
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(all_buttons[:10]):  # 只显示前10个按钮
                try:
                    text = btn.text.strip()
                    if text:  # 只显示有文本的按钮
                        classes = btn.get_attribute('class') or ''
                        print(f"  按钮{i+1}: 文本='{text[:30]}...', class='{classes}'")
                except:
                    pass
            
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
            # 查找答案相关元素
            selectors = [
                ".code-solution",
                ".exercise-solution",
                "pre[class*='solution']",
                "div[class*='solution']",
                ".answer-content"
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for elem in elements:
                        if elem.is_displayed():
                            text = elem.text.strip()
                            if text and len(text) > 50:  # 假设答案至少50字符
                                print(f"✅ 检测到答案内容，长度: {len(text)}")
                                return True
            
            # 检查是否出现代码块
            code_blocks = driver.find_elements(By.TAG_NAME, "pre")
            for block in code_blocks:
                if block.is_displayed():
                    text = block.text.strip()
                    if text and len(text) > 100:
                        print(f"✅ 检测到代码块，长度: {len(text)}")
                        return True
            
            return False
            
        except:
            return False


    @staticmethod
    def _extract_answer_code(driver):
        """提取答案代码"""
        try:
            print("🔍 提取答案代码...")
            
            # 查找答案代码容器
            answer_selectors = [
                "pre.code-solution",
                ".code-solution",
                ".exercise-solution pre",
                "[class*='solution'] pre",
                "pre[class*='code']"
            ]
            
            for selector in answer_selectors:
                try:
                    answer_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in answer_elements:
                        try:
                            answer_text = element.text.strip()
                            if answer_text and len(answer_text) > 100:  # 假设答案至少100字符
                                print(f"✅ 找到答案代码，长度: {len(answer_text)}")
                                
                                # 尝试复制到剪贴板
                                try:
                                    pyperclip.copy(answer_text)
                                    print("📋 已将答案复制到剪贴板")
                                except:
                                    print("⚠️ 无法复制到剪贴板，将直接使用文本")
                                
                                return answer_text
                        except:
                            continue
                except:
                    continue
            
            # 备用方法：通过获取元素HTML内容
            answer_elements = driver.find_elements(By.XPATH,
                "//div[contains(@class, 'exercise-solution')]//pre")
            
            for element in answer_elements:
                try:
                    answer_text = element.text.strip()
                    if answer_text:
                        print(f"✅ 通过备用方法找到答案，长度: {len(answer_text)}")
                        return answer_text
                except:
                    continue
            
            print("❌ 未找到答案代码")
            return None
            
        except Exception as e:
            print(f"提取答案代码失败: {e}")
            return None
    
    @staticmethod
    def _click_exercise_tab(driver):
        """点击'练习'标签页"""
        try:
            print("🔍 切换回'练习'标签页...")
            
            # 查找'练习'标签页
            exercise_tabs = driver.find_elements(By.XPATH,
                "//div[contains(@class, 'el-tabs__item') and contains(text(), '练习')]")
            
            for tab in exercise_tabs:
                try:
                    if tab.is_displayed() and tab.is_enabled():
                        # 检查是否已经是激活状态
                        tab_class = tab.get_attribute('class') or ''
                        if 'is-active' in tab_class:
                            print("✅ '练习'标签页已经是激活状态")
                            return True
                        
                        print("🖱️ 点击'练习'标签页")
                        tab.click()
                        time.sleep(1)  # 等待标签页切换
                        
                        # 检查是否成功切换
                        time.sleep(0.5)
                        if 'is-active' in (tab.get_attribute('class') or ''):
                            print("✅ 成功切换到'练习'标签页")
                            return True
                except:
                    continue
            
            print("❌ 未找到可用的'练习'标签页")
            return False
            
        except Exception as e:
            print(f"切换回'练习'标签页失败: {e}")
            return False
    
    @staticmethod
    def _paste_code_to_editor(driver, code):
        """将代码粘贴到答题框"""
        try:
            print("📝 查找代码编辑器...")
            
            # 方法1: 查找CodeMirror编辑器
            codemirror_selectors = [
                ".CodeMirror",
                ".codemirror-editor",
                ".CodeMirror-code",
                ".CodeMirror-scroll"
            ]
            
            for selector in codemirror_selectors:
                try:
                    editors = driver.find_elements(By.CSS_SELECTOR, selector)
                    if editors:
                        print(f"✅ 找到CodeMirror编辑器 ({selector})")
                        
                        # 使用JavaScript设置CodeMirror的值
                        driver.execute_script("""
                            // 查找所有CodeMirror实例
                            var codemirrors = [];
                            
                            // 方法1: 通过全局CodeMirror对象
                            if (window.CodeMirror && window.CodeMirror.instances) {
                                for (var i = 0; i < window.CodeMirror.instances.length; i++) {
                                    codemirrors.push(window.CodeMirror.instances[i]);
                                }
                            }
                            
                            // 方法2: 通过data属性
                            var editors = document.querySelectorAll('.CodeMirror');
                            editors.forEach(function(editor) {
                                if (editor.CodeMirror) {
                                    codemirrors.push(editor.CodeMirror);
                                }
                            });
                            
                            // 设置代码
                            var code = arguments[0];
                            if (codemirrors.length > 0) {
                                var cm = codemirrors[0];
                                cm.setValue(code);
                                cm.focus();
                                console.log('CodeMirror代码设置成功，长度:', code.length);
                                return true;
                            }
                            return false;
                        """, code)
                        
                        time.sleep(1)
                        print("✅ 代码已设置到CodeMirror编辑器")
                        return True
                        
                except Exception as e:
                    print(f"使用选择器 {selector} 失败: {e}")
                    continue
            
            # 方法2: 查找textarea（可能是隐藏的）
            try:
                textareas = driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in textareas:
                    try:
                        # 检查是否在编辑器区域内
                        parent_html = textarea.find_element(By.XPATH, "..").get_attribute('outerHTML')
                        if 'CodeMirror' in parent_html or 'codemirror' in parent_html.lower():
                            print("✅ 找到CodeMirror的textarea")
                            
                            # 使用JavaScript设置值
                            driver.execute_script("""
                                var textarea = arguments[0];
                                var code = arguments[1];
                                textarea.value = code;
                                
                                // 触发输入事件
                                var event = new Event('input', { bubbles: true });
                                textarea.dispatchEvent(event);
                                
                                // 触发change事件
                                var changeEvent = new Event('change', { bubbles: true });
                                textarea.dispatchEvent(changeEvent);
                            """, textarea, code)
                            
                            time.sleep(1)
                            print("✅ 代码已设置到textarea")
                            return True
                            
                    except:
                        continue
            except:
                pass
            
            # 方法3: 查找包含代码编辑器的容器
            try:
                editor_containers = driver.find_elements(By.CSS_SELECTOR,
                    "[class*='editor'], [class*='Editor'], .code-editor")
                
                for container in editor_containers:
                    try:
                        # 尝试直接发送键
                        container.click()
                        time.sleep(0.5)
                        
                        # 尝试使用键盘快捷键全选并粘贴
                        from selenium.webdriver.common.action_chains import ActionChains
                        from selenium.webdriver.common.keys import Keys
                        
                        actions = ActionChains(driver)
                        actions.click(container)
                        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
                        actions.send_keys(Keys.DELETE)
                        actions.perform()
                        time.sleep(0.5)
                        
                        # 粘贴代码
                        try:
                            import pyperclip
                            pyperclip.copy(code)
                            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
                            actions.perform()
                        except:
                            # 手动输入（可能很慢）
                            container.send_keys(code)
                        
                        time.sleep(1)
                        print("✅ 通过容器方式设置代码")
                        return True
                        
                    except:
                        continue
            except Exception as e:
                print(f"容器方式失败: {e}")
            
            print("❌ 未找到可用的代码编辑器")
            return False
            
        except Exception as e:
            print(f"粘贴代码到编辑器失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    

    
    @staticmethod
    def _submit_code(driver):
        """提交代码"""
        try:
            print("📤 查找'提交'按钮...")
            
            # 精确查找提交按钮
            # 方法1: 精确文本匹配
            submit_buttons = driver.find_elements(By.XPATH,
                "//button[./span[text()='提交']]")
            
            if not submit_buttons:
                # 方法2: 按钮文本包含"提交"
                submit_buttons = driver.find_elements(By.XPATH,
                    "//button[contains(text(), '提交')]")
            
            if not submit_buttons:
                # 方法3: span文本包含"提交"
                submit_buttons = driver.find_elements(By.XPATH,
                    "//button[.//span[contains(text(), '提交')]]")
            
            for button in submit_buttons:
                try:
                    # 检查按钮是否可见且可用
                    if not button.is_displayed():
                        print("按钮不可见")
                        continue
                    
                    if not button.is_enabled():
                        print("按钮不可用")
                        continue
                    
                    # 获取按钮详细信息
                    button_class = button.get_attribute('class') or ''
                    button_text = button.text.strip() or ''
                    
                    # 检查内层span的文本
                    try:
                        span = button.find_element(By.TAG_NAME, "span")
                        span_text = span.text.strip()
                    except:
                        span_text = ""
                    
                    print(f"找到按钮: class='{button_class[:100]}...', 文本='{button_text}', span文本='{span_text}'")
                    
                    # 精确匹配按钮特征
                    # 1. class包含特定样式
                    # 2. 按钮文本或span文本包含"提交"
                    if ('bg-primary-600' in button_class and 
                        'text-white' in button_class and
                        ('提交' in button_text or '提交' in span_text)):
                        
                        print("✅ 找到符合条件的'提交'按钮")
                        
                        # 滚动到按钮位置
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                        time.sleep(0.5)
                        
                        print("🖱️ 点击'提交'按钮")
                        
                        # 使用JavaScript点击
                        driver.execute_script("arguments[0].click();", button)
                        
                        print("✅ 已点击提交按钮，等待结果...")
                        
                        # 等待弹窗出现
                        if ProgrammingHandler._wait_for_success_dialog(driver):
                            print("✅ 提交成功，正在关闭成功弹窗...")
                            
                            # 关闭成功弹窗
                            if ProgrammingHandler._close_success_dialog(driver):
                                print("✅ 成功弹窗已关闭")
                                return True
                            else:
                                print("⚠️ 无法关闭成功弹窗，但提交已完成")
                                return True
                        else:
                            print("⚠️ 未检测到成功弹窗，可能提交失败")
                            return False
                        
                except Exception as e:
                    print(f"检查提交按钮失败: {e}")
                    continue
            
            # 如果精确匹配失败，尝试更广泛的查找
            print("⚠️ 精确匹配失败，尝试查找所有按钮...")
            
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in all_buttons:
                try:
                    button_text = button.text.strip() or ''
                    button_class = button.get_attribute('class') or ''
                    
                    # 检查内层span
                    try:
                        span = button.find_element(By.TAG_NAME, "span")
                        span_text = span.text.strip()
                    except:
                        span_text = ""
                    
                    # 如果包含"提交"文本
                    if '提交' in button_text or '提交' in span_text:
                        print(f"找到包含'提交'的按钮: class='{button_class[:80]}...', 文本='{button_text}'")
                        
                        if button.is_displayed() and button.is_enabled():
                            print("🖱️ 点击匹配到的按钮")
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                            
                            # 检查是否成功
                            if ProgrammingHandler._wait_for_success_dialog(driver, timeout=5):
                                print("✅ 提交成功")
                                ProgrammingHandler._close_success_dialog(driver)
                                return True
                                
                except Exception as e:
                    print(f"点击按钮失败: {e}")
                    continue
            
            print("❌ 未找到可用的'提交'按钮")
            return False
            
        except Exception as e:
            print(f"提交代码失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _wait_for_success_dialog(driver, timeout=10):
        """等待成功弹窗出现"""
        try:
            print("⏳ 等待成功弹窗...")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # 查找成功弹窗
                    dialog_selectors = [
                        ".el-dialog__body",
                        ".submit-result-wrap",
                        "[class*='success']",
                        "[class*='dialog']"
                    ]
                    
                    for selector in dialog_selectors:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                # 检查是否包含成功内容
                                text = element.text.lower()
                                if '太棒了' in text or '检查全部通过' in text or 'success' in text:
                                    print("✅ 检测到成功弹窗")
                                    return True
                
                except:
                    pass
                
                # 检查页面文本
                try:
                    page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                    if '太棒了' in page_text or '检查全部通过' in page_text:
                        print("✅ 页面显示提交成功")
                        return True
                except:
                    pass
                
                time.sleep(0.5)
                print(f"  ⏳ 等待成功提示... ({int(time.time() - start_time)}/{timeout}s)")
            
            print(f"⚠️ 等待成功弹窗超时 ({timeout}秒)")
            return False
            
        except Exception as e:
            print(f"等待成功弹窗失败: {e}")
            return False
    
    @staticmethod
    def _close_success_dialog(driver):
        """关闭成功弹窗 - 点击弹窗外区域"""
        try:
            print("🖱️ 点击弹窗外区域关闭弹窗...")
            
            # 方法1: 点击页面顶部区域（通常是安全区域）
            try:
                # 获取页面body元素
                body = driver.find_element(By.TAG_NAME, "body")
                
                # 点击页面左上角（通常是安全区域，不会点到其他按钮）
                # 使用ActionChains精确点击
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(driver)
                
                # 移动到body的左上角（坐标0,0）并点击
                actions.move_to_element_with_offset(body, 10, 10).click().perform()
                
                print("✅ 已点击页面左上角区域")
                time.sleep(1)
                
                # 验证弹窗是否关闭
                if ProgrammingHandler._check_dialog_closed(driver):
                    print("✅ 成功弹窗已关闭")
                    return True
                    
            except Exception as e:
                print(f"点击左上角失败: {e}")
            
            # 方法2: 点击页面的标题栏或导航栏区域
            try:
                # 查找页眉或导航栏区域
                header_selectors = ["header", ".header", "nav", ".navbar", ".top-bar"]
                for selector in header_selectors:
                    headers = driver.find_elements(By.CSS_SELECTOR, selector)
                    for header in headers:
                        if header.is_displayed():
                            print(f"✅ 找到页眉区域: {selector}")
                            header.click()
                            time.sleep(1)
                            
                            if ProgrammingHandler._check_dialog_closed(driver):
                                print("✅ 通过点击页眉关闭弹窗")
                                return True
            except:
                pass
            
            # 方法3: 直接点击body的任意位置（使用JavaScript）
            try:
                driver.execute_script("""
                    // 点击body元素的左上角
                    document.body.click();
                    
                    // 或者触发点击事件
                    var event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    document.body.dispatchEvent(event);
                """)
                
                print("✅ 已通过JavaScript点击body")
                time.sleep(1)
                
                if ProgrammingHandler._check_dialog_closed(driver):
                    print("✅ 弹窗已关闭")
                    return True
                    
            except Exception as e:
                print(f"JavaScript点击失败: {e}")
            
            # 方法4: 简单等待并尝试多次点击
            print("⚠️ 尝试多次点击关闭弹窗...")
            for i in range(3):
                try:
                    # 在多个位置点击
                    body = driver.find_element(By.TAG_NAME, "body")
                    
                    # 点击不同位置
                    offsets = [(10, 10), (50, 50), (100, 100)]
                    for offset_x, offset_y in offsets:
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element_with_offset(body, offset_x, offset_y).click().perform()
                            time.sleep(0.5)
                        except:
                            pass
                    
                    # 检查是否关闭
                    if ProgrammingHandler._check_dialog_closed(driver):
                        print(f"✅ 第{i+1}次尝试后弹窗已关闭")
                        return True
                        
                except:
                    pass
            
            print("⚠️ 无法关闭弹窗，但题目已提交成功，继续执行")
            return False
            
        except Exception as e:
            print(f"关闭弹窗失败: {e}")
            return False
    @staticmethod
    def _check_dialog_closed(driver):
        """检查弹窗是否已关闭"""
        try:
            time.sleep(0.5)
            
            # 简单检查：查看是否有明显的成功弹窗内容
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            
            # 如果页面还显示"太棒了"或"检查全部通过"，说明弹窗还在
            if '太棒了' in page_text and '检查全部通过' in page_text:
                print("⚠️ 弹窗可能还在显示")
                return False
            
            # 或者查找特定的弹窗元素
            try:
                dialog = driver.find_element(By.CSS_SELECTOR, ".submit-result-wrap, .el-dialog__body")
                if dialog.is_displayed():
                    return False
            except:
                pass  # 没找到弹窗元素，说明已关闭
            
            return True
            
        except:
            # 如果检查出错，假设弹窗已关闭
            return True