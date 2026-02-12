# check.py — синхронный вариант (рекомендую запустить именно его первым)
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
#
# # Три самых вероятных варианта пути (выбери один)
# DATABASE_URL = "sqlite:///app.db"  # относительно текущей папки запуска
# # DATABASE_URL = "sqlite:///./app.db"                 # то же самое, но с явной точкой
# # DATABASE_URL = r"sqlite:///D:\Projects1\portfolio\cms_uni\app.db"   # абсолютный путь — самый надёжный
#
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
#
# SessionLocal = sessionmaker(bind=engine)
#
# try:
#     with SessionLocal() as session:
#         result = session.execute(text("SELECT 1"))
#         print("Подключение успешно! База найдена.")
#         print("Результат:", result.scalar_one())
# except Exception as e:
#     print("Ошибка подключения:", str(e))


import os

print("Проверка переменных окружения:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'не установлена')}")

if os.getenv("DATABASE_URL"):
    url = os.getenv("DATABASE_URL")
    print(f"Длина: {len(url)}")
    print(f"Содержимое: {repr(url)}")

    # Проверим символы
    for i, char in enumerate(url):
        if ord(char) > 127:  # Не-ASCII символ
            print(f"Не-ASCII символ на позиции {i}: '{char}' (код: {ord(char)})")
