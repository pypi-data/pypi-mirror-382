from wauo.db import PostgresqlClient


def test():
    psql = PostgresqlClient(
        host='localhost',
        port=5432,
        db='test',
        user='wauo',
        password='admin1'
    )
    psql.connect()

    items = psql.fetchall("SELECT * FROM test limit 5")
    for item in items:
        print(dict(item))

    # data = {'name': 'Alice', 'age': 30}
    # inserted_rows = psql.insert_one('test', data)
    # print(f"插入的行数: {inserted_rows}")

    # datas = [{'name': f'Test-{i}'} for i in range(3)]
    # inserted_rows = psql.insert_many('test', datas)
    # print(f"批量插入的行数: {inserted_rows}")

    # n = psql.update(
    #     'test', {'name': '11'},
    #     "id < %s and gender='男'", (10,)
    # )
    # print(f"更新的行数: {n}")

    # d = psql.delete('test', "name='11'")
    # print(f"删除的行数: {d}")

    name = 'test_user'
    psql.create_table(name, ['name', 'gender'])
    n = psql.insert_one(name, {'Name': 'clos', 'gender': 'man'})
    print(f"插入的行数: {n}")


if __name__ == '__main__':
    test()
