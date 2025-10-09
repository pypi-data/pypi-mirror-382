#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的MySQL create_table方法
"""

from wauo.db.mysql import MysqlClient


def test_create_table():
    """测试create_table方法"""

    # 创建数据库连接（请根据实际情况修改连接参数）
    db = MysqlClient(
        host="localhost",
        port=3306,
        user="root",
        password="your_password",  # 请修改为实际密码
        database="test_db",  # 请修改为实际数据库名
    )

    try:
        # 测试1: 不生成ID字段
        print("=== 测试1: 不生成ID字段 ===")
        fields1 = ["name", "age", "email", "phone"]
        db.create_table("users", fields1, gen_id=False)
        print(f"创建表 users，字段: {fields1}")
        print("所有字段都将被创建为 VARCHAR(255)")

        # 测试2: 生成ID字段
        print("\n=== 测试2: 生成ID字段 ===")
        fields2 = ["title", "content", "author", "created_at"]
        db.create_table("articles", fields2, gen_id=True)
        print(f"创建表 articles，字段: {fields2}")
        print("将生成自增ID字段，其他字段为 VARCHAR(255)")

        # 测试3: 带空格的字段名
        print("\n=== 测试3: 带空格的字段名 ===")
        fields3 = [" user_name ", " user_age ", " user_email "]
        db.create_table("test_users", fields3, gen_id=True)
        print(f"创建表 test_users，字段: {fields3}")
        print("字段名中的空格会被自动处理")

        print("\n✅ 所有测试完成！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("请检查数据库连接参数是否正确")

    finally:
        # 关闭连接
        db.close()


def show_sql_examples():
    """显示生成的SQL示例"""
    print("\n=== 生成的SQL示例 ===")

    # 示例1: 不生成ID
    fields1 = ["name", "age", "email"]
    field_definitions1 = [f"`{field.strip()}` VARCHAR(255)" for field in fields1]
    sql1 = f"CREATE TABLE IF NOT EXISTS `users` ({', '.join(field_definitions1)}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    print("1. 不生成ID字段:")
    print(f"   字段: {fields1}")
    print(f"   SQL: {sql1}")

    # 示例2: 生成ID
    fields2 = ["title", "content"]
    field_definitions2 = [f"`{field.strip()}` VARCHAR(255)" for field in fields2]
    field_definitions2.insert(0, "`id` INT AUTO_INCREMENT PRIMARY KEY")
    sql2 = f"CREATE TABLE IF NOT EXISTS `articles` ({', '.join(field_definitions2)}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    print("\n2. 生成ID字段:")
    print(f"   字段: {fields2}")
    print(f"   SQL: {sql2}")


if __name__ == "__main__":
    print("MySQL create_table 方法测试")
    print("=" * 50)

    # 显示SQL示例
    show_sql_examples()

    # 运行测试（需要实际的数据库连接）
    print("\n" + "=" * 50)
    print("注意: 以下测试需要实际的数据库连接")
    print("请修改连接参数后再运行测试")

    # test_create_table()  # 取消注释以运行实际测试
