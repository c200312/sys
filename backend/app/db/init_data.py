"""
数据初始化模块
创建初始用户数据（与前端 localStorage 初始化逻辑一致）
"""
from app.core import get_password_hash
from app.models import User, Teacher, Student, UserRole, Gender
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


async def init_default_data(session: AsyncSession):
    """
    初始化默认数据

    创建 5 个教师账号和 100 个学生账号
    与前端 localStorage-service.ts 中的 initializeData() 保持一致
    """
    # 检查是否已有用户
    result = await session.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        return  # 已有数据，跳过初始化

    print("初始化默认用户数据...")

    # 创建教师
    for i in range(1, 6):
        username = f"teacher{i}"
        user = User(
            username=username,
            password=get_password_hash("123456"),
            role=UserRole.TEACHER
        )
        session.add(user)
        await session.flush()

        teacher = Teacher(
            user_id=user.id,
            teacher_no=username,
            name=f"教师{i}",
            gender=Gender.MALE if i % 2 == 1 else Gender.FEMALE,
            email=f"{username}@example.com"
        )
        session.add(teacher)

    # 创建学生
    for i in range(1, 101):
        username = f"student{i}"

        # 分配班级
        if i <= 40:
            class_name = "一班"
        elif i <= 80:
            class_name = "二班"
        else:
            class_name = "三班"

        user = User(
            username=username,
            password=get_password_hash("123456"),
            role=UserRole.STUDENT
        )
        session.add(user)
        await session.flush()

        student = Student(
            user_id=user.id,
            student_no=username,
            name=f"学生{i}",
            class_name=class_name,
            gender=Gender.MALE if i % 2 == 1 else Gender.FEMALE
        )
        session.add(student)

    await session.commit()
    print("默认用户数据初始化完成！")
    print("- 教师账号: teacher1 ~ teacher5 (密码: 123456)")
    print("- 学生账号: student1 ~ student100 (密码: 123456)")
