from tea.handlers import app
from tea.db import init_db

init_db()

app.run()