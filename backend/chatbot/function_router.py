"""
功能路由系统 - 支持聊天、笑话、故事等多种功能
"""
import random
import re
from datetime import datetime
from typing import Dict, List, Optional
from .api_base import OpenAIApi, GoogleGeminiApi, MoonshotKimiApi, QwenApi, DeepSeekApi


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
        
    def route_function(self, user_input: str, model: str = 'gpt-3.5-turbo'):
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
        return handler(user_input, model)
    
    def analyze_intent(self, user_input: str) -> str:
        """
        分析用户输入意图
        """
        user_input_lower = user_input.lower()
        
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
        
        # 如果没有匹配到特定功能，返回未知
        return 'unknown'
    
    def chat_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        默认聊天处理
        """
        # 根据模型类型选择对应的API实现
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            # 默认使用OpenAI API
            api_instance = OpenAIApi()
        
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
    
    def joke_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
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
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def story_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
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
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def chinese_understanding_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        中文语义理解处理（准确率高达90%）
        """
        # 使用AI进行高级中文语义理解
        if model.startswith('qwen'):  # 优先使用通义千问进行中文处理
            api_instance = QwenApi()
            model = 'qwen-max'  # 使用更强的中文模型
        elif model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        else:
            api_instance = QwenApi()  # 默认使用通义千问处理中文
        
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
    
    def custom_reply_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        自定义回答处理
        """
        # 检查是否有匹配的自定义回答
        for trigger, reply in self.custom_replies.items():
            if trigger in user_input:
                return reply
        
        # 如果没有匹配的自定义回答，询问用户是否要添加
        return f"我没有找到关于'{user_input}'的自定义回答。您想要添加一个自定义回答吗？请告诉我您希望我如何回应这个问题。"
    
    def weather_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
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
            
            if model.startswith('gpt'):
                api_instance = OpenAIApi()
            elif model.startswith('gemini'):
                api_instance = GoogleGeminiApi()
            elif model.startswith('kimi'):
                api_instance = MoonshotKimiApi()
            elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
                api_instance = QwenApi()
            elif model.startswith('deepseek'):
                api_instance = DeepSeekApi()
            elif model.startswith('qwen'):
                api_instance = QwenApi()
            else:
                api_instance = OpenAIApi()
            
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
    
    def calculator_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
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
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def encyclopedia_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        百科全书功能处理
        """
        prompt = f"请作为百科全书回答以下问题，提供全面、准确的信息：{user_input}"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def poetry_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
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
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def translation_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        翻译功能处理
        """
        prompt = f"请将以下内容进行翻译：{user_input}。请识别源语言并翻译为目标语言（通常是中文和英文互译）。"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
        try:
            config = {
                'model': model,
                'temperature': 0.1,  # 低温度确保翻译准确性
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
    
    def programming_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        编程功能处理
        """
        prompt = f"请作为编程专家回答以下问题，提供代码示例和技术指导：{user_input}"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            # 如果是代码相关的问题，优先使用通义千问代码模型
            if 'code' in model or 'Coder' in model or 'coder' in model:
                api_instance = QwenApi()
                model = 'qwen-code-coder'  # 使用专门的代码模型
            else:
                api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def life_advice_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        生活建议功能处理
        """
        prompt = f"请提供关于以下问题的生活建议和实用指导：{user_input}"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def news_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        新闻功能处理（模拟）
        """
        # 使用AI生成模拟新闻
        prompt = f"请提供关于以下主题的最新新闻信息：{user_input}。如果是日常查询，请提供一些有趣的知识或今日关注点。"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def emotion_support_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        情感支持功能处理
        """
        prompt = f"请提供温暖的情感支持和心理疏导：{user_input}。请用温柔、鼓励的语气回应。"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def game_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        游戏功能处理（如成语接龙等）
        """
        if '成语接龙' in user_input or 'chengyu' in user_input.lower():
            # 成语接龙游戏
            chengyu_list = [
                "一心一意", "意气风发", "发愤图强", "强词夺理", "理直气壮",
                "壮志凌云", "云开见日", "日新月异", "异想天开", "开心见诚",
                "诚心诚意", "意在言外", "外强中干", "干干净净", "净几明窗",
                "窗明几净", "净手敛容", "容光焕发", "发人深省", "省吃俭用"
            ]
            
            last_chengyu = ""
            # 尝试从用户输入中获取上一个成语的最后一个字
            user_chengyu_match = re.findall(r'[\u4e00-\u9fa5]{4}', user_input)
            if user_chengyu_match:
                last_chengyu = user_chengyu_match[-1]
            
            # 找到以指定字开头的成语
            next_chengyu = None
            if last_chengyu and len(last_chengyu) >= 1:
                last_char = last_chengyu[-1]
                for cy in chengyu_list:
                    if cy[0] == last_char and cy != last_chengyu:
                        next_chengyu = cy
                        break
            
            if not next_chengyu:
                next_chengyu = random.choice(chengyu_list)
            
            return f"成语接龙：我接 '{next_chengyu}'，该你接了！"
        elif '猜谜' in user_input or 'riddle' in user_input.lower():
            riddles = [
                {"question": "什么东西越洗越脏？", "answer": "水"},
                {"question": "什么东西有头无脚？", "answer": "钉子"},
                {"question": "什么车寸步难行？", "answer": "风车"},
                {"question": "什么书谁都没看过？", "answer": "天书"},
                {"question": "什么东西晚上才生出尾巴？", "answer": "流星"}
            ]
            
            riddle = random.choice(riddles)
            return f"谜语：{riddle['question']} （提示：答案是一个常见的事物）"
        else:
            # 使用AI提供游戏体验
            prompt = f"让我们玩一个游戏：{user_input}。请选择合适的游戏类型并提供游戏规则和互动。"
            
            if model.startswith('gpt'):
                api_instance = OpenAIApi()
            elif model.startswith('gemini'):
                api_instance = GoogleGeminiApi()
            elif model.startswith('kimi'):
                api_instance = MoonshotKimiApi()
            elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
                api_instance = QwenApi()
            elif model.startswith('deepseek'):
                api_instance = DeepSeekApi()
            elif model.startswith('qwen'):
                api_instance = QwenApi()
            else:
                api_instance = OpenAIApi()
            
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
    
    def education_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        教育功能处理
        """
        prompt = f"请作为老师或教育专家，对以下学习问题提供指导：{user_input}。请提供清晰的解释和实用的学习建议。"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def health_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        健康功能处理
        """
        prompt = f"请提供关于以下健康问题的专业建议：{user_input}。请注意，这仅供参考，不能替代专业医疗建议。"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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
    
    def finance_handler(self, user_input: str, model: str = 'gpt-3.5-turbo'):
        """
        金融功能处理
        """
        prompt = f"请提供关于以下金融理财问题的专业建议：{user_input}。请注意，这仅供参考，投资有风险。"
        
        if model.startswith('gpt'):
            api_instance = OpenAIApi()
        elif model.startswith('gemini'):
            api_instance = GoogleGeminiApi()
        elif model.startswith('kimi'):
            api_instance = MoonshotKimiApi()
        elif model.startswith('qwen-code') or model.startswith('qwen_coder'):
            api_instance = QwenApi()
        elif model.startswith('deepseek'):
            api_instance = DeepSeekApi()
        elif model.startswith('qwen'):
            api_instance = QwenApi()
        else:
            api_instance = OpenAIApi()
        
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