from tea.handlers import app
from tea.db import init_db

init_db()

if __name__ == "__main__":
    app.run('0.0.0.0', 5000)
