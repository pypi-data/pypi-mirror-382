# 🧱 SQLMorph: Migrations & Schema Visualization for SQLModel and SQLAlchemy

> **SQLMorph** — Zero-config migrations, schema inspection, and ER diagram generation for SQLModel **and** SQLAlchemy.  
> No boilerplate. No manual scripts. Just magic. ⚡

[![PyPI version](https://img.shields.io/pypi/v/sqlmorph.svg)](https://pypi.org/project/sqlmorph/)
[![License](https://img.shields.io/github/license/yourusername/sqlmorph)](LICENSE)

---

## ✨ Why SQLMorph?

| Feature | Alembic | SQLMorph |
|----------|----------|----------|
| Auto-detects model changes | ❌ | ✅ |
| Zero configuration | ❌ | ✅ |
| Schema health check | ❌ | ✅ |
| ER diagram generator | ❌ | ✅ |
| Live migration watch | ❌ | ✅ |
| Works with SQLAlchemy + SQLModel | ✅ | ✅ |
| Interactive shell | ❌ | ✅ |
| JSON + Mermaid export | ❌ | ✅ |

---

## 🚀 Features

SQLMorph is more than just a migration tool — it’s a **complete database companion** for your ORM projects.

- 🚀 **Zero-Config Migrations**: Automatically detects schema changes and generates migration scripts.
- 🩺 **Schema Health Checks**: Detects drift between your models and the database.
- 📝 **Safe Planning**: Preview SQL changes before migrating.
- 🔍 **Advanced Inspection**: View models and relationships as tables or JSON.
- 🎨 **Auto Diagrams**: Generate Mermaid.js ERDs directly from your models.
- 🌱 **Data Seeding**: Load seed data via JSON or YAML.
- 👀 **Live Watch Mode**: Automatically detect model changes.
- 🔧 **Reverse Engineering**: Generate ORM classes from existing DBs.
- 🗄️ **Interactive Shell**: Native database shell integration.
- 🧠 **SQLAlchemy + SQLModel**: Full compatibility with both ORMs.

---

## 📦 Installation

```bash
pip install -e .
# For shell command support on Debian/Ubuntu
sudo apt update && sudo apt install sqlite3
```

---

## ⚡ Quick Start

### Define your models

```python
# models.py
from typing import Optional
from sqlmorph import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
```

### Create your first migration

```bash
sqlmorph makemigration "create_user_table" --models models.py
sqlmorph migrate
```

### Make changes and apply them

```python
# models.py
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str  # <-- new field
```

```bash
sqlmorph plan
sqlmorph makemigration "add_email_to_user"
sqlmorph migrate
```

---

## 🧠 Works with SQLAlchemy Too

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")
```

Both ORM types work seamlessly.

---

## 🧰 Command Reference

| Command | Description |
|----------|--------------|
| `makemigration <name>` | Generate migration script for detected schema changes |
| `migrate` | Apply pending migrations |
| `rollback` | Undo the last migration |
| `plan` | Preview upcoming SQL operations |
| `doctor` | Detect drift between DB and models |
| `inspect` | Show model tables and relationships |
| `diagram` | Generate Mermaid.js ER diagrams |
| `snapshot` | Save current schema state |
| `explain <query>` | Analyze query performance |
| `seed --file <path>` | Load seed data from JSON/YAML |
| `watch` | Monitor models for changes |
| `diffdb --url <db_url>` | Reverse engineer SQLModel from DB |
| `shell` | Open database shell |
| `help` | Show command reference |

---

## 🧪 CI/CD Example

```yaml
- name: Validate Schema
  run: |
    pip install sqlmorph
    sqlmorph doctor
```

---

## 🧩 How It Works

SQLMorph introspects your ORM metadata (`SQLModel.metadata` or `Base.metadata`), snapshots its structure, and generates safe migration plans.  
All migrations are **explicit**, **auditable**, and **reversible**.

---

## 🛠️ Roadmap

- [ ] Plugin system for lifecycle hooks  
- [ ] Cloud schema diff dashboard  
- [ ] FastAPI integration helpers  
- [ ] Visual web UI for migration planning  

---

## 🧑‍💻 Contributing

Pull requests are welcome! Please run tests before submitting:
```bash
pytest
```

---

## 📜 License

MIT License © 2025 SQLMorph Contributors
