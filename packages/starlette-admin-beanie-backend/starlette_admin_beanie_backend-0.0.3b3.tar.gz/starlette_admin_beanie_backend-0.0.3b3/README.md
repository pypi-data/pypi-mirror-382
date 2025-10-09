# starlette-admin-beanie-backend

🧪 A work-in-progress package to use Beanie-ODM as a backend with starlette-admin.

## 🔧 Install (when released)
```bash
  pip install starlette-admin-beanie-backend
```

## ⚙️ Usage
```python
from starlette_admin_beanie_backend import Admin, ModelView
from .auth import AdminAuthProvider
from .models import User

def set_db_admin(app):
    # Create the Admin Interface
    admin = Admin(
        title="Test App",
        base_url="/admin",
        debug=True,
        auth_provider=AdminAuthProvider(),
    )
    
    # Add the Admin Views
    admin.add_view(ModelView(User, icon="fa fa-users"))

    # Mount app
    admin.mount_to(app)
```

## 🤝 Contribute
Contributions are welcome! Whether you’ve spotted a bug, have ideas to improve the Package, or want to extend functionality — I’d love your input. Please fork the repository, work on the dev-colab branch, and open a pull request when ready. Be sure to include clear commit messages and tests where applicable. Let’s build something great together!

- Submit PRs to `dev-colab`
- Please follow the coding style
---

## 🙏🏼 Credits
- jowilf (https://github.com/jowilf)
- BeanieODM (https://github.com/BeanieODM)
- pydantic (https://github.com/pydantic)
