"""
Data model definition
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class Message(BaseModel):
    """Message model"""
    role: str = Field(..., description="Message role: user, system, assistant")
    content: str = Field(..., description="Message content")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'system', 'assistant']:
            raise ValueError('role must be one of: user, system, assistant')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        # Allow empty string, but the length cannot exceed the limit
        if v and len(v) > 1000000:
            raise ValueError('content too long (max 1000000 characters)')
        return v.strip() if v else v


class GuardrailRequest(BaseModel):
    """Guardrail detection request model"""
    model: str = Field(..., description="模型名称")
    messages: List[Message] = Field(..., description="Message list")
        
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('messages cannot be empty')
        return v


class ComplianceResult(BaseModel):
    """Compliance detection result"""
    risk_level: str = Field(..., description="Risk level: no_risk, low_risk, medium_risk, high_risk")
    categories: List[str] = Field(default_factory=list, description="Risk categories list")


class SecurityResult(BaseModel):
    """Security detection result"""
    risk_level: str = Field(..., description="Risk level: no_risk, low_risk, medium_risk, high_risk")
    categories: List[str] = Field(default_factory=list, description="Risk categories list")


class DataSecurityResult(BaseModel):
    """Data security detection result"""
    risk_level: str = Field(..., description="Risk level: no_risk, low_risk, medium_risk, high_risk")
    categories: List[str] = Field(default_factory=list, description="Sensitive data categories list")


class GuardrailResult(BaseModel):
    """Guardrail detection result"""
    compliance: ComplianceResult = Field(..., description="Compliance detection result")
    security: SecurityResult = Field(..., description="Security detection result")
    data: Optional[DataSecurityResult] = Field(None, description="Data security detection result")


class GuardrailResponse(BaseModel):
    """Guardrail API response model"""
    id: str = Field(..., description="Request unique identifier")
    result: GuardrailResult = Field(..., description="Detection result")
    overall_risk_level: str = Field(..., description="Overall risk level: no_risk, low_risk, medium_risk, high_risk")
    suggest_action: str = Field(..., description="Suggested action: pass, reject, replace")
    suggest_answer: Optional[str] = Field(None, description="Suggested answer content")
    score: Optional[float] = Field(None, description="Detection confidence score")
    
    @property
    def is_safe(self) -> bool:
        """Check if the content is safe"""
        return self.suggest_action == "pass"
    
    @property
    def is_blocked(self) -> bool:
        """Check if the content is blocked"""
        return self.suggest_action == "reject"
    
    @property
    def has_substitute(self) -> bool:
        """Check if there is a substitute answer"""
        return self.suggest_action == "replace" or self.suggest_action == "reject"
    
    
    @property
    def all_categories(self) -> List[str]:
        """Get all risk categories"""
        categories = []
        categories.extend(self.result.compliance.categories)
        categories.extend(self.result.security.categories)
        if self.result.data:
            categories.extend(self.result.data.categories)
        return list(set(categories))  # Remove duplicates