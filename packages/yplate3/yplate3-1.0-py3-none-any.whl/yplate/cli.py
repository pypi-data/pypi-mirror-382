import os
import sys

BASE_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Yplate — базовая страница</title>
<link rel="icon" href="https://cdn.itrypro.ru/yplate.png" type="image/png">
<style>
body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    color: #fff; display:flex; justify-content:center; align-items:center;
    height:100vh; flex-direction:column;
}
h1 { font-weight: 700; margin-bottom: 10px; }
p { color: #aaa; }
</style>
</head>
<body>
<h1>Добро пожаловать в Yplate 💎</h1>
<p>Это базовая страница. Проект успешно создан!</p>
</body>
</html>
"""

INDEX_TEMPLATE = """from yplate import Yplate

app = Yplate()

@app.route("/")
def home():
    return open("main/content/base.html", "r", encoding="utf-8").read()

if __name__ == "__main__":
    app.run()
"""

SETTINGS_TEMPLATE = """# Настройки Yplate
DEBUG = True
PORT = 8000
"""

ROUTES_TEMPLATE = """from yplate import Yplate
app = Yplate()

@app.route("/about")
def about():
    return "<h1>О проекте Yplate</h1><p>Лёгкий Python-фреймворк для веба</p>"
"""

def create_project(name):
    if os.path.exists(name):
        print(f"❌ Папка '{name}' уже существует!")
        return

    os.makedirs(f"{name}/site", exist_ok=True)
    os.makedirs(f"{name}/main/content", exist_ok=True)

    with open(f"{name}/index.py", "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE)

    with open(f"{name}/site/settings.py", "w", encoding="utf-8") as f:
        f.write(SETTINGS_TEMPLATE)

    with open(f"{name}/main/routes.py", "w", encoding="utf-8") as f:
        f.write(ROUTES_TEMPLATE)

    with open(f"{name}/main/content/base.html", "w", encoding="utf-8") as f:
        f.write(BASE_PAGE)

    with open(f"{name}/main/content/style.css", "w", encoding="utf-8") as f:
        f.write("body { font-family: sans-serif; }")

    print(f"✅ Проект '{name}' успешно создан!")
    print("👉 Запусти: cd", name)
    print("👉 Затем: python index.py")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "start":
        project_name = sys.argv[2]
        create_project(project_name)
    else:
        print("Использование: python -m yplate.cli start <имя_проекта>")
