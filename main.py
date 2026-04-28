"""
Random Quote Generator
GUI приложение для генерации случайных цитат с историей и фильтрацией
Автор: Габсалямов Амир Альмирович
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import os
from datetime import datetime
from typing import List, Dict, Optional


class Quote:
    """Класс для представления цитаты"""
    
    def __init__(self, text: str, author: str, topic: str):
        self.text = text
        self.author = author
        self.topic = topic
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        """Преобразование в словарь для JSON"""
        return {
            "text": self.text,
            "author": self.author,
            "topic": self.topic,
            "date": self.date
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Создание цитаты из словаря"""
        quote = cls(data["text"], data["author"], data["topic"])
        quote.date = data.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return quote


class QuoteApp:
    """Главный класс приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Предопределённые цитаты
        self.default_quotes = [
            Quote("Будь изменением, которое ты хочешь видеть в мире.", "Махатма Ганди", "мотивация"),
            Quote("Жизнь - это то, что с тобой происходит, пока ты строишь планы.", "Джон Леннон", "жизнь"),
            Quote("Успех - это способность идти от поражения к поражению, не теряя энтузиазма.", "Уинстон Черчилль", "успех"),
            Quote("Единственный способ делать великую работу - любить то, что ты делаешь.", "Стив Джобс", "работа"),
            Quote("2B or not 2B, that is the question.", "Шекспир", "литература"),
            Quote("Знание - сила.", "Фрэнсис Бэкон", "философия"),
            Quote("Вперёд, к звёздам!", "Константин Циолковский", "космос"),
            Quote("Мечтай, дерзай, твори!", "Мария Склодовская-Кюри", "мотивация"),
            Quote("Жизнь прекрасна", "Марк Туллий Цицерон", "жизнь"),
        ]
        
        # История цитат
        self.history: List[Quote] = []
        self.filtered_history: List[Quote] = []
        
        # Инициализация данных
        self.load_history()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Обновление отображения
        self.refresh_display()
    
    def setup_ui(self):
        """Создание интерфейса пользователя"""
        
        # Верхняя панель с кнопкой генерации
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(top_frame, text="🎲 Сгенерировать цитату", 
                   command=self.generate_quote, width=25).pack(pady=10)
        
        # Панель отображения текущей цитаты
        self.current_quote_frame = ttk.LabelFrame(self.root, text="Текущая цитата", padding="10")
        self.current_quote_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        self.current_quote_label = tk.Text(self.current_quote_frame, height=8, wrap=tk.WORD, font=("Arial", 12))
        self.current_quote_label.pack(fill=tk.BOTH, expand=True)
        
        # Панель фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация истории", padding="10")
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по автору:").grid(row=0, column=0, padx=5)
        self.author_filter = ttk.Entry(filter_frame, width=20)
        self.author_filter.grid(row=0, column=1, padx=5)
        self.author_filter.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        ttk.Label(filter_frame, text="Фильтр по теме:").grid(row=0, column=2, padx=5)
        self.topic_filter = ttk.Entry(filter_frame, width=20)
        self.topic_filter.grid(row=0, column=3, padx=5)
        self.topic_filter.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        ttk.Button(filter_frame, text="Сбросить фильтры", 
                   command=self.reset_filters).grid(row=0, column=4, padx=10)
        
        # Панель добавления новой цитаты
        add_frame = ttk.LabelFrame(self.root, text="Добавить новую цитату", padding="10")
        add_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(add_frame, text="Цитата:").grid(row=0, column=0, sticky=tk.W)
        self.quote_text = tk.Text(add_frame, height=3, width=50)
        self.quote_text.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky=tk.W)
        self.author_entry = ttk.Entry(add_frame, width=50)
        self.author_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Тема:").grid(row=2, column=0, sticky=tk.W)
        self.topic_entry = ttk.Entry(add_frame, width=50)
        self.topic_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(add_frame, text="➕ Добавить цитату", 
                   command=self.add_quote).grid(row=3, column=1, pady=10)
        
        # История цитат
        history_frame = ttk.LabelFrame(self.root, text="История цитат", padding="10")
        history_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Создание Treeview для отображения истории
        columns = ("Дата", "Автор", "Тема", "Цитата")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            if col == "Цитата":
                self.history_tree.column(col, width=400)
            else:
                self.history_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Нижняя панель с кнопками управления
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(bottom_frame, text="💾 Сохранить историю", 
                   command=self.save_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="🗑️ Очистить историю", 
                   command=self.clear_history).pack(side=tk.LEFT, padx=5)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(4, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
    
    def generate_quote(self):
        """Генерация случайной цитаты"""
        # Объединяем стандартные и добавленные цитаты
        all_quotes = self.default_quotes + self.history
        
        if not all_quotes:
            messagebox.showwarning("Нет цитат", "Нет доступных цитат для генерации!")
            return
        
        # Выбираем случайную цитату
        quote = random.choice(all_quotes)
        
        # Отображаем цитату
        self.display_quote(quote)
        
        # Добавляем в историю
        self.history.append(quote)
        self.apply_filters()
    
    def display_quote(self, quote: Quote):
        """Отображение цитаты в интерфейсе"""
        self.current_quote_label.delete(1.0, tk.END)
        display_text = f'"{quote.text}"\n\n— {quote.author}\nТема: {quote.topic}'
        self.current_quote_label.insert(1.0, display_text)
    
    def add_quote(self):
        """Добавление новой цитаты пользователем"""
        text = self.quote_text.get(1.0, tk.END).strip()
        author = self.author_entry.get().strip()
        topic = self.topic_entry.get().strip()
        
        # Валидация ввода
        if not text:
            messagebox.showerror("Ошибка", "Цитата не может быть пустой!")
            return
        
        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым!")
            return
        
        if not topic:
            messagebox.showerror("Ошибка", "Тема не может быть пустой!")
            return
        
        # Создаём и добавляем цитату
        new_quote = Quote(text, author, topic)
        self.history.append(new_quote)
        self.apply_filters()
        
        # Очищаем поля ввода
        self.quote_text.delete(1.0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.topic_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Цитата успешно добавлена!")
        
        # Сохраняем историю
        self.save_history()
    
    def apply_filters(self):
        """Применение фильтров к истории"""
        author_filter = self.author_filter.get().strip().lower()
        topic_filter = self.topic_filter.get().strip().lower()
        
        self.filtered_history = self.history.copy()
        
        if author_filter:
            self.filtered_history = [
                q for q in self.filtered_history 
                if author_filter in q.author.lower()
            ]
        
        if topic_filter:
            self.filtered_history = [
                q for q in self.filtered_history 
                if topic_filter in q.topic.lower()
            ]
        
        self.update_history_display()
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.author_filter.delete(0, tk.END)
        self.topic_filter.delete(0, tk.END)
        self.apply_filters()
    
    def update_history_display(self):
        """Обновление отображения истории"""
        # Очищаем текущее отображение
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавляем отфильтрованные цитаты
        for quote in self.filtered_history:
            self.history_tree.insert("", tk.END, values=(
                quote.date,
                quote.author,
                quote.topic,
                quote.text[:100] + ("..." if len(quote.text) > 100 else "")
            ))
    
    def refresh_display(self):
        """Обновление всего интерфейса"""
        self.apply_filters()
    
    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open("quotes_history.json", "w", encoding="utf-8") as f:
                json.dump([quote.to_dict() for quote in self.history], 
                         f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "История сохранена в файл quotes_history.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def load_history(self):
        """Загрузка истории из JSON файла"""
        try:
            if os.path.exists("quotes_history.json"):
                with open("quotes_history.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = [Quote.from_dict(item) for item in data]
        except Exception as e:
            print(f"Не удалось загрузить историю: {e}")
            self.history = []
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.apply_filters()
            self.save_history()
            messagebox.showinfo("Успех", "История очищена")


def main():
    """Главная функция запуска приложения"""
    root = tk.Tk()
    app = QuoteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()