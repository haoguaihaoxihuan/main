import json
import numpy as np
from sqlalchemy.orm import Session
from app.core.response import BizException
from app.models.customers import Customer
from app.models.email_record import EmailRecord
from app.models.operation_log import OperationLog
from app.models.prompt_template import PromptTemplate
from app.services.llm_service import LLMService


def get_targets(db: Session, percentile: float = 0.9, page: int = 1, per_page: int = 20) -> dict:
    customers = db.query(Customer).filter(Customer.predicted_prob.isnot(None)).all()
    if not customers:
        raise BizException(3002, "无预测数据，请先执行预测", 400)
    probs = [c.predicted_prob for c in customers]
    threshold = float(np.quantile(probs, percentile))
    targets = [c for c in customers if c.predicted_prob >= threshold]
    total = len(targets)
    start = (page - 1) * per_page
    page_items = targets[start:start + per_page]
    return {
        "threshold": threshold,
        "total": total,
        "customers": [{
            "id": c.id,
            "gender": c.gender,
            "age": c.age,
            "annual_premium": c.annual_premium,
            "predicted_prob": c.predicted_prob,
        } for c in page_items],
    }


def generate_emails(db: Session, user_id: int, customer_ids: list = None,
                    limit: int = 5) -> dict:
    llm = LLMService()
    tpl = PromptTemplate.get_active(db)
    prompt_template = tpl.content if tpl else None
    if customer_ids:
        customers = db.query(Customer).filter(Customer.id.in_(customer_ids)).all()
    else:
        customers = db.query(Customer).filter(Customer.predicted_prob.isnot(None)).order_by(
            Customer.predicted_prob.desc()).limit(limit).all()
    if not customers:
        raise BizException(2001, "没有可生成邮件的客户", 400)
    generated_count = 0
    failed_count = 0
    records = []
    for c in customers:
        customer_data = {
            "gender": c.gender, "age": c.age, "driving_license": c.driving_license,
            "vehicle_age": c.vehicle_age, "vehicle_damage": c.vehicle_damage,
            "annual_premium": c.annual_premium,
        }
        result = llm.generate_email(customer_data, prompt_template)
        if result.get("success"):
            status = "generated"
            generated_count += 1
        else:
            status = "failed"
            failed_count += 1
        email_record = EmailRecord(
            customer_id=c.id,
            subject=result.get("subject", "生成失败"),
            content=result.get("content", result.get("error", "")),
            status=status,
            created_by=user_id,
        )
        db.add(email_record)
        records.append({
            "customer_id": c.id,
            "status": status,
            "subject": result.get("subject", ""),
        })
    db.commit()
    OperationLog.create(db, user_id, "email_generation",
                        json.dumps({"generated_count": generated_count, "failed_count": failed_count}))
    return {"generated_count": generated_count, "failed_count": failed_count, "records": records}


def get_prompt(db: Session) -> dict:
    tpl = PromptTemplate.get_active(db)
    return {"name": tpl.name if tpl else "default", "content": tpl.content if tpl else ""}


def update_prompt(db: Session, content: str) -> dict:
    tpl = PromptTemplate.update_content(db, content)
    return {"name": tpl.name, "content": tpl.content}