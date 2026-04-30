import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

# --- Глобальные переменные ---
trainings = []  # Список для хранения данных о тренировках

# --- Функции для работы с данными ---

def load_data():
    """Загружает данные о тренировках из файла trainings.json, если он существует."""
    global trainings
    if os.path.exists("trainings.json"):
        try:
            with open("trainings.json", "r", encoding="utf-8") as f:
                trainings = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {e}")
            trainings = []
    else:
        trainings = []

def save_data():
    """Сохраняет текущий список тренировок в файл trainings.json."""
    try:
        with open("trainings.json", "w", encoding="utf-8") as f:
            json.dump(trainings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка сохранения данных: {e}")

# --- Функции для валидации и логики ---

def validate_input(date_str, duration_str):
    """Проверяет корректность введённых даты и длительности тренировки."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректный формат даты (используйте ГГГГ-ММ-ДД)")
        return False

    try:
        duration = float(duration_str)
        if duration <= 0:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
            return False
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректный формат длительности")
        return False

    return True

def add_training():
    """Обрабатывает добавление новой тренировки в список и обновляет интерфейс."""
    date_str = date_entry.get()
    training_type = type_combo.get()
    duration_str = duration_entry.get()

    if not all([date_str, training_type, duration_str]):
        messagebox.showerror("Ошибка", "Заполните все поля")
        return

    if not validate_input(date_str, duration_str):
        return

    training = {
        "id": len(trainings) + 1,
        "date": date_str,
        "type": training_type,
        "duration": float(duration_str)
    }

    trainings.append(training)
    save_data()
    refresh_table()
    clear_input()

def clear_input():
    """Очищает поля ввода после добавления тренировки."""
    date_entry.delete(0, tk.END)
    type_combo.set("")
    duration_entry.delete(0, tk.END)

# --- Функции для отображения и фильтрации ---

def refresh_table(data_to_display=None):
    """Обновляет таблицу с тренировками.
    Если передан аргумент data_to_display, отображает его. Иначе — выводит весь список."""
    # Очищаем текущую таблицу
    for item in tree.get_children():
        tree.delete(item)

    # Определяем, какие данные выводить
    display_data = data_to_display if data_to_display is not None else trainings

    # Заполняем таблицу данными
    for training in display_data:
        tree.insert("", "end", values=(
            training["id"],
            training["date"],
            training["type"],
            f"{training['duration']:.0f}"  # Длительность без десятичных знаков
        ))

def apply_filter():
    """Применяет фильтры по типу и дате к списку тренировок и обновляет таблицу."""
    filtered = trainings.copy()

    # Фильтр по типу тренировки
    type_filter = filter_type.get()
    if type_filter != "Все":
        filtered = [t for t in filtered if t["type"] == type_filter]

    # Фильтр по дате (начало периода)
    start_date_str = start_date_entry.get()
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            filtered = [t for t in filtered if datetime.strptime(t["date"], "%Y-%m-%d") >= start_date]
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат начальной даты")
            return

    # Фильтр по дате (конец периода)
    end_date_str = end_date_entry.get()
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            filtered = [t for t in filtered if datetime.strptime(t["date"], "%Y-%m-%d") <= end_date]
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат конечной даты")
            return

    refresh_table(filtered)

def clear_filter():
    """Сбрасывает все фильтры и обновляет таблицу, показывая все тренировки."""
    filter_type.set("Все")
    start_date_entry.delete(0, tk.END)
    end_date_entry.delete(0, tk.END)
    refresh_table()

# --- Создание главного окна приложения ---
root = tk.Tk()
root.title("Training Planner")
root.geometry("800x600")

# Загружаем данные при запуске программы
load_data()

# --- Создание интерфейса ---

# Фрейм для ввода данных о новой тренировке
input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
date_entry = ttk.Entry(input_frame)
date_entry.grid(row=0, column=1, padx=5)

ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5)
type_combo = ttk.Combobox(
    input_frame,
    values=["Кардио", "Силовая", "Йога", "Растяжка", "Функциональная"]
)
type_combo.grid(row=0, column=3, padx=5)

ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5)
duration_entry = ttk.Entry(input_frame)
duration_entry.grid(row=0, column=5, padx=5)

add_button = ttk.Button(input_frame, text="Добавить тренировку", command=add_training)
add_button.grid(row=0, column=6, padx=5)

# Таблица для отображения списка тренировок
columns = ("ID", "Дата", "Тип тренировки", "Длительность (мин)")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(padx=10, pady=10, fill="both", expand=True)
refresh_table()  # Первоначальное заполнение таблицы данными

# Фрейм для фильтрации списка тренировок
filter_frame = ttk.Frame(root)
filter_frame.pack(pady=10)

ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5)
filter_type = ttk.Combobox(
    filter_frame,
    values=["Все"] + ["Кардио", "Силовая", "Йога", "Растяжка", "Функциональная"]
)
filter_type.set("Все")
filter_type.grid(row=0, column=1, padx=5)

ttk.Label(filter_frame, text="С даты (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
start_date_entry = ttk.Entry(filter_frame)
start_date_entry.grid(row=0, column=3, padx=5)

ttk.Label(filter_frame, text="По дату (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
end_date_entry = ttk.Entry(filter_frame)
end_date_entry.grid(row=0, column=5, padx=5)

filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=apply_filter)
filter_button.grid(row=0, column=6, padx=5)

clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=clear_filter)
clear_filter_button.grid(row=0, column=7, padx=5)

# Запуск основного цикла приложения
root.mainloop()