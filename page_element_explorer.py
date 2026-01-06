from selenium.webdriver.common.by import By

def explore_all_page_elements(driver, max_elements=100):
    """
    探索页面所有元素结构，不分类别
    
    Args:
        driver: WebDriver实例
        max_elements: 最大显示元素数量（避免输出过长）
    
    Returns:
        list: 所有元素信息
    """
    print("=" * 60)
    print("页面所有元素结构探索")
    print("=" * 60)
    
    all_elements_info = []
    
    try:
        # 获取页面所有元素
        print("正在扫描页面元素...")
        all_elements = driver.find_elements(By.XPATH, "//*")
        total_elements = len(all_elements)
        print(f"\n页面总元素数量: {total_elements}")
        
        # 遍历元素
        print("\n" + "=" * 100)
        print(f"{'序号':<6} {'标签':<10} {'ID':<20} {'Class':<30} {'文本(前50字符)':<50}")
        print("=" * 100)
        
        for i, elem in enumerate(all_elements[:max_elements]):
            try:
                # 获取元素基本信息
                tag_name = elem.tag_name
                elem_id = elem.get_attribute('id') or ''
                elem_class = elem.get_attribute('class') or ''
                
                # 获取文本（截断避免太长）
                try:
                    elem_text = elem.text.strip()
                    if len(elem_text) > 50:
                        elem_text = elem_text[:50] + "..."
                except:
                    elem_text = "[无法获取文本]"
                
                # 收集信息
                element_info = {
                    'index': i,
                    'tag': tag_name,
                    'id': elem_id,
                    'class': elem_class,
                    'text': elem_text,
                    'element': elem
                }
                all_elements_info.append(element_info)
                
                # 打印信息
                print(f"{i:<6} {tag_name:<10} {elem_id:<20} {elem_class[:28]:<30} {elem_text:<50}")
                
            except Exception as e:
                print(f"{i:<6} [错误] 无法获取元素信息: {e}")
        
        # 如果元素超过最大显示数量，显示统计
        if total_elements > max_elements:
            print(f"\n... 已显示前 {max_elements} 个元素，共 {total_elements} 个元素")
        
        # 按标签类型统计
        print("\n" + "=" * 60)
        print("元素按标签类型统计:")
        print("-" * 60)
        
        tag_stats = {}
        for info in all_elements_info:
            tag = info['tag']
            tag_stats[tag] = tag_stats.get(tag, 0) + 1
        
        # 按数量排序
        sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)
        
        for tag, count in sorted_tags[:20]:  # 显示前20种标签
            print(f"{tag:<10}: {count:>4} 个 ({count/total_elements*100:.1f}%)")
        
        # 统计有ID的元素
        elements_with_id = sum(1 for info in all_elements_info if info['id'])
        print(f"\n有ID的元素: {elements_with_id} 个 ({elements_with_id/total_elements*100:.1f}%)")
        
        # 统计有Class的元素
        elements_with_class = sum(1 for info in all_elements_info if info['class'])
        print(f"有Class的元素: {elements_with_class} 个 ({elements_with_class/total_elements*100:.1f}%)")
        
        # 统计有文本的元素
        elements_with_text = sum(1 for info in all_elements_info if info['text'] and info['text'] != "[无法获取文本]")
        print(f"有文本内容的元素: {elements_with_text} 个 ({elements_with_text/total_elements*100:.1f}%)")
        
        # 查找重要元素
        print("\n" + "=" * 60)
        print("重要元素查找结果:")
        print("-" * 60)
        
        # 查找按钮元素
        buttons = [info for info in all_elements_info if info['tag'] == 'button']
        print(f"按钮元素: {len(buttons)} 个")
        if buttons:
            print("按钮示例:")
            for btn in buttons[:5]:  # 显示前5个按钮
                print(f"  按钮{btn['index']}: class='{btn['class']}', text='{btn['text']}'")
        
        # 查找输入框
        inputs = [info for info in all_elements_info if info['tag'] in ['input', 'textarea']]
        print(f"\n输入框元素: {len(inputs)} 个")
        if inputs:
            print("输入框示例:")
            for inp in inputs[:3]:
                inp_type = inp['element'].get_attribute('type') if inp['tag'] == 'input' else 'textarea'
                print(f"  {inp['tag']}{inp['index']}: type='{inp_type}', class='{inp['class']}'")
        
        # 查找链接
        links = [info for info in all_elements_info if info['tag'] == 'a']
        print(f"\n链接元素: {len(links)} 个")
        if links:
            print("链接示例:")
            for link in links[:3]:
                href = link['element'].get_attribute('href') or ''
                if len(href) > 50:
                    href = href[:50] + "..."
                print(f"  链接{link['index']}: href='{href}', text='{link['text']}'")
        
        # 查找可能的选择题选项
        print("\n" + "=" * 60)
        print("可能的选择题相关元素:")
        print("-" * 60)
        
        # 查找选项相关元素
        option_keywords = ['option', 'choice', 'select', 'radio', 'checkbox']
        option_elements = []
        
        for info in all_elements_info:
            class_lower = info['class'].lower()
            text_lower = info['text'].lower()
            
            for keyword in option_keywords:
                if keyword in class_lower or keyword in text_lower:
                    option_elements.append(info)
                    break
        
        print(f"找到 {len(option_elements)} 个可能的选择题相关元素")
        if option_elements:
            for opt in option_elements[:10]:  # 显示前10个
                print(f"  元素{opt['index']} [{opt['tag']}]: class='{opt['class']}', text='{opt['text']}'")
        
        print("\n" + "=" * 60)
        print("探索完成!")
        print("=" * 60)
        
        return all_elements_info
        
    except Exception as e:
        print(f"探索过程中出现错误: {e}")
        return []

