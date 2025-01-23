import importlib
from sqlalchemy import create_engine, Column, Integer, inspect, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///db.sqlite3"  # Путь к базе данных
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_column_if_not_exists(column, table_name: str):
    # Проверяем существующие колонки в таблице
    with engine.begin() as conn:
        inspector = inspect(engine)
        existing_columns = {col["name"] for col in inspector.get_columns(table_name)}

        # Если колонки нет, то добавляем
        if column.name not in existing_columns:
            column_type = column.type
            default_value = column.default.arg if column.default else None
            nullable = "NULL" if column.nullable else "NOT NULL"
            
            # Формируем запрос на добавление колонки
            query = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {column_type} "
            if default_value is not None:
                query += f"DEFAULT {default_value} "
            query += f"{nullable}"
            
            # Выполняем запрос
            conn.execute(text(query))
            print(f"Колонка {column.name} добавлена в таблицу {table_name}.")

def update_database(model_path, column_name):
    # Динамически импортируем модель
    module_name, class_name = model_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    model_class = getattr(module, class_name)

    # Ищем колонку в модели по имени
    column = None
    for col in model_class.__table__.columns:
        if col.name == column_name:
            column = col
            break

    if column is not None:
        add_column_if_not_exists(column, model_class.__tablename__)
    else:
        print(f"Колонка {column_name} не найдена в модели {model_class.__name__}.")

if __name__ == "__main__":
    update_database('app.database.models.User', 'name')
