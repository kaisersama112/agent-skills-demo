from fastapi import APIRouter, HTTPException
from backend.models.requests import (
    ChatRequest, ChatResponse,
    GenerateAppRequest, GenerateAppResponse,
    ExecuteTaskRequest, ExecuteTaskResponse,
    HealthResponse
)
from backend.core.conversation_engine import conversation_engine
from backend.core.task_planner import task_planner
from backend.agents.orchestrator import agent_orchestrator
from backend.services.app_generator import app_generator
from backend.core.response_builder import ResponseBuilder
from backend.models.schemas import Session, IntentType, StructuredResponse, Task, TaskStatus
import uuid

router = APIRouter()

sessions = {}


@router.get("/health", response_model=HealthResponse,summary="检查应用健康状态")
async def health_check():
    return HealthResponse(status="ok", version="1.0.0")




@router.post("/generate-app", response_model=StructuredResponse,summary="根据用户意图生成应用")
async def generate_app(request: GenerateAppRequest):
    intent_result = await conversation_engine.detect_intent(request.message)
    
    app = await app_generator.generate_from_intent(intent_result, request.message)
    
    return ResponseBuilder.from_app_generation(
        app_id=app.id,
        name=app.spec.name,
        description=app.spec.description,
        url=app.url,
        session_id=request.session_id
    )




@router.get("/sessions/{session_id}", response_model=Session,summary="查询会话详情")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]


@router.delete("/sessions/{session_id}",summary="删除会话")
async def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "deleted", "session_id": session_id}


@router.get("/agents", response_model=list[str],summary="获取所有可用的Agent列表")
async def list_agents():
    """获取所有可用的Agent列表"""
    agents = agent_orchestrator.list_agents()
    return agents


@router.post("/agents/reload",summary="重新加载技能Agent")
async def reload_agents():
    """重新加载技能Agent"""
    from backend.agents.skill_manager import skill_manager
    count = skill_manager.reload_skills()
    return {"status": "success", "reloaded_skills": count}



@router.post("/generate-multimodal", response_model=StructuredResponse,summary="生成多模态内容")
async def generate_multimodal(request: ChatRequest):
    """生成多模态内容"""
    session_id = request.session_id or str(uuid.uuid4())
    
    print(f"\n=== 开始处理多模态内容生成 ===")
    print(f"会话ID: {session_id}")
    print(f"用户消息: {request.message}")
    
    if session_id not in sessions:
        print(f"创建新会话: {session_id}")
        sessions[session_id] = conversation_engine.create_session(session_id)
    else:
        print(f"使用现有会话: {session_id}")
    
    session = sessions[session_id]
    print(f"会话状态: {session}")
    
    # 检测意图
    print(f"\n=== 步骤1: 检测用户意图 ===")
    intent_result = await conversation_engine.detect_intent(request.message)
    print(f"意图检测结果: {intent_result}")
    print(f"识别的意图: {intent_result.intent.value}")
    print(f"领域: {intent_result.domain}")
    print(f"组件: {intent_result.components}")
    print(f"原始输出: {intent_result.raw_output}")
    
    # 创建执行计划
    print(f"\n=== 步骤2: 创建执行计划 ===")
    plan = await task_planner.create_plan(intent_result, request.message)
    print(f"生成的计划: {plan}")
    print(f"任务数量: {len(plan.tasks)}")
    for i, task in enumerate(plan.tasks):
        print(f"任务{i+1}: ID={task.id}, Agent={task.agent}, Action={task.action}")
        print(f"  输入数据: {task.input_data}")
    print(f"执行顺序: {plan.execution_order}")
    
    # 执行计划
    print(f"\n=== 步骤3: 执行计划 ===")
    results = await agent_orchestrator.execute_plan(plan)
    print(f"执行结果数量: {len(results)}")
    
    # 构建响应
    print(f"\n=== 步骤4: 构建响应 ===")
    builder = ResponseBuilder()
    builder.set_session_id(session_id)
    
    # 处理执行结果
    text_content = ""
    for i, result in enumerate(results):
        print(f"\n处理结果{i+1}:")
        print(f"  Agent: {result.agent}")
        print(f"  成功: {result.success}")
        print(f"  执行时间: {result.execution_time:.2f}秒")
        if result.success and result.output:
            output = result.output
            print(f"  输出类型: {type(output).__name__}")
            print(f"  输出内容: {output}")
            # 根据输出类型构建不同的响应块
            if isinstance(output, dict):
                if "text" in output:
                    text_content = output["text"]
                    print(f"  添加文本内容: {text_content[:100]}...")
                elif "url" in output:
                    # 尝试添加图像或SVG
                    if output.get("style") or output.get("description"):
                        builder.add_image(output["url"], alt_text=output.get("description"))
                        print(f"  添加图像: {output['url']}")
                    else:
                        builder.add_svg(output.get("content", ""))
                        print(f"  添加SVG内容")
                elif "app_id" in output:
                    builder.add_artifact(
                        artifact_id=output["app_id"],
                        name=output.get("name", "Generated App"),
                        description=output.get("description", ""),
                        url=output.get("url", "")
                    )
                    print(f"  添加应用 artifact: {output['app_id']}")
                elif "chart_type" in output and "config" in output:
                    # 添加图表块
                    builder.add_chart(output["config"])
                    print(f"  添加图表: {output['chart_type']}")
            else:
                # 如果输出不是字典，作为文本添加
                text_content = str(output)
                print(f"  添加文本内容: {text_content[:100]}...")
    
    # 如果不是选择题，使用原始文本内容
    if text_content:
        builder.add_text(text_content)
        print(f"\n添加最终文本内容: {text_content[:100]}...")
    
    # 添加后续问题
    follow_ups = [
        "你对生成的内容满意吗？",
        "需要对内容进行哪些修改？",
        "还需要生成其他类型的内容吗？"
    ]
    builder.add_follow_up(follow_ups)
    print(f"添加后续问题: {follow_ups}")
    
    response = builder.build()
    print(f"\n=== 响应构建完成 ===")
    print(f"响应类型: {type(response).__name__}")
    print(f"响应内容: {response}")
    print(f"=== 处理完成 ===\n")
    return response
