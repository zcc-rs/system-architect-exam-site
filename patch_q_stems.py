import json, re

with open('data/question-bank.js', 'r', encoding='utf-8') as f:
    content = f.read()

# find first { and last }
start = content.find('{')
end = content.rfind('}')
json_str = content[start:end+1]

obj_data = json.loads(json_str)

for paper in obj_data.get('papers', []):
    if paper.get('id') == 'zk1':
        for q in paper.get('questions', []):
            if q['number'] == 21:
                q['stem'] = "按照传统的软件生命周期方法学，可以把软件生命周期划分为软件定义、( 1 ) 和软件运行与维护三个阶段。其中，使软件持久满足用户的要求是( 2 ) 阶段的主要任务。\n\n本题填空( 1 )"
            elif q['number'] == 22:
                q['stem'] = "按照传统的软件生命周期方法学，可以把软件生命周期划分为软件定义、( 1 ) 和软件运行与维护三个阶段。其中，使软件持久满足用户的要求是( 2 ) 阶段的主要任务。\n\n本题填空( 2 )"
            elif q['number'] == 26:
                q['stem'] = "( 1 ) 的目的是检查每个模块能否正确地实现设计说明中的功能、性能、接口和其他设计约束等条件，发现模块内可能存在的各种差错。其测试的技术依据是 ( 2 ) 。\n\n本题填空( 1 )"
            elif q['number'] == 27:
                q['stem'] = "( 1 ) 的目的是检查每个模块能否正确地实现设计说明中的功能、性能、接口和其他设计约束等条件，发现模块内可能存在的各种差错。其测试的技术依据是 ( 2 ) 。\n\n本题填空( 2 )"
            elif q['number'] == 28:
                q['stem'] = "在面向对象设计的原则中，( ) 原则是指一个对象应当对其他对象有尽可能少的了解。"
            elif q['number'] == 29:
                q['stem'] = "关于设计模式，下面说法正确的是 ( ) 。"
            elif q['number'] == 30:
                q['stem'] = "软件配置管理核心内容包括 ( ) 。\n①版本控制 ②变更管理 ③代码审查 ④构建管理"

new_content = "window.QUESTION_BANK = " + json.dumps(obj_data, ensure_ascii=False, indent=2) + ";\n"

with open('data/question-bank.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Patch applied for 21, 22, 26, 27, 28, 29, 30 in zk1.")
