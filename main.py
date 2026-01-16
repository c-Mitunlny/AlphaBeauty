from selenium import webdriver
from modules.banner import printbanners, printVideoBanners
from modules.login import login
from modules.navigation import *
from modules.question_handler import *
from modules.choice_question_handler import *
from modules.video import Vmain
import time


def main():
    printbanners()
    Browser = input("请选择您的默认浏览器或常用浏览器（无法启动请尝试选择不同浏览器）\nA.Edge(微软) B.Chrome(谷歌)\n输入选项：")
    if Browser == 'A' or Browser == 'a':
        driver = webdriver.Edge()
    elif Browser == 'B' or Browser == 'b':
        driver = webdriver.Chrome()
    else:
        print("无效的选项！")
    
    try:
        login(driver)
        
        class_name = input("你想要完成的课程名称:\nA:软件python科目\nB:软件web科目\n请选择:")
        
        if class_name.upper() == 'A':
            print("目前python仅支持视频刷课，是否启动？(y/n)")
            choice = input().lower()
            if choice in ['y', 'yes']:
                printVideoBanners()
                url = input("请输入你当前所看到的进度,PS：如果你一个都没看，那就从第一页开始吧~(ง •_•)ง\n输入视频所在页面的网址：")
                print("自动观看视频开始...请不要频繁刷新或点击页面，否则程序可能失效！")
                driver.get(url)
                pages_processed = Vmain(driver, max_pages=5000)
                print(f"成功处理了 {pages_processed} 个页面")
            else:
                print("程序结束，未启动刷课模块。")
        elif class_name.upper() == 'B':
            choose = input("请输入你想要实现的功能(1/2)\n1.完成【作业】任务(脚本会按照顺序完成所有题目)\n2.完成【课堂】任务(当前仅支持看视频)\n")
            
            if choose == '1':
                attempt_count = 0
                max_attempts = 30  # 设置最大尝试次数防止无限循环
                
                while attempt_count < max_attempts:
                    attempt_count += 1
                    print(f"\n{'='*60}")
                    print(f"第 {attempt_count} 次尝试查找作业任务...")
                    
                    try:
                        # 确保在任务页面
                        driver.get("https://tyutr.alphacoding.cn/task")
                        time.sleep(2)
                        
                        answer_button = locate_answer_button(driver, 0)
                        
                        if answer_button is None:
                            print("🎉 所有作业任务已完成！程序结束。")
                            break
                        
                        answer_button.click()
                        time.sleep(1.5)
                        
                        if click_do_homework_button(driver, 0):
                            print("开始处理作业题目...")
                            complete_all_questions_smart(driver)
                        else:
                            print("未找到做作业按钮，可能任务状态有变化")
                            time.sleep(2)
                            
                    except Exception as e:
                        print(f"处理过程中出错: {e}")
                        time.sleep(3)
                
                if attempt_count >= max_attempts:
                    print(f"已达到最大尝试次数 ({max_attempts})，程序结束")            
                    
            elif choose == '2':
                printVideoBanners()
                url = input("请输入你当前所看到的进度,PS：如果你一个都没看，那就从第一页开始吧~(ง •_•)ง\n输入视频所在页面的网址：")
                print("自动观看视频开始...请不要频繁刷新或点击页面，否则程序可能失效！")
                driver.get(url)
                pages_processed = Vmain(driver, max_pages=5000)
                print(f"成功处理了 {pages_processed} 个页面")
            else:
                print("无效的功能选择，程序结束。")
        else:
            print("无效的课程选择，程序结束。")
            
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        print("100s后自动关闭浏览器...")
        time.sleep(100)
        driver.quit()

if __name__ == "__main__":
    main()