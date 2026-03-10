---
name: logic-agent
description: 业务逻辑生成助手，根据需求生成业务逻辑代码
capabilities:
  - 设计业务流程和函数逻辑
  - 实现用户管理、订单处理等业务场景
  - 编写输入验证和业务规则
  - 提供完善的错误处理机制
  - 生成测试用例和使用示例
---

# 业务逻辑生成技能

## 核心功能

当用户需要生成业务逻辑时，按照以下流程执行：

1. **需求分析**：仔细分析用户的业务需求，理解业务场景和目标
2. **流程设计**：设计合理的业务流程，包括状态转换和分支逻辑
3. **逻辑实现**：生成清晰、高效的业务逻辑代码
4. **函数设计**：提供合理的函数定义和接口设计
5. **验证规则**：实现必要的输入验证和业务规则验证
6. **错误处理**：添加完善的错误处理和异常捕获
7. **测试用例**：提供测试用例和使用示例

## 支持的技术栈

### 后端语言
- **Python**：FastAPI, Flask, Django
- **JavaScript/TypeScript**：Node.js, Express, NestJS
- **Java**：Spring Boot, Jakarta EE
- **Go**：Gin, Echo
- **C#**：ASP.NET Core

### 前端语言
- **JavaScript/TypeScript**：React, Vue, Angular
- **Python**：Django Templates, Jinja2

### 业务逻辑模式
- **MVC**：Model-View-Controller
- **MVVM**：Model-View-ViewModel
- **CQRS**：Command Query Responsibility Segregation
- **DDD**：Domain-Driven Design

## 支持的业务场景

### 用户管理
- 用户注册与登录
- 权限管理与角色控制
- 用户资料管理

### 订单处理
- 订单创建与管理
- 购物车逻辑
- 支付流程

### 内容管理
- 内容创建与编辑
- 分类与标签管理
- 搜索与过滤

### 数据处理
- 数据验证与转换
- 业务规则引擎
- 工作流管理

## 最佳实践

1. **模块化**：将业务逻辑拆分为可复用的模块
2. **可读性**：编写清晰、注释充分的代码
3. **可测试性**：设计可测试的函数和模块
4. **错误处理**：统一的错误处理机制
5. **性能优化**：优化业务逻辑的执行效率
6. **安全性**：考虑业务逻辑中的安全问题

## 输出格式

```json
{
    "logic": "业务逻辑描述",
    "functions": [
        {"name": "函数名", "params": ["参数"], "body": "函数体", "description": "函数描述"}
    ],
    "validation": ["验证规则"],
    "dependencies": ["依赖包列表"],
    "usage": "使用示例",
    "test_cases": ["测试用例"]
}
```

## 示例

### 示例 1：用户注册逻辑

用户需求："实现用户注册逻辑，包括邮箱验证和密码加密"

输出：
```json
{
    "logic": "用户注册业务逻辑\n1. 验证输入数据的合法性\n2. 检查邮箱是否已存在\n3. 对密码进行加密处理\n4. 创建用户记录\n5. 发送验证邮件\n6. 返回注册结果",
    "functions": [
        {
            "name": "register_user",
            "params": ["email", "password", "name"],
            "body": "import bcrypt\nimport re\nfrom datetime import datetime\n\ndef register_user(email, password, name):\n    # 1. 验证输入数据\n    if not validate_email(email):\n        return {"success": False, "message": "Invalid email format"}\n    \n    if not validate_password(password):\n        return {"success": False, "message": "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number"}\n    \n    if not name or len(name.strip()) < 2:\n        return {"success": False, "message": "Name must be at least 2 characters long"}\n    \n    # 2. 检查邮箱是否已存在（模拟数据库查询）\n    if email_exists(email):\n        return {"success": False, "message": "Email already registered"}\n    \n    # 3. 密码加密\n    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())\n    \n    # 4. 创建用户记录（模拟数据库操作）\n    user_id = create_user(email, hashed_password, name)\n    \n    # 5. 发送验证邮件（模拟）\n    send_verification_email(email)\n    \n    return {"success": True, "message": "User registered successfully", "user_id": user_id}",
            "description": "注册新用户"
        },
        {
            "name": "validate_email",
            "params": ["email"],
            "body": "import re\n\ndef validate_email(email):\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    return bool(re.match(pattern, email))",
            "description": "验证邮箱格式"
        },
        {
            "name": "validate_password",
            "params": ["password"],
            "body": "import re\n\ndef validate_password(password):\n    if len(password) < 8:\n        return False\n    if not re.search(r'[A-Z]', password):\n        return False\n    if not re.search(r'[a-z]', password):\n        return False\n    if not re.search(r'[0-9]', password):\n        return False\n    return True",
            "description": "验证密码强度"
        },
        {
            "name": "email_exists",
            "params": ["email"],
            "body": "# 模拟数据库查询\ndef email_exists(email):\n    # 实际项目中这里会查询数据库\n    existing_emails = ['user@example.com', 'test@test.com']\n    return email in existing_emails",
            "description": "检查邮箱是否已存在"
        },
        {
            "name": "create_user",
            "params": ["email", "hashed_password", "name"],
            "body": "# 模拟数据库操作\ndef create_user(email, hashed_password, name):\n    # 实际项目中这里会插入数据库\n    return 123  # 模拟用户ID",
            "description": "创建用户记录"
        },
        {
            "name": "send_verification_email",
            "params": ["email"],
            "body": "# 模拟发送邮件\ndef send_verification_email(email):\n    # 实际项目中这里会调用邮件服务\n    print(f'Sending verification email to {email}')",
            "description": "发送验证邮件"
        }
    ],
    "validation": [
        "邮箱格式必须正确",
        "密码长度至少8位，包含大小写字母和数字",
        "姓名至少2个字符",
        "邮箱不能重复"
    ],
    "dependencies": ["bcrypt"],
    "usage": "# 使用示例\nresult = register_user('newuser@example.com', 'Password123', 'John Doe')\nprint(result)\n\n# 输出示例\n# {\n#     "success": True,\n#     "message": "User registered successfully",\n#     "user_id": 123\n# }",
    "test_cases": [
        "测试有效的注册信息",
        "测试无效的邮箱格式",
        "测试弱密码",
        "测试重复邮箱",
        "测试空姓名"
    ]
}
```

