"""
简单的 .env 配置示例

展示如何在外部项目中使用 PyAdvanceKit 的 .env 配置功能
"""

# 方式1: 最简单的使用方式
from pyadvincekit import create_app_from_env

# 自动查找 .env 文件并创建应用
app = create_app_from_env(
    app_title="我的应用",
    app_description="使用 .env 配置的简单应用"
)

# 添加一个简单的路由
@app.get("/")
async def root():
    return {"message": "Hello from PyAdvanceKit with .env config!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

