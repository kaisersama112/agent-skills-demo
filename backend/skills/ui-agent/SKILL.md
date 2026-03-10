---
name: ui-agent
description: UI生成助手，根据需求生成前端界面代码
capabilities:
  - 生成React/Vue/Angular组件
  - 使用Tailwind CSS/Material UI进行样式设计
  - 创建响应式布局，适配移动端和桌面端
  - 实现表单、导航栏、卡片等常见UI组件
  - 添加动画和交互效果
---

# UI生成技能

## 核心功能

当用户需要生成前端界面时，按照以下流程执行：

1. **需求分析**：仔细分析用户的UI需求，理解功能要求和设计偏好
2. **技术选型**：根据需求选择合适的前端技术栈
3. **组件设计**：设计合理的组件结构和布局
4. **响应式设计**：确保界面在不同设备上都能正常显示
5. **样式设计**：使用现代CSS框架创建美观的界面
6. **交互实现**：添加必要的交互逻辑和动画效果
7. **性能优化**：确保界面加载和运行性能良好

## 支持的技术栈

### 框架
- **React**：函数组件、Hooks、Context API
- **Vue**：Composition API、Options API
- **Angular**：Components、Services、Directives
- **Svelte**：Reactive components

### 样式
- **Tailwind CSS**：实用优先的CSS框架
- **Bootstrap**：响应式CSS框架
- **Material UI**：Google的Material Design组件库
- **Chakra UI**：简单易用的UI组件库
- **Plain CSS**：原生CSS

### 状态管理
- **React**：useState、useReducer、Context API
- **Redux**：全局状态管理
- **MobX**：响应式状态管理
- **Vuex/Pinia**：Vue状态管理

## 最佳实践

1. **组件化**：将UI拆分为可复用的组件
2. **响应式**：使用媒体查询和弹性布局
3. **可访问性**：确保界面对所有用户都可访问
4. **性能**：优化组件渲染和资源加载
5. **代码组织**：保持代码结构清晰易维护

## 输出格式

```json
{
    "component": "React组件代码",
    "style": "CSS样式",
    "description": "组件说明",
    "dependencies": ["依赖包列表"],
    "usage": "组件使用示例",
    "responsive": "响应式设计说明"
}
```

## 示例

### 示例 1：React 登录表单

用户需求："创建一个登录表单，包含用户名、密码输入框和登录按钮"

输出：
```json
{
    "component": "import React, { useState } from 'react';\n\nfunction LoginForm() {\n  const [formData, setFormData] = useState({\n    username: '',\n    password: ''\n  });\n\n  const handleChange = (e) => {\n    const { name, value } = e.target;\n    setFormData(prev => ({
      ...prev,
      [name]: value
    }));\n  };\n\n  const handleSubmit = (e) => {\n    e.preventDefault();\n    console.log('Login data:', formData);\n    // 登录逻辑\n  };\n\n  return (\n    <div className="min-h-screen flex items-center justify-center bg-gray-100">\n      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">\n        <h2 className="text-2xl font-bold mb-6 text-center">登录</h2>\n        <form onSubmit={handleSubmit} className="space-y-4">\n          <div>\n            <label htmlFor="username" className="block text-sm font-medium text-gray-700">用户名</label>\n            <input\n              type="text"\n              id="username"\n              name="username"\n              value={formData.username}\n              onChange={handleChange}\n              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"\n              required\n            />\n          </div>\n          <div>\n            <label htmlFor="password" className="block text-sm font-medium text-gray-700">密码</label>\n            <input\n              type="password"\n              id="password"\n              name="password"\n              value={formData.password}\n              onChange={handleChange}\n              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"\n              required\n            />\n          </div>\n          <div>\n            <button\n              type="submit"\n              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"\n            >\n              登录\n            </button>\n          </div>\n        </form>\n      </div>\n    </div>\n  );\n}\n\nexport default LoginForm;",
    "style": "/* 使用Tailwind CSS，无需额外样式 */",
    "description": "一个响应式登录表单组件，包含用户名、密码输入框和登录按钮",
    "dependencies": ["react", "react-dom", "tailwindcss"],
    "usage": "import LoginForm from './LoginForm';\n\nfunction App() {\n  return <LoginForm />;\n}",
    "responsive": "支持移动端、平板和桌面端，在小屏幕上自动调整布局"
}
```

### 示例 2：响应式导航栏

用户需求："创建一个响应式导航栏，包含logo、导航链接和移动端菜单"

输出：
```json
{
    "component": "import React, { useState } from 'react';\n\nfunction Navbar() {\n  const [isOpen, setIsOpen] = useState(false);\n\n  const navLinks = [\n    { name: '首页', href: '#' },\n    { name: '产品', href: '#' },\n    { name: '关于我们', href: '#' },\n    { name: '联系我们', href: '#' }\n  ];\n\n  return (\n    <nav className="bg-white shadow-md">\n      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n        <div className="flex justify-between h-16">\n          <div className="flex items-center">\n            <div className="flex-shrink-0">\n              <span className="text-xl font-bold text-indigo-600">Logo</span>\n            </div>\n            <div className="hidden md:block ml-10">\n              <div className="flex space-x-4">\n                {navLinks.map((link) => (\n                  <a\n                    key={link.name}\n                    href={link.href}\n                    className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100"
                  >\n                    {link.name}\n                  </a>\n                ))}\n              </div>\n            </div>\n          </div>\n          <div className="md:hidden flex items-center">\n            <button\n              onClick={() => setIsOpen(!isOpen)}\n              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 focus:outline-none"
            >\n              <svg\n                className="h-6 w-6"\n                xmlns="http://www.w3.org/2000/svg"\n                fill="none"\n                viewBox="0 0 24 24"\n                stroke="currentColor"
              >\n                {isOpen ? (\n                  <path\n                    strokeLinecap="round"\n                    strokeLinejoin="round"\n                    strokeWidth={2}\n                    d="M6 18L18 6M6 6l12 12"\n                  />\n                ) : (\n                  <path\n                    strokeLinecap="round"\n                    strokeLinejoin="round"\n                    strokeWidth={2}\n                    d="M4 6h16M4 12h16M4 18h16"\n                  />\n                )}\n              </svg>\n            </button>\n          </div>\n        </div>\n      </div>\n      \n      {/* 移动端菜单 */}\n      {isOpen && (\n        <div className="md:hidden">\n          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">\n            {navLinks.map((link) => (\n              <a\n                key={link.name}\n                href={link.href}\n                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100"
                onClick={() => setIsOpen(false)}\n              >\n                {link.name}\n              </a>\n            ))}\n          </div>\n        </div>\n      )}\n    </nav>\n  );\n}\n\nexport default Navbar;",
    "style": "/* 使用Tailwind CSS，无需额外样式 */",
    "description": "一个响应式导航栏，包含logo、导航链接和移动端菜单",
    "dependencies": ["react", "react-dom", "tailwindcss"],
    "usage": "import Navbar from './Navbar';\n\nfunction App() {\n  return <Navbar />;\n}",
    "responsive": "在桌面端显示水平导航，在移动端显示汉堡菜单"\n}
```