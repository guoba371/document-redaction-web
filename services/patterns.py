from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Union


RegexGroup = Union[int, str]


@dataclass(frozen=True)
class PatternSpec:
    pattern: re.Pattern[str]
    group: RegexGroup = 0


@dataclass(frozen=True)
class FieldRule:
    key: str
    label: str
    replacement: str
    patterns: List[PatternSpec]


def build_field_rules() -> Dict[str, FieldRule]:
    return {
        "name": FieldRule(
            key="name",
            label="姓名",
            replacement="XXX",
            patterns=[
                PatternSpec(
                    re.compile(
                        r"(?:(?:姓名|联系人|收件人|客户|用户|员工|申请人|法人|代表人|负责人)"
                        r"\s*[:：]?\s*)(?P<value>[A-Za-z\u4e00-\u9fff·]{2,30})"
                    ),
                    "value",
                )
            ],
        ),
        "id_card": FieldRule(
            key="id_card",
            label="身份证号",
            replacement="******************",
            patterns=[
                PatternSpec(
                    re.compile(r"(?<!\d)(?:\d{17}[\dXx]|\d{15})(?!\d)")
                )
            ],
        ),
        "phone": FieldRule(
            key="phone",
            label="手机号",
            replacement="***********",
            patterns=[
                PatternSpec(
                    re.compile(r"(?<!\d)(?:\+?86[-\s]?)?1[3-9]\d{9}(?!\d)")
                )
            ],
        ),
        "email": FieldRule(
            key="email",
            label="邮箱",
            replacement="***@***.***",
            patterns=[
                PatternSpec(
                    re.compile(
                        r"(?<![A-Za-z0-9._%+-])"
                        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
                        r"(?![A-Za-z0-9._%+-])"
                    )
                )
            ],
        ),
        "address": FieldRule(
            key="address",
            label="地址",
            replacement="******",
            patterns=[
                PatternSpec(
                    re.compile(
                        r"(?:(?:地址|住址|联系地址|通讯地址|收货地址|办公地址)"
                        r"\s*[:：]?\s*)(?P<value>[^\n\r，,；;。]{4,80})"
                    ),
                    "value",
                )
            ],
        ),
        "company": FieldRule(
            key="company",
            label="公司名称",
            replacement="******公司",
            patterns=[
                PatternSpec(
                    re.compile(
                        r"(?:(?:公司名称|单位名称|工作单位|单位|企业名称)"
                        r"\s*[:：]?\s*)(?P<value>[^\n\r，,；;。]{2,80})"
                    ),
                    "value",
                ),
                PatternSpec(
                    re.compile(
                        r"(?P<value>"
                        r"[A-Za-z0-9\u4e00-\u9fff（）()·\-\s]{2,80}"
                        r"(?:有限公司|股份有限公司|集团有限公司|集团|公司|银行|研究院|事务所|中心|学校|大学|医院|委员会|政府|局|院|厂)"
                        r")"
                    ),
                    "value",
                ),
            ],
        ),
    }


def field_items(field_rules: Dict[str, FieldRule]) -> Iterable[FieldRule]:
    return field_rules.values()
