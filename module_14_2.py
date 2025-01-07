import sqlite3

connection = sqlite3.connect('not_telegram_14_2.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER,
        balance INTEGER NOT NULL
    )
''')

for i in range(1, 11):
    cursor.execute(
        'INSERT INTO Users (username, email, age, balance) '
        'VALUES (?, ?, ?, ?)',
        (f'User{i}', f'example{i}@gmail.com', i * 10, 1000))

cursor.execute("SELECT id FROM Users")
ids = cursor.fetchall()

for i in range(len(ids)):
    if (i + 1) % 2:  # каждая 2-я запись начиная с 1-й
        cursor.execute(
            'UPDATE Users SET balance = 500 WHERE id = ?',
            (ids[i][0],))

for i in range(len(ids)):
    if (i + 1) % 3 == 1:  # каждая 3-я запись начиная с 1-й
        cursor.execute(
            'DELETE FROM Users WHERE id = ?',
            (ids[i][0],))

cursor.execute('DELETE FROM Users WHERE id = ?', (6,))

cursor.execute('SELECT COUNT(*) FROM Users')
total_users = cursor.fetchone()[0]

cursor.execute('SELECT SUM(balance) FROM Users')
all_balances = cursor.fetchone()[0]

print(all_balances / total_users)

connection.commit()
connection.close()
