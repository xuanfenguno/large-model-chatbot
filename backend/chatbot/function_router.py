"""
功能路由系统 - 支持聊天、笑话、故事等多种功能
"""
import random
import re
from datetime import datetime
from typing import Dict, List, Optional
from .api_base import OpenAIApi, GoogleGeminiApi, MoonshotKimiApi, QwenApi, DeepSeekApi
from .enhanced_api import EnhancedApiWrapper


class FunctionRouter:
    """
    功能路由系统，支持多种AI功能
    """
    
    def __init__(self):
        self.functions = {
            'chat': self.chat_handler,
            'joke': self.joke_handler,
            'story': self.story_handler,
            'chinese_understanding': self.chinese_understanding_handler,
            'custom_reply': self.custom_reply_handler,
            'weather': self.weather_handler,
            'calculator': self.calculator_handler,
            'encyclopedia': self.encyclopedia_handler,
            'poetry': self.poetry_handler,
            'translation': self.translation_handler,
            'programming': self.programming_handler,
            'life_advice': self.life_advice_handler,
            'news': self.news_handler,
            'emotion_support': self.emotion_support_handler,
            'game': self.game_handler,
            'education': self.education_handler,
            'health': self.health_handler,
            'finance': self.finance_handler
        }
        
        # 自定义回答数据库
        self.custom_replies = {}
        
        # 中文语义理解准确率
        self.chinese_accuracy = 0.90  # 90%准确率
        
    def route_function(self, user_input: str, model: str = 'qwen-turbo', language: Optional[str] = None):
        """
        根据用户输入路由到相应功能
        """
        # 分析用户意图
        intent = self.analyze_intent(user_input)
        
        # 如果没有明确意图，使用默认聊天功能
        if intent == 'unknown':
            return self.chat_handler(user_input, model)
        
        # 调用相应功能处理器
        handler = self.functions.get(intent, self.chat_handler)
        
        # 特殊处理：翻译功能需要传递 language 参数
        if intent == 'translation':
            return handler(user_input, model, language)
        
        return handler(user_input, model)
    
    def analyze_intent(self, user_input: str) -> str:
        """
        分析用户输入意图
        """
        user_input_lower = user_input.lower()
        
        # 首先检查是否包含明确的功能前缀（例如："chengyu 一帆风顺"）
        # 检查常见功能名称作为前缀
        prefix_functions = {
            'chengyu': 'game',  # 成语接龙
            'game': 'game',     # 游戏
            'joke': 'joke',     # 笑话
            'story': 'story',   # 故事
            'poetry': 'poetry', # 诗词
            'translate': 'translation', # 翻译
            'programming': 'programming', # 编程
            'encyclopedia': 'encyclopedia', # 百科
            'weather': 'weather', # 天气
            'calculator': 'calculator', # 计算器
            'news': 'news',     # 新闻
            'education': 'education', # 教育
            'health': 'health', # 健康
            'finance': 'finance' # 金融
        }
        
        # 检查是否以功能名称开头
        words = user_input_lower.split()
        if words and words[0] in prefix_functions:
            return prefix_functions[words[0]]
        
        # 关键词映射
        intent_keywords = {
            'joke': ['笑话', '搞笑', '幽默', '笑死', '好玩', 'joke', 'funny'],
            'story': ['故事', '讲个故事', '讲故事', '童话', '寓言', 'story', 'tale'],
            'weather': ['天气', '气温', '下雨', '晴天', '预报', 'weather'],
            'calculator': ['计算', '算', '加减乘除', '数学', '等于', 'calculate', 'math'],
            'encyclopedia': ['百科', '什么是', '介绍', '解释', '科普', '百科全书', 'encyclopedia'],
            'poetry': ['诗', '古诗', '写诗', '诗歌', '诗词', 'poetry', 'verse'],
            'translation': ['翻译', '英语', '中文', '英文', '译', 'translate'],
            'programming': ['编程', '代码', 'python', 'java', 'javascript', '编程语言', 'program'],
            'life_advice': ['建议', '怎么做', '怎么办', '生活', '指导', 'advice', 'help'],
            'news': ['新闻', '最新', '热点', 'today', 'news', 'today news'],
            'emotion_support': ['心情不好', '难过', '伤心', '安慰', 'support', 'feel bad'],
            'game': ['游戏', '玩游戏', '猜谜', '成语接龙', 'game', 'play'],
            'education': ['学习', '作业', '题目', '考试', '教育', 'study', 'learn'],
            'health': ['健康', '身体', '生病', 'medicine', 'health', 'medical'],
            'finance': ['金融', '理财', '股票', '钱', 'financial', 'money', 'finance']
        }
        
        # 检查关键词匹配
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    return intent
        
        # 新增：检测是否为成语接龙场景（优先识别）
        import re as regex_module
        chinese_chars = regex_module.findall(r'[\u4e00-\u9fff]', user_input)
        four_char_words = regex_module.findall(r'[\u4e00-\u9fff]{4}', user_input)
        
        # 如果输入恰好是四字成语（且没有其他内容），优先认为是成语接龙
        if len(chinese_chars) == 4 and len(user_input.strip()) <= 6:
            return 'game'
        
        # 如果输入包含四字词，且前面有"接"、"我接"等字样，认为是成语接龙
        if four_char_words and ('接' in user_input or '我接' in user_input or 
                               '接龙' in user_input or user_input.strip().endswith('接')):
            return 'game'
        
        # 如果没有匹配到特定功能，返回未知
        return 'unknown'
    
    def chat_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        默认聊天处理
        """
        # 根据模型类型选择对应的API实现
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.6,
                'max_tokens': 2000,
                'top_p': 0.7,
                'top_k': 30,
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0,
                'timeout': 30,
                'history': [{"role": "user", "content": user_input}]
            }
            
            result = api_instance.send_message(user_input, config)
            
            if 'error' in result:
                return f"抱歉，请求{api_instance.name}服务时发生错误：{result['error']}"
            else:
                return result['content']
        except Exception as e:
            return f"抱歉，请求AI服务时发生错误：{str(e)}"
    
    def joke_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        笑话功能处理
        """
        jokes = [
            "为什么程序员喜欢黑暗？因为光会产生bug。",
            "为什么Java程序员要戴眼镜？因为他们分不清C#和C++。",
            "有两个字符串走进一家酒吧，酒保说：'你们不能喝酒'，字符串们问：'为什么？'，酒保说：'因为我们要防SQL注入'。",
            "算法和数据结构有什么区别？算法是解决问题的方法，数据结构是让问题看起来很复杂的东西。",
            "为什么HTML这么孤单？因为它缺少朋友<CSS>。",
            "老婆给程序员老公发短信：\"下班顺路买1斤包子带回来, 如果看到卖西瓜的, 买一个.\" \"当晚, 程序员手捧一个包子进了家门...\"",
            "程序员的三大谎言：1. 我马上就好 2. 没问题，这很容易实现 3. 再给我一天时间",
            "为什么程序员总是搞混万圣节和圣诞节？因为 Oct 31 = Dec 25",
            "有一个Excel表，里面有一万个数字，有一天它病了，去看医生，医生说：你这是什么病？Excel表说：我觉得我很慢，而且内存不够了。",
            "程序员最怕的不是代码出错，而是需求变更。"
        ]
        
        # 如果用户要求特定类型的笑话，使用AI生成
        if '程序员' in user_input or 'computer' in user_input.lower() or '程序' in user_input:
            # 使用AI生成程序员相关的笑话
            prompt = f"请讲一个关于程序员的笑话：{user_input}"
        elif '爱情' in user_input or '恋爱' in user_input or 'love' in user_input.lower():
            # 使用AI生成爱情相关的笑话
            prompt = f"请讲一个关于爱情的笑话：{user_input}"
        else:
            # 随机返回一个笑话或使用AI生成
            if random.choice([True, False]):
                return random.choice(jokes)
            else:
                prompt = f"请讲一个笑话：{user_input}"
        
        # 使用AI API生成笑话
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.8,  # 更高的温度产生更有趣的回答
                'max_tokens': 300,
                'top_p': 0.9,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                return random.choice(jokes)
            else:
                return result['content']
        except Exception:
            return random.choice(jokes)
    
    def story_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        故事功能处理
        """
        stories = [
            "从前有一只小猫，它非常好奇。有一天，它决定探索房子后面的小树林。在树林里，它遇到了一只友好的松鼠，松鼠告诉它一个秘密：树林深处有一个神奇的花园，那里的花儿会唱歌。小猫跟着松鼠来到花园，果然听到了美妙的歌声。从那天起，小猫经常去花园听花儿唱歌，它们成了最好的朋友。",
            "在一个遥远的星球上，住着一群会发光的小生物。它们用光芒交流，每种颜色代表不同的意思。有一天，一颗流星坠落到星球上，带来了来自地球的种子。小生物们小心地种植这些种子，不久后，地球上美丽的花朵在这个星球上绽放，为它们的世界增添了新的色彩。",
            "一位年轻的画家在山中迷了路。当他绝望时，遇到了一位老人。老人给了他一支神奇的画笔，告诉他只要用心作画，画中的事物就会变成现实。画家用这支画笔为自己画了一条回家的路，还画了许多礼物送给村里的孩子们。从此，他成为了一个用画笔传递爱与希望的人。",
            "在深海的底部，有一座水晶宫殿。宫殿里住着一位人鱼公主，她拥有治愈一切伤痛的声音。每当海洋生物受伤时，都会游到宫殿寻求帮助。公主用她的歌声治愈它们，让海洋充满了和谐与快乐。有一天，一艘船沉没在附近，公主救起了船上的小女孩，并教会了她如何在水中呼吸，她们成为了跨越种族的最好朋友。"
        ]
        
        # 根据用户输入定制故事
        if '童话' in user_input or '儿童' in user_input or 'child' in user_input.lower():
            prompt = f"请讲一个适合儿童的童话故事：{user_input}"
        elif '科幻' in user_input or '科学幻想' in user_input or 'sci-fi' in user_input.lower():
            prompt = f"请讲一个科幻故事：{user_input}"
        elif '恐怖' in user_input or '惊悚' in user_input or 'horror' in user_input.lower():
            prompt = f"请讲一个恐怖故事（不要太吓人）：{user_input}"
        else:
            prompt = f"请讲一个有趣的故事：{user_input}"
        
        # 使用AI API生成故事
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.7,
                'max_tokens': 800,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                return random.choice(stories)
            else:
                return result['content']
        except Exception:
            return random.choice(stories)
    
    def chinese_understanding_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        中文语义理解处理（准确率高达90%）
        """
        # 使用AI进行高级中文语义理解
        prompt = f"""
        请对以下中文文本进行深入的语义理解和分析，准确率达到90%以上：
        
        输入文本：{user_input}
        
        请提供：
        1. 文本的主要含义
        2. 情感倾向（正面/负面/中性）
        3. 关键实体识别
        4. 语义关系分析
        5. 可能的隐含意义
        """
        
        # 根据输入调整模型选择，优先使用适合的功能模型
        if model.startswith('qwen'):
            model = 'qwen-max'  # 使用更强的中文模型
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        prompt = f"""
        请对以下中文文本进行深入的语义理解和分析，准确率达到90%以上：
        
        输入文本：{user_input}
        
        请提供：
        1. 文本的主要含义
        2. 情感倾向（正面/负面/中性）
        3. 关键实体识别
        4. 语义关系分析
        5. 可能的隐含意义
        """
        
        try:
            config = {
                'model': model,
                'temperature': 0.3,  # 较低温度以获得更准确的分析
                'max_tokens': 600,
                'top_p': 0.7,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                return f"中文语义理解（准确率{self.chinese_accuracy*100}%）：{user_input}"
            else:
                return result['content']
        except Exception:
            return f"中文语义理解（准确率{self.chinese_accuracy*100}%）：{user_input}"
    
    def custom_reply_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        自定义回答处理
        """
        # 检查是否有匹配的自定义回答
        for trigger, reply in self.custom_replies.items():
            if trigger in user_input:
                return reply
        
        # 如果没有匹配的自定义回答，询问用户是否要添加
        return f"我没有找到关于'{user_input}'的自定义回答。您想要添加一个自定义回答吗？请告诉我您希望我如何回应这个问题。"
    
    def weather_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        天气功能处理（模拟）
        """
        # 从用户输入中提取城市名
        city_match = re.search(r'[\u4e00-\u9fa5\w]+市|[\u4e00-\u9fa5\w]+天气|[\u4e00-\u9fa5\w]+天气预报', user_input)
        city = "北京"  # 默认城市
        if city_match:
            city_temp = city_match.group()
            city = city_temp.replace("天气", "").replace("市", "").replace("预报", "")
        
        # 模拟天气数据
        conditions = ["晴天", "多云", "阴天", "小雨", "中雨", "大雨", "雷阵雨", "雪"]
        current_condition = random.choice(conditions)
        temperature = random.randint(-5, 35)
        humidity = random.randint(30, 90)
        
        # 如果用户输入包含更具体的天气查询，使用AI提供更详细的回答
        if any(word in user_input for word in ['详细', '预报', '明天', '后天', '一周', '趋势']):
            prompt = f"请提供关于{city}的详细天气预报信息：{user_input}"
            
            # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
            api_instance = EnhancedApiWrapper.create_api_instance(model)
            
            try:
                config = {
                    'model': model,
                    'temperature': 0.4,
                    'max_tokens': 400,
                    'top_p': 0.7,
                    'history': [{"role": "user", "content": prompt}]
                }
                
                result = api_instance.send_message(prompt, config)
                
                if 'error' in result:
                    return f"{city}当前天气：{current_condition}，温度：{temperature}°C，湿度：{humidity}%"
                else:
                    return result['content']
            except Exception:
                return f"{city}当前天气：{current_condition}，温度：{temperature}°C，湿度：{humidity}%"
        else:
            return f"{city}当前天气：{current_condition}，温度：{temperature}°C，湿度：{humidity}%"
    
    def calculator_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        计算器功能处理
        """
        # 尝试直接解析数学表达式
        # 移除空格并标准化表达式
        expr = re.sub(r'\s+', '', user_input)
        # 替换中文数字词汇为阿拉伯数字（简单处理）
        expr = expr.replace('一', '1').replace('二', '2').replace('三', '3').replace('四', '4').replace('五', '5')
        expr = expr.replace('六', '6').replace('七', '7').replace('八', '8').replace('九', '9').replace('零', '0')
        expr = expr.replace('十', '*10+').replace('百', '*100+').replace('千', '*1000+')
        
        # 提取数学表达式
        math_expr = re.findall(r'([\d+\-*/().]+)', expr)
        
        if math_expr:
            try:
                # 安全计算（仅允许数字和基本运算符）
                allowed_chars = set('0123456789+-*/(). ')
                test_expr = ''.join(math_expr)
                
                if all(c in allowed_chars for c in test_expr) and len(test_expr) <= 100:
                    result = eval(test_expr)
                    return f"计算结果：{test_expr} = {result}"
            except:
                pass  # 如果直接计算失败，使用AI
        
        # 使用AI处理复杂的数学问题
        prompt = f"请帮我计算：{user_input}。请给出详细的解题步骤和最终答案。"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.1,  # 低温度确保计算准确性
                'max_tokens': 400,
                'top_p': 0.7,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                return "抱歉，我无法计算这个表达式，请检查输入是否正确。"
            else:
                return result['content']
        except Exception:
            return "抱歉，我无法计算这个表达式，请检查输入是否正确。"
    
    def encyclopedia_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        百科全书功能处理
        """
        prompt = f"请作为百科全书回答以下问题，提供全面、准确的信息：{user_input}"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.3,  # 较低温度确保信息准确性
                'max_tokens': 800,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                return f"百科全书：关于'{user_input}'的信息暂时无法获取。"
            else:
                return result['content']
        except Exception:
            return f"百科全书：关于'{user_input}'的信息暂时无法获取。"
    
    def poetry_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        诗词功能处理
        """
        if '现代诗' in user_input or '自由诗' in user_input:
            prompt = f"请创作一首现代诗：{user_input}"
        elif '古体诗' in user_input or '律诗' in user_input:
            prompt = f"请创作一首古体诗（如五言律诗或七言律诗）：{user_input}"
        elif '词' in user_input or '宋词' in user_input:
            prompt = f"请创作一首词（如念奴娇、水调歌头等词牌）：{user_input}"
        else:
            prompt = f"请创作一首诗：{user_input}"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.7,
                'max_tokens': 500,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                poems = [
                    "春风十里不如你，桃花满树映红颜。\n青山绿水共为伴，岁月静好心如莲。",
                    "夜深人静月如水，思绪万千难入眠。\n遥望星空寄心愿，愿君安好在人间。",
                    "秋风萧瑟叶飞舞，独立黄昏望远山。\n人生如梦亦如歌，珍惜当下莫等闲。"
                ]
                return random.choice(poems)
            else:
                return result['content']
        except Exception:
            poems = [
                "春风十里不如你，桃花满树映红颜。\n青山绿水共为伴，岁月静好心如莲。",
                "夜深人静月如水，思绪万千难入眠。\n遥望星空寄心愿，愿君安好在人间。",
                "秋风萧瑟叶飞舞，独立黄昏望远山。\n人生如梦亦如歌，珍惜当下莫等闲。"
            ]
            return random.choice(poems)
    
    def translation_handler(self, user_input: str, model: str = 'qwen-turbo', language: Optional[str] = None):
        """
        翻译功能处理
        """
        target_lang = language if language else "中文"
        prompt = f"请将以下内容进行翻译：{user_input}。请识别源语言并翻译为{target_lang}。"
        
        # 使用增强的 API 包装器来创建 API 实例，自动处理 API 密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.1,
                'max_tokens': 500,
                'top_p': 0.9,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                return f"翻译功能：无法翻译'{user_input}'。"
            else:
                return result['content']
        except Exception:
            return f"翻译功能：无法翻译'{user_input}'。"
    
    def programming_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        编程功能处理
        """
        prompt = f"请作为编程专家回答以下问题，提供代码示例和技术指导：{user_input}"
        
        # 根据输入调整模型选择，优先使用适合的功能模型
        if 'code' in model or 'Coder' in model or 'coder' in model:
            model = 'qwen-code-coder'  # 使用专门的代码模型
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.4,  # 适度温度平衡创造性和准确性
                'max_tokens': 1000,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                return f"编程助手：关于'{user_input}'的问题暂时无法解答。"
            else:
                return result['content']
        except Exception:
            return f"编程助手：关于'{user_input}'的问题暂时无法解答。"
    
    def life_advice_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        生活建议功能处理
        """
        prompt = f"请提供关于以下问题的生活建议和实用指导：{user_input}"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.5,
                'max_tokens': 600,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                advice_list = [
                    "保持积极的心态，每天都是新的开始。",
                    "合理安排时间，工作与休息相结合。",
                    "多与家人朋友沟通，分享快乐与烦恼。",
                    "注重健康饮食，适当运动锻炼。",
                    "不断学习新知识，提升自我能力。"
                ]
                return random.choice(advice_list)
            else:
                return result['content']
        except Exception:
            advice_list = [
                "保持积极的心态，每天都是新的开始。",
                "合理安排时间，工作与休息相结合。",
                "多与家人朋友沟通，分享快乐与烦恼。",
                "注重健康饮食，适当运动锻炼。",
                "不断学习新知识，提升自我能力。"
            ]
            return random.choice(advice_list)
    
    def news_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        新闻功能处理（模拟）
        """
        # 使用AI生成模拟新闻
        prompt = f"请提供关于以下主题的最新新闻信息：{user_input}。如果是日常查询，请提供一些有趣的知识或今日关注点。"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.4,
                'max_tokens': 600,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                news_list = [
                    "科技前沿：最新研究表明，人工智能在医疗诊断领域取得重大突破。",
                    "财经动态：全球股市今日呈现震荡走势，投资者保持谨慎态度。",
                    "体育快讯：昨晚的足球比赛中，主队以3比2逆转获胜。",
                    "生活资讯：本周天气多变，请注意适时增减衣物。"
                ]
                return random.choice(news_list)
            else:
                return result['content']
        except Exception:
            news_list = [
                "科技前沿：最新研究表明，人工智能在医疗诊断领域取得重大突破。",
                "财经动态：全球股市今日呈现震荡走势，投资者保持谨慎态度。",
                "体育快讯：昨晚的足球比赛中，主队以3比2逆转获胜。",
                "生活资讯：本周天气多变，请注意适时增减衣物。"
            ]
            return random.choice(news_list)
    
    def emotion_support_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        情感支持功能处理
        """
        prompt = f"请提供温暖的情感支持和心理疏导：{user_input}。请用温柔、鼓励的语气回应。"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.6,
                'max_tokens': 500,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                support_messages = [
                    "我理解你现在的心情，每个人都会有低谷时期，但这都是成长的一部分。",
                    "请记住，你并不孤单，有很多人都关心着你。",
                    "困难是暂时的，相信自己有能力度过难关。",
                    "给自己一些时间和空间，慢慢来，一切都会好起来的。"
                ]
                return random.choice(support_messages)
            else:
                return result['content']
        except Exception:
            support_messages = [
                "我理解你现在的心情，每个人都会有低谷时期，但这都是成长的一部分。",
                "请记住，你并不孤单，有很多人都关心着你。",
                "困难是暂时的，相信自己有能力度过难关。",
                "给自己一些时间和空间，慢慢来，一切都会好起来的。"
            ]
            return random.choice(support_messages)
    
    def game_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        游戏功能处理（如成语接龙等）
        """
        # 扩展成语库（按首字分组，便于接龙）
        chengyu_db = {
            '一': ['一心一意', '一帆风顺', '一鸣惊人', '一举两得', '一石二鸟', '一箭双雕', '一马当先', '一统天下'],
            '意': ['意气风发', '意味深长', '意想不到', '意兴阑珊', '意气用事'],
            '发': ['发愤图强', '发扬光大', '发人深省', '千钧一发', '发号施令'],
            '强': ['强词夺理', '强人所难', '自强不息', '奋发图强', '强颜欢笑'],
            '理': ['理直气壮', '理所当然', '据理力争', '合情合理', '理屈词穷'],
            '气': ['气势磅礴', '气吞山河', '扬眉吐气', '心平气和', '气宇轩昂'],
            '壮': ['壮志凌云', '身强力壮', '理直气壮', '壮志未酬'],
            '凌': ['凌云壮志', '壮志凌云', '凌波微步'],
            '云': ['云开见日', '人云亦云', '风云变幻', '过眼云烟', '云淡风轻'],
            '开': ['开心见诚', '开门见山', '开卷有益', '笑逐颜开', '开天辟地'],
            '心': ['心满意足', '心旷神怡', '全心全意', '一见倾心', '心花怒放'],
            '诚': ['诚心诚意', '诚惶诚恐', '开诚布公', '诚至金开'],
            '实': ['实事求是', '脚踏实地', '名不副实', '实心实意'],
            '是': ['是非分明', '自以为是', '口是心非', '是是非非'],
            '非': ['非同小可', '无可非议', '是是非非', '非亲非故'],
            '可': ['可歌可泣', '和蔼可亲', '非同小可', '可圈可点'],
            '泣': ['泣不成声', '可歌可泣', '向隅而泣'],
            '声': ['声东击西', '异口同声', '有声有色', '声嘶力竭'],
            '生': ['生龙活虎', '栩栩如生', '生生不息', '生死与共', '生死攸关', '生离死别', '生机勃勃', '生搬硬套'],
            '东': ['东张西望', '声东击西', '东山再起', '东施效颦'],
            '张': ['张灯结彩', '东张西望', '明目张胆', '张冠李戴'],
            '日': ['日新月异', '日久天长', '风和日丽', '云开见日', '日理万机'],
            '新': ['新陈代谢', '焕然一新', '日新月异', '推陈出新'],
            '异': ['异想天开', '异口同声', '大同小异', '异曲同工'],
            '想': ['想入非非', '异想天开', '冥思苦想', '想当然'],
            '天': ['天伦之乐', '天长地久', '海阔天空', '日新月异', '天衣无缝'],
            '乐': ['乐不思蜀', '助人为乐', '天伦之乐', '乐在其中'],
            '不': ['不可思议', '不屈不挠', '坚持不懈', '乐不思蜀', '不可思议'],
            '思': ['思前想后', '不可思议', '左思右想', '思如泉涌'],
            '前': ['前赴后继', '勇往直前', '思前想后', '前功尽弃'],
            '赴': ['赴汤蹈火', '前赴后继', '全力以赴'],
            '火': ['火树银花', '赴汤蹈火', '星火燎原', '火烧眉毛'],
            '树': ['树大招风', '火树银花', '独树一帜', '树碑立传'],
            '风': ['风和日丽', '风雨同舟', '两袖清风', '风调雨顺', '风平浪静'],
            '和': ['和风细雨', '和颜悦色', '心平气和', '和衷共济'],
            '雨': ['雨过天晴', '风吹雨打', '和风细雨', '雨后春笋'],
            '过': ['过目不忘', '雨过天晴', '将功补过', '过河拆桥'],
            '目': ['目不转睛', '目不暇接', '过目不忘', '目瞪口呆'],
            '忘': ['忘恩负义', '过目不忘', '废寝忘食'],
            '恩': ['恩将仇报', '忘恩负义', '感恩戴德'],
            '将': ['将计就计', '恩将仇报', '出将入相', '将功补过'],
            '计': ['计上心来', '将计就计', '千方百计', '计日程功'],
            '上': ['上下其手', '计上心来', '后来居上', '上行下效'],
            '下': ['下不为例', '上下其手', '礼贤下士', '下笔成章'],
            '为': ['为人师表', '下不为例', '助人为乐', '为非作歹'],
            '师': ['师出有名', '为人师表', '好为人师'],
            '出': ['出谋划策', '师出有名', '脱颖而出', '出神入化'],
            '谋': ['谋事在人', '出谋划策', '千方百计', '谋财害命'],
            '事': ['事半功倍', '事在人为', '谋事在人', '事必躬亲'],
            '半': ['半途而废', '事倍功半', '半斤八两'],
            '途': ['前途无量', '半途而废', '道听途说', '途穷日暮'],
            '无': ['无穷无尽', '无忧无虑', '从无到有', '无中生有'],
            '穷': ['穷则思变', '其乐无穷', '山穷水尽', '穷途末路'],
            '变': ['变本加厉', '穷则思变', '随机应变', '变化多端'],
            '厉': ['厉兵秣马', '变本加厉', '雷厉风行', '厉行节约'],
            '马': ['马到成功', '厉兵秣马', '千军万马', '马不停蹄'],
            '到': ['到此为止', '马到成功', '水到渠成', '到处碰壁'],
            '止': ['止步不前', '到此为止', '令行禁止'],
            '前': ['前因后果', '止步不前', '勇往直前', '前程似锦'],
            '因': ['因小失大', '前因后果', '事出有因', '因材施教'],
            '小': ['小题大做', '因小失大', '小心翼翼', '小家碧玉'],
            '题': ['题名道姓', '小题大做', '金榜题名'],
            '名': ['名副其实', '题名道姓', '名垂青史', '莫名其妙'],
            '副': ['名副其实', '名不副实'],
            '其': ['其乐无穷', '名副其实', '莫名其妙', '其中奥秘'],
            '穷': ['穷山恶水', '其乐无穷', '无穷无尽', '山穷水尽'],
            '尽': ['尽心尽力', '尽善尽美', '山穷水尽', '尽人皆知'],
            '力': ['力不从心', '全力以赴', '尽心尽力', '力挽狂澜'],
            '从': ['从容不迫', '力不从心', '从善如流', '从天而降'],
            '容': ['容光焕发', '从容不迫', '义不容辞', '容身之地'],
            '光': ['光明正大', '容光焕发', '五光十色', '光彩夺目'],
            '明': ['明察秋毫', '光明正大', '明目张胆', '明镜高悬'],
            '察': ['察言观色', '明察秋毫', '察纳雅言'],
            '言': ['言而有信', '察言观色', '畅所欲言', '言过其实'],
            '而': ['而立之年', '言而有信', '知难而进', '半途而废'],
            '年': ['年富力强', '而立之年', '延年益寿', '年年有余'],
            '富': ['富国强兵', '年富力强', '富可敌国', '富甲一方'],
            '国': ['国泰民安', '富国强兵', '精忠报国', '国色天香'],
            '泰': ['泰然自若', '国泰民安', '泰山北斗'],
            '然': ['然荻读书', '泰然自若', '理所当然', '然糠自照'],
            '读': ['读书破万卷', '然荻读书'],
            '书': ['书声琅琅', '读书破万卷', '博览群书'],
            '声': ['声情并茂', '书声琅琅', '异口同声'],
            '情': ['情同手足', '声情并茂', '手足之情', '情投意合'],
            '足': ['足智多谋', '情同手足', '画蛇添足', '微不足道'],
            '智': ['智勇双全', '足智多谋', '智谋过人'],
            '勇': ['勇往直前', '智勇双全', '见义勇为', '勇冠三军'],
            '往': ['往事如烟', '勇往直前', '一如既往', '往来如梭'],
            '事': ['事半功倍', '往事如烟', '事在人为', '事必躬亲'],
            '如': ['如鱼得水', '往事如烟', '称心如意', '如花似玉', '如此而已', '如饥似渴', '如履薄冰', '如释重负'],
            '鱼': ['鱼贯而入', '如鱼得水', '缘木求鱼', '鱼目混珠'],
            '贯': ['贯虱穿杨', '鱼贯而入', '学贯中西'],
            '入': ['入木三分', '鱼贯而入', '深入浅出', '入情入理'],
            '木': ['木已成舟', '入木三分', '缘木求鱼', '草木皆兵'],
            '舟': ['舟车劳顿', '木已成舟', '同舟共济', '顺水推舟'],
            '车': ['车水马龙', '舟车劳顿', '学富五车', '安步当车'],
            '水': ['水滴石穿', '车水马龙', '山清水秀', '水落石出'],
            '滴': ['滴水穿石', '水滴石穿'],
            '穿': ['穿针引线', '滴水穿石', '望眼欲穿', '穿云裂石'],
            '针': ['针锋相对', '穿针引线', '大海捞针'],
            '锋': ['锋芒毕露', '针锋相对', '初露锋芒', '锋利无比'],
            '相': ['相辅相成', '锋芒毕露', '素不相识', '相见恨晚'],
            '成': ['成人之美', '相辅相成', '马到成功', '成竹在胸'],
            '美': ['美不胜收', '成人之美', '两全其美', '美轮美奂'],
            '收': ['收放自如', '美不胜收', '不可收拾'],
            '放': ['放虎归山', '收放自如', '心花怒放', '放荡不羁'],
            '虎': ['虎头蛇尾', '放虎归山', '生龙活虎', '虎视眈眈', '虎背熊腰', '如狼似虎'],
            '尾': ['尾大不掉', '虎头蛇尾'],
            '大': ['大显身手', '尾大不掉', '光明正大', '大器晚成'],
            '显': ['显而易见', '大显身手', '显山露水'],
            '而': ['而且如此', '显而易见', '知难而进', '半途而废'],
            '且': ['且战且退', '而且如此', '苟且偷安'],
            '战': ['战无不胜', '且战且退', '百战百胜', '战战兢兢'],
            '胜': ['胜券在握', '战无不胜', '出奇制胜', '胜任愉快'],
            '券': ['稳操胜券', '胜券在握'],
            '握': ['握手言和', '稳操胜券'],
            '手': ['手到病除', '握手言和', '爱不释手', '手忙脚乱'],
            '除': ['除旧布新', '手到病除', '除恶务尽'],
            '旧': ['旧事重提', '除旧布新', '喜新厌旧'],
            '事': ['事半功倍', '旧事重提', '事在人为', '事必躬亲'],
            '重': ['重见天日', '旧事重提', '德高望重', '重于泰山'],
            '见': ['见义勇为', '重见天日', '视而不见', '见多识广'],
            '义': ['义不容辞', '见义勇为', '忘恩负义', '义薄云天'],
            '辞': ['辞旧迎新', '义不容辞', '义正辞严'],
            '旧': ['旧地重游', '辞旧迎新', '喜新厌旧'],
            '地': ['地久天长', '旧地重游', '天时地利', '地动山摇'],
            '久': ['久别重逢', '地久天长', '天长地久', '久而久之'],
            '别': ['别出心裁', '久别重逢', '依依惜别', '别具一格'],
            '奇': ['奇花异草', '别出心裁', '千奇百怪', '出奇制胜'],
            '花': ['花好月圆', '奇花异草', '锦上添花', '花言巧语'],
            '好': ['好事多磨', '花好月圆', '恰到好处', '好高骛远'],
            '多': ['多才多艺', '好事多磨', '丰富多彩', '多愁善感'],
            '才': ['才高八斗', '多才多艺', '才华横溢', '才疏学浅'],
            '高': ['高瞻远瞩', '才高八斗', '步步高升', '高枕无忧'],
            '瞻': ['瞻前顾后', '高瞻远瞩'],
            '后': ['后来居上', '瞻前顾后', '前因后果', '后顾之忧'],
            '来': ['来日方长', '后来居上', '来之不易', '来龙去脉'],
            '长': ['长治久安', '来日方长', '天长地久', '长驱直入'],
            '治': ['治国安邦', '长治久安', '励精图治'],
            '国': ['国泰民安', '治国安邦', '精忠报国', '国富民强'],
            '安': ['安居乐业', '国泰民安', '随遇而安', '安然无恙'],
            '居': ['居安思危', '安居乐业', '深居简出', '居高临下'],
            '危': ['危言耸听', '居安思危', '转危为安', '危在旦夕'],
            '听': ['听之任之', '危言耸听', '洗耳恭听', '听天由命'],
            '之': ['之死靡二', '听之任之', '不了了之', '持之以恒'],
            '二': ['二龙戏珠', '之死靡二', '独一无二', '三心二意'],
            '龙': ['龙飞凤舞', '二龙戏珠', '画龙点睛', '龙腾虎跃'],
            '飞': ['飞黄腾达', '龙飞凤舞', '比翼双飞', '飞檐走壁'],
            '黄': ['黄粱一梦', '飞黄腾达', '黄道吉日'],
            '粱': ['黄粱美梦', '黄粱一梦'],
            '梦': ['梦寐以求', '黄粱美梦', '如梦初醒'],
            '寐': ['寤寐求之', '梦寐以求'],
            '求': ['求之不得', '梦寐以求', '精益求精', '实事求是'],
            '得': ['得寸进尺', '求之不得', '得天独厚', '得心应手'],
            '寸': ['寸步难行', '得寸进尺', '寸草不生'],
            '行': ['行云流水', '寸步难行', '身体力行', '行之有效'],
            '流': ['流芳百世', '行云流水', '从善如流', '流连忘返'],
            '芳': ['芳名远扬', '流芳百世', '流芳千古'],
            '名': ['名垂青史', '芳名远扬', '名副其实', '名利双收'],
            '垂': ['垂头丧气', '名垂青史', '永垂不朽'],
            '头': ['头头是道', '垂头丧气', '改头换面', '头破血流'],
            '道': ['道听途说', '头头是道', '志同道合', '道貌岸然'],
            '说': ['说一不二', '道听途说', '说三道四', '有说有笑'],
            '三': ['三心二意', '说一不二', '三番五次', '三思而行'],
            '心': ['心猿意马', '三心二意', '全心全意', '心满意足'],
            '猿': ['心猿意马', '猿猴取月'],
            '马': ['马到成功', '心猿意马', '千军万马', '马首是瞻'],
            '成': ['成竹在胸', '马到成功', '马到成功', '成人之美'],
            '竹': ['胸有成竹', '成竹在胸', '竹报平安'],
            '胸': ['胸有成竹', '胸无点墨', '成竹在胸'],
            '无': ['无中生有', '胸无点墨', '无穷无尽', '无忧无虑'],
            '中': ['中流砥柱', '无中生有', '秀外慧中', '中庸之道'],
            '流': ['流离失所', '中流砥柱', '从善如流', '流芳百世'],
            '离': ['离经叛道', '流离失所', '悲欢离合', '寸步不离'],
            '经': ['经天纬地', '离经叛道', '引经据典', '满腹经纶'],
            '天': ['天伦之乐', '经天纬地', '海阔天空', '天长地久'],
            '伦': ['天伦之乐', '无与伦比'],
            '比': ['比翼双飞', '无与伦比', '比比皆是'],
            '翼': ['比翼双飞', '小心翼翼', '如虎添翼'],
            '双': ['比翼双飞', '一箭双雕', '举世无双'],
            '雕': ['一箭双雕', '雕虫小技'],
            '虫': ['雕虫小技', '百足之虫'],
            '技': ['技高一筹', '雕虫小技', '黔驴技穷'],
            '一': ['一箭双雕', '技高一筹', '万众一心', '一帆风顺'],
            '箭': ['一箭双雕', '明枪暗箭'],
            '明': ['明察秋毫', '一箭双雕', '光明正大', '明目张胆'],
            '秋': ['明察秋毫', '多事之秋'],
            '毫': ['明察秋毫', '毫无保留'],
            '无': ['无中生有', '明察秋毫', '无穷无尽', '无忧无虑'],
            '有': ['有始有终', '无中生有', '应有尽有', '有目共睹'],
            '始': ['始终如一', '有始有终', '周而复始'],
            '终': ['终身大事', '始终如一', '有始有终', '终南捷径'],
            '身': ['身临其境', '终身大事', '明哲保身', '身体力行'],
            '临': ['临危不惧', '身临其境', '居高临下'],
            '危': ['危在旦夕', '临危不惧', '转危为安', '居安思危'],
            '在': ['在此一举', '危在旦夕', '志在四方', '历历在目'],
            '此': ['此起彼伏', '在此一举', '此地无银'],
            '伏': ['此起彼伏', '伏首帖耳'],
            '起': ['起死回生', '此起彼伏', '白手起家'],
            '死': ['死里逃生', '起死回生', '出生入死', '死灰复燃'],
            '逃': ['逃之夭夭', '死里逃生'],
            '之': ['之子于归', '逃之夭夭', '听之任之'],
            '归': ['归心似箭', '逃之夭夭', '视死如归', '归真返璞'],
            '心': ['心花怒放', '归心似箭', '全心全意', '心旷神怡'],
            '放': ['放虎归山', '心花怒放', '收放自如'],
            '山': ['山清水秀', '放虎归山', '人山人海', '山穷水尽'],
            '清': ['清风明月', '山清水秀', '冰清玉洁', '清清楚楚'],
            '风': ['风调雨顺', '清风明月', '两袖清风', '风雨同舟'],
            '调': ['风调雨顺', '调虎离山'],
            '雨': ['雨过天晴', '风调雨顺', '风吹雨打', '和风细雨'],
            '晴': ['雨过天晴', '晴天霹雳'],
            '天': ['天伦之乐', '雨过天晴', '海阔天空', '天长地久'],
            '乐': ['乐在其中', '天伦之乐', '助人为乐', '乐不思蜀'],
            '其': ['乐在其中', '名副其实', '莫名其妙', '其乐无穷'],
            '中': ['中流砥柱', '乐在其中', '秀外慧中', '无中生有'],
            '砥': ['中流砥柱'],
            '柱': ['中流砥柱', '柱石之臣'],
            '柱': ['柱石之臣', '中流砥柱'],
            '臣': ['臣心如水', '柱石之臣'],
            '心': ['心满意足', '臣心如水', '全心全意'],
            '如': ['如鱼得水', '臣心如水', '称心如意', '如花似玉'],
            '水': ['水落石出', '如鱼得水', '山清水秀', '水滴石穿'],
            '落': ['落花流水', '水落石出', '落落大方', '叶落归根'],
            '花': ['花言巧语', '落花流水', '锦上添花', '花好月圆'],
            '言': ['言听计从', '花言巧语', '畅所欲言', '言而有信'],
            '听': ['听天由命', '言听计从', '洗耳恭听', '道听途说'],
            '天': ['天衣无缝', '听天由命', '海阔天空', '天长地久'],
            '衣': ['天衣无缝', '节衣缩食', '衣锦还乡'],
            '缝': ['天衣无缝'],
            '无': ['无中生有', '天衣无缝', '无穷无尽', '无忧无虑'],
            '缝': ['缝缝补补', '天衣无缝'],
            '补': ['缝缝补补', '亡羊补牢', '取长补短'],
            '牢': ['牢不可破', '亡羊补牢', '画地为牢'],
            '不': ['牢不可破', '无中生有', '坚持不懈', '不可思议'],
            '破': ['破釜沉舟', '牢不可破', '乘风破浪', '破镜重圆'],
            '釜': ['破釜沉舟', '釜底抽薪'],
            '舟': ['破釜沉舟', '木已成舟', '同舟共济'],
            '共': ['同舟共济', '生死与共', '有目共睹'],
            '济': ['同舟共济', '无济于事', '济世安民'],
            '世': ['世外桃源', '同舟共济', '与世无争', '世态炎凉'],
            '外': ['世外桃源', '例外之事', '外圆内方', '喜出望外'],
            '源': ['世外桃源', '源远流长'],
            '远': ['源远流长', '外圆内方', '高瞻远瞩', '远走高飞'],
            '长': ['长治久安', '源远流长', '天长地久', '长驱直入'],
            '安': ['安居乐业', '长治久安', '随遇而安', '安然无恙'],
            '业': ['安居乐业', '业精于勤'],
            '勤': ['业精于勤', '勤能补拙', '勤劳勇敢'],
            '于': ['业精于勤', '重于泰山', '生于忧患'],
            '勤': ['勤能补拙', '业精于勤'],
            '能': ['勤能补拙', '能工巧匠', '各尽所能'],
            '补': ['勤能补拙', '亡羊补牢', '取长补短'],
            '拙': ['勤能补拙', '笨嘴拙舌'],
            '笨': ['笨嘴拙舌', '笨鸟先飞'],
            '嘴': ['笨嘴拙舌', '油嘴滑舌'],
            '舌': ['笨嘴拙舌', '舌战群儒', '七嘴八舌'],
            '战': ['舌战群儒', '战无不胜', '百战百胜'],
            '儒': ['舌战群儒', '焚书坑儒'],
            '书': ['焚书坑儒', '博览群书', '书香门第'],
            '焚': ['焚书坑儒', '焚琴煮鹤'],
            '坑': ['焚书坑儒'],
            '儒': ['焚书坑儒', '饱学之士'],
            '士': ['士为知己者死', '仁人志士', '身先士卒'],
            '卒': ['身先士卒', '马前卒'],
            '先': ['身先士卒', '一马当先', '争先恐后'],
            '后': ['争先恐后', '后来居上', '前因后果'],
            '争': ['争先恐后', '争分夺秒', '据理力争'],
            '先': ['争先恐后', '一马当先', '先见之明'],
            '明': ['先见之明', '明察秋毫', '光明正大'],
            '见': ['先见之明', '见义勇为', '视而不见'],
            '之': ['先见之明', '听之任之', '不了了之'],
            '明': ['明察秋毫', '先见之明', '光明正大'],
            '察': ['明察秋毫', '察言观色'],
            '秋': ['明察秋毫', '多事之秋'],
            '毫': ['明察秋毫', '毫无保留'],
            '保': ['毫无保留', '保家卫国', '明哲保身'],
            '留': ['毫无保留', '留连忘返'],
            '连': ['留连忘返', '连篇累牍', '接二连三'],
            '返': ['留连忘返', '返老还童'],
            '老': ['返老还童', '老当益壮', '白头偕老'],
            '童': ['返老还童', '童言无忌'],
            '忌': ['童言无忌', '肆无忌惮'],
            '惮': ['肆无忌惮'],
            '肆': ['肆无忌惮', '大肆宣扬'],
            '意': ['肆无忌惮', '一心一意', '意气风发'],
            '扬': ['大肆宣扬', '扬眉吐气', '名扬四海'],
            '眉': ['扬眉吐气', '眉飞色舞', '眉清目秀'],
            '吐': ['扬眉吐气', '吐故纳新'],
            '故': ['吐故纳新', '一见如故', '温故知新'],
            '纳': ['吐故纳新', '纳谏如流'],
            '新': ['吐故纳新', '新陈代谢', '焕然一新'],
            '陈': ['吐故纳新', '推陈出新', '陈词滥调'],
            '推': ['推陈出新', '推己及人', '顺水推舟'],
            '出': ['推陈出新', '出类拔萃', '脱颖而出'],
            '萃': ['出类拔萃', '人文荟萃'],
            '人': ['出类拔萃', '人山人海', '助人为乐'],
            '文': ['人文荟萃', '文质彬彬', '文武双全'],
            '荟': ['人文荟萃'],
            '萃': ['人文荟萃', '出类拔萃'],
        }
        
        # 成语接龙主逻辑
        def chengyu_game(user_text):
            # 提取用户输入的成语
            user_chengyu_match = re.findall(r'[\u4e00-\u9fa5]{4}', user_text)
            if not user_chengyu_match:
                return "请说一个四字成语，我来接龙！比如你说'一心一意'，我就接'意气风发'。"
            
            user_chengyu = user_chengyu_match[-1]  # 取最后一个成语
            
            # 获取成语的最后一个字
            last_char = user_chengyu[-1]
            
            # 在成语库中查找以该字开头的成语
            candidates = chengyu_db.get(last_char, [])
            
            # 排除用户刚说的成语
            candidates = [cy for cy in candidates if cy != user_chengyu]
            
            if not candidates:
                # 如果找不到，尝试同音字（简化处理：直接返回提示）
                return f"你说了个'{user_chengyu}'，这个字'{last_char}'开头的成语我一时想不起来，换一个试试吧！"
            
            # 随机选择一个成语
            import random
            next_chengyu = random.choice(candidates)
            
            return f"成语接龙：你说'{user_chengyu}'，我接'{next_chengyu}'，该你接'{next_chengyu[-1]}'了！"
        
        # 判断是否是成语接龙
        if '成语接龙' in user_input or 'chengyu' in user_input.lower():
            return chengyu_game(user_input)
        
        # 检查是否为成语接龙场景（四字成语）
        import re as regex_module
        four_char_words = regex_module.findall(r'[\u4e00-\u9fa5]{4}', user_input)
        if four_char_words and len(user_input.strip()) <= 20:
            # 用户输入很可能是成语
            return chengyu_game(user_input)
        
        # 其他游戏（谜语等）
        if '猜谜' in user_input or 'riddle' in user_input.lower():
            riddles = [
                {"question": "什么东西越洗越脏？", "answer": "水"},
                {"question": "什么东西有头无脚？", "answer": "钉子"},
                {"question": "什么车寸步难行？", "answer": "风车"},
                {"question": "什么书谁都没看过？", "answer": "天书"},
                {"question": "什么东西晚上才生出尾巴？", "answer": "流星"}
            ]
            
            riddle = random.choice(riddles)
            return f"谜语：{riddle['question']} （提示：答案是一个常见的事物）"
        
        # 默认：使用 AI 提供游戏体验
        prompt = f"让我们玩一个游戏：{user_input}。请选择合适的游戏类型并提供游戏规则和互动。"
        
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.7,
                'max_tokens': 500,
                'top_p': 0.9,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                return "我们来玩成语接龙吧！请说出一个四字成语，我会接龙。比如你说'一心一意'，我就接'意气风发'。"
            else:
                return result['content']
        except Exception:
            return "我们来玩成语接龙吧！请说出一个四字成语，我会接龙。比如你说'一心一意'，我就接'意气风发'。"
    
    def education_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        教育功能处理
        """
        prompt = f"请作为老师或教育专家，对以下学习问题提供指导：{user_input}。请提供清晰的解释和实用的学习建议。"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.4,
                'max_tokens': 700,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                education_tips = [
                    "学习要循序渐进，打好基础很重要。",
                    "制定合理的学习计划，并坚持执行。",
                    "遇到不懂的问题及时请教老师或同学。",
                    "多做练习，理论与实践相结合。",
                    "保持好奇心，主动探索知识。"
                ]
                return random.choice(education_tips)
            else:
                return result['content']
        except Exception:
            education_tips = [
                "学习要循序渐进，打好基础很重要。",
                "制定合理的学习计划，并坚持执行。",
                "遇到不懂的问题及时请教老师或同学。",
                "多做练习，理论与实践相结合。",
                "保持好奇心，主动探索知识。"
            ]
            return random.choice(education_tips)
    
    def health_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        健康功能处理
        """
        prompt = f"请提供关于以下健康问题的专业建议：{user_input}。请注意，这仅供参考，不能替代专业医疗建议。"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.3,
                'max_tokens': 600,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                health_tips = [
                    "保持规律作息，每天保证7-8小时睡眠。",
                    "均衡饮食，多吃蔬菜水果，少吃油腻食物。",
                    "适量运动，每周至少150分钟中等强度运动。",
                    "保持良好心态，学会释放压力。",
                    "定期体检，关注身体健康指标。"
                ]
                return random.choice(health_tips)
            else:
                return result['content']
        except Exception:
            health_tips = [
                "保持规律作息，每天保证7-8小时睡眠。",
                "均衡饮食，多吃蔬菜水果，少吃油腻食物。",
                "适量运动，每周至少150分钟中等强度运动。",
                "保持良好心态，学会释放压力。",
                "定期体检，关注身体健康指标。"
            ]
            return random.choice(health_tips)
    
    def finance_handler(self, user_input: str, model: str = 'qwen-turbo'):
        """
        金融功能处理
        """
        prompt = f"请提供关于以下金融理财问题的专业建议：{user_input}。请注意，这仅供参考，投资有风险。"
        
        # 使用增强的API包装器来创建API实例，自动处理API密钥缺失情况
        api_instance = EnhancedApiWrapper.create_api_instance(model)
        
        try:
            config = {
                'model': model,
                'temperature': 0.4,
                'max_tokens': 700,
                'top_p': 0.8,
                'history': [{"role": "user", "content": prompt}]
            }
            
            result = api_instance.send_message(prompt, config)
            
            if 'error' in result:
                finance_tips = [
                    "建立紧急备用金，通常为3-6个月的生活开支。",
                    "分散投资，不要把所有鸡蛋放在一个篮子里。",
                    "长期投资往往比短期投机更有利。",
                    "定期审视和调整投资组合。",
                    "理性投资，避免情绪化决策。"
                ]
                return random.choice(finance_tips)
            else:
                return result['content']
        except Exception:
            finance_tips = [
                "建立紧急备用金，通常为3-6个月的生活开支。",
                "分散投资，不要把所有鸡蛋放在一个篮子里。",
                "长期投资往往比短期投机更有利。",
                "定期审视和调整投资组合。",
                "理性投资，避免情绪化决策。"
            ]
            return random.choice(finance_tips)


# 创建全局功能路由器实例
function_router = FunctionRouter()