# EleganPlot 🎨

**EleganPlot** — это элегантная надстройка над Matplotlib для создания красивых и стильных визуализаций в Python. Библиотека предоставляет систему тем, кастомные методы построения графиков и специальные эффекты для создания профессиональных визуализаций.

## ✨ Основные возможности

- **🎭 Система тем** — предустановленные и кастомные темы оформления
- **🌟 Эффекты свечения** — создание линий с эффектом glow 
- **🌈 Градиентные заливки** — заливка под кривыми с градиентом
- **🎨 Градиентные фоны** — фигуры с красивым градиентным фоном
- **🔧 Кастомные методы** — легкое расширение функциональности
- **📊 Готовые компоненты** — доверительные интервалы, мультилинии и другое
- **🎯 Простой API** — знакомый интерфейс в стиле matplotlib

## 📦 Установка

```bash
pip install eleganplot
```

Или для разработки:
```bash
git clone https://github.com/yourusername/eleganplot.git
cd eleganplot
pip install -e .
```

## 🚀 Быстрый старт

```python
import eleganplot as eplt
import numpy as np

# Создаём данные
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

# Простой график с темой
fig, ax = eplt.subplots()
ax.plot(x, y, label='sin(x)')
ax.legend()
eplt.show()
```

## 🎨 Система тем

```python
import eleganplot as eplt

# Просмотр доступных тем
print(eplt.list_themes())

# Установка темы
eplt.set_current_theme('dark')

# Создание графика с темой
fig, ax = eplt.subplots()
ax.plot(x, y)
eplt.show()
```

## 🌟 Эффект свечения (Glow)

Создание линий с эффектом свечения:

```python
fig, ax = eplt.subplots()

# Базовое свечение
main_line, glow_lines = ax.glow_line(x, y, 
                                    glow_color='cyan', 
                                    glow_width=5.0)

# Продвинутое свечение с настройками
main_line, glow_lines = ax.glow_line(x, y,
                                    glow_color='orange',
                                    glow_width=8.0,
                                    glow_alpha=0.7,
                                    glow_layers=20,
                                    decay_function='gaussian')
eplt.show()
```

### Функции затухания
- `'linear'` — линейное затухание
- `'exponential'` — экспоненциальное затухание  
- `'gaussian'` — гауссово затухание (по умолчанию)
- `'quadratic'` — квадратичное затухание
- `'cubic'` — кубическое затухание
- `'sine'` — синусоидальное затухание

## 🌈 Градиентные заливки

```python
fig, ax = eplt.subplots()

# Градиентная заливка под кривой
line, gradient = ax.gradient_plot(x, y, 
                                 fill_color='blue', 
                                 alpha_coef=0.7)

# Градиент до минимума осей
line, gradient = ax.gradient_plot(x, y, 
                                 fill_color='red',
                                 gradient_to_min=True)
eplt.show()
```

## 🎭 Градиентный фон

Создание графиков с красивым градиентным фоном:

```python
# Простое использование с настройками по умолчанию
fig, ax = eplt.gradient_subplots(dpi=200)
ax.plot(x, y, linewidth=2, label='sin(x)')
ax.set_title('График с градиентным фоном')
ax.legend()
eplt.show()

# С кастомными цветами градиента
fig, ax = eplt.gradient_subplots(
    figsize=(10, 6),
    dpi=200,
    gradient_colors=("#1a0033", "#330066"),  # Фиолетовый градиент
)
ax.plot(x, y, color='#FF6B9D', linewidth=2)
eplt.show()
```

### Готовые цветовые схемы
- **Тёмный сине-зелёный:** `("#00080a", "#042628")` (по умолчанию)
- **Фиолетовый:** `("#1a0033", "#330066")`
- **Зелёный:** `("#002200", "#004400")`
- **Синий:** `("#000033", "#001166")`

## 🔧 Кастомные методы

### Использование готовых методов

```python
fig, ax = eplt.subplots()

# Доверительная полоса
y_mean = np.sin(x)
y_std = 0.2 * np.ones_like(x)
ax.confidence_band(x, y_mean, y_std, confidence=0.95)

# Несколько линий
y_data = [np.sin(x), np.cos(x), np.tan(x/4)]
ax.multi_line(x, y_data, 
              labels=['sin', 'cos', 'tan'],
              colors=['red', 'blue', 'green'])
eplt.show()
```

