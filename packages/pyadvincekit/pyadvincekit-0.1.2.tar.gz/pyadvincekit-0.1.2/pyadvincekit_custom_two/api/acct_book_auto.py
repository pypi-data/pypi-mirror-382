#!/usr/bin/env python3
"""
账务登记表 API 接口（自动生成方式）

使用 PyAdvanceKit 的 auto_generate_api 自动生成完整的 CRUD 接口
"""

import sys
from pathlib import Path

# PyAdvanceKit Admin Backend 的标准做法
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from pyadvincekit import auto_generate_api
from models.t_mntx_acct_book import TMntxAcctBook


# 注意：auto_generate_api 会自动基于 ORM 模型生成所需的 Pydantic schemas
# 无需手动导入 TMntxAcctBookCreate, TMntxAcctBookUpdate 等

# 🚀 使用 PyAdvanceKit 自动生成完整的 CRUD 接口
acct_book_auto_router = auto_generate_api(
    model_class=TMntxAcctBook,                    # 正确的参数名
    router_prefix="/api/acct-book/auto",          # 路由前缀
    tags=["账务登记（自动生成）"],                  # API 标签
    include_endpoints=[                           # 包含的端点
        "create", "get", "query", "update", 
        "delete", "count", "exists", "restore"
    ]
)

"""
auto_generate_api 自动生成的接口：

基于 TMntxAcctBook ORM 模型，PyAdvanceKit 会自动生成：

 POST /api/acct-book/auto/create     - 创建账务登记
 POST /api/acct-book/auto/get        - 获取单个账务登记  
 POST /api/acct-book/auto/query      - 查询账务登记列表
 POST /api/acct-book/auto/update     - 更新账务登记
 POST /api/acct-book/auto/delete     - 删除账务登记
 POST /api/acct-book/auto/count      - 统计账务登记数量
 POST /api/acct-book/auto/exists     - 检查记录是否存在
 POST /api/acct-book/auto/restore    - 恢复软删除记  
特点：
-  完全自动化：基于 ORM 模型自动推断 Pydantic schemas
-  统一格式：所有接口使用 PyAdvanceKit 标准 POST 风格
-  自动文档：FastAPI 自动生成 Swagger 文档
- ️ 类型安全：自动参数验证和类型检查
-  标准响应：统一的三层响应格式 (sysHead, appHead, body)

适用场景：
- 🚀 快速原型开发
- 📊 标准业务表的 CRUD 操作
- 🔧 减少样板代码
"""
