"""
数据初始化模块
创建初始用户数据、课程和作业
"""
import random
from datetime import datetime, timedelta
from app.core import get_password_hash
from app.models import (
    User, Teacher, Student, Course, Homework,
    CourseEnrollment, UserRole, Gender, HomeworkSubmission
)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


# 中国常见姓氏
SURNAMES = [
    "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周",
    "徐", "孙", "马", "朱", "胡", "郭", "林", "何", "高", "罗",
    "郑", "梁", "谢", "宋", "唐", "许", "邓", "冯", "韩", "曹"
]

# 男性名字
MALE_NAMES = [
    "伟", "强", "磊", "军", "勇", "杰", "涛", "明", "超", "华",
    "志强", "建国", "建华", "志明", "国强", "文杰", "俊杰", "浩然", "子轩", "宇轩",
    "晨阳", "天宇", "浩宇", "皓轩", "宇航", "博文", "泽宇", "鹏飞", "嘉豪", "铭轩"
]

# 女性名字
FEMALE_NAMES = [
    "芳", "娟", "敏", "静", "丽", "艳", "秀英", "玉兰", "桂英", "秀珍",
    "晓红", "小芳", "雪梅", "美玲", "晓燕", "思琪", "欣怡", "诗涵", "雨萱", "梦瑶",
    "紫萱", "雅婷", "雨涵", "欣悦", "佳怡", "思雨", "婉婷", "诗雨", "晓彤", "梓涵"
]

# 教师名字
TEACHER_NAMES = [
    ("张建国", Gender.MALE),
    ("李秀英", Gender.FEMALE),
    ("王志强", Gender.MALE),
    ("陈雪梅", Gender.FEMALE),
    ("刘明华", Gender.MALE)
]

# 示例作业提交内容
SAMPLE_SUBMISSION_CONTENTS = [
    "# 作业完成报告\n\n## 实现思路\n\n我采用了模块化的设计方法，将问题分解为多个子问题分别解决。首先分析了题目要求，然后设计了核心算法，最后进行了测试验证。\n\n## 代码实现\n\n```python\ndef solve(n):\n    result = []\n    for i in range(n):\n        result.append(i * 2)\n    return result\n```\n\n## 测试结果\n\n所有测试用例均通过，程序运行正常。\n\n## 总结\n\n通过本次作业，我深入理解了相关概念，提升了编程能力。",
    
    "# 实验报告\n\n## 一、实验目的\n\n通过本次实验，掌握相关知识点的实际应用。\n\n## 二、实验内容\n\n按照题目要求，完成了以下功能：\n1. 数据读取与处理\n2. 算法实现与优化\n3. 结果输出与验证\n\n## 三、实验结果\n\n经过多次测试，程序能够正确处理各种输入情况。\n\n## 四、心得体会\n\n本次实验让我收获很多，加深了对课程内容的理解。",
    
    "## 作业答案\n\n### 问题分析\n\n仔细阅读题目后，我认为这个问题的核心在于如何高效地处理数据。\n\n### 解决方案\n\n采用递归的方法解决问题，时间复杂度为O(n)。\n\n### 代码\n\n```python\nclass Solution:\n    def process(self, data):\n        if not data:\n            return None\n        return self.helper(data, 0, len(data)-1)\n    \n    def helper(self, data, left, right):\n        if left > right:\n            return None\n        mid = (left + right) // 2\n        return data[mid]\n```\n\n### 运行截图\n\n程序运行成功，输出符合预期。",
    
    "作业题目：综合练习\n\n完成情况：\n\n1. 第一题：采用动态规划方法，定义状态dp[i]表示前i个元素的最优解。状态转移方程为dp[i] = max(dp[i-1], dp[i-2] + nums[i])。\n\n2. 第二题：使用双指针技巧，left从0开始，right从末尾开始，逐步向中间靠拢。\n\n3. 第三题：利用哈希表存储已访问的元素，实现O(1)的查找效率。\n\n所有代码已测试通过，详见附件。",
    
    "# 学习笔记与作业\n\n## 本周学习内容\n\n- 理论知识：深入学习了相关概念和原理\n- 实践练习：完成了课后习题和编程作业\n\n## 作业解答\n\n根据课堂所学，我完成了本次作业。主要思路是：\n\n1. 首先理解问题的本质\n2. 然后选择合适的数据结构\n3. 最后实现并验证算法的正确性\n\n## 遇到的问题\n\n在实现过程中遇到了边界条件处理的问题，通过查阅资料和反复调试解决了。\n\n## 收获与反思\n\n本次作业加深了我对知识点的理解，也提升了解决问题的能力。"
]