# 快捷函数：查看特定类型的元素
def find_elements_by_pattern(driver, pattern_type="all", max_results=20):
    """
    快速查找特定模式元素
    
    Args:
        driver: WebDriver实例
        pattern_type: 查找模式，可选值：
            - "all": 所有元素
            - "buttons": 所有按钮
            - "inputs": 输入框
            - "links": 链接
            - "options": 选择题选项
            - "with_text": 有文本的元素
        max_results: 最大显示结果数
    """
    print(f"\n查找模式: {pattern_type}")
    print("-" * 50)
    
    all_elements = driver.find_elements(By.XPATH, "//*")
    
    if pattern_type == "buttons":
        elements = [e for e in all_elements if e.tag_name == 'button']
    elif pattern_type == "inputs":
        elements = [e for e in all_elements if e.tag_name in ['input', 'textarea']]
    elif pattern_type == "links":
        elements = [e for e in all_elements if e.tag_name == 'a']
    elif pattern_type == "options":
        elements = []
        for e in all_elements:
            class_attr = e.get_attribute('class') or ''
            text = e.text or ''
            if any(keyword in class_attr.lower() or keyword in text.lower() 
                   for keyword in ['option', 'choice', 'select', 'radio', 'checkbox']):
                elements.append(e)
    elif pattern_type == "with_text":
        elements = [e for e in all_elements if e.text and e.text.strip()]
    else:
        elements = all_elements
    
    print(f"找到 {len(elements)} 个匹配元素")
    
    for i, elem in enumerate(elements[:max_results]):
        try:
            tag = elem.tag_name
            elem_id = elem.get_attribute('id') or ''
            elem_class = elem.get_attribute('class') or ''
            elem_text = elem.text[:50] + "..." if len(elem.text) > 50 else elem.text
            
            print(f"{i+1:>3}. [{tag}] id='{elem_id}' class='{elem_class}' text='{elem_text}'")
        except:
            print(f"{i+1:>3}. [无法获取信息]")
    
    if len(elements) > max_results:
        print(f"... 还有 {len(elements) - max_results} 个元素未显示")
    
    return elements

# 使用示例
if __name__ == "__main__":
    # 完整探索
    elements_info = explore_all_page_elements(driver)
    
    # 或者快速查找特定类型
    buttons = find_elements_by_pattern(driver, "buttons", 10)
    inputs = find_elements_by_pattern(driver, "inputs", 10)
    options = find_elements_by_pattern(driver, "options", 10)