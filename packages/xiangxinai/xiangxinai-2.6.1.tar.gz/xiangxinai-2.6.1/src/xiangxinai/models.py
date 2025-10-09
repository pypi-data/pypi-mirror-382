"""
数据模型定义
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="消息角色: user, system, assistant")
    content: str = Field(..., description="消息内容")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'system', 'assistant']:
            raise ValueError('role must be one of: user, system, assistant')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        # 允许空字符串，但长度不能超过限制
        if v and len(v) > 1000000:
            raise ValueError('content too long (max 1000000 characters)')
        return v.strip() if v else v


class GuardrailRequest(BaseModel):
    """护栏检测请求模型"""
    model: str = Field(..., description="模型名称")
    messages: List[Message] = Field(..., description="消息列表")
        
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('messages cannot be empty')
        return v


class ComplianceResult(BaseModel):
    """合规检测结果"""
    risk_level: str = Field(..., description="风险等级: 无风险, 低风险, 中风险, 高风险")
    categories: List[str] = Field(default_factory=list, description="风险类别列表")


class SecurityResult(BaseModel):
    """安全检测结果"""
    risk_level: str = Field(..., description="风险等级: 无风险, 低风险, 中风险, 高风险")
    categories: List[str] = Field(default_factory=list, description="风险类别列表")


class DataSecurityResult(BaseModel):
    """数据安全检测结果"""
    risk_level: str = Field(..., description="风险等级: 无风险, 低风险, 中风险, 高风险")
    categories: List[str] = Field(default_factory=list, description="敏感数据类别列表")


class GuardrailResult(BaseModel):
    """护栏检测结果"""
    compliance: ComplianceResult = Field(..., description="合规检测结果")
    security: SecurityResult = Field(..., description="安全检测结果")
    data: Optional[DataSecurityResult] = Field(None, description="数据安全检测结果")


class GuardrailResponse(BaseModel):
    """护栏API响应模型"""
    id: str = Field(..., description="请求唯一标识")
    result: GuardrailResult = Field(..., description="检测结果")
    overall_risk_level: str = Field(..., description="综合风险等级: no_risk, low_risk, medium_risk, high_risk")
    suggest_action: str = Field(..., description="建议动作: pass, reject, replace")
    suggest_answer: Optional[str] = Field(None, description="建议回答内容")
    score: Optional[float] = Field(None, description="检测置信度分数")
    
    @property
    def is_safe(self) -> bool:
        """判断内容是否安全"""
        return self.suggest_action == "pass"
    
    @property
    def is_blocked(self) -> bool:
        """判断内容是否被阻断"""
        return self.suggest_action == "reject"
    
    @property
    def has_substitute(self) -> bool:
        """判断是否有代答"""
        return self.suggest_action == "replace" or self.suggest_action == "reject"
    
    
    @property
    def all_categories(self) -> List[str]:
        """获取所有风险类别"""
        categories = []
        categories.extend(self.result.compliance.categories)
        categories.extend(self.result.security.categories)
        if self.result.data:
            categories.extend(self.result.data.categories)
        return list(set(categories))  # 去重