# 课程数据
COURSES_DATA = [
    {
        "name": "Python程序设计",
        "description": "本课程系统介绍Python编程语言的基础知识和高级特性，包括数据类型、控制结构、函数、面向对象编程、文件操作、异常处理等内容。通过大量实践案例，培养学生的编程思维和解决实际问题的能力。",
        "teacher_index": 0,  # 张建国
        "homeworks": [
            {
                "title": "Python基础语法练习",
                "description": "请完成以下练习：\n1. 编写一个程序，输入一个整数n，计算1到n的和\n2. 编写一个程序，判断一个数是否为素数\n3. 编写一个程序，实现冒泡排序算法\n\n要求：代码规范，添加必要注释",
                "deadline_days": 7
            },
            {
                "title": "面向对象编程实践",
                "description": "设计一个简单的学生管理系统类：\n1. 包含学生类(Student)，属性包括学号、姓名、成绩\n2. 包含班级类(Class)，可以添加、删除学生，计算平均成绩\n3. 实现__str__方法用于打印信息\n\n提交：源代码文件和运行截图",
                "deadline_days": 14
            },
            {
                "title": "文件操作与异常处理",
                "description": "编写一个程序实现以下功能：\n1. 读取一个CSV文件，解析其中的数据\n2. 对数据进行统计分析（求和、平均值、最大最小值）\n3. 将结果写入新的文件\n4. 正确处理文件不存在、格式错误等异常情况",
                "deadline_days": 10
            }
        ]
    },
    {
        "name": "数据结构与算法",
        "description": "本课程讲解常用数据结构（数组、链表、栈、队列、树、图、哈希表）和基本算法（排序、查找、递归、动态规划），分析算法时间和空间复杂度，培养学生的算法设计与分析能力。",
        "teacher_index": 0,  # 张建国
        "homeworks": [
            {
                "title": "链表操作实现",
                "description": "实现一个双向链表类，包含以下方法：\n1. append(value) - 在末尾添加节点\n2. prepend(value) - 在头部添加节点\n3. delete(value) - 删除指定值的节点\n4. find(value) - 查找节点\n5. reverse() - 反转链表\n\n要求：使用Python或Java实现",
                "deadline_days": 7
            },
            {
                "title": "二叉树遍历",
                "description": "实现二叉树的三种遍历方式：\n1. 前序遍历（递归和非递归）\n2. 中序遍历（递归和非递归）\n3. 后序遍历（递归和非递归）\n4. 层序遍历\n\n并分析各算法的时间和空间复杂度",
                "deadline_days": 10
            }
        ]
    },
    {
        "name": "Web前端开发",
        "description": "本课程涵盖现代Web前端开发技术，包括HTML5、CSS3、JavaScript ES6+、React框架等内容。通过项目实践，让学生掌握响应式设计、组件化开发、状态管理等前端开发核心技能。",
        "teacher_index": 1,  # 李秀英
        "homeworks": [
            {
                "title": "HTML+CSS页面设计",
                "description": "设计并实现一个个人主页，要求：\n1. 使用HTML5语义化标签\n2. 使用CSS3实现美观的布局\n3. 实现响应式设计，适配手机和PC\n4. 至少包含：首页、关于我、作品展示三个页面\n\n提交：源代码和页面截图",
                "deadline_days": 14
            },
            {
                "title": "JavaScript交互效果",
                "description": "为个人主页添加交互功能：\n1. 实现导航栏的滚动效果\n2. 实现图片轮播组件\n3. 实现表单验证功能\n4. 使用LocalStorage保存用户偏好设置\n\n要求：不使用jQuery，使用原生JavaScript",
                "deadline_days": 10
            },
            {
                "title": "React组件开发",
                "description": "使用React开发一个待办事项(Todo)应用：\n1. 可以添加、删除、编辑待办事项\n2. 可以标记完成/未完成\n3. 可以按状态筛选\n4. 数据持久化到LocalStorage\n\n提交：项目源代码（含package.json）",
                "deadline_days": 14
            }
        ]
    },
    {
        "name": "数据库原理与应用",
        "description": "本课程介绍关系数据库的基本原理，包括数据模型、SQL语言、数据库设计、事务管理、索引优化等内容。结合MySQL数据库进行实践，培养学生的数据库设计和应用开发能力。",
        "teacher_index": 2,  # 王志强
        "homeworks": [
            {
                "title": "数据库设计与建表",
                "description": "设计一个图书管理系统的数据库：\n1. 画出E-R图\n2. 进行关系模式设计（至少达到3NF）\n3. 编写建表SQL语句\n4. 插入测试数据\n\n要求：数据库包含图书、读者、借阅记录等表",
                "deadline_days": 10
            },
            {
                "title": "SQL查询练习",
                "description": "针对图书管理系统，完成以下查询：\n1. 查询借阅次数最多的前10本书\n2. 查询从未借过书的读者\n3. 统计每个月的借阅量\n4. 查询逾期未还的图书信息\n5. 使用视图简化复杂查询\n\n提交：SQL语句和查询结果截图",
                "deadline_days": 7
            }
        ]
    },
    {
        "name": "计算机网络",
        "description": "本课程系统讲解计算机网络的体系结构、各层协议工作原理，包括物理层、数据链路层、网络层、传输层、应用层的核心概念和技术，以及网络安全基础知识。",
        "teacher_index": 3,  # 陈雪梅
        "homeworks": [
            {
                "title": "网络协议分析",
                "description": "使用Wireshark抓包工具：\n1. 捕获并分析HTTP请求和响应过程\n2. 分析TCP三次握手和四次挥手过程\n3. 观察DNS域名解析过程\n4. 分析ARP协议工作过程\n\n提交：抓包截图和分析报告",
                "deadline_days": 10
            },
            {
                "title": "Socket编程实践",
                "description": "使用Socket编程实现：\n1. 一个简单的TCP聊天程序（客户端和服务端）\n2. 支持多个客户端同时连接\n3. 实现基本的消息收发功能\n\n可选加分项：实现私聊功能、在线用户列表",
                "deadline_days": 14
            }
        ]
    },
    {
        "name": "人工智能导论",
        "description": "本课程介绍人工智能的基本概念、发展历史和主要分支，包括机器学习、深度学习、自然语言处理、计算机视觉等领域的基础知识，并通过实践项目让学生体验AI应用开发。",
        "teacher_index": 4,  # 刘明华
        "homeworks": [
            {
                "title": "机器学习算法实践",
                "description": "使用sklearn库完成以下任务：\n1. 使用KNN算法对鸢尾花数据集进行分类\n2. 使用决策树算法进行预测\n3. 比较不同参数对模型性能的影响\n4. 绘制混淆矩阵和ROC曲线\n\n提交：Jupyter Notebook文件",
                "deadline_days": 14
            },
            {
                "title": "深度学习入门",
                "description": "使用PyTorch或TensorFlow：\n1. 构建一个简单的神经网络\n2. 在MNIST数据集上训练手写数字识别模型\n3. 记录训练过程中的loss和accuracy变化\n4. 测试模型并分析结果\n\n提交：代码和训练日志",
                "deadline_days": 14
            }
        ]
    }
]


