# -- coding: utf-8 --
# Project: fiuaiapp
# Created Date: 2025 05 Tu
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

# const
AI_ALLOWED_DOCTYPE_META = [
    "Contract", 
    "Contract Item", 
    "Bank Transaction",
    "Bank Statement",
    # "invoice"
    ]
USED_COUNTRY_LIST =  ["China", "United States", "Japan", "Thailand", "India", "Indonesia", "Malaysia", "Philippines", "Singapore", "South Korea", "United Kingdom", "Vietnam"]
USED_LANGUAGE_LIST = ["zh", "en", "ja", "th", "id", "ms", "ph", "sg", "kr", "uk", "vn"]
from .type import (
    UOM, 
    Currency, 
    Country,
    Language,
    DocTypeMeta,
    DocField,
    AiRecognitionValue
)
from typing import List
from logging import getLogger

from .client import FiuaiSDK

logger = getLogger(__name__)



def load_uom_data(client: FiuaiSDK)-> List[UOM]:
    """
    从frappe获取uom数据
    """
    uom_list = client.internal_get_list(doctype="UOM", fields=["name", "uom_name", "common_code"])
    return [UOM(name=uom["name"], uom_name=uom["uom_name"], common_code=uom["common_code"]) for uom in uom_list]

def load_currency_data(client: FiuaiSDK)-> List[Currency]:
    """
    从frappe获取currency数据
    """
    currency_list = client.internal_get_list(
        doctype="Currency", 
        filters={"enabled": 1},
        fields=["name", "currency_name", "fraction_units", "smallest_currency_fraction_value"]
        )
    return [Currency(name=currency["name"], currency_name=currency["currency_name"], fraction_units=currency["fraction_units"], smallest_currency_fraction_value=currency["smallest_currency_fraction_value"]) for currency in currency_list]

def load_country_data(client: FiuaiSDK)-> List[Country]:
    """
    从frappe获取country数据
    """
    country_list = client.internal_get_list(
        doctype="Country", 
        filters={"name": ["in", USED_COUNTRY_LIST]},
        fields=["name", "code"]
    )
    return [Country(name=country["name"], code=country["code"]) for country in country_list]

def load_language_data(client: FiuaiSDK)-> List[Language]:
    """
    从frappe获取language数据
    """
    language_list = client.internal_get_list(
        doctype="Language", 
        filters={"name": ["in", USED_LANGUAGE_LIST]},
        fields=["name", "language_name"]
    )
    return [Language(name=language["name"], language_name=language["language_name"]) for language in language_list]

def load_doctype_meta(client: FiuaiSDK, doctype: str, max_api_retry: int = 3, only_has_prompt: bool = True, show_hidden: bool = False)-> DocTypeMeta:
    """
    从frappe获取doctype数据
    """

    retry_count = 0
    doc_meta = None
    while retry_count < max_api_retry:
            
        doc_meta = _get_meta(client, doctype, only_has_prompt, show_hidden)
        
        if doc_meta:
            break
        else:
            retry_count += 1
           
    return doc_meta        

def _get_meta(client: FiuaiSDK, doctype: str, only_has_prompt: bool = True, show_hidden: bool = False) -> DocTypeMeta:
    try:
        m = client.get_meta(doctype)
        
        if m is None:
            return None

        _fields = []
        links = []
        child_docs = []
        for _f in m["fields"]:
            field_name = _f["fieldname"]
            field_type = _f["fieldtype"]
            field_prompt = _f.get("field_prompt", "")
            options_str = _f.get("options", "")
            hidden = _f.get("hidden", 0)
            reqd = _f.get("reqd", 0)
            read_only = _f.get("read_only", 0)
            description = _f.get("description", "")

            options = []
            match field_type:
                case "Select":
                    options = options_str.split("\n")
                case "Link":
                    links.append(options_str)
                    options.append(options_str)
                case "Table":
                    child_docs.append(options_str)
                    options.append(options_str) 
                case _:
                    pass


            if field_prompt == "" and only_has_prompt:
                # 仅有prompt的field才是应该关心的字段，降低复杂度
                continue
            if hidden == 1 and not show_hidden:
                continue
            
            
            _fields.append(DocField(
                fieldname=field_name, 
                description=description,
                fieldtype=field_type, 
                hidden=True if _f.get("hidden", 0) == 1 else False,
                read_only=True if _f.get("read_only", 0) == 1 else False,
                reqd=True if _f.get("reqd", 0) == 1 else False,
                options=options,
                field_prompt=field_prompt,
                mandatory=True if _f.get("mandatory", 0) == 1 else False,
                in_list_view=True if _f.get("in_list_view", 0) == 1 else False,
                in_mobile_view=True if _f.get("in_mobile_view", 0) == 1 else False,
                # ai_recognition_value=AiRecognitionValue(value=None, confidence=0, ai_comment="")
            ))
        
        # links, child 去重
        links = list(set(links))
        child_docs = list(set(child_docs))

        doc_meta = DocTypeMeta(
                name=doctype, 
                doctype_prompts=m.get("doctype_prompts", ""), 
                fields=_fields,
                link_docs=links,
                child_docs=child_docs
            )
        return doc_meta
    except Exception as e:
        logger.error(f"load doctype {doctype} meta failed: {e.args}")
        return None
        
        
def load_all_allowed_doctype_meta(client: FiuaiSDK, only_has_prompt: bool = True, show_hidden: bool = False)-> List[DocTypeMeta]:
    """
    从frappe获取doctype数据
    """
    r = []
    for _d in AI_ALLOWED_DOCTYPE_META:
        m = load_doctype_meta(client, _d, only_has_prompt, show_hidden)
        r.append(m)
    return r
