"""
video.py - 自动视频播放与翻页模块
简化版：仅包含视频检测、播放和翻页功能
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoPlayer:
    def __init__(self, driver, wait_timeout=30):
        """
        初始化视频播放器
        
        Args:
            driver: Selenium WebDriver 实例
            wait_timeout: 等待超时时间（秒）
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.target_speed = "2x"  # 目标倍速
        self.completion_threshold = 0.5  # 50%即认为播放完成
        
    def has_video_element(self):
        """检测页面是否存在视频元素"""
        try:
            # 查找video标签
            video_elements = self.driver.find_elements(By.TAG_NAME, 'video')
            if video_elements:
                logger.info(f"找到 {len(video_elements)} 个video元素")
                return True
                
            # 查找iframe中的视频
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if any(video_keyword in src.lower() for video_keyword in 
                      ['youtube', 'vimeo', 'video', 'player', 'stream']):
                    logger.info("找到视频iframe")
                    return True
                    
        except Exception as e:
            logger.error(f"检测视频元素时出错: {e}")
            
        logger.info("未检测到视频元素")
        return False
    
    def find_and_click_speed_button(self, retry_count=3):
        """
        查找并点击2倍速按钮
        
        Args:
            retry_count: 重试次数
        
        Returns:
            bool: 是否成功点击
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"尝试查找2倍速按钮 (第{attempt+1}次尝试)")
                
                # 查找倍速选择器（根据提供的HTML结构）
                speed_selectors = [
                    # 根据提供的HTML结构查找
                    ".el-radio-group .el-radio-button input[value='2x']",
                    f".el-radio-group .el-radio-button input[value='{self.target_speed}']",
                    ".el-radio-group label.el-radio-button:nth-child(4)",  # 第四个是2x按钮
                    "label.el-radio-button:has(input[value='2x'])",
                    ".el-radio-button__inner:contains('2x')"
                ]
                
                for selector in speed_selectors:
                    try:
                        # 先尝试通过CSS选择器查找
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            try:
                                # 确保元素可见
                                if element.is_displayed():
                                    # 如果是input，找到其父级label并点击
                                    if element.get_attribute('type') == 'radio':
                                        label = self.driver.execute_script(
                                            "return arguments[0].closest('label.el-radio-button');", 
                                            element
                                        )
                                        if label:
                                            label.click()
                                            logger.info(f"成功点击2倍速按钮 (选择器: {selector})")
                                            return True
                                    else:
                                        # 直接点击元素
                                        element.click()
                                        logger.info(f"成功点击2倍速按钮 (选择器: {selector})")
                                        return True
                            except StaleElementReferenceException:
                                continue
                    except Exception as e:
                        logger.debug(f"选择器 {selector} 查找失败: {e}")
                
                # 通过XPath查找
                xpaths = [
                    f"//input[@value='{self.target_speed}']",
                    f"//label[.//span[contains(text(), '{self.target_speed}')]]",
                    f"//label[.//span[text()='{self.target_speed}']]",
                    f"//span[contains(@class, 'el-radio-button__inner') and text()='{self.target_speed}']"
                ]
                
                for xpath in xpaths:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            try:
                                if element.is_displayed():
                                    element.click()
                                    logger.info(f"成功点击2倍速按钮 (XPath: {xpath})")
                                    return True
                            except StaleElementReferenceException:
                                continue
                    except Exception as e:
                        logger.debug(f"XPath {xpath} 查找失败: {e}")
                
                # 如果没找到，等待一下再重试
                if attempt < retry_count - 1:
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"查找倍速按钮时出错: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2)
        
        logger.warning(f"未找到2倍速按钮，已重试{retry_count}次")
        return False
    
    def wait_for_video_to_start(self, timeout=10):
        """
        等待视频开始播放
        
        Args:
            timeout: 等待超时时间（秒）
        
        Returns:
            bool: 视频是否开始播放
        """
        start_time = time.time()
        logger.info("等待视频开始播放...(或请手动点击开始播放)")
        
        while time.time() - start_time < timeout:
            try:
                videos = self.driver.find_elements(By.TAG_NAME, 'video')
                for video in videos:
                    try:
                        current_time = self.driver.execute_script(
                            "return arguments[0].currentTime;", video
                        )
                        # 检查视频是否在播放（currentTime > 0）
                        if current_time > 0:
                            logger.info("视频已开始播放")
                            return True
                    except:
                        continue
                
                # 检查播放状态
                for video in videos:
                    try:
                        paused = self.driver.execute_script(
                            "return arguments[0].paused;", video
                        )
                        if not paused:
                            logger.info("视频正在播放中")
                            return True
                    except:
                        continue
                        
                time.sleep(1)
                
            except Exception as e:
                logger.debug(f"检查视频播放状态时出错: {e}")
                time.sleep(1)
        
        logger.warning("视频未能开始播放")
        return False
    
    def play_video(self):
        """尝试播放视频"""
        try:
            # 首先尝试查找video标签并播放
            video_elements = self.driver.find_elements(By.TAG_NAME, 'video')
            for video in video_elements:
                try:
                    if video.is_displayed():
                        # 使用JavaScript播放视频
                        self.driver.execute_script("arguments[0].play();", video)
                        logger.info("通过JavaScript播放视频")
                        
                        # 等待视频开始播放
                        if self.wait_for_video_to_start():
                            # 视频开始后设置倍速
                            time.sleep(1)  # 短暂等待确保播放器完全加载
                            if self.find_and_click_speed_button():
                                logger.info("成功设置2倍速")
                            else:
                                logger.warning("设置2倍速失败，继续播放")
                        
                        return True
                except Exception as e:
                    logger.error(f"播放video元素失败: {e}")
                    continue
                    
            # 尝试点击播放按钮
            play_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                'button[title*="Play"], button[title*="播放"], .play-button, .vjs-play-button')
            
            for button in play_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        logger.info("点击视频播放按钮")
                        
                        # 等待视频开始播放
                        if self.wait_for_video_to_start():
                            # 视频开始后设置倍速
                            time.sleep(1)  # 短暂等待确保播放器完全加载
                            if self.find_and_click_speed_button():
                                logger.info("成功设置2倍速")
                            else:
                                logger.warning("设置2倍速失败，继续播放")
                        
                        return True
                except Exception as e:
                    logger.error(f"点击播放按钮失败: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"播放视频时出错: {e}")
            
        logger.warning("无法播放视频")
        return False
    
    def wait_for_video_completion(self, timeout=300):
        """
        等待视频播放完成（播放到50%即认为完成）
        
        Args:
            timeout: 最大等待时间（秒）
        """
        start_time = time.time()
        logger.info("开始监控视频播放进度（50%完成）")
        
        last_progress = 0
        
        while time.time() - start_time < timeout:
            try:
                # 检查视频是否结束
                videos = self.driver.find_elements(By.TAG_NAME, 'video')
                for video in videos:
                    try:
                        # 检查播放进度
                        current_time = self.driver.execute_script(
                            "return arguments[0].currentTime;", video
                        )
                        duration = self.driver.execute_script(
                            "return arguments[0].duration;", video
                        )
                        
                        if duration > 0:
                            progress = current_time / duration
                            
                            # 每10%打印一次进度（但只关心0-50%的部分）
                            current_percent = int(progress * 100)
                            if current_percent > last_progress and current_percent % 10 == 0:
                                logger.info(f"视频播放进度: {current_percent}%")
                                last_progress = current_percent
                            
                            # 达到50%即认为完成
                            if progress >= self.completion_threshold:
                                logger.info(f"视频播放达到{self.completion_threshold*100}%，视为完成")
                                return True
                                
                            # 如果视频已经结束，也视为完成
                            ended = self.driver.execute_script(
                                "return arguments[0].ended;", video
                            )
                            if ended:
                                logger.info("视频自然结束")
                                return True
                                
                    except Exception as e:
                        logger.debug(f"获取视频进度失败: {e}")
                        continue
                
                # 短暂等待后继续检查
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"监控视频播放时出错: {e}")
                time.sleep(3)
                
        logger.warning(f"视频播放超时（{timeout}秒）")
        return False
    
    def click_next_button(self):
        """点击下一页按钮"""
        try:
            # 根据提供的HTML结构定位下一页按钮
            # 查找包含fa-chevron-right图标的按钮
            next_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'border') and .//i[contains(@class, 'fa-chevron-right')]]")
                )
            )
            
            # 确保按钮在course-navigations-buttons容器内
            parent_div = next_button.find_element(By.XPATH, "..")
            if 'course-navigations-buttons' in parent_div.get_attribute('class'):
                next_button.click()
                logger.info("成功点击下一页按钮")
                return True
                
        except TimeoutException:
            logger.warning("未找到下一页按钮，尝试备用定位方式")
            
        # 备用定位方式：直接通过CSS选择器
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "div.course-navigations-buttons > button")
            
            # 最后一个按钮应该是下一页按钮
            if len(buttons) >= 3:
                next_btn = buttons[2]  # 第三个按钮是下一页
                if next_btn.is_displayed() and next_btn.is_enabled():
                    next_btn.click()
                    logger.info("通过备用方式点击下一页按钮")
                    return True
                    
        except Exception as e:
            logger.error(f"点击下一页按钮失败: {e}")
            
        return False
    
    def process_page(self):
        """处理当前页面"""
        logger.info("开始处理页面")
        
        # 检查是否有视频
        if self.has_video_element():
            logger.info("检测到视频，尝试播放")
            
            # 尝试播放视频（会自动设置2倍速）
            if self.play_video():
                # 等待视频播放到50%
                self.wait_for_video_completion()
                logger.info("视频播放到50%，准备翻页")
            else:
                logger.warning("无法播放视频，继续处理")
        else:
            logger.info("页面无视频，直接翻页")
        
        # 点击下一页
        if self.click_next_button():
            logger.info("成功翻页")
            # 等待页面加载
            time.sleep(2)
            return True
        else:
            logger.error("无法点击下一页按钮")
            return False


def Vmain(driver, max_pages=1000):
    """
    主函数 - 连续处理多个页面
    
    Args:
        driver: Selenium WebDriver 实例（由主程序提供）
        max_pages: 最大处理页面数量
    
    Returns:
        int: 成功处理的页面数量
    """
    logger.info("开始自动视频播放与翻页流程（2倍速，50%完成）")
    
    player = VideoPlayer(driver)
    pages_processed = 0
    
    for page_num in range(1, max_pages + 1):
        logger.info(f"处理第 {page_num} 页")
        
        try:
            # 处理当前页面
            if player.process_page():
                pages_processed += 1
            else:
                logger.warning(f"第 {page_num} 页处理失败")
                break
                
            # 短暂等待页面稳定
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("用户中断操作")
            break
        except Exception as e:
            logger.error(f"处理页面时发生错误: {e}")
            break
    
    logger.info(f"处理完成，共处理 {pages_processed} 页")
    return pages_processed