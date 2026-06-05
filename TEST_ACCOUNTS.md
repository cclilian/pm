# 测试账号与凭据

> 仅用于本地开发 / 联调，请勿用于生产环境。

## 应用登录账号

前端登录页：http://localhost:5173/login

| 用户名 | 密码 | 角色 | 显示名称 | 用途说明 |
|--------|------|------|----------|----------|
| `pm_test_auth` | `test123456` | pm（项目经理） | 项目经理 | 项目管理、成员与需求相关功能 |
| `pm` | `pm123456` | pm（项目经理） | 项目经理 | 项目管理、成员与需求相关功能 |
| `dev` | `dev123456` | dev（开发） | 开发工程师 | 开发与任务相关功能 |
| `test` | `test123456` | test（测试） | 测试工程师 | 测试与验收相关功能 |

密码规则：至少 6 位（见 `UserCreate` 校验）。

## 数据库（MySQL）

| 项 | 值 |
|----|-----|
| 主机 | `localhost`（WSL2 Docker，见 README 网络说明） |
| 端口 | `3306` |
| 数据库 | `agile_pm` |
| 用户名 | `root` |
| 密码 | `123456` |

连接串示例（与 `backend/.env.example` 一致）：

```env
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/agile_pm
```

## 首次写入测试用户

库表迁移完成后，若尚无用户，可在 `backend` 目录执行（需已激活虚拟环境并配置 `.env`）：

```bash
cd backend
python -c "
from app.core.database import SessionLocal
from app.schemas.user import UserCreate
from app.models.user import UserRole
from app.services import user_service

accounts = [
    UserCreate(username='pm', password='pm123456', display_name='项目经理', role=UserRole.PM),
    UserCreate(username='dev', password='dev123456', display_name='开发工程师', role=UserRole.DEV),
    UserCreate(username='test', password='test123456', display_name='测试工程师', role=UserRole.TEST),
]

db = SessionLocal()
try:
    for data in accounts:
        try:
            user_service.create_user(db, data)
            print(f'created: {data.username}')
        except user_service.UsernameExistsError:
            print(f'skip (exists): {data.username}')
finally:
    db.close()
"
```

之后可用上表任意账号登录；已存在用户会被跳过。

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-06-05 | 初始化三类角色测试账号及 MySQL 凭据 |