### Создание собственных методов

```python
from eleganplot import custom_axes_method

@custom_axes_method("my_plot")
def my_custom_plot(ax, x, y, style='fancy', **kwargs):
    """Мой кастомный метод построения графиков."""
    if style == 'fancy':
        return ax._ax.plot(x, y, marker='o', linestyle='--', **kwargs)
    else:
        return ax._ax.plot(x, y, **kwargs)

# Использование
fig, ax = eplt.subplots()
ax.my_plot(x, y, style='fancy', color='purple')
eplt.show()
```

## 📊 Примеры использования

### Научные графики

```python
import eleganplot as eplt
import numpy as np

# Данные эксперимента
x = np.linspace(0, 10, 50)
y_true = 2 * np.exp(-x/3) * np.sin(x)
y_measured = y_true + 0.1 * np.random.randn(50)
y_error = 0.1 * np.ones_like(x)

# График с доверительным интервалом
fig, ax = eplt.subplots(figsize=(10, 6))
ax.confidence_band(x, y_measured, y_error, 
                   confidence=0.95, 
                   label='Измерения ±σ')
ax.plot(x, y_true, 'r--', label='Теория', linewidth=2)
ax.legend()
ax.set_title('Экспериментальные данные с доверительным интервалом')
eplt.show()
```

### Эффектные презентационные графики

```python
# Тёмная тема с эффектами свечения
eplt.set_current_theme('dark')

fig, ax = eplt.subplots(figsize=(12, 8))

# Несколько линий с свечением
colors = ['cyan', 'magenta', 'yellow', 'lime']
for i, color in enumerate(colors):
    y = np.sin(x + i*np.pi/4) * np.exp(-x/8)
    ax.glow_line(x, y, 
                glow_color=color,
                glow_width=6.0,
                glow_alpha=0.8,
                linewidth=2)

ax.set_title('Эффектные линии с свечением', fontsize=16)
eplt.show()
```

## 📁 Структура проекта

```
eleganplot/
├── src/eleganplot/
│   ├── __init__.py          # Основные экспорты
│   ├── pyplot.py            # Обёртки matplotlib
│   ├── theme.py             # Система тем
│   └── utils/
│       ├── custom_methods.py # Готовые кастомные методы
│       ├── decorators.py     # Система декораторов
│       ├── glow.py          # Эффекты свечения
│       └── gradient.py      # Градиентные заливки
├── examples/                # Примеры использования
└── docs/                   # Документация
```

## 📚 Документация

### 🎨 [Галерея визуализаций](docs/GALLERY.md)
Коллекция примеров с изображениями и кодом

### Полные руководства
- [Руководство по эффектам свечения](docs/GLOW_LINE_GUIDE.md) - эффект glow для линий
- [Руководство по градиентным фонам](docs/GRADIENT_BACKGROUND_GUIDE.md) - создание графиков с градиентным фоном
- [Система кастомных методов](docs/CUSTOM_METHODS.md) - расширение функциональности
- [Руководство по комбинированию методов](docs/COMBINATION_GUIDE.md) - комбинация различных эффектов

### Быстрые справки
- [Быстрый старт: gradient_subplots](docs/GRADIENT_SUBPLOTS_QUICKSTART.md) - краткая шпаргалка
- [Итоги: gradient_subplots](docs/GRADIENT_SUBPLOTS_SUMMARY.md) - сводка возможностей

### 📖 [Оглавление документации](docs/README.md)
Полный указатель всех материалов

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие EleganPlot! 

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License — смотрите файл [LICENSE](LICENSE) для деталей.

## 🔗 Зависимости

- Python >= 3.9
- matplotlib >= 3.7
- numpy (через matplotlib)

## 📈 Версии

**v0.1.0** (текущая)
- Базовая система тем
- Эффекты свечения для линий
- Градиентные заливки
- Градиентные фоны (gradient_subplots)
- Система кастомных методов
- Готовые компоненты (доверительные интервалы, мультилинии)

## 👨‍💻 Автор

**Alex Frauch**

---

**EleganPlot** — делаем визуализацию данных элегантной! ✨