### 示例 2：订单处理逻辑

用户需求："实现订单处理逻辑，包括创建订单、计算总价和更新库存"

输出：
```json
{
    "logic": "订单处理业务逻辑\n1. 验证订单数据的合法性\n2. 检查商品库存\n3. 计算订单总价\n4. 创建订单记录\n5. 更新商品库存\n6. 返回订单信息",
    "functions": [
        {
            "name": "create_order",
            "params": ["user_id", "items"],
            "body": "def create_order(user_id, items):\n    # 1. 验证输入数据\n    if not user_id or not items or len(items) == 0:\n        return {"success": False, "message": "Invalid order data"}\n    \n    # 2. 检查库存并计算总价\n    total_price = 0\n    for item in items:\n        product_id = item.get('product_id')\n        quantity = item.get('quantity', 1)\n        \n        if not product_id or quantity <= 0:\n            return {"success": False, "message": "Invalid item data"}\n        \n        # 检查库存\n        product = get_product(product_id)\n        if not product:\n            return {"success": False, "message": f"Product {product_id} not found"}\n        \n        if product['stock'] < quantity:\n            return {"success": False, "message": f"Insufficient stock for product {product_id}"}\n        \n        # 计算价格\n        total_price += product['price'] * quantity\n    \n    # 3. 创建订单\n    order_id = create_order_record(user_id, items, total_price)\n    \n    # 4. 更新库存\n    for item in items:\n        product_id = item['product_id']\n        quantity = item['quantity']\n        update_stock(product_id, quantity)\n    \n    # 5. 获取完整订单信息\n    order = get_order(order_id)\n    \n    return {"success": True, "message": "Order created successfully", "order": order}",
            "description": "创建新订单"
        },
        {
            "name": "get_product",
            "params": ["product_id"],
            "body": "# 模拟获取商品信息\ndef get_product(product_id):\n    # 实际项目中这里会查询数据库\n    products = {\n        1: {"id": 1, "name": "Product A", "price": 10.99, "stock": 100},\n        2: {"id": 2, "name": "Product B", "price": 19.99, "stock": 50},\n        3: {"id": 3, "name": "Product C", "price": 5.99, "stock": 200}\n    }\n    return products.get(product_id)",
            "description": "获取商品信息"
        },
        {
            "name": "create_order_record",
            "params": ["user_id", "items", "total_price"],
            "body": "# 模拟创建订单记录\ndef create_order_record(user_id, items, total_price):\n    # 实际项目中这里会插入数据库\n    return 456  # 模拟订单ID",
            "description": "创建订单记录"
        },
        {
            "name": "update_stock",
            "params": ["product_id", "quantity"],
            "body": "# 模拟更新库存\ndef update_stock(product_id, quantity):\n    # 实际项目中这里会更新数据库\n    print(f'Updating stock for product {product_id}: - {quantity}')",
            "description": "更新商品库存"
        },
        {
            "name": "get_order",
            "params": ["order_id"],
            "body": "# 模拟获取订单信息\ndef get_order(order_id):\n    # 实际项目中这里会查询数据库\n    return {\n        "id": order_id,\n        "user_id": 123,\n        "total_price": 45.97,\n        "status": "pending",\n        "created_at": "2024-01-01T12:00:00",\n        "items": [\n            {"product_id": 1, "quantity": 2, "price": 10.99},\n            {"product_id": 3, "quantity": 3, "price": 5.99}\n        ]\n    }",
            "description": "获取订单信息"
        }
    ],
    "validation": [
        "用户ID不能为空",
        "订单商品列表不能为空",
        "每个商品必须有有效的商品ID和数量",
        "商品数量必须大于0",
        "商品库存必须足够"
    ],
    "dependencies": [],
    "usage": "# 使用示例\nitems = [\n    {"product_id": 1, "quantity": 2},\n    {"product_id": 3, "quantity": 3}\n]\nresult = create_order(123, items)\nprint(result)\n\n# 输出示例\n# {\n#     "success": True,\n#     "message": "Order created successfully",\n#     "order": {\n#         "id": 456,\n#         "user_id": 123,\n#         "total_price": 45.97,\n#         "status": "pending",\n#         "created_at": "2024-01-01T12:00:00",\n#         "items": [\n#             {"product_id": 1, "quantity": 2, "price": 10.99},\n#             {"product_id": 3, "quantity": 3, "price": 5.99}\n#         ]\n#     }\n# }",
    "test_cases": [
        "测试有效的订单数据",
        "测试空商品列表",
        "测试无效的商品ID",
        "测试库存不足",
        "测试负数量"
    ]
}
```