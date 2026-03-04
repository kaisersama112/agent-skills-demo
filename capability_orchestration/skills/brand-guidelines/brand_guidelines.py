from typing import Dict, Any, List
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class BrandGuidelinesInput(SkillInput):
    """
    品牌指南输入
    """
    brand_name: str = Field(..., description="品牌名称")
    brand_values: List[str] = Field(..., description="品牌价值观")
    industry: str = Field(..., description="行业")


class BrandGuidelinesOutput(SkillOutput):
    """
    品牌指南输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def brand_guidelines_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    品牌指南执行函数
    """
    # 生成品牌指南
    guidelines = generate_brand_guidelines(
        input_data.get("brand_name"),
        input_data.get("brand_values"),
        input_data.get("industry")
    )
    
    return {
        "guidelines": guidelines,
        "brand_name": input_data.get("brand_name"),
        "industry": input_data.get("industry")
    }


def generate_brand_guidelines(brand_name: str, brand_values: List[str], industry: str) -> str:
    """
    生成品牌指南
    """
    # 简单的品牌指南生成
    guidelines = f"""# {brand_name} 品牌指南

## 1. 品牌概述

### 品牌名称
{brand_name}

### 行业
{industry}

### 品牌价值观

{''.join([f'- {value}\n' for value in brand_values])}

## 2. 品牌标识

### 标志
- **主要标志**：[描述品牌标志]
- **辅助标志**：[描述辅助标志]
- **标志使用规范**：[描述标志使用规范]

### 色彩系统
- **主色调**：[描述主色调]
- **辅助色**：[描述辅助色]
- **中性色**：[描述中性色]
- **色彩使用规范**：[描述色彩使用规范]

### 排版
- **标题字体**：[描述标题字体]
- **正文字体**：[描述正文字体]
- **字体层次结构**：[描述字体层次结构]

## 3. 品牌声音与语调

### 品牌声音
[描述品牌声音]

### 语调
[描述品牌语调]

### 沟通风格
[描述沟通风格]

## 4. 品牌应用

### 数字应用
- **网站**：[描述网站应用]
- **社交媒体**：[描述社交媒体应用]
- **移动应用**：[描述移动应用]

### 印刷应用
- **名片**：[描述名片应用]
- **宣传册**：[描述宣传册应用]
- **包装**：[描述包装应用]

### 环境应用
- **办公环境**：[描述办公环境应用]
- **零售环境**：[描述零售环境应用]

## 5. 品牌一致性

### 品牌使用指南
[描述品牌使用指南]

### 常见错误
[描述常见错误]

### 审批流程
[描述审批流程]

## 6. 品牌资源

### 可下载资源
[描述可下载资源]

### 联系人
[描述联系人信息]"""
    return guidelines


# 技能定义
skill = AgentSkill(
    name="brand-guidelines",
    description="Creating comprehensive brand guidelines for businesses and organizations",
    input_schema=BrandGuidelinesInput,
    output_schema=BrandGuidelinesOutput,
    execute=brand_guidelines_execute
)