def generate_student_name(index: int) -> tuple:
    """生成学生姓名和性别"""
    surname = SURNAMES[index % len(SURNAMES)]
    if index % 2 == 0:
        name = surname + MALE_NAMES[index // 2 % len(MALE_NAMES)]
        gender = Gender.MALE
    else:
        name = surname + FEMALE_NAMES[index // 2 % len(FEMALE_NAMES)]
        gender = Gender.FEMALE
    return name, gender


async def init_default_data(session: AsyncSession):
    """
    初始化默认数据

    创建 5 个教师账号和 100 个学生账号
    创建课程和作业
    """
    # 检查是否已有用户
    result = await session.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        return  # 已有数据，跳过初始化

    print("初始化默认数据...")

    # 存储创建的教师用户ID，用于后续创建课程
    teacher_user_ids = []

    # 创建教师
    for i, (name, gender) in enumerate(TEACHER_NAMES):
        username = f"teacher{i + 1}"
        user = User(
            username=username,
            password=get_password_hash("123456"),
            role=UserRole.TEACHER
        )
        session.add(user)
        await session.flush()
        teacher_user_ids.append(user.id)

        teacher = Teacher(
            user_id=user.id,
            teacher_no=f"T{str(i + 1).zfill(4)}",
            name=name,
            gender=gender,
            email=f"{username}@edu.example.com"
        )
        session.add(teacher)

    # 存储学生信息，用于选课和提交作业
    # student_info: {user_id: student_id}
    student_info = {}
    student_user_ids = []

    # 创建学生
    for i in range(1, 101):
        username = f"student{i}"
        name, gender = generate_student_name(i)

        # 分配班级
        if i <= 40:
            class_name = "计算机2301班"
        elif i <= 80:
            class_name = "计算机2302班"
        else:
            class_name = "计算机2303班"

        user = User(
            username=username,
            password=get_password_hash("123456"),
            role=UserRole.STUDENT
        )
        session.add(user)
        await session.flush()

        student = Student(
            user_id=user.id,
            student_no=f"2023{str(i).zfill(4)}",
            name=name,
            class_name=class_name,
            gender=gender
        )
        session.add(student)
        await session.flush()
        
        # 保存 user_id 和 student.id 的映射
        student_info[user.id] = student.id
        student_user_ids.append(user.id)

    # 统计提交数量
    total_submissions = 0

    # 创建课程和作业
    for course_data in COURSES_DATA:
        teacher_user_id = teacher_user_ids[course_data["teacher_index"]]

        # 计算选课学生数量（每个课程约 30-60 名学生）
        student_count = random.randint(30, 60)

        course = Course(
            name=course_data["name"],
            description=course_data["description"],
            teacher_id=teacher_user_id,
            student_count=student_count
        )
        session.add(course)
        await session.flush()

        # 为课程创建选课记录（随机选择学生）
        selected_students = random.sample(student_user_ids, student_count)
        for student_user_id in selected_students:
            enrollment = CourseEnrollment(
                course_id=course.id,
                student_id=student_user_id
            )
            session.add(enrollment)

        # 创建作业和提交
        for hw_data in course_data["homeworks"]:
            deadline = datetime.utcnow() + timedelta(days=hw_data["deadline_days"])
            homework = Homework(
                course_id=course.id,
                title=hw_data["title"],
                description=hw_data["description"],
                deadline=deadline,
                grading_criteria={
                    "type": "text",
                    "content": "评分标准：\n1. 代码正确性 (40分)\n2. 代码规范性 (20分)\n3. 注释和文档 (20分)\n4. 创新性和扩展 (20分)"
                }
            )
            session.add(homework)
            await session.flush()
            
            # 为部分选课学生创建作业提交（60%-80%的提交率）
            submission_rate = random.uniform(0.6, 0.8)
            submitting_students = random.sample(
                selected_students, 
                int(len(selected_students) * submission_rate)
            )
            
            for student_user_id in submitting_students:
                student_id = student_info[student_user_id]
                
                # 随机选择提交内容
                content = random.choice(SAMPLE_SUBMISSION_CONTENTS)
                
                # 随机生成提交时间（在作业发布后1-5天内）
                days_after = random.randint(1, min(5, hw_data["deadline_days"]))
                submitted_at = datetime.utcnow() - timedelta(days=hw_data["deadline_days"] - days_after)
                
                submission = HomeworkSubmission(
                    homework_id=homework.id,
                    student_id=student_id,
                    content=content,
                    submitted_at=submitted_at
                )
                session.add(submission)
                total_submissions += 1

    await session.commit()
    print("默认数据初始化完成！")
    print("=" * 50)
    print("教师账号:")
    for i, (name, _) in enumerate(TEACHER_NAMES):
        print(f"  teacher{i + 1} - {name} (密码: 123456)")
    print("-" * 50)
    print("学生账号: student1 ~ student100 (密码: 123456)")
    print("  学号: 20230001 ~ 20230100")
    print("  班级: 计算机2301班、计算机2302班、计算机2303班")
    print("-" * 50)
    print(f"课程数量: {len(COURSES_DATA)}")
    total_homeworks = sum(len(c["homeworks"]) for c in COURSES_DATA)
    print(f"作业数量: {total_homeworks}")
    print(f"作业提交数量: {total_submissions}")
    print("=" * 50)

