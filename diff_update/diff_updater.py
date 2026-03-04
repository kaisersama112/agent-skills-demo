from typing import Dict, List, Any, Optional
import json

class JsonPatch:
    """
    JSON Patch (RFC 6902) 实现
    """
    
    @staticmethod
    def generate(old_obj: Dict[str, Any], new_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成JSON Patch
        
        Args:
            old_obj: 旧对象
            new_obj: 新对象
            
        Returns:
            JSON Patch操作列表
        """
        patch = []
        JsonPatch._generate_patch("", old_obj, new_obj, patch)
        return patch
    
    @staticmethod
    def _generate_patch(path: str, old_val: Any, new_val: Any, patch: List[Dict[str, Any]]):
        """
        递归生成Patch
        """
        if isinstance(old_val, dict) and isinstance(new_val, dict):
            # 处理对象
            old_keys = set(old_val.keys())
            new_keys = set(new_val.keys())
            
            # 添加新键
            for key in new_keys - old_keys:
                patch.append({
                    "op": "add",
                    "path": f"{path}/{key}" if path else f"/{key}",
                    "value": new_val[key]
                })
            
            # 删除旧键
            for key in old_keys - new_keys:
                patch.append({
                    "op": "remove",
                    "path": f"{path}/{key}" if path else f"/{key}"
                })
            
            # 更新共同键
            for key in old_keys & new_keys:
                if old_val[key] != new_val[key]:
                    JsonPatch._generate_patch(
                        f"{path}/{key}" if path else f"/{key}",
                        old_val[key],
                        new_val[key],
                        patch
                    )
        elif isinstance(old_val, list) and isinstance(new_val, list):
            # 处理数组
            min_len = min(len(old_val), len(new_val))
            
            # 更新共同元素
            for i in range(min_len):
                if old_val[i] != new_val[i]:
                    JsonPatch._generate_patch(
                        f"{path}/{i}" if path else f"/{i}",
                        old_val[i],
                        new_val[i],
                        patch
                    )
            
            # 添加新元素
            for i in range(min_len, len(new_val)):
                patch.append({
                    "op": "add",
                    "path": f"{path}/{i}" if path else f"/{i}",
                    "value": new_val[i]
                })
            
            # 删除多余元素
            if len(old_val) > len(new_val):
                # 从后往前删除，避免索引变化
                for i in range(len(old_val) - 1, len(new_val) - 1, -1):
                    patch.append({
                        "op": "remove",
                        "path": f"{path}/{i}" if path else f"/{i}"
                    })
        else:
            # 处理基本类型
            if old_val != new_val:
                patch.append({
                    "op": "replace",
                    "path": path if path else "/",
                    "value": new_val
                })
    
    @staticmethod
    def apply(obj: Dict[str, Any], patch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        应用JSON Patch
        
        Args:
            obj: 原始对象
            patch: JSON Patch操作列表
            
        Returns:
            应用Patch后的对象
        """
        result = json.loads(json.dumps(obj))  # 深拷贝
        
        for operation in patch:
            op = operation["op"]
            path = operation["path"]
            
            # 解析路径
            keys = path.strip("/").split("/") if path != "/" else []
            
            if op == "add":
                JsonPatch._apply_add(result, keys, operation["value"])
            elif op == "remove":
                JsonPatch._apply_remove(result, keys)
            elif op == "replace":
                JsonPatch._apply_replace(result, keys, operation["value"])
            elif op == "move":
                # 简化实现，只处理基本移动
                pass
            elif op == "copy":
                # 简化实现，只处理基本复制
                pass
            elif op == "test":
                # 简化实现，跳过测试
                pass
        
        return result
    
    @staticmethod
    def _apply_add(obj: Dict[str, Any], keys: List[str], value: Any):
        """
        应用add操作
        """
        if not keys:
            return
        
        current = obj
        for i, key in enumerate(keys[:-1]):
            if key.isdigit():
                key = int(key)
            current = current[key]
        
        last_key = keys[-1]
        if last_key.isdigit():
            last_key = int(last_key)
            current.insert(last_key, value)
        else:
            current[last_key] = value
    
    @staticmethod
    def _apply_remove(obj: Dict[str, Any], keys: List[str]):
        """
        应用remove操作
        """
        if not keys:
            return
        
        current = obj
        for i, key in enumerate(keys[:-1]):
            if key.isdigit():
                key = int(key)
            current = current[key]
        
        last_key = keys[-1]
        if last_key.isdigit():
            last_key = int(last_key)
            del current[last_key]
        else:
            del current[last_key]
    
    @staticmethod
    def _apply_replace(obj: Dict[str, Any], keys: List[str], value: Any):
        """
        应用replace操作
        """
        if not keys:
            return
        
        current = obj
        for i, key in enumerate(keys[:-1]):
            if key.isdigit():
                key = int(key)
            current = current[key]
        
        last_key = keys[-1]
        if last_key.isdigit():
            last_key = int(last_key)
            current[last_key] = value
        else:
            current[last_key] = value

class DiffUpdater:
    """
    Diff局部刷新器
    """
    
    def __init__(self):
        self.previous_state = {}
    
    def generate_diff(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成状态差异
        
        Args:
            current_state: 当前状态
            
        Returns:
            JSON Patch操作列表
        """
        patch = JsonPatch.generate(self.previous_state, current_state)
        self.previous_state = json.loads(json.dumps(current_state))  # 深拷贝
        return patch
    
    def apply_diff(self, state: Dict[str, Any], patch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        应用状态差异
        
        Args:
            state: 原始状态
            patch: JSON Patch操作列表
            
        Returns:
            应用差异后的状态
        """
        return JsonPatch.apply(state, patch)
    
    def should_update(self, old_props: Dict[str, Any], new_props: Dict[str, Any]) -> bool:
        """
        判断是否需要更新
        
        Args:
            old_props: 旧属性
            new_props: 新属性
            
        Returns:
            是否需要更新
        """
        # 简单的浅比较
        if old_props.keys() != new_props.keys():
            return True
        
        for key, value in old_props.items():
            if key not in new_props or old_props[key] != new_props[key]:
                return True
        
        return False
    
    def optimize_render(self, component_name: str, props: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化渲染
        
        Args:
            component_name: 组件名称
            props: 组件属性
            
        Returns:
            优化后的属性
        """
        # 这里可以实现具体的渲染优化逻辑
        # 例如，为React组件添加memo，为Vue组件添加v-memo
        return props
    
    def get_render_optimization_hints(self) -> Dict[str, str]:
        """
        获取渲染优化提示
        
        Returns:
            优化提示
        """
        return {
            "React": "使用React.memo()包装组件，避免不必要的重渲染",
            "Vue": "使用v-memo指令，指定需要比较的属性",
            "General": "只传输变更部分，减少数据传输量"
        }

# 示例用法
if __name__ == "__main__":
    # 测试JSON Patch
    old_obj = {
        "title": "待办事项",
        "tasks": [
            {"id": "1", "content": "学习Python", "completed": False},
            {"id": "2", "content": "练习瑜伽", "completed": True}
        ]
    }
    
    new_obj = {
        "title": "我的待办事项",
        "tasks": [
            {"id": "1", "content": "学习Python", "completed": True},
            {"id": "3", "content": "阅读书籍", "completed": False}
        ],
        "filter": "all"
    }
    
    # 生成Patch
    patch = JsonPatch.generate(old_obj, new_obj)
    print("JSON Patch:")
    print(json.dumps(patch, indent=2, ensure_ascii=False))
    
    # 应用Patch
    result = JsonPatch.apply(old_obj, patch)
    print("\n应用Patch后的结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试DiffUpdater
    updater = DiffUpdater()
    updater.previous_state = old_obj
    
    diff = updater.generate_diff(new_obj)
    print("\nDiffUpdater生成的Patch:")
    print(json.dumps(diff, indent=2, ensure_ascii=False))
    
    # 测试是否需要更新
    old_props = {"count": 1, "text": "Hello"}
    new_props = {"count": 1, "text": "Hello"}
    print("\n是否需要更新:", updater.should_update(old_props, new_props))
    
    new_props["count"] = 2
    print("是否需要更新:", updater.should_update(old_props, new_props))