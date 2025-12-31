"""
数据迁移脚本：将数据库中的 Base64 文件迁移到 MinIO

使用方法：
1. 确保 MinIO 服务已启动
2. 在 backend 目录下运行: python -m scripts.migrate_to_minio
"""
import asyncio
import base64
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import async_session
from app.models import CourseFile, Homework, HomeworkSubmission
from app.services.minio_service import get_minio_service


async def migrate_course_files(session: AsyncSession, minio):
    """迁移课程文件"""
    print("\n=== 迁移课程文件 ===")

    # 查询所有有 content 但没有 object_name 的文件
    # 注意：由于模型已更改，需要使用原始 SQL 查询
    result = await session.execute(
        text("SELECT id, name, type, content FROM course_files WHERE content IS NOT NULL AND content != ''")
    )
    files = result.fetchall()

    migrated = 0
    failed = 0

    for file_row in files:
        file_id, name, file_type, content = file_row

        try:
            # 解码 Base64
            if "," in content:
                content = content.split(",", 1)[1]

            file_data = base64.b64decode(content)

            # 上传到 MinIO
            object_name = minio.upload_file(
                file_data,
                name,
                file_type or "application/octet-stream",
                prefix="courses/"
            )

            # 更新数据库记录
            await session.execute(
                text("UPDATE course_files SET object_name = :object_name, content = NULL WHERE id = :id"),
                {"object_name": object_name, "id": file_id}
            )

            migrated += 1
            print(f"  ✓ 迁移文件: {name}")

        except Exception as e:
            failed += 1
            print(f"  ✗ 迁移失败 {name}: {e}")

    await session.commit()
    print(f"\n课程文件迁移完成: 成功 {migrated}, 失败 {failed}")


async def migrate_homework_attachments(session: AsyncSession, minio):
    """迁移作业附件"""
    print("\n=== 迁移作业附件 ===")

    result = await session.execute(
        text("SELECT id, attachment, grading_criteria FROM homeworks WHERE attachment IS NOT NULL OR grading_criteria IS NOT NULL")
    )
    homeworks = result.fetchall()

    migrated = 0
    failed = 0

    for hw_row in homeworks:
        hw_id, attachment, grading_criteria = hw_row

        update_data = {}

        # 迁移附件
        if attachment:
            try:
                import json
                att = json.loads(attachment) if isinstance(attachment, str) else attachment

                if att and att.get("content") and not att.get("object_name"):
                    content = att["content"]
                    if "," in content:
                        content = content.split(",", 1)[1]

                    file_data = base64.b64decode(content)
                    object_name = minio.upload_file(
                        file_data,
                        att["name"],
                        att.get("type", "application/octet-stream"),
                        prefix="homeworks/"
                    )

                    att["object_name"] = object_name
                    del att["content"]
                    update_data["attachment"] = json.dumps(att)
                    migrated += 1
                    print(f"  ✓ 迁移作业附件: {att['name']}")

            except Exception as e:
                failed += 1
                print(f"  ✗ 迁移作业附件失败 (ID: {hw_id}): {e}")

        # 迁移批改标准文件
        if grading_criteria:
            try:
                import json
                gc = json.loads(grading_criteria) if isinstance(grading_criteria, str) else grading_criteria

                if gc and gc.get("type") == "file" and gc.get("content") and not gc.get("object_name"):
                    content = gc["content"]
                    if "," in content:
                        content = content.split(",", 1)[1]

                    file_data = base64.b64decode(content)
                    object_name = minio.upload_file(
                        file_data,
                        gc.get("file_name", "grading_criteria"),
                        "application/octet-stream",
                        prefix="homeworks/grading/"
                    )

                    gc["object_name"] = object_name
                    gc["content"] = ""
                    update_data["grading_criteria"] = json.dumps(gc)
                    migrated += 1
                    print(f"  ✓ 迁移批改标准: {gc.get('file_name')}")

            except Exception as e:
                failed += 1
                print(f"  ✗ 迁移批改标准失败 (ID: {hw_id}): {e}")

        # 更新数据库
        if update_data:
            set_clause = ", ".join([f"{k} = :{k}" for k in update_data])
            update_data["id"] = hw_id
            await session.execute(
                text(f"UPDATE homeworks SET {set_clause} WHERE id = :id"),
                update_data
            )

    await session.commit()
    print(f"\n作业附件迁移完成: 成功 {migrated}, 失败 {failed}")


async def migrate_submission_attachments(session: AsyncSession, minio):
    """迁移学生提交附件"""
    print("\n=== 迁移学生提交附件 ===")

    result = await session.execute(
        text("SELECT id, attachments FROM homework_submissions WHERE attachments IS NOT NULL")
    )
    submissions = result.fetchall()

    migrated = 0
    failed = 0

    for sub_row in submissions:
        sub_id, attachments = sub_row

        if not attachments:
            continue

        try:
            import json
            atts = json.loads(attachments) if isinstance(attachments, str) else attachments

            if not atts:
                continue

            updated = False
            new_atts = []

            for att in atts:
                if att.get("content") and not att.get("object_name"):
                    content = att["content"]
                    if "," in content:
                        content = content.split(",", 1)[1]

                    file_data = base64.b64decode(content)
                    object_name = minio.upload_file(
                        file_data,
                        att["name"],
                        att.get("type", "application/octet-stream"),
                        prefix="submissions/"
                    )

                    new_att = {
                        "name": att["name"],
                        "type": att.get("type", ""),
                        "size": att.get("size", len(file_data)),
                        "object_name": object_name
                    }
                    new_atts.append(new_att)
                    updated = True
                    migrated += 1
                    print(f"  ✓ 迁移提交附件: {att['name']}")
                else:
                    new_atts.append(att)

            if updated:
                await session.execute(
                    text("UPDATE homework_submissions SET attachments = :attachments WHERE id = :id"),
                    {"attachments": json.dumps(new_atts), "id": sub_id}
                )

        except Exception as e:
            failed += 1
            print(f"  ✗ 迁移提交附件失败 (ID: {sub_id}): {e}")

    await session.commit()
    print(f"\n学生提交附件迁移完成: 成功 {migrated}, 失败 {failed}")


async def main():
    print("=" * 50)
    print("MinIO 数据迁移工具")
    print("=" * 50)

    try:
        minio = get_minio_service()
        print(f"\n✓ MinIO 连接成功")
    except Exception as e:
        print(f"\n✗ MinIO 连接失败: {e}")
        print("请确保 MinIO 服务已启动并且配置正确")
        return

    async with async_session() as session:
        await migrate_course_files(session, minio)
        await migrate_homework_attachments(session, minio)
        await migrate_submission_attachments(session, minio)

    print("\n" + "=" * 50)
    print("迁移完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
