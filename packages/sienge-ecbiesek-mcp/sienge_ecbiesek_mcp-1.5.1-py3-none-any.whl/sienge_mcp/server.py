#!/usr/bin/env python3
"""
SIENGE MCP COMPLETO - FastMCP com Autenticação Flexível
Suporta Bearer Token e Basic Auth
"""

from fastmcp import FastMCP
import httpx
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import time
import uuid
import asyncio
import logging
import traceback

# logger
from .utils.logger import get_logger
logger = get_logger()

# Optional: prefer tenacity for robust retries; linter will warn if not installed but code falls back
try:
    from tenacity import AsyncRetrying, wait_exponential, stop_after_attempt, retry_if_exception_type  # type: ignore
    TENACITY_AVAILABLE = True
except Exception:
    TENACITY_AVAILABLE = False

# Supabase client (optional)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False
    create_client = None
    Client = None

# Carrega as variáveis de ambiente
load_dotenv()

mcp = FastMCP("Sienge API Integration 🏗️ - ChatGPT Compatible")

# Configurações da API do Sienge
SIENGE_BASE_URL = os.getenv("SIENGE_BASE_URL", "https://api.sienge.com.br")
SIENGE_SUBDOMAIN = os.getenv("SIENGE_SUBDOMAIN", "")
SIENGE_USERNAME = os.getenv("SIENGE_USERNAME", "")
SIENGE_PASSWORD = os.getenv("SIENGE_PASSWORD", "")
SIENGE_API_KEY = os.getenv("SIENGE_API_KEY", "")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_SCHEMA = "sienge_data"  # Schema fixo: sienge_data


class SiengeAPIError(Exception):
    """Exceção customizada para erros da API do Sienge"""

    pass


async def make_sienge_request(
    method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None, files: Optional[Dict] = None
) -> Dict:
    """
    Função auxiliar para fazer requisições à API do Sienge (v1)
    Suporta tanto Bearer Token quanto Basic Auth
    Suporta multipart/form-data via parâmetro 'files'
    """
    # Attach a request id and measure latency
    request_id = str(uuid.uuid4())
    start_ts = time.time()

    # Para multipart/form-data, não enviar Content-Type (httpx adiciona automaticamente com boundary)
    if files:
        headers = {"Accept": "application/json", "X-Request-Id": request_id}
    else:
        headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Request-Id": request_id}

    # Configurar autenticação e URL
    auth = None

    if SIENGE_API_KEY and SIENGE_API_KEY != "sua_api_key_aqui":
        headers["Authorization"] = f"Bearer {SIENGE_API_KEY}"
        url = f"{SIENGE_BASE_URL}/{SIENGE_SUBDOMAIN}/public/api/v1{endpoint}"
    elif SIENGE_USERNAME and SIENGE_PASSWORD:
        auth = httpx.BasicAuth(SIENGE_USERNAME, SIENGE_PASSWORD)
        url = f"{SIENGE_BASE_URL}/{SIENGE_SUBDOMAIN}/public/api/v1{endpoint}"
    else:
        return {
            "success": False,
            "error": "No Authentication",
            "message": "Configure SIENGE_API_KEY ou SIENGE_USERNAME/PASSWORD no .env",
            "request_id": request_id,
        }

    async def _do_request(client: httpx.AsyncClient):
        return await client.request(method=method, url=url, headers=headers, params=params, json=json_data, files=files, auth=auth)

    try:
        max_attempts = 5
        attempts = 0
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            while True:
                attempts += 1
                try:
                    response = await client.request(method=method, url=url, headers=headers, params=params, json=json_data, files=files, auth=auth)
                except (httpx.RequestError, httpx.TimeoutException) as exc:
                    logger.warning(f"Request error to {url}: {exc} (attempt {attempts}/{max_attempts})")
                    if attempts >= max_attempts:
                        raise
                    await asyncio.sleep(min(2 ** attempts, 60))
                    continue

                # Handle rate limit explicitly
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    try:
                        wait_seconds = int(retry_after) if retry_after is not None else min(2 ** attempts, 60)
                    except Exception:
                        wait_seconds = min(2 ** attempts, 60)
                    logger.warning(f"HTTP 429 from {url}, retrying after {wait_seconds}s (attempt {attempts}/{max_attempts})")
                    if attempts >= max_attempts:
                        latency_ms = int((time.time() - start_ts) * 1000)
                        return {"success": False, "error": "HTTP 429", "message": response.text, "status_code": 429, "latency_ms": latency_ms, "request_id": request_id}
                    await asyncio.sleep(wait_seconds)
                    continue

                latency_ms = int((time.time() - start_ts) * 1000)

                if response.status_code in [200, 201, 204]:
                    try:
                        # HTTP 204 No Content não tem body
                        if response.status_code == 204:
                            return {"success": True, "data": None, "status_code": response.status_code, "latency_ms": latency_ms, "request_id": request_id}
                        return {"success": True, "data": response.json(), "status_code": response.status_code, "latency_ms": latency_ms, "request_id": request_id}
                    except BaseException:
                        return {"success": True, "data": {"message": "Success"}, "status_code": response.status_code, "latency_ms": latency_ms, "request_id": request_id}
                else:
                    logger.warning(f"HTTP {response.status_code} from {url}: {response.text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "message": response.text,
                        "status_code": response.status_code,
                        "latency_ms": latency_ms,
                        "request_id": request_id,
                    }

    except httpx.TimeoutException:
        latency_ms = int((time.time() - start_ts) * 1000)
        return {"success": False, "error": "Timeout", "message": f"A requisição excedeu o tempo limite de {REQUEST_TIMEOUT}s", "latency_ms": latency_ms, "request_id": request_id}
    except Exception as e:
        latency_ms = int((time.time() - start_ts) * 1000)
        return {"success": False, "error": str(e), "message": f"Erro na requisição: {str(e)}", "latency_ms": latency_ms, "request_id": request_id}


async def make_sienge_bulk_request(
    method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None
) -> Dict:
    """
    Função auxiliar para fazer requisições à API bulk-data do Sienge
    Suporta tanto Bearer Token quanto Basic Auth
    """
    # Similar to make_sienge_request but targeting bulk-data endpoints
    request_id = str(uuid.uuid4())
    start_ts = time.time()

    headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Request-Id": request_id}

    auth = None
    if SIENGE_API_KEY and SIENGE_API_KEY != "sua_api_key_aqui":
        headers["Authorization"] = f"Bearer {SIENGE_API_KEY}"
        url = f"{SIENGE_BASE_URL}/{SIENGE_SUBDOMAIN}/public/api/bulk-data/v1{endpoint}"
    elif SIENGE_USERNAME and SIENGE_PASSWORD:
        auth = httpx.BasicAuth(SIENGE_USERNAME, SIENGE_PASSWORD)
        url = f"{SIENGE_BASE_URL}/{SIENGE_SUBDOMAIN}/public/api/bulk-data/v1{endpoint}"
    else:
        return {
            "success": False,
            "error": "No Authentication",
            "message": "Configure SIENGE_API_KEY ou SIENGE_USERNAME/PASSWORD no .env",
            "request_id": request_id,
        }

    async def _do_request(client: httpx.AsyncClient):
        return await client.request(method=method, url=url, headers=headers, params=params, json=json_data, auth=auth)

    try:
        max_attempts = 5
        attempts = 0
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            while True:
                attempts += 1
                try:
                    response = await client.request(method=method, url=url, headers=headers, params=params, json=json_data, auth=auth)
                except (httpx.RequestError, httpx.TimeoutException) as exc:
                    logger.warning(f"Bulk request error to {url}: {exc} (attempt {attempts}/{max_attempts})")
                    if attempts >= max_attempts:
                        raise
                    await asyncio.sleep(min(2 ** attempts, 60))
                    continue

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    try:
                        wait_seconds = int(retry_after) if retry_after is not None else min(2 ** attempts, 60)
                    except Exception:
                        wait_seconds = min(2 ** attempts, 60)
                    logger.warning(f"HTTP 429 from bulk {url}, retrying after {wait_seconds}s (attempt {attempts}/{max_attempts})")
                    if attempts >= max_attempts:
                        latency_ms = int((time.time() - start_ts) * 1000)
                        return {"success": False, "error": "HTTP 429", "message": response.text, "status_code": 429, "latency_ms": latency_ms, "request_id": request_id}
                    await asyncio.sleep(wait_seconds)
                    continue

                latency_ms = int((time.time() - start_ts) * 1000)

                if response.status_code in [200, 201, 204]:
                    try:
                        # HTTP 204 No Content não tem body
                        if response.status_code == 204:
                            return {"success": True, "data": None, "status_code": response.status_code, "latency_ms": latency_ms, "request_id": request_id}
                        return {"success": True, "data": response.json(), "status_code": response.status_code, "latency_ms": latency_ms, "request_id": request_id}
                    except BaseException:
                        return {"success": True, "data": {"message": "Success"}, "status_code": response.status_code, "latency_ms": latency_ms, "request_id": request_id}
                else:
                    logger.warning(f"HTTP {response.status_code} from bulk {url}: {response.text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "message": response.text,
                        "status_code": response.status_code,
                        "latency_ms": latency_ms,
                        "request_id": request_id,
                    }

    except httpx.TimeoutException:
        latency_ms = int((time.time() - start_ts) * 1000)
        return {"success": False, "error": "Timeout", "message": f"A requisição excedeu o tempo limite de {REQUEST_TIMEOUT}s", "latency_ms": latency_ms, "request_id": request_id}
    except Exception as e:
        latency_ms = int((time.time() - start_ts) * 1000)
        return {"success": False, "error": str(e), "message": f"Erro na requisição bulk-data: {str(e)}", "latency_ms": latency_ms, "request_id": request_id}


# ============ CONEXÃO E TESTE ============


@mcp.tool
async def test_sienge_connection(_meta: Optional[Dict[str, Any]] = None) -> Dict:
    """Testa a conexão com a API do Sienge e retorna métricas básicas"""
    try:
        # Tentar endpoint mais simples primeiro
        result = await make_sienge_request("GET", "/customer-types")

        if result["success"]:
            auth_method = "Bearer Token" if SIENGE_API_KEY else "Basic Auth"
            return {
                "success": True,
                "message": "✅ Conexão com API do Sienge estabelecida com sucesso!",
                "api_status": "Online",
                "auth_method": auth_method,
                "timestamp": datetime.now().isoformat(),
                "latency_ms": result.get("latency_ms"),
                "request_id": result.get("request_id"),
            }
        else:
            return {
                "success": False,
                "message": "❌ Falha ao conectar com API do Sienge",
                "error": result.get("error"),
                "details": result.get("message"),
                "timestamp": datetime.now().isoformat(),
                "latency_ms": result.get("latency_ms"),
                "request_id": result.get("request_id"),
            }
    except Exception as e:
        return {
            "success": False,
            "message": "❌ Erro ao testar conexão",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# ============ CLIENTES ============


@mcp.tool
async def get_sienge_customers(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    search: Optional[str] = None,
    customer_type_id: Optional[str] = None,
    fetch_all: Optional[bool] = False,
    max_records: Optional[int] = None,
) -> Dict:
    """
    Busca clientes no Sienge com filtros

    Args:
        limit: Máximo de registros (padrão: 50)
        offset: Pular registros (padrão: 0)
        search: Buscar por nome ou documento
        customer_type_id: Filtrar por tipo de cliente
    """
    params = {"limit": min(limit or 50, 200), "offset": offset or 0}

    if search:
        params["search"] = search
    if customer_type_id:
        params["customer_type_id"] = customer_type_id

    # Basic in-memory cache for lightweight GETs
    cache_key = f"customers:{limit}:{offset}:{search}:{customer_type_id}"
    try:
        cached = _simple_cache_get(cache_key)
        if cached:
            return cached
    except Exception:
        pass

    # If caller asked to fetch all, use helper to iterate pages
    if fetch_all:
        items = await _fetch_all_paginated("/customers", params=params, page_size=200, max_records=max_records)
        if isinstance(items, dict) and not items.get("success", True):
            return {"success": False, "error": items.get("error"), "message": items.get("message")}

        customers = items
        total_count = len(customers)
        response = {
            "success": True,
            "message": f"✅ Encontrados {len(customers)} clientes (fetch_all)",
            "customers": customers,
            "count": len(customers),
            "filters_applied": params,
        }
        try:
            _simple_cache_set(cache_key, response, ttl=30)
        except Exception:
            pass
        return response

    result = await make_sienge_request("GET", "/customers", params=params)

    if result["success"]:
        data = result["data"]
        customers = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(customers))

        response = {
            "success": True,
            "message": f"✅ Encontrados {len(customers)} clientes (total: {total_count})",
            "customers": customers,
            "count": len(customers),
            "filters_applied": params,
        }
        try:
            _simple_cache_set(cache_key, response, ttl=30)
        except Exception:
            pass
        return response

    return {
        "success": False,
        "message": "❌ Erro ao buscar clientes",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_customer_types() -> Dict:
    """Lista tipos de clientes disponíveis"""
    result = await make_sienge_request("GET", "/customer-types")

    if result["success"]:
        data = result["data"]
        customer_types = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(customer_types))

        response = {
            "success": True,
            "message": f"✅ Encontrados {len(customer_types)} tipos de clientes (total: {total_count})",
            "customer_types": customer_types,
            "count": len(customer_types),
        }
        try:
            _simple_cache_set("customer_types", response, ttl=300)
        except Exception:
            pass
        return response

    return {
        "success": False,
        "message": "❌ Erro ao buscar tipos de clientes",
        "error": result.get("error"),
        "details": result.get("message"),
    }


# ============ CREDORES ============


@mcp.tool
async def get_sienge_creditors(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    search: Optional[str] = None,
    fetch_all: Optional[bool] = False,
    max_records: Optional[int] = None,
) -> Dict:
    """
    Busca credores/fornecedores

    Args:
        limit: Máximo de registros (padrão: 50)
        offset: Pular registros (padrão: 0)
        search: Buscar por nome
    """
    params = {"limit": min(limit or 50, 200), "offset": offset or 0}
    if search:
        params["search"] = search

    cache_key = f"creditors:{limit}:{offset}:{search}:{fetch_all}:{max_records}"
    try:
        cached = _simple_cache_get(cache_key)
        if cached:
            return cached
    except Exception:
        pass

    # Support fetching all pages when requested
    if fetch_all:
        items = await _fetch_all_paginated("/creditors", params=params, page_size=200, max_records=max_records)
        if isinstance(items, dict) and not items.get("success", True):
            return {"success": False, "error": items.get("error"), "message": items.get("message")}

        creditors = items
        response = {
            "success": True,
            "message": f"✅ Encontrados {len(creditors)} credores (fetch_all)",
            "creditors": creditors,
            "count": len(creditors),
        }
        try:
            _simple_cache_set(cache_key, response, ttl=30)
        except Exception:
            pass
        return response

    result = await make_sienge_request("GET", "/creditors", params=params)

    if result["success"]:
        data = result["data"]
        creditors = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(creditors))

        response = {
            "success": True,
            "message": f"✅ Encontrados {len(creditors)} credores (total: {total_count})",
            "creditors": creditors,
            "count": len(creditors),
        }
        try:
            _simple_cache_set(cache_key, response, ttl=30)
        except Exception:
            pass
        return response

    return {
        "success": False,
        "message": "❌ Erro ao buscar credores",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_creditor_bank_info(creditor_id: str) -> Dict:
    """
    Consulta informações bancárias de um credor

    Args:
        creditor_id: ID do credor (obrigatório)
    """
    result = await make_sienge_request("GET", f"/creditors/{creditor_id}/bank-informations")

    if result["success"]:
        return {
            "success": True,
            "message": f"✅ Informações bancárias do credor {creditor_id}",
            "creditor_id": creditor_id,
            "bank_info": result["data"],
        }

    return {
        "success": False,
        "message": f"❌ Erro ao buscar info bancária do credor {creditor_id}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


# ============ FINANCEIRO ============


@mcp.tool
async def get_sienge_accounts_receivable(
    start_date: str,
    end_date: str,
    selection_type: str = "D",
    company_id: Optional[int] = None,
    cost_centers_id: Optional[List[int]] = None,
    correction_indexer_id: Optional[int] = None,
    correction_date: Optional[str] = None,
    change_start_date: Optional[str] = None,
    completed_bills: Optional[str] = None,
    origins_ids: Optional[List[str]] = None,
    bearers_id_in: Optional[List[int]] = None,
    bearers_id_not_in: Optional[List[int]] = None,
) -> Dict:
    """
    Consulta parcelas do contas a receber via API bulk-data

    Args:
        start_date: Data de início do período (YYYY-MM-DD) - OBRIGATÓRIO
        end_date: Data do fim do período (YYYY-MM-DD) - OBRIGATÓRIO
        selection_type: Seleção da data do período (I=emissão, D=vencimento, P=pagamento, B=competência) - padrão: D
        company_id: Código da empresa
        cost_centers_id: Lista de códigos de centro de custo
        correction_indexer_id: Código do indexador de correção
        correction_date: Data para correção do indexador (YYYY-MM-DD)
        change_start_date: Data inicial de alteração do título/parcela (YYYY-MM-DD)
        completed_bills: Filtrar por títulos completos (S)
        origins_ids: Códigos dos módulos de origem (CR, CO, ME, CA, CI, AR, SC, LO, NE, NS, AC, NF)
        bearers_id_in: Filtrar parcelas com códigos de portador específicos
        bearers_id_not_in: Filtrar parcelas excluindo códigos de portador específicos
    """
    params = {"startDate": start_date, "endDate": end_date, "selectionType": selection_type}

    if company_id:
        params["companyId"] = company_id
    if cost_centers_id:
        params["costCentersId"] = cost_centers_id
    if correction_indexer_id:
        params["correctionIndexerId"] = correction_indexer_id
    if correction_date:
        params["correctionDate"] = correction_date
    if change_start_date:
        params["changeStartDate"] = change_start_date
    if completed_bills:
        params["completedBills"] = completed_bills
    if origins_ids:
        params["originsIds"] = origins_ids
    if bearers_id_in:
        params["bearersIdIn"] = bearers_id_in
    if bearers_id_not_in:
        params["bearersIdNotIn"] = bearers_id_not_in

    result = await make_sienge_bulk_request("GET", "/income", params=params)

    if result["success"]:
        data = result["data"]
        income_data = data.get("data", []) if isinstance(data, dict) else data

        return {
            "success": True,
            "message": f"✅ Encontradas {len(income_data)} parcelas a receber",
            "income_data": income_data,
            "count": len(income_data),
            "period": f"{start_date} a {end_date}",
            "selection_type": selection_type,
            "filters": params,
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar parcelas a receber",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_accounts_receivable_by_bills(
    bills_ids: List[int], correction_indexer_id: Optional[int] = None, correction_date: Optional[str] = None
) -> Dict:
    """
    Consulta parcelas dos títulos informados via API bulk-data

    Args:
        bills_ids: Lista de códigos dos títulos - OBRIGATÓRIO
        correction_indexer_id: Código do indexador de correção
        correction_date: Data para correção do indexador (YYYY-MM-DD)
    """
    params = {"billsIds": bills_ids}

    if correction_indexer_id:
        params["correctionIndexerId"] = correction_indexer_id
    if correction_date:
        params["correctionDate"] = correction_date

    result = await make_sienge_bulk_request("GET", "/income/by-bills", params=params)

    if result["success"]:
        data = result["data"]
        income_data = data.get("data", []) if isinstance(data, dict) else data

        return {
            "success": True,
            "message": f"✅ Encontradas {len(income_data)} parcelas dos títulos informados",
            "income_data": income_data,
            "count": len(income_data),
            "bills_consulted": bills_ids,
            "filters": params,
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar parcelas dos títulos informados",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_bills(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    creditor_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = 50,
) -> Dict:
    """
    Consulta títulos a pagar (contas a pagar) - REQUER startDate obrigatório

    Args:
        start_date: Data inicial obrigatória (YYYY-MM-DD) - padrão últimos 30 dias
        end_date: Data final (YYYY-MM-DD) - padrão hoje
        creditor_id: ID do credor
        status: Status do título (ex: open, paid, cancelled)
        limit: Máximo de registros (padrão: 50, máx: 200)
    """
    from datetime import datetime, timedelta

    # Se start_date não fornecido, usar últimos 30 dias
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # Se end_date não fornecido, usar hoje
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # Parâmetros obrigatórios
    params = {"startDate": start_date, "endDate": end_date, "limit": min(limit or 50, 200)}  # OBRIGATÓRIO pela API

    # Parâmetros opcionais
    if creditor_id:
        params["creditor_id"] = creditor_id
    if status:
        params["status"] = status

    result = await make_sienge_request("GET", "/bills", params=params)

    if result["success"]:
        data = result["data"]
        bills = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(bills))

        return {
            "success": True,
            "message": f"✅ Encontrados {len(bills)} títulos a pagar (total: {total_count}) - período: {start_date} a {end_date}",
            "bills": bills,
            "count": len(bills),
            "total_count": total_count,
            "period": {"start_date": start_date, "end_date": end_date},
            "filters": params,
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar títulos a pagar",
        "error": result.get("error"),
        "details": result.get("message"),
    }


# ============ COMPRAS ============


@mcp.tool
async def get_sienge_purchase_orders(
    purchase_order_id: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    limit: Optional[int] = 50,
) -> Dict:
    """
    Consulta pedidos de compra

    Args:
        purchase_order_id: ID específico do pedido
        status: Status do pedido
        date_from: Data inicial (YYYY-MM-DD)
        limit: Máximo de registros
    """
    if purchase_order_id:
        result = await make_sienge_request("GET", f"/purchase-orders/{purchase_order_id}")
        if result["success"]:
            return {"success": True, "message": f"✅ Pedido {purchase_order_id} encontrado", "purchase_order": result["data"]}
        return result

    params = {"limit": min(limit or 50, 200)}
    if status:
        params["status"] = status
    if date_from:
        params["date_from"] = date_from

    result = await make_sienge_request("GET", "/purchase-orders", params=params)

    if result["success"]:
        data = result["data"]
        orders = data.get("results", []) if isinstance(data, dict) else data

        return {
            "success": True,
            "message": f"✅ Encontrados {len(orders)} pedidos de compra",
            "purchase_orders": orders,
            "count": len(orders),
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar pedidos de compra",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_purchase_order_items(purchase_order_id: str) -> Dict:
    """
    Consulta itens de um pedido de compra específico

    Args:
        purchase_order_id: ID do pedido (obrigatório)
    """
    result = await make_sienge_request("GET", f"/purchase-orders/{purchase_order_id}/items")

    if result["success"]:
        data = result["data"]
        items = data.get("results", []) if isinstance(data, dict) else data

        return {
            "success": True,
            "message": f"✅ Encontrados {len(items)} itens no pedido {purchase_order_id}",
            "purchase_order_id": purchase_order_id,
            "items": items,
            "count": len(items),
        }

    return {
        "success": False,
        "message": f"❌ Erro ao buscar itens do pedido {purchase_order_id}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_purchase_requests(purchase_request_id: Optional[str] = None, limit: Optional[int] = 50) -> Dict:
    """
    Consulta solicitações de compra

    Args:
        purchase_request_id: ID específico da solicitação
        limit: Máximo de registros
    """
    if purchase_request_id:
        result = await make_sienge_request("GET", f"/purchase-requests/{purchase_request_id}")
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ Solicitação {purchase_request_id} encontrada",
                "purchase_request": result["data"],
            }
        return result

    params = {"limit": min(limit or 50, 200)}
    result = await make_sienge_request("GET", "/purchase-requests", params=params)

    if result["success"]:
        data = result["data"]
        requests = data.get("results", []) if isinstance(data, dict) else data

        return {
            "success": True,
            "message": f"✅ Encontradas {len(requests)} solicitações de compra",
            "purchase_requests": requests,
            "count": len(requests),
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar solicitações de compra",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def create_sienge_purchase_request(description: str, project_id: str, items: List[Dict[str, Any]]) -> Dict:
    """
    Cria nova solicitação de compra

    Args:
        description: Descrição da solicitação
        project_id: ID do projeto/obra
        items: Lista de itens da solicitação
    """
    request_data = {
        "description": description,
        "project_id": project_id,
        "items": items,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    result = await make_sienge_request("POST", "/purchase-requests", json_data=request_data)

    if result["success"]:
        return {
            "success": True,
            "message": "✅ Solicitação de compra criada com sucesso",
            "request_id": result["data"].get("id"),
            "data": result["data"],
        }

    return {
        "success": False,
        "message": "❌ Erro ao criar solicitação de compra",
        "error": result.get("error"),
        "details": result.get("message"),
    }


# ============ NOTAS FISCAIS DE COMPRA ============


@mcp.tool
async def get_sienge_purchase_invoice(sequential_number: int) -> Dict:
    """
    Consulta nota fiscal de compra por número sequencial

    Args:
        sequential_number: Número sequencial da nota fiscal
    """
    result = await make_sienge_request("GET", f"/purchase-invoices/{sequential_number}")

    if result["success"]:
        return {"success": True, "message": f"✅ Nota fiscal {sequential_number} encontrada", "invoice": result["data"]}

    return {
        "success": False,
        "message": f"❌ Erro ao buscar nota fiscal {sequential_number}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_purchase_invoice_items(sequential_number: int) -> Dict:
    """
    Consulta itens de uma nota fiscal de compra

    Args:
        sequential_number: Número sequencial da nota fiscal
    """
    result = await make_sienge_request("GET", f"/purchase-invoices/{sequential_number}/items")

    if result["success"]:
        data = result["data"]
        items = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}

        return {
            "success": True,
            "message": f"✅ Encontrados {len(items)} itens na nota fiscal {sequential_number}",
            "items": items,
            "count": len(items),
            "metadata": metadata,
        }

    return {
        "success": False,
        "message": f"❌ Erro ao buscar itens da nota fiscal {sequential_number}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def create_sienge_purchase_invoice(
    document_id: str,
    number: str,
    supplier_id: int,
    company_id: int,
    movement_type_id: int,
    movement_date: str,
    issue_date: str,
    series: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict:
    """
    Cadastra uma nova nota fiscal de compra

    Args:
        document_id: ID do documento (ex: "NF")
        number: Número da nota fiscal
        supplier_id: ID do fornecedor
        company_id: ID da empresa
        movement_type_id: ID do tipo de movimento
        movement_date: Data do movimento (YYYY-MM-DD)
        issue_date: Data de emissão (YYYY-MM-DD)
        series: Série da nota fiscal (opcional)
        notes: Observações (opcional)
    """
    invoice_data = {
        "documentId": document_id,
        "number": number,
        "supplierId": supplier_id,
        "companyId": company_id,
        "movementTypeId": movement_type_id,
        "movementDate": movement_date,
        "issueDate": issue_date,
    }

    if series:
        invoice_data["series"] = series
    if notes:
        invoice_data["notes"] = notes

    result = await make_sienge_request("POST", "/purchase-invoices", json_data=invoice_data)

    if result["success"]:
        return {"success": True, "message": f"✅ Nota fiscal {number} criada com sucesso", "invoice": result["data"]}

    return {
        "success": False,
        "message": f"❌ Erro ao criar nota fiscal {number}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def add_items_to_purchase_invoice(
    sequential_number: int,
    deliveries_order: List[Dict[str, Any]],
    copy_notes_purchase_orders: bool = True,
    copy_notes_resources: bool = False,
    copy_attachments_purchase_orders: bool = True,
) -> Dict:
    """
    Insere itens em uma nota fiscal a partir de entregas de pedidos de compra

    Args:
        sequential_number: Número sequencial da nota fiscal
        deliveries_order: Lista de entregas com estrutura:
            - purchaseOrderId: ID do pedido de compra
            - itemNumber: Número do item no pedido
            - deliveryScheduleNumber: Número da programação de entrega
            - deliveredQuantity: Quantidade entregue
            - keepBalance: Manter saldo (true/false)
        copy_notes_purchase_orders: Copiar observações dos pedidos de compra
        copy_notes_resources: Copiar observações dos recursos
        copy_attachments_purchase_orders: Copiar anexos dos pedidos de compra
    """
    item_data = {
        "deliveriesOrder": deliveries_order,
        "copyNotesPurchaseOrders": copy_notes_purchase_orders,
        "copyNotesResources": copy_notes_resources,
        "copyAttachmentsPurchaseOrders": copy_attachments_purchase_orders,
    }

    result = await make_sienge_request(
        "POST", f"/purchase-invoices/{sequential_number}/items/purchase-orders/delivery-schedules", json_data=item_data
    )

    if result["success"]:
        return {
            "success": True,
            "message": f"✅ Itens adicionados à nota fiscal {sequential_number} com sucesso",
            "item": result["data"],
        }

    return {
        "success": False,
        "message": f"❌ Erro ao adicionar itens à nota fiscal {sequential_number}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_purchase_invoices_deliveries_attended(
    bill_id: Optional[int] = None,
    sequential_number: Optional[int] = None,
    purchase_order_id: Optional[int] = None,
    invoice_item_number: Optional[int] = None,
    purchase_order_item_number: Optional[int] = None,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
) -> Dict:
    """
    Lista entregas atendidas entre pedidos de compra e notas fiscais

    Args:
        bill_id: ID do título da nota fiscal
        sequential_number: Número sequencial da nota fiscal
        purchase_order_id: ID do pedido de compra
        invoice_item_number: Número do item da nota fiscal
        purchase_order_item_number: Número do item do pedido de compra
        limit: Máximo de registros (padrão: 100, máximo: 200)
        offset: Deslocamento (padrão: 0)
    """
    params = {"limit": min(limit or 100, 200), "offset": offset or 0}

    if bill_id:
        params["billId"] = bill_id
    if sequential_number:
        params["sequentialNumber"] = sequential_number
    if purchase_order_id:
        params["purchaseOrderId"] = purchase_order_id
    if invoice_item_number:
        params["invoiceItemNumber"] = invoice_item_number
    if purchase_order_item_number:
        params["purchaseOrderItemNumber"] = purchase_order_item_number

    result = await make_sienge_request("GET", "/purchase-invoices/deliveries-attended", params=params)

    if result["success"]:
        data = result["data"]
        deliveries = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}

        return {
            "success": True,
            "message": f"✅ Encontradas {len(deliveries)} entregas atendidas",
            "deliveries": deliveries,
            "count": len(deliveries),
            "metadata": metadata,
            "filters": params,
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar entregas atendidas",
        "error": result.get("error"),
        "details": result.get("message"),
    }

# ----------------- helpers de arredondamento -----------------
def _to_cents(value: Decimal) -> int:
    return int((value * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def _from_cents(cents: int) -> Decimal:
    return (Decimal(cents) / Decimal(100)).quantize(Decimal("0.01"))

def split_installments_exact(total: Decimal, n: int) -> List[Decimal]:
    if n <= 0:
        raise ValueError("n must be >= 1")
    total_cents = _to_cents(total)
    base = total_cents // n
    resto = total_cents % n
    cents = [base + (1 if i < resto else 0) for i in range(n)]
    return [_from_cents(c) for c in cents]

def _infer_invoice_total(invoice: Dict[str, Any]) -> Optional[Decimal]:
    for k in ("totalAmount", "invoiceTotal", "amount", "total", "grandTotal"):
        if k in invoice and invoice[k] is not None:
            try:
                return Decimal(str(invoice[k]))
            except Exception:
                pass
    return None

# ----------------- pipeline sem anexo -----------------
@mcp.tool
async def process_purchase_invoice_pipeline(
    invoice: Optional[Dict[str, Any]] = None,
    sequential_number: Optional[int] = None,
    deliveries_order: Optional[List[Dict[str, Any]]] = None,
    installments: Optional[Dict[str, Any]] = None,
    bill_id: Optional[int] = None,
    options: Optional[Dict[str, Any]] = None,
) -> Dict:
    """
    Pipeline REFATORADO (sem criação de título):
      1) Cria (ou reutiliza) a NF de compra
      2) Adiciona itens (via pedidos + cronogramas) — opcional
      3) (NOVO) Atualiza parcelas do título criado automaticamente pelo Sienge

    IMPORTANTE: O Sienge cria títulos automaticamente ao lançar NF.
    Este pipeline NÃO cria títulos manualmente por padrão.

    Args:
        invoice: payload para POST /purchase-invoices (se sequential_number não for passado)
        sequential_number: usar NF já existente
        deliveries_order: lista p/ POST /purchase-invoices/{seq}/items/purchase-orders/delivery-schedules
        installments: {"dueDates": ["2025-11-03","2025-12-03"], "amounts": [920.70, 920.70]} 
                      ou {"daysToDue": [30, 60, 90], "baseDate": "YYYY-MM-DD", "amounts": [...]}
        bill_id: ID do título (opcional; se ausente, auto-descobre)
        options: {"dryRun": bool, "resumeIfExists": bool, "copyNotesPurchaseOrders": bool,
                  "copyNotesResources": bool, "copyAttachmentsPurchaseOrders": bool,
                  "forceCreateBill": bool (use apenas se Sienge não criar automaticamente)}
    """
    corr_id = str(uuid.uuid4())
    opts = options or {}
    dry = bool(opts.get("dryRun", False))
    resume = bool(opts.get("resumeIfExists", True))
    force_create = bool(opts.get("forceCreateBill", False))

    out: Dict[str, Any] = {"success": True, "correlationId": corr_id, "steps": []}
    log.info("Pipeline iniciado - correlationId: %s, dryRun: %s", corr_id, dry)

    # 1) NF: criar ou reutilizar
    nf_seq = sequential_number
    nf_obj: Optional[Dict[str, Any]] = None

    if nf_seq is None and invoice:
        if dry:
            out["steps"].append({"step": "create_invoice", "dryRun": True, "payload": invoice})
        else:
            r = await safe_request("POST", "/purchase-invoices", json_data=invoice)
            if not r.get("success"):
                out.update(success=False)
                out["steps"].append({"step":"create_invoice","ok":False,"error":r.get("error"),"details":r.get("message")})
                return out
            nf_obj = r.get("data") or {}
            nf_seq = nf_obj.get("sequentialNumber") or nf_obj.get("id")
            out["steps"].append({"step":"create_invoice","ok":True,"sequentialNumber":nf_seq})
            log.info("NF criada - sequentialNumber: %s", nf_seq)
    elif nf_seq is not None and resume:
        if dry:
            out["steps"].append({"step":"load_invoice","dryRun":True,"sequentialNumber":nf_seq})
        else:
            r = await safe_request("GET", f"/purchase-invoices/{nf_seq}")
            if not r.get("success"):
                out.update(success=False)
                out["steps"].append({"step":"load_invoice","ok":False,"sequentialNumber":nf_seq,"error":r.get("error"),"details":r.get("message")})
                return out
            nf_obj = r.get("data") or {}
            out["steps"].append({"step":"load_invoice","ok":True,"sequentialNumber":nf_seq})
            log.info("NF carregada - sequentialNumber: %s", nf_seq)

    if nf_seq is None:
        out.update(success=False)
        out["steps"].append({"step":"create_or_load_invoice","ok":False,"error":"Sem sequential_number e sem invoice"})
        return out

    # 2) Itens via pedidos/cronogramas (opcional)
    if deliveries_order:
        payload_items = {
            "deliveriesOrder": deliveries_order,
            "copyNotesPurchaseOrders": bool(opts.get("copyNotesPurchaseOrders", True)),
            "copyNotesResources": bool(opts.get("copyNotesResources", False)),
            "copyAttachmentsPurchaseOrders": bool(opts.get("copyAttachmentsPurchaseOrders", True)),
        }
        if dry:
            out["steps"].append({"step":"add_items_from_purchase_orders","dryRun":True,"payload":payload_items})
        else:
            r = await safe_request("POST", f"/purchase-invoices/{nf_seq}/items/purchase-orders/delivery-schedules", json_data=payload_items)
            if not r.get("success"):
                out.update(success=False)
                out["steps"].append({"step":"add_items_from_purchase_orders","ok":False,"error":r.get("error"),"details":r.get("message")})
                return out
            out["steps"].append({"step":"add_items_from_purchase_orders","ok":True})
            log.info("Itens adicionados à NF %s", nf_seq)
    else:
        out["steps"].append({"step":"add_items_from_purchase_orders","skipped":True})

    # 3) NOVO: Atualizar parcelas do título auto-criado (se installments fornecido)
    if installments:
        if dry:
            out["steps"].append({"step":"update_auto_bill_installments","dryRun":True,"payload":installments})
        else:
            log.info("Atualizando parcelas do título auto-criado para NF %s", nf_seq)
            upd = await ap_update_auto_bill_installments(
                sequential_number=nf_seq,
                bill_id=bill_id,
                due_dates=installments.get("dueDates"),
                days_to_due=installments.get("daysToDue"),
                base_date=installments.get("baseDate"),
                amounts=installments.get("amounts"),
            )
            
            # Extrair apenas campos relevantes para o step (sem installments completos)
            step_data = {
                "step": "update_auto_bill_installments",
                "ok": upd.get("success"),
                "billId": upd.get("billId"),
                "sumInstallments": upd.get("sumInstallments"),
                "expectedAmount": upd.get("expectedAmount"),
                "count": len(upd.get("installments", []))
            }
            
            if not upd.get("success"):
                step_data.update({
                    "error": upd.get("error"),
                    "details": upd.get("message"),
                    "note": upd.get("note")
                })
                out.update(success=False)
            
            out["steps"].append(step_data)
            
            if not upd.get("success"):
                log.warning("Falha ao atualizar parcelas: %s", upd.get("message"))
                return out
            
            log.info("Parcelas atualizadas com sucesso - billId: %s", upd.get("billId"))
            out["billId"] = upd.get("billId")
    else:
        out["steps"].append({"step":"update_auto_bill_installments","skipped":True,"note":"Sienge criou título automaticamente, mas parcelas não foram atualizadas (installments não fornecido)"})

    out["success"] = True
    out["invoiceSequential"] = nf_seq
    log.info("Pipeline concluído com sucesso - NF: %s", nf_seq)
    return out


# ============ TÍTULOS A PAGAR (ACCOUNTS PAYABLE) - REFATORADO ============
# Nota: O Sienge cria títulos automaticamente ao lançar NF.
# Este módulo ATUALIZA parcelas do título auto-criado, não cria novos títulos por padrão.

# ---------- Logger seguro ----------
log = logging.getLogger("sienge_mcp.ap")
if not log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    log.addHandler(_h)
log.setLevel(logging.INFO)

# ---------- Wrapper seguro para evitar "objeto não chamável" ----------
async def safe_request(method: str, path: str, **kwargs):
    """
    Wrapper seguro que garante make_sienge_request é callable e retorna dict.
    Previne erros de 'objeto não chamável' e anexa trace em exceções.
    """
    try:
        fn = globals().get("make_sienge_request")
        if not callable(fn):
            return {
                "success": False,
                "error": "TypeError",
                "message": "make_sienge_request não é chamável (sombreado?)"
            }
        res = await fn(method, path, **kwargs)
        if not isinstance(res, dict):
            return {
                "success": False,
                "error": "TypeError",
                "message": f"Resposta não-dict em {path}: {type(res)}"
            }
        return res
    except Exception as e:
        log.error("Exceção em %s %s: %s", method, path, e)
        return {
            "success": False,
            "error": type(e).__name__,
            "message": str(e),
            "trace": traceback.format_exc()
        }

# ---------- Helpers de precisão financeira (centavos) ----------
def _to_cents(x: Decimal) -> int:
    """Converte Decimal para centavos com arredondamento correto."""
    return int((x * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def _from_cents(c: int) -> Decimal:
    """Converte centavos de volta para Decimal com 2 casas decimais."""
    return (Decimal(c) / Decimal(100)).quantize(Decimal("0.01"))

def split_installments_exact(total: Decimal, n: int) -> List[Decimal]:
    """
    Divide total em n parcelas garantindo soma exata.
    Distribui o resto (centavos) nas primeiras parcelas.
    """
    if n <= 0:
        raise ValueError("n must be >= 1")
    cents = _to_cents(total)
    base, resto = divmod(cents, n)
    parts = [base + (1 if i < resto else 0) for i in range(n)]
    return [_from_cents(p) for p in parts]

def _infer_invoice_total(invoice: Dict[str, Any]) -> Optional[Decimal]:
    """Tenta extrair total da NF de vários campos possíveis."""
    for k in ("totalAmount", "invoiceTotal", "amount", "total", "grandTotal", "netAmount", "grossAmount"):
        v = invoice.get(k)
        if v is not None:
            try:
                return Decimal(str(v))
            except Exception:
                pass
    return None

def _iso(d: datetime) -> str:
    """Formata datetime para string ISO date."""
    return d.strftime("%Y-%m-%d")

def _today_utc_date_str() -> str:
    """Retorna data de hoje em UTC como string ISO."""
    return datetime.utcnow().strftime("%Y-%m-%d")

# ---------- Descoberta automática de billId (RESILIENTE com 3 fallbacks) ----------

async def _try_bill_from_invoice(sequential_number: int) -> Optional[int]:
    """
    Fallback #1: Tenta encontrar billId dentro do GET /purchase-invoices/{seq}.
    Algumas configurações do Sienge expõem o vínculo direto na NF.
    """
    try:
        r = await safe_request("GET", f"/purchase-invoices/{sequential_number}")
        if not r.get("success"):
            return None
        inv = r.get("data") or {}
        
        # Tenta chaves comuns de billId
        for key in ("billId", "titleId", "financialBillId", "accountsPayableBillId"):
            if inv.get(key):
                try:
                    return int(inv[key])
                except Exception:
                    pass
        
        # Às vezes vem aninhado em objetos
        for parent_key in ("financial", "accountsPayable", "bill", "title"):
            nested = inv.get(parent_key) or {}
            for key in ("billId", "id", "titleId"):
                if nested.get(key):
                    try:
                        return int(nested[key])
                    except Exception:
                        pass
        
        return None
    except Exception as e:
        log.debug("Fallback #1 (NF) falhou para NF %s: %s", sequential_number, e)
        return None


async def _try_bill_via_bills_search(
    creditor_id: int,
    company_id: int,
    invoice_total: Optional[Decimal],
    issue_date: Optional[str],
    movement_date: Optional[str]
) -> Optional[int]:
    """
    Fallback #2: Busca via GET /bills com filtros (creditor, company, período).
    Depende da disponibilidade dos filtros no ambiente Sienge.
    """
    try:
        # Janela de datas (±7 dias do movimento/emissão)
        base = movement_date or issue_date
        params = {
            "creditorId": creditor_id,
            "companyId": company_id,
            "limit": 50,
            "offset": 0
        }
        
        if base:
            try:
                dt = datetime.strptime(base, "%Y-%m-%d")
                params["registeredDateFrom"] = (dt - timedelta(days=7)).strftime("%Y-%m-%d")
                params["registeredDateTo"] = (dt + timedelta(days=7)).strftime("%Y-%m-%d")
            except Exception:
                pass
        
        r = await safe_request("GET", "/bills", params=params)
        if not r.get("success"):
            return None
        
        data = r.get("data") or {}
        rows = data.get("results", []) if isinstance(data, dict) else data or []
        if not rows:
            return None
        
        # 1) Casa por total exato da NF
        if invoice_total is not None:
            for b in rows:
                amt = b.get("amount")
                try:
                    if Decimal(str(amt)).quantize(Decimal("0.01")) == invoice_total.quantize(Decimal("0.01")):
                        bid = b.get("id") or b.get("billId")
                        if bid:
                            log.info("Fallback #2 (Bills API) encontrou billId %s por valor exato", bid)
                            return int(bid)
                except Exception:
                    continue
        
        # 2) Caso contrário, retorna o mais recente "Em Aberto"
        for b in rows:
            status_str = str(b.get("status", "")).lower()
            if status_str in ("open", "em aberto", "aberto", "pending", "pendente"):
                bid = b.get("id") or b.get("billId")
                if bid:
                    log.info("Fallback #2 (Bills API) encontrou billId %s (status aberto)", bid)
                    return int(bid)
        
        return None
    except Exception as e:
        log.debug("Fallback #2 (Bills API) falhou: %s", e)
        return None


async def _try_bill_via_bulk_outcome(
    creditor_id: int,
    company_id: int,
    invoice_total: Optional[Decimal],
    window_days: int = 14
) -> Optional[int]:
    """
    Fallback #3: Bulk Data - Parcelas do Contas a Pagar.
    Agrupa parcelas por billId e compara soma com total da NF.
    Esta é a "bala de prata" porque Bulk Data sempre retorna billId.
    """
    if invoice_total is None:
        log.debug("Fallback #3 (Bulk Data) ignorado: sem total da NF")
        return None
    
    try:
        from collections import defaultdict
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        start_date = (datetime.utcnow() - timedelta(days=window_days)).strftime("%Y-%m-%d")
        
        params = {
            "creditorId": creditor_id,
            "companyId": company_id,
            "registeredDateFrom": start_date,
            "registeredDateTo": today,
            "limit": 500,
            "offset": 0
        }
        
        # Tenta diferentes paths do Bulk Data
        for path in ("/bulk-data/outcome", "/bulk-data/v1/outcome", "/accounts-payable/installments"):
            r = await safe_request("GET", path, params=params)
            if not r.get("success"):
                continue
            
            data = r.get("data") or {}
            rows = data.get("results", []) if isinstance(data, dict) else data or []
            if not rows:
                continue
            
            # Agrupa por billId e soma valores
            sums = defaultdict(Decimal)
            for item in rows:
                bid = item.get("billId") or item.get("idBill") or item.get("titleId")
                val = item.get("amount") or item.get("value") or item.get("installmentAmount")
                try:
                    if bid and val is not None:
                        sums[int(bid)] += Decimal(str(val))
                except Exception:
                    pass
            
            # Procura billId cuja soma de parcelas = total da NF
            for bid, total_sum in sums.items():
                if total_sum.quantize(Decimal("0.01")) == invoice_total.quantize(Decimal("0.01")):
                    log.info("Fallback #3 (Bulk Data) encontrou billId %s (soma = NF)", bid)
                    return int(bid)
        
        return None
    except Exception as e:
        log.debug("Fallback #3 (Bulk Data) falhou: %s", e)
        return None


async def _try_bill_from_deliveries_attended(sequential_number: int) -> Optional[int]:
    """
    Fallback #0 (original): Tenta via endpoint deliveries-attended.
    Mantido por compatibilidade, mas nem sempre funciona.
    """
    try:
        r = await safe_request(
            "GET",
            "/purchase-invoices/deliveries-attended",
            params={"sequentialNumber": sequential_number, "limit": 1, "offset": 0}
        )
        if r.get("success"):
            data = r.get("data") or {}
            rows = data.get("results", []) if isinstance(data, dict) else data or []
            if rows:
                bid = rows[0].get("billId")
                try:
                    if bid is not None:
                        log.info("Fallback #0 (deliveries-attended) encontrou billId %s", bid)
                        return int(bid)
                except Exception:
                    pass
    except Exception as e:
        log.debug("Fallback #0 (deliveries-attended) falhou: %s", e)
    return None


async def resolve_bill_id_for_invoice(
    sequential_number: int,
    creditor_id: Optional[int] = None,
    company_id: Optional[int] = None
) -> Optional[int]:
    """
    Sistema resiliente de descoberta de billId com 4 estratégias (em ordem):
    
    0. deliveries-attended (original, rápido mas nem sempre funciona)
    1. Dentro da própria NF (quando tenant expõe billId)
    2. Bills API (filtrando por creditor, company, período e valor)
    3. Bulk Data outcome (agrupa parcelas por billId e compara soma)
    
    Args:
        sequential_number: Sequential number da NF
        creditor_id: ID do fornecedor (opcional, será buscado da NF se omitido)
        company_id: ID da empresa (opcional, será buscado da NF se omitido)
    
    Returns:
        billId encontrado ou None
    """
    log.info("Iniciando descoberta resiliente de billId para NF %s", sequential_number)
    
    # Fallback #0: deliveries-attended (mantido por compatibilidade)
    bid = await _try_bill_from_deliveries_attended(sequential_number)
    if bid:
        return bid
    
    # Busca NF para ter metadados (total, datas, creditor, company)
    inv_res = await safe_request("GET", f"/purchase-invoices/{sequential_number}")
    if not inv_res.get("success"):
        log.warning("Não foi possível buscar NF %s para descoberta de billId", sequential_number)
        return None
    
    invoice = inv_res.get("data") or {}
    total = _infer_invoice_total(invoice)
    issue_date = invoice.get("issueDate")
    movement_date = invoice.get("movementDate")
    cred = creditor_id or invoice.get("supplierId") or invoice.get("creditorId")
    comp = company_id or invoice.get("companyId")
    
    # Fallback #1: Direto na NF
    bid = await _try_bill_from_invoice(sequential_number)
    if bid:
        return bid
    
    # Fallback #2 e #3: Precisam de creditor e company
    if not cred or not comp:
        log.warning(
            "Fallbacks #2 e #3 requerem creditorId e companyId. "
            "NF %s não tem esses dados ou não foram fornecidos.",
            sequential_number
        )
        return None
    
    # Fallback #2: Bills API
    bid = await _try_bill_via_bills_search(int(cred), int(comp), total, issue_date, movement_date)
    if bid:
        return bid
    
    # Fallback #3: Bulk Data (bala de prata)
    bid = await _try_bill_via_bulk_outcome(int(cred), int(comp), total)
    if bid:
        return bid
    
    log.warning("Todos os 4 fallbacks falharam para NF %s", sequential_number)
    return None

# ---------- Tools principais (Nova Arquitetura) ----------

@mcp.tool
async def ap_update_auto_bill_installments(
    sequential_number: int,
    bill_id: Optional[int] = None,
    due_dates: Optional[List[str]] = None,
    days_to_due: Optional[List[int]] = None,
    base_date: Optional[str] = None,
    amounts: Optional[List[float]] = None
) -> Dict:
    """
    Atualiza parcelas do título (criado automaticamente pelo Sienge ao lançar NF).
    
    Args:
        sequential_number: Sequential number da nota fiscal
        bill_id: ID do título (opcional; se ausente, descoberto automaticamente)
        due_dates: Lista de datas de vencimento ["2025-11-03", "2025-12-03"]
        days_to_due: Lista de dias até vencimento [30, 60, 90] (relativo a base_date)
        base_date: Data base para days_to_due (padrão: hoje UTC) "YYYY-MM-DD"
        amounts: Lista de valores das parcelas (se omitido, divide igualmente o total da NF)
    
    Returns:
        Dict com success, billId, soma das parcelas, parcelas com daysToDue calculado
    
    Examples:
        - Com datas explícitas: {"sequential_number": 2360, "due_dates": ["2025-11-03", "2025-12-03"]}
        - Com dias relativos: {"sequential_number": 2360, "days_to_due": [30, 60, 90]}
        - Com valores customizados: {"sequential_number": 2360, "due_dates": [...], "amounts": [920.70, 920.70]}
    """
    log.info("Atualizando parcelas - NF: %s, bill_id: %s", sequential_number, bill_id)
    
    # 1) Buscar NF (para pegar total se necessário)
    inv = await safe_request("GET", f"/purchase-invoices/{sequential_number}")
    if not inv.get("success"):
        return {
            "success": False,
            "message": f"❌ NF {sequential_number} não encontrada",
            "details": inv.get("message"),
            "error": inv.get("error")
        }
    invoice = inv.get("data") or {}
    
    # 2) Descobrir billId com sistema resiliente (4 fallbacks)
    bid = bill_id or await resolve_bill_id_for_invoice(sequential_number)
    if not bid:
        return {
            "success": False,
            "message": "❌ Não foi possível descobrir o billId automaticamente após 4 tentativas.",
            "hint": "Envie 'bill_id' explicitamente. Para melhorar auto-descoberta, garanta que a NF tem creditorId e companyId.",
            "fallbacks_tried": [
                "deliveries-attended (endpoint específico)",
                "Dentro da própria NF (campos billId, financial.billId, etc)",
                "Bills API (busca por creditor, company e valor)",
                "Bulk Data outcome (agrupa parcelas por billId)"
            ],
            "need": {
                "bill_id": "Requerido se auto-descoberta falhar",
                "creditorId": "Opcional, melhora precisão dos fallbacks #2 e #3",
                "companyId": "Opcional, melhora precisão dos fallbacks #2 e #3"
            }
        }
    
    log.info("BillId identificado: %s", bid)
    
    # 3) Calcular datas de vencimento
    base = datetime.strptime(base_date, "%Y-%m-%d") if base_date else datetime.utcnow()
    
    if due_dates:
        ds = due_dates
    else:
        if not days_to_due:
            return {
                "success": False,
                "message": "❌ Informe 'due_dates' ou 'days_to_due'.",
                "error": "MISSING_DUE_DATES"
            }
        ds = [_iso(base + timedelta(days=int(x))) for x in days_to_due]
    
    # 4) Calcular valores das parcelas
    if amounts:
        vals = [Decimal(str(x)) for x in amounts]
        total = sum(vals)
        if len(vals) != len(ds):
            return {
                "success": False,
                "message": f"❌ 'amounts' ({len(vals)}) e datas ({len(ds)}) devem ter o mesmo tamanho",
                "error": "SIZE_MISMATCH"
            }
    else:
        total_nf = _infer_invoice_total(invoice)
        if total_nf is None:
            return {
                "success": False,
                "message": "❌ Não foi possível inferir o total da NF. Informe 'amounts' explicitamente.",
                "error": "MISSING_INVOICE_TOTAL",
                "hint": "Campos tentados: totalAmount, invoiceTotal, amount, total, grandTotal, netAmount, grossAmount"
            }
        vals = split_installments_exact(total_nf, len(ds))
        total = sum(vals)
    
    log.info("Calculadas %d parcelas - Total: %s", len(vals), total)
    
    # 5) Montar payload de parcelas
    parcels = [
        {
            "number": i + 1,
            "amount": float(v),
            "dueDate": ds[i]
        }
        for i, v in enumerate(vals)
    ]
    
    # 6) IMPORTANTE: Tentar PUT primeiro (se API mudar no futuro)
    # Atualmente a API Sienge não suporta atualização de parcelas via API
    # Este código está preparado para quando/se suportarem
    upd = await safe_request("PUT", f"/bills/{int(bid)}/installments", json_data={"installments": parcels})
    
    if not upd.get("success"):
        log.warning("PUT não suportado, tentando POST...")
        upd = await safe_request("POST", f"/bills/{int(bid)}/installments", json_data={"installments": parcels})
    
    if not upd.get("success"):
        return {
            "success": False,
            "message": "❌ Erro ao atualizar parcelas (API pode não suportar atualização)",
            "billId": bid,
            "details": upd.get("message"),
            "error": upd.get("error"),
            "note": "⚠️ A API Sienge pode não permitir atualização de parcelas após criação do título. Considere ajuste manual no ERP."
        }
    
    log.info("Parcelas atualizadas com sucesso")
    
    # 7) Buscar parcelas atualizadas + verificar soma
    lst = await safe_request("GET", f"/bills/{int(bid)}/installments")
    if not lst.get("success"):
        return {
            "success": False,
            "message": "⚠️ Parcelas podem ter sido atualizadas, mas falhou conferência de leitura",
            "billId": bid,
            "details": lst.get("message")
        }
    
    data = lst.get("data") or {}
    items = data.get("results", []) if isinstance(data, dict) else data or []
    soma = sum(Decimal(str(p.get("amount", 0))) for p in items)
    
    # 8) Calcular daysToDue para cada parcela (no retorno, não grava no Sienge)
    for p in items:
        try:
            dd = datetime.strptime(str(p.get("dueDate")), "%Y-%m-%d")
            p["daysToDue"] = (dd - base).days
        except Exception:
            p["daysToDue"] = None
    
    ok = (soma.quantize(Decimal("0.01")) == total.quantize(Decimal("0.01")))
    
    return {
        "success": ok,
        "message": "✅ Parcelas atualizadas e soma confere" if ok else "⚠️ Parcelas atualizadas, mas soma não confere",
        "billId": bid,
        "invoiceSequential": sequential_number,
        "sumInstallments": float(soma),
        "expectedAmount": float(total),
        "installments": items,
        "calculationBase": _iso(base) if base else None
    }

# ---------- Tools de atualização de título (cabeçalho) ----------

@mcp.tool
async def ap_patch_bill(
    bill_id: int,
    document_identification_id: Optional[str] = None,
    document_number: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Atualiza campos do Título (cabeçalho) via PATCH. Espera 204 em caso de sucesso.
    
    Args:
        bill_id: ID do título
        document_identification_id: Tipo do documento (ex: "NF", "DP")
        document_number: Número do documento
        extra_fields: Campos adicionais conforme parametrização do Sienge
    
    Returns:
        Dict com success status e dados do título atualizado
    
    Examples:
        {"bill_id": 123456, "document_identification_id": "NF", "document_number": "AX123"}
    """
    log.info("Atualizando título %s via PATCH", bill_id)
    
    body = {}
    if document_identification_id is not None:
        body["documentIdentificationId"] = document_identification_id
    if document_number is not None:
        body["documentNumber"] = document_number
    if extra_fields:
        body.update(extra_fields)
    
    if not body:
        return {
            "success": False,
            "message": "❌ Nenhum campo para atualizar no PATCH do Título.",
            "hint": "Informe ao menos 'document_identification_id', 'document_number' ou 'extra_fields'"
        }
    
    log.info("Campos a atualizar: %s", list(body.keys()))
    
    res = await safe_request("PATCH", f"/bills/{bill_id}", json_data=body)
    if not res.get("success"):
        return {
            "success": False,
            "message": "❌ Erro ao atualizar o título",
            "billId": bill_id,
            "error": res.get("error"),
            "details": res.get("message"),
        }
    
    # Read-back opcional (confirma estado após 204)
    get_res = await safe_request("GET", f"/bills/{bill_id}")
    if get_res.get("success"):
        log.info("Título %s atualizado e confirmado via GET", bill_id)
        return {
            "success": True,
            "message": "✅ Título atualizado com sucesso",
            "billId": bill_id,
            "bill": get_res.get("data")
        }
    
    return {
        "success": True,
        "message": "✅ Título atualizado (204); falha ao ler estado final",
        "billId": bill_id,
        "readbackError": get_res.get("message"),
    }


@mcp.tool
async def ap_attach_bill(
    bill_id: int,
    description: str,
    file_path: Optional[str] = None,
    file_name: Optional[str] = None,
    file_content_base64: Optional[str] = None,
    content_type: Optional[str] = None
) -> Dict:
    """
    Insere anexo no Título via POST multipart/form-data.
    
    Args:
        bill_id: ID do título
        description: Descrição do anexo (obrigatório)
        file_path: Caminho do arquivo no sistema (usar OU file_content_base64)
        file_name: Nome do arquivo (obrigatório se usar file_content_base64)
        file_content_base64: Conteúdo do arquivo em Base64
        content_type: MIME type (opcional, detectado automaticamente)
    
    Returns:
        Dict com success status e lista de anexos
    
    Examples:
        - Via path: {"bill_id": 123456, "description": "NF-e", "file_path": "/tmp/nota.pdf"}
        - Via Base64: {"bill_id": 123456, "description": "NF-e", "file_name": "nota.pdf", "file_content_base64": "JVBERi0..."}
    """
    import base64
    import mimetypes
    import os
    
    log.info("Anexando arquivo ao título %s", bill_id)
    
    if not description:
        return {
            "success": False,
            "message": "❌ Descrição do anexo é obrigatória.",
            "hint": "Informe 'description' para identificar o anexo"
        }
    
    # Carregar conteúdo
    if file_path:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"❌ Arquivo não encontrado: {file_path}",
                "error": "FILE_NOT_FOUND"
            }
        file_name = file_name or os.path.basename(file_path)
        if not content_type:
            ctype, _ = mimetypes.guess_type(file_name)
            content_type = ctype or "application/octet-stream"
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        log.info("Arquivo carregado: %s (%d bytes)", file_name, len(file_bytes))
    elif file_content_base64 and file_name:
        try:
            file_bytes = base64.b64decode(file_content_base64)
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Erro ao decodificar Base64: {e}",
                "error": "INVALID_BASE64"
            }
        if not content_type:
            ctype, _ = mimetypes.guess_type(file_name)
            content_type = ctype or "application/octet-stream"
        log.info("Arquivo Base64 decodificado: %s (%d bytes)", file_name, len(file_bytes))
    else:
        return {
            "success": False,
            "message": "❌ Informe 'file_path' OU ('file_name' + 'file_content_base64').",
            "error": "MISSING_FILE"
        }
    
    # Montar multipart (campo deve chamar 'file')
    files = {
        "file": (file_name, file_bytes, content_type),
    }
    
    # description é QUERY PARAM segundo a API
    params = {"description": description}
    
    res = await safe_request(
        "POST",
        f"/bills/{bill_id}/attachments",
        params=params,
        files=files
    )
    
    if not res.get("success"):
        return {
            "success": False,
            "message": "❌ Erro ao inserir anexo",
            "billId": bill_id,
            "fileName": file_name,
            "error": res.get("error"),
            "details": res.get("message"),
        }
    
    log.info("Anexo %s inserido com sucesso no título %s", file_name, bill_id)
    
    # Conferência: listar anexos
    check = await safe_request("GET", f"/bills/{bill_id}/attachments")
    attachments = None
    if check.get("success"):
        data = check.get("data") or {}
        attachments = data.get("results", []) if isinstance(data, dict) else data
    
    return {
        "success": True,
        "message": f"✅ Anexo '{file_name}' inserido com sucesso",
        "billId": bill_id,
        "fileName": file_name,
        "attachments": attachments,
        "attachmentsCount": len(attachments) if attachments else None
    }


@mcp.tool
async def ap_finalize_bill(
    bill_id: int,
    patch_body: Optional[Dict[str, Any]] = None,
    attachment: Optional[Dict[str, Any]] = None,
    audit: bool = True
) -> Dict:
    """
    Orquestrador: faz PATCH do título (se informado), insere anexo (se informado) e audita status/anexos no final.
    
    Args:
        bill_id: ID do título
        patch_body: Campos para atualizar via PATCH (ex: {"documentIdentificationId": "NF", "documentNumber": "123"})
        attachment: Dados do anexo (ex: {"description": "NF-e", "file_path": "/tmp/nota.pdf"})
        audit: Se True, audita status e anexos ao final
    
    Returns:
        Dict com steps executados e auditoria final
    
    Examples:
        - Só PATCH: {"bill_id": 123456, "patch_body": {"documentNumber": "AX123"}}
        - Só anexo: {"bill_id": 123456, "attachment": {"description": "NF-e", "file_path": "/tmp/nota.pdf"}}
        - Completo: {"bill_id": 123456, "patch_body": {...}, "attachment": {...}, "audit": true}
    """
    import base64
    import mimetypes
    import os
    
    log.info("Finalizando título %s (PATCH + Anexo + Auditoria)", bill_id)
    
    out = {"billId": bill_id, "steps": []}
    
    # 1) PATCH (se houver)
    if patch_body:
        log.info("Executando PATCH no título %s", bill_id)
        
        # Montar payload do PATCH
        payload = {}
        if patch_body.get("documentIdentificationId"):
            payload["documentIdentificationId"] = patch_body["documentIdentificationId"]
        if patch_body.get("documentNumber"):
            payload["documentNumber"] = patch_body["documentNumber"]
        
        # Adicionar campos extras
        extra = {k: v for k, v in patch_body.items() 
                if k not in ("documentIdentificationId", "documentNumber")}
        payload.update(extra)
        
        # Executar PATCH
        res_patch = await safe_request("PATCH", f"/bills/{bill_id}", json_data=payload)
        
        # Verificar se funcionou (HTTP 204 retorna data=None)
        if res_patch.get("success"):
            # Confirmar com GET
            check = await safe_request("GET", f"/bills/{bill_id}")
            out["steps"].append({
                "step": "patch",
                "result": {
                    "success": True,
                    "message": "✅ Título atualizado",
                    "bill": check.get("data") if check.get("success") else None
                }
            })
        else:
            out["steps"].append({"step": "patch", "result": res_patch})
            out["success"] = False
            out["message"] = "❌ Falha no PATCH do título."
            log.warning("PATCH falhou para título %s: %s", bill_id, res_patch.get("error"))
            return out
    
    # 2) Anexo (se houver)
    if attachment:
        log.info("Anexando arquivo ao título %s", bill_id)
        
        description = attachment.get("description", "Anexo")
        file_path = attachment.get("file_path")
        file_name = attachment.get("file_name")
        file_content_base64 = attachment.get("file_content_base64")
        content_type = attachment.get("content_type")
        
        # Validações
        if not description:
            out["steps"].append({
                "step": "attachment",
                "result": {"success": False, "error": "MISSING_DESCRIPTION"}
            })
            out["success"] = False
            out["message"] = "❌ Descrição do anexo é obrigatória."
            return out
        
        # Carregar arquivo
        if file_path:
            if not os.path.exists(file_path):
                out["steps"].append({
                    "step": "attachment",
                    "result": {"success": False, "error": "FILE_NOT_FOUND", "path": file_path}
                })
                out["success"] = False
                out["message"] = f"❌ Arquivo não encontrado: {file_path}"
                return out
            
            file_name = file_name or os.path.basename(file_path)
            if not content_type:
                ctype, _ = mimetypes.guess_type(file_name)
                content_type = ctype or "application/octet-stream"
            
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            log.info("Arquivo carregado: %s (%d bytes)", file_name, len(file_bytes))
            
        elif file_content_base64 and file_name:
            try:
                file_bytes = base64.b64decode(file_content_base64)
            except Exception as e:
                out["steps"].append({
                    "step": "attachment",
                    "result": {"success": False, "error": "INVALID_BASE64", "details": str(e)}
                })
                out["success"] = False
                out["message"] = f"❌ Erro ao decodificar Base64: {e}"
                return out
            
            if not content_type:
                ctype, _ = mimetypes.guess_type(file_name)
                content_type = ctype or "application/octet-stream"
            log.info("Arquivo Base64 decodificado: %s (%d bytes)", file_name, len(file_bytes))
        else:
            out["steps"].append({
                "step": "attachment",
                "result": {"success": False, "error": "MISSING_FILE"}
            })
            out["success"] = False
            out["message"] = "❌ Informe 'file_path' OU ('file_name' + 'file_content_base64')."
            return out
        
        # Preparar multipart
        files = {"file": (file_name, file_bytes, content_type)}
        params = {"description": description}
        
        # Executar POST
        res_att = await safe_request("POST", f"/bills/{bill_id}/attachments", params=params, files=files)
        
        if res_att.get("success"):
            # Listar anexos para confirmar
            check = await safe_request("GET", f"/bills/{bill_id}/attachments")
            attachments = None
            if check.get("success"):
                data = check.get("data") or {}
                attachments = data.get("results", []) if isinstance(data, dict) else data
            
            out["steps"].append({
                "step": "attachment",
                "result": {
                    "success": True,
                    "message": f"✅ Anexo '{file_name}' inserido",
                    "fileName": file_name,
                    "attachments": attachments
                }
            })
        else:
            out["steps"].append({"step": "attachment", "result": res_att})
            out["success"] = False
            out["message"] = "❌ Falha ao anexar arquivo."
            log.warning("Anexo falhou para título %s: %s", bill_id, res_att.get("error"))
            return out
    
    # 3) Auditoria rápida
    if audit:
        log.info("Auditando título %s", bill_id)
        bill_res = await safe_request("GET", f"/bills/{bill_id}")
        atts_res = await safe_request("GET", f"/bills/{bill_id}/attachments")
        
        status = None
        document_number = None
        if bill_res.get("success"):
            b = bill_res.get("data") or {}
            status = b.get("status")
            document_number = b.get("documentNumber")
        
        att_count = None
        att_list = None
        if atts_res.get("success"):
            data = atts_res.get("data") or {}
            lst = data.get("results", []) if isinstance(data, dict) else data
            att_count = len(lst or [])
            att_list = [{"name": a.get("name"), "description": a.get("description")} 
                       for a in (lst or [])]
        
        out["audit"] = {
            "status": status,
            "documentNumber": document_number,
            "attachmentsCount": att_count,
            "attachments": att_list
        }
    
    out["success"] = True
    out["message"] = "✅ Título finalizado (PATCH/anexo executados com sucesso)."
    log.info("Título %s finalizado com sucesso", bill_id)
    return out


# ---------- Tools de consulta (mantidas) ----------

@mcp.tool
async def ap_list_installments(bill_id: int) -> Dict:
    """
    Lista parcelas de um título (somente leitura).
    
    Args:
        bill_id: ID do título
    
    Returns:
        Dict com lista de parcelas, contagem e metadata
    """
    log.info("Listando parcelas do título: %s", bill_id)
    res = await safe_request("GET", f"/bills/{bill_id}/installments")
    
    if res.get("success"):
        data = res.get("data")
        items = data.get("results", []) if isinstance(data, dict) else data or []
        meta = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        
        return {
            "success": True,
            "installments": items,
            "count": len(items),
            "metadata": meta
        }
    
    return {
        "success": False,
        "message": f"❌ Erro ao listar parcelas do título {bill_id}",
        "error": res.get("error"),
        "details": res.get("message")
    }

# ---------- Tools DEPRECATED (criação de título - apenas fallback) ----------

@mcp.tool
async def ap_create_bill(bill: Dict[str, Any], force_create: bool = False) -> Dict:
    """
    [DEPRECATED] Cria título manualmente (use apenas se Sienge não criar automaticamente).
    
    O Sienge cria títulos automaticamente ao lançar NF. Esta tool existe apenas como fallback.
    
    Args:
        bill: Payload do título (documentId, creditorId, companyId, amount, issueDate, dueDate)
        force_create: Deve ser True para confirmar criação manual
    
    Returns:
        Dict com success status e dados do título criado
    """
    if not force_create:
        return {
            "success": False,
            "message": "⚠️ DEPRECATED: O Sienge cria títulos automaticamente ao lançar NF.",
            "hint": "Use 'ap_update_auto_bill_installments' para atualizar o título criado automaticamente.",
            "note": "Se realmente precisa criar manualmente, passe force_create=True"
        }
    
    log.warning("Criação manual de título (force_create=True) - documentId: %s", bill.get("documentId"))
    
    try:
        res = await safe_request("POST", "/bills", json_data=bill)
        
        if res.get("success"):
            data = res.get("data") or {}
            bill_id = data.get("id") or data.get("billId")
            return {
                "success": True,
                "message": "✅ Título criado manualmente",
                "bill": data,
                "billId": bill_id,
                "warning": "⚠️ Este título foi criado manualmente, não pelo processo automático do Sienge"
            }
        
        return {
            "success": False,
            "message": "❌ Erro ao criar título",
            "error": res.get("error"),
            "details": res.get("message")
        }
    except Exception as e:
        log.error("Exceção em ap_create_bill: %s", e, exc_info=True)
        return {
            "success": False,
            "message": "❌ Exceção interna",
            "error": type(e).__name__,
            "details": str(e)
        }

@mcp.tool
async def ap_create_bill_from_invoice(
    sequential_number: str,
    bill_payload: Dict[str, Any],
    installments_count: str = "1",
    due_dates_list: str = "",
    first_due_date: str = "",
    force_create: bool = False
) -> Dict:
    """
    [DEPRECATED] Cria título a partir de NF (use apenas se Sienge não criar automaticamente).
    
    O Sienge cria títulos automaticamente ao lançar NF. Esta tool existe apenas como fallback.
    Use 'ap_update_auto_bill_installments' em vez disso.
    
    Args:
        sequential_number: Sequential number da nota fiscal
        bill_payload: Dados do título (documentId, creditorId, companyId, etc.)
        installments_count: Número de parcelas como string (padrão: "1")
        due_dates_list: Datas separadas por vírgula "2025-11-05,2025-12-05"
        first_due_date: Data padrão se due_dates_list não fornecido "YYYY-MM-DD"
        force_create: Deve ser True para confirmar criação manual
    
    Returns:
        Dict com status e informações do título criado
    """
    if not force_create:
        return {
            "success": False,
            "message": "⚠️ DEPRECATED: O Sienge cria títulos automaticamente ao lançar NF.",
            "hint": "Use 'ap_update_auto_bill_installments' para atualizar o título criado automaticamente.",
            "note": "Se realmente precisa criar manualmente, passe force_create=True"
        }
    
    log.warning("Criação manual de título a partir de NF %s (force_create=True)", sequential_number)
    
    try:
        # Validate and convert sequential_number
        try:
            seq_num = int(sequential_number)
        except (ValueError, TypeError):
            return {
                "success": False,
                "message": f"❌ Invalid sequential_number: must be numeric, got '{sequential_number}'",
                "error": "INVALID_SEQUENTIAL_NUMBER"
            }
        
        # 1) Get invoice
        inv_res = await make_sienge_request("GET", f"/purchase-invoices/{seq_num}")
        if not inv_res.get("success"):
            return {
                "success": False,
                "message": f"❌ Invoice {seq_num} not found",
                "details": inv_res.get("message"),
                "error": inv_res.get("error")
            }
        
        invoice = inv_res.get("data") or {}
        
        # 2) Determine amount
        amount = bill_payload.get("amount")
        if amount is None:
            tot = _infer_invoice_total_ap(invoice)
            if tot is None:
                return {
                    "success": False,
                    "message": "❌ Provide bill_payload.amount or ensure invoice has total"
                }
            amount = float(tot)
        
        # 3) Create bill
        bill_data = {**bill_payload, "amount": amount}
        created_res = await make_sienge_request("POST", "/bills", json_data=bill_data)
        
        if not created_res.get("success"):
            return {
                "success": False,
                "message": "❌ Error creating bill",
                "error": created_res.get("error"),
                "details": created_res.get("message")
            }
        
        bill_info = created_res.get("data") or {}
        bill_id = bill_info.get("id") or bill_info.get("billId")
        
        if not bill_id:
            return {
                "success": False,
                "message": "❌ Bill created but no ID returned"
            }
        
        # 4) Calculate exact installments
        due_dates: List[str] = []
        if due_dates_list and due_dates_list.strip():
            due_dates = [d.strip() for d in due_dates_list.split(",") if d.strip()]
        
        try:
            n = len(due_dates) if due_dates else int(installments_count or "1")
        except (ValueError, TypeError):
            return {
                "success": False,
                "message": f"❌ Invalid installments_count: must be numeric, got '{installments_count}'",
                "error": "INVALID_INSTALLMENTS_COUNT"
            }
        
        values = _split_installments_exact(Decimal(str(amount)), n)
        
        parcels = []
        for i, v in enumerate(values, start=1):
            due = (due_dates[i-1] if due_dates and i-1 < len(due_dates) else 
                   (first_due_date.strip() if first_due_date and first_due_date.strip() else None))
            parcels.append({
                "number": i,
                "amount": float(v),
                "dueDate": due
            })
        
        # 5) Set installments
        inst_res = await make_sienge_request(
            "POST",
            f"/bills/{bill_id}/installments",
            json_data={"installments": parcels}
        )
        
        if not inst_res.get("success"):
            return {
                "success": False,
                "message": "❌ Bill created but error setting installments",
                "billId": str(bill_id),
                "error": inst_res.get("error"),
                "details": inst_res.get("message")
            }
        
        # 6) Verify installments sum
        list_res = await make_sienge_request("GET", f"/bills/{bill_id}/installments")
        
        if not list_res.get("success"):
            return {
                "success": False,
                "message": "⚠️ Bill created but could not verify installments",
                "billId": str(bill_id),
                "error": list_res.get("error")
            }
        
        data = list_res.get("data")
        items = data.get("results", []) if isinstance(data, dict) else data or []
        soma = sum(Decimal(str(p.get("amount", 0))) for p in items)
        ok = soma.quantize(Decimal("0.01")) == Decimal(str(amount)).quantize(Decimal("0.01"))
        
        return {
            "success": ok,
            "message": "✅ Bill created and installments verified" if ok else "⚠️ Bill created but sum mismatch",
            "billId": str(bill_id),
            "bill": bill_info,
            "expectedAmount": float(amount),
            "sumInstallments": float(soma),
            "invoiceSequential": str(seq_num),
            "installments": items
        }
        
    except Exception as e:
        logger.error(f"Exception in ap_create_bill_from_invoice: {e}", exc_info=True)
        return {
            "success": False,
            "message": "❌ Internal exception",
            "error": type(e).__name__,
            "details": str(e)
        }

# ============ ESTOQUE ============


@mcp.tool
async def get_sienge_stock_inventory(cost_center_id: str, resource_id: Optional[str] = None) -> Dict:

    """
    Consulta inventário de estoque por centro de custo

    Args:
        cost_center_id: ID do centro de custo (obrigatório)
        resource_id: ID do insumo específico (opcional)
    """
    if resource_id:
        endpoint = f"/stock-inventories/{cost_center_id}/items/{resource_id}"
    else:
        endpoint = f"/stock-inventories/{cost_center_id}/items"

    result = await make_sienge_request("GET", endpoint)

    if result["success"]:
        data = result["data"]
        items = data.get("results", []) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 1

        return {
            "success": True,
            "message": f"✅ Inventário do centro de custo {cost_center_id}",
            "cost_center_id": cost_center_id,
            "inventory": items,
            "count": count,
        }

    return {
        "success": False,
        "message": f"❌ Erro ao consultar estoque do centro {cost_center_id}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_stock_reservations(limit: Optional[int] = 50) -> Dict:
    """
    Lista reservas de estoque

    Args:
        limit: Máximo de registros
    """
    params = {"limit": min(limit or 50, 200)}
    result = await make_sienge_request("GET", "/stock-reservations", params=params)

    if result["success"]:
        data = result["data"]
        reservations = data.get("results", []) if isinstance(data, dict) else data

        return {
            "success": True,
            "message": f"✅ Encontradas {len(reservations)} reservas de estoque",
            "reservations": reservations,
            "count": len(reservations),
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar reservas de estoque",
        "error": result.get("error"),
        "details": result.get("message"),
    }


# ============ PROJETOS/OBRAS ============


@mcp.tool
async def get_sienge_projects(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    company_id: Optional[int] = None,
    enterprise_type: Optional[int] = None,
    receivable_register: Optional[str] = None,
    only_buildings_enabled: Optional[bool] = False,
) -> Dict:
    """
    Busca empreendimentos/obras no Sienge

    Args:
        limit: Máximo de registros (padrão: 100, máximo: 200)
        offset: Pular registros (padrão: 0)
        company_id: Código da empresa
        enterprise_type: Tipo do empreendimento (1: Obra e Centro de custo, 2: Obra, 3: Centro de custo, 4: Centro de custo associado a obra)
        receivable_register: Filtro de registro de recebíveis (B3, CERC)
        only_buildings_enabled: Retornar apenas obras habilitadas para integração orçamentária
    """
    params = {"limit": min(limit or 100, 200), "offset": offset or 0}

    if company_id:
        params["companyId"] = company_id
    if enterprise_type:
        params["type"] = enterprise_type
    if receivable_register:
        params["receivableRegister"] = receivable_register
    if only_buildings_enabled:
        params["onlyBuildingsEnabledForIntegration"] = only_buildings_enabled

    result = await make_sienge_request("GET", "/enterprises", params=params)

    if result["success"]:
        data = result["data"]
        enterprises = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}

        return {
            "success": True,
            "message": f"✅ Encontrados {len(enterprises)} empreendimentos",
            "enterprises": enterprises,
            "count": len(enterprises),
            "metadata": metadata,
            "filters": params,
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar empreendimentos",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_enterprise_by_id(enterprise_id: int) -> Dict:
    """
    Busca um empreendimento específico por ID no Sienge

    Args:
        enterprise_id: ID do empreendimento
    """
    result = await make_sienge_request("GET", f"/enterprises/{enterprise_id}")

    if result["success"]:
        return {"success": True, "message": f"✅ Empreendimento {enterprise_id} encontrado", "enterprise": result["data"]}

    return {
        "success": False,
        "message": f"❌ Erro ao buscar empreendimento {enterprise_id}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_enterprise_groupings(enterprise_id: int) -> Dict:
    """
    Busca agrupamentos de unidades de um empreendimento específico

    Args:
        enterprise_id: ID do empreendimento
    """
    result = await make_sienge_request("GET", f"/enterprises/{enterprise_id}/groupings")

    if result["success"]:
        groupings = result["data"]
        return {
            "success": True,
            "message": f"✅ Agrupamentos do empreendimento {enterprise_id} encontrados",
            "groupings": groupings,
            "count": len(groupings) if isinstance(groupings, list) else 0,
        }

    return {
        "success": False,
        "message": f"❌ Erro ao buscar agrupamentos do empreendimento {enterprise_id}",
        "error": result.get("error"),
        "details": result.get("message"),
    }


@mcp.tool
async def get_sienge_units(limit: Optional[int] = 50, offset: Optional[int] = 0) -> Dict:
    """
    Consulta unidades cadastradas no Sienge

    Args:
        limit: Máximo de registros (padrão: 50)
        offset: Pular registros (padrão: 0)
    """
    params = {"limit": min(limit or 50, 200), "offset": offset or 0}
    result = await make_sienge_request("GET", "/units", params=params)

    if result["success"]:
        data = result["data"]
        units = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(units))

        return {
            "success": True,
            "message": f"✅ Encontradas {len(units)} unidades (total: {total_count})",
            "units": units,
            "count": len(units),
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar unidades",
        "error": result.get("error"),
        "details": result.get("message"),
    }


# ============ CUSTOS ============


@mcp.tool
async def get_sienge_unit_cost_tables(
    table_code: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = "Active",
    integration_enabled: Optional[bool] = None,
) -> Dict:
    """
    Consulta tabelas de custos unitários

    Args:
        table_code: Código da tabela (opcional)
        description: Descrição da tabela (opcional)
        status: Status (Active/Inactive)
        integration_enabled: Se habilitada para integração
    """
    params = {"status": status or "Active"}

    if table_code:
        params["table_code"] = table_code
    if description:
        params["description"] = description
    if integration_enabled is not None:
        params["integration_enabled"] = integration_enabled

    result = await make_sienge_request("GET", "/unit-cost-tables", params=params)

    if result["success"]:
        data = result["data"]
        tables = data.get("results", []) if isinstance(data, dict) else data

        return {
            "success": True,
            "message": f"✅ Encontradas {len(tables)} tabelas de custos",
            "cost_tables": tables,
            "count": len(tables),
        }

    return {
        "success": False,
        "message": "❌ Erro ao buscar tabelas de custos",
        "error": result.get("error"),
        "details": result.get("message"),
    }


# ============ SEARCH UNIVERSAL (COMPATIBILIDADE CHATGPT) ============


@mcp.tool
async def search_sienge_data(
    query: str,
    entity_type: Optional[str] = None,
    limit: Optional[int] = 20,
    filters: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Busca universal no Sienge - compatível com ChatGPT/OpenAI MCP
    
    ⚠️ IMPORTANTE: Para buscas mais eficientes e com maior volume de dados, 
    use as ferramentas do Supabase:
    - search_supabase_data() para busca universal no banco
    - query_supabase_database() para consultas diretas
    
    Permite buscar em múltiplas entidades do Sienge de forma unificada.
    
    Args:
        query: Termo de busca (nome, código, descrição, etc.)
        entity_type: Tipo de entidade (customers, creditors, projects, bills, purchase_orders, etc.)
        limit: Máximo de registros (padrão: 20, máximo: 100)
        filters: Filtros específicos por tipo de entidade
    """
    search_results = []
    limit = min(limit or 20, 100)
    
    # Se entity_type específico, buscar apenas nele
    if entity_type:
        result = await _search_specific_entity(entity_type, query, limit, filters or {})
        if result["success"]:
            # Adicionar sugestão para usar Supabase se busca for específica
            if entity_type in ["customers", "creditors", "enterprises"] and len(result.get("data", [])) > 0:
                result["suggestion"] = f"💡 Para busca mais eficiente em {entity_type}, use: search_supabase_data(search_term='{query}', table_names=['{entity_type}'])"
            return result
        else:
            return {
                "success": False,
                "message": f"❌ Erro na busca em {entity_type}",
                "error": result.get("error"),
                "query": query,
                "entity_type": entity_type,
                "suggestion": f"💡 Tente usar: search_supabase_data(search_term='{query}', table_names=['{entity_type}'])"
            }
    
    # Busca universal em múltiplas entidades
    entities_to_search = [
        ("customers", "clientes"),
        ("creditors", "credores/fornecedores"), 
        ("projects", "empreendimentos/obras"),
        ("bills", "títulos a pagar"),
        ("purchase_orders", "pedidos de compra")
    ]
    
    total_found = 0
    
    for entity_key, entity_name in entities_to_search:
        try:
            entity_result = await _search_specific_entity(entity_key, query, min(5, limit), {})
            if entity_result["success"] and entity_result.get("count", 0) > 0:
                search_results.append({
                    "entity_type": entity_key,
                    "entity_name": entity_name,
                    "count": entity_result["count"],
                    "results": entity_result["data"][:5],  # Limitar a 5 por entidade na busca universal
                    "has_more": entity_result["count"] > 5
                })
                total_found += entity_result["count"]
        except Exception as e:
            # Continuar com outras entidades se uma falhar
            continue
    
    if search_results:
        return {
            "success": True,
            "message": f"✅ Busca '{query}' encontrou resultados em {len(search_results)} entidades (total: {total_found} registros)",
            "query": query,
            "total_entities": len(search_results),
            "total_records": total_found,
            "results_by_entity": search_results,
            "suggestion": "Use entity_type para buscar especificamente em uma entidade e obter mais resultados",
            "supabase_suggestion": f"💡 Para busca mais eficiente e completa, use: search_supabase_data(search_term='{query}')"
        }
    else:
        return {
            "success": False,
            "message": f"❌ Nenhum resultado encontrado para '{query}'",
            "query": query,
            "searched_entities": [name for _, name in entities_to_search],
            "suggestion": "Tente termos mais específicos ou use os tools específicos de cada entidade",
            "supabase_suggestion": f"💡 Para busca mais eficiente, use: search_supabase_data(search_term='{query}')"
        }


async def _search_specific_entity(entity_type: str, query: str, limit: int, filters: Dict) -> Dict:
    """Função auxiliar para buscar em uma entidade específica"""
    
    if entity_type == "customers":
        result = await get_sienge_customers(limit=limit, search=query)
        if result["success"]:
            return {
                "success": True,
                "data": result["customers"],
                "count": result["count"],
                "entity_type": "customers"
            }
    
    elif entity_type == "creditors":
        result = await get_sienge_creditors(limit=limit, search=query)
        if result["success"]:
            return {
                "success": True,
                "data": result["creditors"],
                "count": result["count"],
                "entity_type": "creditors"
            }
    
    elif entity_type == "projects" or entity_type == "enterprises":
        # Para projetos, usar filtros mais específicos se disponível
        company_id = filters.get("company_id")
        result = await get_sienge_projects(limit=limit, company_id=company_id)
        if result["success"]:
            # Filtrar por query se fornecida
            projects = result["enterprises"]
            if query:
                projects = [
                    p for p in projects 
                    if query.lower() in str(p.get("description", "")).lower() 
                    or query.lower() in str(p.get("name", "")).lower()
                    or query.lower() in str(p.get("code", "")).lower()
                ]
            return {
                "success": True,
                "data": projects,
                "count": len(projects),
                "entity_type": "projects"
            }
    
    elif entity_type == "bills":
        # Para títulos, usar data padrão se não especificada
        start_date = filters.get("start_date")
        end_date = filters.get("end_date") 
        result = await get_sienge_bills(
            start_date=start_date, 
            end_date=end_date, 
            limit=limit
        )
        if result["success"]:
            return {
                "success": True,
                "data": result["bills"],
                "count": result["count"],
                "entity_type": "bills"
            }
    
    elif entity_type == "purchase_orders":
        result = await get_sienge_purchase_orders(limit=limit)
        if result["success"]:
            orders = result["purchase_orders"]
            # Filtrar por query se fornecida
            if query:
                orders = [
                    o for o in orders 
                    if query.lower() in str(o.get("description", "")).lower()
                    or query.lower() in str(o.get("id", "")).lower()
                ]
            return {
                "success": True,
                "data": orders,
                "count": len(orders),
                "entity_type": "purchase_orders"
            }
    
    # Se chegou aqui, entidade não suportada ou erro
    return {
        "success": False,
        "error": f"Entidade '{entity_type}' não suportada ou erro na busca",
        "supported_entities": ["customers", "creditors", "projects", "bills", "purchase_orders"]
    }


@mcp.tool
async def list_sienge_entities() -> Dict:
    """
    Lista todas as entidades disponíveis no Sienge MCP para busca
    
    Retorna informações sobre os tipos de dados que podem ser consultados
    """
    entities = [
        {
            "type": "customers",
            "name": "Clientes",
            "description": "Clientes cadastrados no sistema",
            "search_fields": ["nome", "documento", "email"],
            "tools": ["get_sienge_customers", "search_sienge_data"]
        },
        {
            "type": "creditors", 
            "name": "Credores/Fornecedores",
            "description": "Fornecedores e credores cadastrados",
            "search_fields": ["nome", "documento"],
            "tools": ["get_sienge_creditors", "get_sienge_creditor_bank_info"]
        },
        {
            "type": "projects",
            "name": "Empreendimentos/Obras", 
            "description": "Projetos e obras cadastrados",
            "search_fields": ["código", "descrição", "nome"],
            "tools": ["get_sienge_projects", "get_sienge_enterprise_by_id"]
        },
        {
            "type": "bills",
            "name": "Títulos a Pagar",
            "description": "Contas a pagar e títulos financeiros",
            "search_fields": ["número", "credor", "valor"],
            "tools": ["get_sienge_bills"]
        },
        {
            "type": "purchase_orders",
            "name": "Pedidos de Compra",
            "description": "Pedidos de compra e solicitações",
            "search_fields": ["id", "descrição", "status"],
            "tools": ["get_sienge_purchase_orders", "get_sienge_purchase_requests"]
        },
        {
            "type": "invoices",
            "name": "Notas Fiscais",
            "description": "Notas fiscais de compra",
            "search_fields": ["número", "série", "fornecedor"],
            "tools": ["get_sienge_purchase_invoice"]
        },
        {
            "type": "stock",
            "name": "Estoque",
            "description": "Inventário e movimentações de estoque",
            "search_fields": ["centro_custo", "recurso"],
            "tools": ["get_sienge_stock_inventory", "get_sienge_stock_reservations"]
        },
        {
            "type": "financial",
            "name": "Financeiro",
            "description": "Contas a receber e movimentações financeiras",
            "search_fields": ["período", "cliente", "valor"],
            "tools": ["get_sienge_accounts_receivable"]
        }
    ]
    
    return {
        "success": True,
        "message": f"✅ {len(entities)} tipos de entidades disponíveis no Sienge",
        "entities": entities,
        "total_tools": sum(len(e["tools"]) for e in entities),
        "usage_example": {
            "search_all": "search_sienge_data('nome_cliente')",
            "search_specific": "search_sienge_data('nome_cliente', entity_type='customers')",
            "direct_access": "get_sienge_customers(search='nome_cliente')"
        }
    }


# ============ PAGINATION E NAVEGAÇÃO ============


async def _get_data_paginated_internal(
    entity_type: str,
    page: int = 1,
    page_size: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None
) -> Dict:
    """Função interna para paginação (sem decorador @mcp.tool)"""
    page_size = min(page_size, 50)
    offset = (page - 1) * page_size
    
    filters = filters or {}
    
    # Mapear para os tools existentes com offset
    if entity_type == "customers":
        search = filters.get("search")
        customer_type_id = filters.get("customer_type_id")
        result = await get_sienge_customers(
            limit=page_size,
            offset=offset, 
            search=search,
            customer_type_id=customer_type_id
        )
        
    elif entity_type == "creditors":
        search = filters.get("search")
        result = await get_sienge_creditors(
            limit=page_size,
            offset=offset,
            search=search
        )
        
    elif entity_type == "projects":
        result = await get_sienge_projects(
            limit=page_size,
            offset=offset,
            company_id=filters.get("company_id"),
            enterprise_type=filters.get("enterprise_type")
        )
        
    elif entity_type == "bills":
        result = await get_sienge_bills(
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date"),
            creditor_id=filters.get("creditor_id"),
            status=filters.get("status"),
            limit=page_size
        )
        
    else:
        return {
            "success": False,
            "message": f"❌ Tipo de entidade '{entity_type}' não suportado para paginação",
            "supported_types": ["customers", "creditors", "projects", "bills"]
        }
    
    if result["success"]:
        # Calcular informações de paginação
        total_count = result.get("total_count", result.get("count", 0))
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
        
        return {
            "success": True,
            "message": f"✅ Página {page} de {total_pages} - {entity_type}",
            "data": result.get(entity_type, result.get("data", [])),
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_records": total_count,
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "next_page": page + 1 if page < total_pages else None,
                "previous_page": page - 1 if page > 1 else None
            },
            "entity_type": entity_type,
            "filters_applied": filters
        }
    
    return result


@mcp.tool 
async def get_sienge_data_paginated(
    entity_type: str,
    page: int = 1,
    page_size: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None
) -> Dict:
    """
    Busca dados do Sienge com paginação avançada - compatível com ChatGPT
    
    Args:
        entity_type: Tipo de entidade (customers, creditors, projects, bills, etc.)
        page: Número da página (começando em 1)
        page_size: Registros por página (máximo 50)
        filters: Filtros específicos da entidade
        sort_by: Campo para ordenação (se suportado)
    """
    return await _get_data_paginated_internal(
        entity_type=entity_type,
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by
    )


async def _search_financial_data_internal(
    period_start: str,
    period_end: str, 
    search_type: str = "both",
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    customer_creditor_search: Optional[str] = None
) -> Dict:
    """Função interna para busca financeira (sem decorador @mcp.tool)"""
    
    financial_results = {
        "receivable": {"success": False, "data": [], "count": 0, "error": None},
        "payable": {"success": False, "data": [], "count": 0, "error": None}
    }
    
    # Buscar contas a receber
    if search_type in ["receivable", "both"]:
        try:
            receivable_result = await get_sienge_accounts_receivable(
                start_date=period_start,
                end_date=period_end,
                selection_type="D"  # Por vencimento
            )
            
            if receivable_result["success"]:
                receivable_data = receivable_result["income_data"]
                
                # Aplicar filtros de valor se especificados
                if amount_min is not None or amount_max is not None:
                    filtered_data = []
                    for item in receivable_data:
                        amount = float(item.get("amount", 0) or 0)
                        if amount_min is not None and amount < amount_min:
                            continue
                        if amount_max is not None and amount > amount_max:
                            continue
                        filtered_data.append(item)
                    receivable_data = filtered_data
                
                # Aplicar filtro de cliente se especificado
                if customer_creditor_search:
                    search_lower = customer_creditor_search.lower()
                    filtered_data = []
                    for item in receivable_data:
                        customer_name = str(item.get("customer_name", "")).lower()
                        if search_lower in customer_name:
                            filtered_data.append(item)
                    receivable_data = filtered_data
                
                financial_results["receivable"] = {
                    "success": True,
                    "data": receivable_data,
                    "count": len(receivable_data),
                    "error": None
                }
            else:
                financial_results["receivable"]["error"] = receivable_result.get("error")
                
        except Exception as e:
            financial_results["receivable"]["error"] = str(e)
    
    # Buscar contas a pagar  
    if search_type in ["payable", "both"]:
        try:
            payable_result = await get_sienge_bills(
                start_date=period_start,
                end_date=period_end,
                limit=100
            )
            
            if payable_result["success"]:
                payable_data = payable_result["bills"]
                
                # Aplicar filtros de valor se especificados
                if amount_min is not None or amount_max is not None:
                    filtered_data = []
                    for item in payable_data:
                        amount = float(item.get("amount", 0) or 0)
                        if amount_min is not None and amount < amount_min:
                            continue
                        if amount_max is not None and amount > amount_max:
                            continue
                        filtered_data.append(item)
                    payable_data = filtered_data
                
                # Aplicar filtro de credor se especificado
                if customer_creditor_search:
                    search_lower = customer_creditor_search.lower()
                    filtered_data = []
                    for item in payable_data:
                        creditor_name = str(item.get("creditor_name", "")).lower()
                        if search_lower in creditor_name:
                            filtered_data.append(item)
                    payable_data = filtered_data
                
                financial_results["payable"] = {
                    "success": True,
                    "data": payable_data,
                    "count": len(payable_data),
                    "error": None
                }
            else:
                financial_results["payable"]["error"] = payable_result.get("error")
                
        except Exception as e:
            financial_results["payable"]["error"] = str(e)
    
    # Compilar resultado final
    total_records = financial_results["receivable"]["count"] + financial_results["payable"]["count"]
    has_errors = bool(financial_results["receivable"]["error"] or financial_results["payable"]["error"])
    
    summary = {
        "period": f"{period_start} a {period_end}",
        "search_type": search_type,
        "total_records": total_records,
        "receivable_count": financial_results["receivable"]["count"],
        "payable_count": financial_results["payable"]["count"],
        "filters_applied": {
            "amount_range": f"{amount_min or 'sem mín'} - {amount_max or 'sem máx'}",
            "customer_creditor": customer_creditor_search or "todos"
        }
    }
    
    if total_records > 0:
        return {
            "success": True,
            "message": f"✅ Busca financeira encontrou {total_records} registros no período",
            "summary": summary,
            "receivable": financial_results["receivable"],
            "payable": financial_results["payable"],
            "has_errors": has_errors
        }
    else:
        return {
            "success": False,
            "message": f"❌ Nenhum registro financeiro encontrado no período {period_start} a {period_end}",
            "summary": summary,
            "errors": {
                "receivable": financial_results["receivable"]["error"],
                "payable": financial_results["payable"]["error"]
            }
        }


@mcp.tool
async def search_sienge_financial_data(
    period_start: str,
    period_end: str, 
    search_type: str = "both",
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    customer_creditor_search: Optional[str] = None
) -> Dict:
    """
    Busca avançada em dados financeiros do Sienge - Contas a Pagar e Receber
    
    Args:
        period_start: Data inicial do período (YYYY-MM-DD)
        period_end: Data final do período (YYYY-MM-DD)
        search_type: Tipo de busca ("receivable", "payable", "both")
        amount_min: Valor mínimo (opcional)
        amount_max: Valor máximo (opcional)
        customer_creditor_search: Buscar por nome de cliente/credor (opcional)
    """
    return await _search_financial_data_internal(
        period_start=period_start,
        period_end=period_end,
        search_type=search_type,
        amount_min=amount_min,
        amount_max=amount_max,
        customer_creditor_search=customer_creditor_search
    )


async def _get_dashboard_summary_internal() -> Dict:
    """Função interna para dashboard (sem decorador @mcp.tool)"""
    
    # Data atual e períodos
    today = datetime.now()
    current_month_start = today.replace(day=1).strftime("%Y-%m-%d")
    current_month_end = today.strftime("%Y-%m-%d")
    
    dashboard_data = {}
    errors = []
    
    # 1. Testar conexão
    try:
        connection_test = await test_sienge_connection()
        dashboard_data["connection"] = connection_test
    except Exception as e:
        errors.append(f"Teste de conexão: {str(e)}")
        dashboard_data["connection"] = {"success": False, "error": str(e)}
    
    # 2. Contar clientes (amostra)
    try:
        customers_result = await get_sienge_customers(limit=1)
        if customers_result["success"]:
            dashboard_data["customers_available"] = True
        else:
            dashboard_data["customers_available"] = False
    except Exception as e:
        errors.append(f"Clientes: {str(e)}")
        dashboard_data["customers_available"] = False
    
    # 3. Contar projetos (amostra)
    try:
        projects_result = await get_sienge_projects(limit=5)
        if projects_result["success"]:
            dashboard_data["projects"] = {
                "available": True,
                "sample_count": len(projects_result["enterprises"]),
                "total_count": projects_result.get("metadata", {}).get("count", "N/A")
            }
        else:
            dashboard_data["projects"] = {"available": False}
    except Exception as e:
        errors.append(f"Projetos: {str(e)}")
        dashboard_data["projects"] = {"available": False, "error": str(e)}
    
    # 4. Títulos a pagar do mês atual
    try:
        bills_result = await get_sienge_bills(
            start_date=current_month_start,
            end_date=current_month_end,
            limit=10
        )
        if bills_result["success"]:
            dashboard_data["monthly_bills"] = {
                "available": True,
                "count": len(bills_result["bills"]),
                "total_count": bills_result.get("total_count", len(bills_result["bills"]))
            }
        else:
            dashboard_data["monthly_bills"] = {"available": False}
    except Exception as e:
        errors.append(f"Títulos mensais: {str(e)}")
        dashboard_data["monthly_bills"] = {"available": False, "error": str(e)}
    
    # 5. Tipos de clientes
    try:
        customer_types_result = await get_sienge_customer_types()
        if customer_types_result["success"]:
            dashboard_data["customer_types"] = {
                "available": True,
                "count": len(customer_types_result["customer_types"])
            }
        else:
            dashboard_data["customer_types"] = {"available": False}
    except Exception as e:
        dashboard_data["customer_types"] = {"available": False, "error": str(e)}
    
    # Compilar resultado
    available_modules = sum(1 for key, value in dashboard_data.items() 
                          if key != "connection" and isinstance(value, dict) and value.get("available"))
    
    return {
        "success": True,
        "message": f"✅ Dashboard do Sienge - {available_modules} módulos disponíveis",
        "timestamp": today.isoformat(),
        "period_analyzed": f"{current_month_start} a {current_month_end}",
        "modules_status": dashboard_data,
        "available_modules": available_modules,
        "errors": errors if errors else None,
        "quick_actions": [
            "search_sienge_data('termo_busca') - Busca universal",
            "list_sienge_entities() - Listar tipos de dados", 
            "get_sienge_customers(search='nome') - Buscar clientes",
            "get_sienge_projects() - Listar projetos/obras",
            "search_sienge_financial_data('2024-01-01', '2024-12-31') - Dados financeiros"
        ]
    }


@mcp.tool
async def get_sienge_dashboard_summary() -> Dict:
    """
    Obtém um resumo tipo dashboard com informações gerais do Sienge
    Útil para visão geral rápida do sistema
    """
    return await _get_dashboard_summary_internal()


# ============ SUPABASE QUERY TOOLS ============


@mcp.tool
async def query_supabase_database(
    table_name: str,
    columns: Optional[str] = "*",
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = 100,
    order_by: Optional[str] = None,
    search_term: Optional[str] = None,
    search_columns: Optional[List[str]] = None
) -> Dict:
    """
    Executa queries no banco de dados Supabase para buscar dados das tabelas do Sienge
    
    Args:
        table_name: Nome da tabela (customers, creditors, enterprises, purchase_invoices, stock_inventories, accounts_receivable, installment_payments, income_installments)
        columns: Colunas a retornar (padrão: "*")
        filters: Filtros WHERE como dict {"campo": "valor"}
        limit: Limite de registros (padrão: 100, máximo: 1000)
        order_by: Campo para ordenação (ex: "name", "created_at desc")
        search_term: Termo de busca para busca textual
        search_columns: Colunas onde fazer busca textual (se não especificado, usa campos de texto principais)
    
    Nota: As queries são executadas no schema 'sienge_data' (fixo)
    """
    # Validação de parâmetros
    if not table_name or not isinstance(table_name, str):
        return {
            "success": False,
            "message": "❌ Nome da tabela é obrigatório e deve ser uma string",
            "error": "INVALID_TABLE_NAME"
        }
    
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        return {
            "success": False,
            "message": "❌ Limite deve ser um número inteiro positivo",
            "error": "INVALID_LIMIT"
        }
    
    if limit and limit > 1000:
        limit = 1000  # Aplicar limite máximo
    
    return await _query_supabase_internal(
        table_name=table_name,
        columns=columns,
        filters=filters,
        limit=limit,
        order_by=order_by,
        search_term=search_term,
        search_columns=search_columns
    )


@mcp.tool
async def get_supabase_table_info(table_name: Optional[str] = None) -> Dict:
    """
    Obtém informações sobre as tabelas disponíveis no Supabase ou detalhes de uma tabela específica
    
    Args:
        table_name: Nome da tabela para obter detalhes (opcional)
    
    Nota: As tabelas estão no schema 'sienge_data' (fixo)
    """
    if not SUPABASE_AVAILABLE:
        return {
            "success": False,
            "message": "❌ Cliente Supabase não disponível",
            "error": "SUPABASE_NOT_AVAILABLE"
        }
    
    client = _get_supabase_client()
    if not client:
        return {
            "success": False,
            "message": "❌ Cliente Supabase não configurado",
            "error": "SUPABASE_NOT_CONFIGURED"
        }
    
    # Informações das tabelas disponíveis
    tables_info = {
        "customers": {
            "name": "Clientes",
            "description": "Clientes cadastrados no Sienge",
            "columns": ["id", "name", "document", "email", "phone", "customer_type_id", "raw", "updated_at", "last_synced_at", "created_at"],
            "search_fields": ["name", "document", "email"],
            "indexes": ["document", "name (trigram)", "updated_at"]
        },
        "creditors": {
            "name": "Credores/Fornecedores", 
            "description": "Fornecedores e credores cadastrados",
            "columns": ["id", "name", "document", "bank_info", "raw", "updated_at", "last_synced_at", "created_at"],
            "search_fields": ["name", "document"],
            "indexes": ["document", "name (trigram)", "updated_at"]
        },
        "enterprises": {
            "name": "Empreendimentos/Obras",
            "description": "Projetos e obras cadastrados",
            "columns": ["id", "code", "name", "description", "company_id", "type", "metadata", "raw", "updated_at", "last_synced_at", "created_at"],
            "search_fields": ["name", "description", "code"],
            "indexes": ["name (trigram)", "company_id", "updated_at"]
        },
        "purchase_invoices": {
            "name": "Notas Fiscais de Compra",
            "description": "Notas fiscais de compra",
            "columns": ["id", "sequential_number", "supplier_id", "company_id", "movement_date", "issue_date", "series", "notes", "raw", "updated_at", "last_synced_at", "created_at"],
            "search_fields": ["sequential_number", "notes"],
            "indexes": ["supplier_id", "sequential_number", "updated_at"]
        },
        "installment_payments": {
            "name": "Pagamentos de Parcelas",
            "description": "Pagamentos efetuados para parcelas",
            "columns": [
                "payment_uid", "installment_uid", "operation_type_id", "operation_type_name",
                "gross_amount", "monetary_correction_amount", "interest_amount", "fine_amount",
                "discount_amount", "tax_amount", "net_amount", "calculation_date", "payment_date",
                "sequential_number", "corrected_net_amount", "payment_authentication"
            ],
            "search_fields": ["installment_uid", "payment_uid"],
            "indexes": ["payment_date", "installment_uid", "payment_uid"],
            "amount_columns": ["gross_amount", "net_amount", "corrected_net_amount"]
        },
        "income_installments": {
            "name": "Parcelas de Receita",
            "description": "Parcelas de contas a receber (busca apenas por valores numéricos)",
            "columns": [
                "installment_uid", "bill_id", "installment_id", "company_id", "company_name",
                "business_area_id", "business_area_name", "project_id", "project_name",
                "group_company_id", "group_company_name", "holding_id", "holding_name",
                "subsidiary_id", "subsidiary_name", "business_type_id", "business_type_name",
                "client_id", "client_name", "document_identification_id", "document_identification_name",
                "document_number", "document_forecast", "origin_id", "original_amount",
                "discount_amount", "tax_amount", "indexer_id", "indexer_name", "due_date",
                "issue_date", "bill_date", "installment_base_date", "balance_amount",
                "corrected_balance_amount", "periodicity_type", "embedded_interest_amount",
                "interest_type", "interest_rate", "correction_type", "interest_base_date",
                "defaulter_situation", "sub_judicie", "main_unit", "installment_number",
                "payment_term_id", "payment_term_description", "bearer_id"
            ],
            "search_fields": ["bill_id (numérico)", "client_id (numérico)", "installment_uid"],
            "indexes": ["due_date", "bill_id", "client_id", "installment_uid"],
            "search_note": "Para buscar nesta tabela, use valores numéricos (ex: '123' para bill_id)",
            "amount_columns": ["original_amount", "balance_amount", "corrected_balance_amount"]
        },
        "stock_inventories": {
            "name": "Inventário de Estoque",
            "description": "Inventário e movimentações de estoque",
            "columns": ["id", "cost_center_id", "resource_id", "inventory", "raw", "updated_at", "last_synced_at", "created_at"],
            "search_fields": ["cost_center_id", "resource_id"],
            "indexes": ["cost_center_id", "resource_id"]
        },
        "accounts_receivable": {
            "name": "Contas a Receber",
            "description": "Contas a receber e movimentações financeiras",
            "columns": ["id", "bill_id", "customer_id", "amount", "due_date", "payment_date", "raw", "updated_at", "last_synced_at", "created_at"],
            "search_fields": ["bill_id", "customer_id"],
            "indexes": ["customer_id", "due_date", "updated_at"]
        },
        "sync_meta": {
            "name": "Metadados de Sincronização",
            "description": "Controle de sincronização entre Sienge e Supabase",
            "columns": ["id", "entity_name", "last_synced_at", "last_record_count", "notes", "created_at"],
            "search_fields": ["entity_name"],
            "indexes": ["entity_name"]
        }
    }
    
    if table_name:
        if table_name in tables_info:
            return {
                "success": True,
                "message": f"✅ Informações da tabela '{table_name}'",
                "table_info": tables_info[table_name],
                "table_name": table_name
            }
        else:
            return {
                "success": False,
                "message": f"❌ Tabela '{table_name}' não encontrada",
                "error": "TABLE_NOT_FOUND",
                "available_tables": list(tables_info.keys())
            }
    else:
        return {
            "success": True,
            "message": f"✅ {len(tables_info)} tabelas disponíveis no Supabase",
            "schema": SUPABASE_SCHEMA,
            "tables": tables_info,
            "usage_examples": {
                "query_customers": "query_supabase_database('customers', search_term='João')",
                "query_bills_by_date": "query_supabase_database('bills', filters={'due_date': '2024-01-01'})",
                "query_enterprises": "query_supabase_database('enterprises', columns='id,name,description', limit=50)"
            }
        }


@mcp.tool
async def search_supabase_data(
    search_term: str,
    table_names: Optional[List[str]] = None,
    limit_per_table: Optional[int] = 20
) -> Dict:
    """
    🚀 Busca universal em múltiplas tabelas do Supabase - MAIS EFICIENTE
    
    ⭐ RECOMENDADO para buscas com volume de dados ou quando search_sienge_data não retorna resultados satisfatórios.
    
    Esta ferramenta é mais eficiente que search_sienge_data() porque:
    - Acessa diretamente o banco de dados
    - Busca em múltiplas tabelas simultaneamente
    - Suporte a busca textual e numérica
    - Melhor performance para grandes volumes
    
    Args:
        search_term: Termo de busca
        table_names: Lista de tabelas para buscar (se não especificado, busca em todas)
        limit_per_table: Limite de resultados por tabela (padrão: 20)
    """
    # Validação de parâmetros
    if not search_term or not isinstance(search_term, str):
        return {
            "success": False,
            "message": "❌ Termo de busca é obrigatório e deve ser uma string",
            "error": "INVALID_SEARCH_TERM"
        }
    
    if limit_per_table is not None and (not isinstance(limit_per_table, int) or limit_per_table <= 0):
        return {
            "success": False,
            "message": "❌ Limite por tabela deve ser um número inteiro positivo",
            "error": "INVALID_LIMIT"
        }
    
    # Validar e processar table_names
    if table_names is not None:
        if not isinstance(table_names, list):
            return {
                "success": False,
                "message": "❌ table_names deve ser uma lista de strings",
                "error": "INVALID_TABLE_NAMES"
            }
        # Filtrar apenas tabelas válidas
        valid_tables = ["customers", "creditors", "enterprises", "purchase_invoices", 
                       "stock_inventories", "accounts_receivable", "sync_meta",
                       "installment_payments", "income_installments"]
        table_names = [t for t in table_names if t in valid_tables]
        if not table_names:
            return {
                "success": False,
                "message": "❌ Nenhuma tabela válida especificada",
                "error": "NO_VALID_TABLES",
                "valid_tables": valid_tables
            }
    else:
        table_names = ["customers", "creditors", "enterprises", "installment_payments", "income_installments"]
    
    results = {}
    total_found = 0
    
    for table_name in table_names:
        try:
            # Chamar a função interna diretamente
            result = await _query_supabase_internal(
                table_name=table_name,
                search_term=search_term,
                limit=limit_per_table or 20
            )
            
            if result["success"]:
                results[table_name] = {
                    "count": result["count"],
                    "data": result["data"][:5] if result["count"] > 5 else result["data"],  # Limitar preview
                    "has_more": result["count"] > 5
                }
                total_found += result["count"]
            else:
                results[table_name] = {
                    "error": result.get("error"),
                    "count": 0
                }
                
        except Exception as e:
            results[table_name] = {
                "error": str(e),
                "count": 0
            }
    
    if total_found > 0:
        return {
            "success": True,
            "message": f"✅ Busca '{search_term}' encontrou {total_found} registros em {len([t for t in results.values() if t.get('count', 0) > 0])} tabelas",
            "search_term": search_term,
            "total_found": total_found,
            "results_by_table": results,
            "suggestion": "Use query_supabase_database() para buscar especificamente em uma tabela e obter mais resultados"
        }
    else:
        return {
            "success": False,
            "message": f"❌ Nenhum resultado encontrado para '{search_term}'",
            "search_term": search_term,
            "searched_tables": table_names,
            "results_by_table": results
        }


# ============ UTILITÁRIOS ============


@mcp.tool
def add(a: int, b: int) -> int:
    """Soma dois números (função de teste)"""
    return a + b


def _get_auth_info_internal() -> Dict:
    """Função interna para verificar configuração de autenticação"""
    if SIENGE_API_KEY and SIENGE_API_KEY != "sua_api_key_aqui":
        return {"auth_method": "Bearer Token", "configured": True, "base_url": SIENGE_BASE_URL, "api_key_configured": True}
    elif SIENGE_USERNAME and SIENGE_PASSWORD:
        return {
            "auth_method": "Basic Auth",
            "configured": True,
            "base_url": SIENGE_BASE_URL,
            "subdomain": SIENGE_SUBDOMAIN,
            "username": SIENGE_USERNAME,
        }
    else:
        return {
            "auth_method": "None",
            "configured": False,
            "message": "Configure SIENGE_API_KEY ou SIENGE_USERNAME/PASSWORD no .env",
        }


def _get_supabase_client() -> Optional[Client]:
    """Função interna para obter cliente do Supabase"""
    if not SUPABASE_AVAILABLE:
        return None
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return None
    try:
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        return client
    except Exception as e:
        logger.warning(f"Erro ao criar cliente Supabase: {e}")
        return None


async def _query_supabase_internal(
    table_name: str,
    columns: Optional[str] = "*",
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = 100,
    order_by: Optional[str] = None,
    search_term: Optional[str] = None,
    search_columns: Optional[List[str]] = None
) -> Dict:
    """Função interna para query no Supabase (sem decorador @mcp.tool)"""
    
    if not SUPABASE_AVAILABLE:
        return {
            "success": False,
            "message": "❌ Cliente Supabase não disponível. Instale: pip install supabase",
            "error": "SUPABASE_NOT_AVAILABLE"
        }
    
    client = _get_supabase_client()
    if not client:
        return {
            "success": False,
            "message": "❌ Cliente Supabase não configurado. Configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY",
            "error": "SUPABASE_NOT_CONFIGURED"
        }
    
    # Validar tabela
    valid_tables = [
        "customers", "creditors", "enterprises", "purchase_invoices", 
        "stock_inventories", "accounts_receivable", "sync_meta",
        "installment_payments", "income_installments"
    ]
    
    if table_name not in valid_tables:
        return {
            "success": False,
            "message": f"❌ Tabela '{table_name}' não é válida",
            "error": "INVALID_TABLE",
            "valid_tables": valid_tables
        }
    
    try:
        # Construir query sempre usando schema sienge_data
        schema_client = client.schema(SUPABASE_SCHEMA)
        query = schema_client.table(table_name).select(columns)
        
        # Aplicar filtros
        if filters:
            for field, value in filters.items():
                if isinstance(value, str) and "%" in value:
                    # Busca com LIKE
                    query = query.like(field, value)
                elif isinstance(value, list):
                    # Busca com IN
                    query = query.in_(field, value)
                else:
                    # Busca exata
                    query = query.eq(field, value)
        
        # Aplicar busca textual se especificada
        if search_term and search_columns:
            # Para busca textual, usar OR entre as colunas
            search_conditions = []
            for col in search_columns:
                search_conditions.append(f"{col}.ilike.%{search_term}%")
            if search_conditions:
                query = query.or_(",".join(search_conditions))
        elif search_term:
            # Busca padrão baseada na tabela
            default_search_columns = {
                "customers": ["name", "document", "email"],
                "creditors": ["name", "document"],
                "enterprises": ["name", "description", "code"],
                "purchase_invoices": ["sequential_number", "notes"],
                "stock_inventories": ["cost_center_id", "resource_id"],
                "accounts_receivable": ["bill_id", "customer_id"],
                "installment_payments": ["installment_uid", "payment_uid"],
                "income_installments": []  # Campos numéricos - sem busca textual
            }
            
            search_cols = default_search_columns.get(table_name, ["name"])
            
            # Se não há colunas de texto para buscar, tentar busca numérica
            if not search_cols:
                # Para tabelas com campos numéricos, tentar converter search_term para número
                try:
                    search_num = int(search_term)
                    # Buscar em campos numéricos comuns
                    numeric_conditions = []
                    if table_name == "income_installments":
                        numeric_conditions = [
                            f"bill_id.eq.{search_num}",
                            f"client_id.eq.{search_num}",
                            f"original_amount.eq.{search_num}",
                            f"balance_amount.eq.{search_num}",
                            f"corrected_balance_amount.eq.{search_num}"
                        ]
                    elif table_name == "installment_payments":
                        numeric_conditions = [
                            f"installment_uid.eq.{search_num}",
                            f"payment_uid.eq.{search_num}",
                            f"gross_amount.eq.{search_num}",
                            f"net_amount.eq.{search_num}",
                            f"corrected_net_amount.eq.{search_num}"
                        ]
                    
                    if numeric_conditions:
                        query = query.or_(",".join(numeric_conditions))
                except ValueError:
                    # Se não é número, não fazer busca
                    pass
            else:
                # Busca textual normal
                search_conditions = [f"{col}.ilike.%{search_term}%" for col in search_cols]
                if search_conditions:
                    query = query.or_(",".join(search_conditions))
        
        # Aplicar ordenação
        if order_by:
            if " desc" in order_by.lower():
                field = order_by.replace(" desc", "").replace(" DESC", "")
                query = query.order(field, desc=True)
            else:
                field = order_by.replace(" asc", "").replace(" ASC", "")
                query = query.order(field)
        
        # Aplicar limite
        limit = min(limit or 100, 1000)
        query = query.limit(limit)
        
        # Executar query
        result = query.execute()
        
        if hasattr(result, 'data'):
            data = result.data
        else:
            data = result
        
        return {
            "success": True,
            "message": f"✅ Query executada com sucesso na tabela '{table_name}'",
            "table_name": table_name,
            "data": data,
            "count": len(data) if isinstance(data, list) else 1,
            "query_info": {
                "columns": columns,
                "filters": filters,
                "limit": limit,
                "order_by": order_by,
                "search_term": search_term,
                "search_columns": search_columns
            }
        }
        
    except Exception as e:
        logger.error(f"Erro na query Supabase: {e}")
        return {
            "success": False,
            "message": f"❌ Erro ao executar query na tabela '{table_name}'",
            "error": str(e),
            "table_name": table_name
        }


# ============ SIMPLE ASYNC CACHE (in-memory, process-local) ============
# Lightweight helper to improve hit-rate on repeated test queries
_SIMPLE_CACHE: Dict[str, Dict[str, Any]] = {}

def _simple_cache_set(key: str, value: Dict[str, Any], ttl: int = 60) -> None:
    expire_at = int(time.time()) + int(ttl)
    _SIMPLE_CACHE[key] = {"value": value, "expire_at": expire_at}

def _simple_cache_get(key: str) -> Optional[Dict[str, Any]]:
    item = _SIMPLE_CACHE.get(key)
    if not item:
        return None
    if int(time.time()) > item.get("expire_at", 0):
        try:
            del _SIMPLE_CACHE[key]
        except KeyError:
            pass
        return None
    return item.get("value")


async def _fetch_all_paginated(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    page_size: int = 200,
    max_records: Optional[int] = None,
    results_key: str = "results",
    use_bulk: bool = False,
) -> List[Dict[str, Any]]:
    """
    Helper to fetch all pages from a paginated endpoint that uses limit/offset.

    - endpoint: API endpoint path (starting with /)
    - params: base params (function will add/override limit and offset)
    - page_size: maximum per request (API typically allows up to 200)
    - max_records: optional soft limit to stop early
    - results_key: key in the JSON response where the array is located (default: 'results')
    - use_bulk: if True expect bulk-data style response where items may be under 'data'
    """
    params = dict(params or {})
    all_items: List[Dict[str, Any]] = []
    offset = int(params.get("offset", 0) or 0)
    page_size = min(int(page_size), 200)

    while True:
        params["limit"] = page_size
        params["offset"] = offset

        # choose the correct requester
        requester = make_sienge_bulk_request if use_bulk else make_sienge_request
        result = await requester("GET", endpoint, params=params)

        if not result.get("success"):
            # stop and raise or return whatever accumulated
            return {"success": False, "error": result.get("error"), "message": result.get("message")}

        data = result.get("data")

        if use_bulk:
            items = data.get("data", []) if isinstance(data, dict) else data
        else:
            items = data.get(results_key, []) if isinstance(data, dict) else data

        if not isinstance(items, list):
            # if API returned single object or unexpected structure, append and stop
            all_items.append(items)
            break

        all_items.extend(items)

        # enforce max_records if provided
        if max_records and len(all_items) >= int(max_records):
            return all_items[: int(max_records)]

        # if fewer items returned than page_size, we've reached the end
        if len(items) < page_size:
            break

        offset += len(items) if len(items) > 0 else page_size

    return all_items


@mcp.tool
def get_auth_info() -> Dict:
    """Retorna informações sobre a configuração de autenticação"""
    return _get_auth_info_internal()


def main():
    """Entry point for the Sienge MCP Server"""
    print("* Iniciando Sienge MCP Server (FastMCP)...")

    # Mostrar info de configuração
    auth_info = _get_auth_info_internal()
    print(f"* Autenticacao: {auth_info['auth_method']}")
    print(f"* Configurado: {auth_info['configured']}")

    if not auth_info["configured"]:
        print("* ERRO: Autenticacao nao configurada!")
        print("Configure as variáveis de ambiente:")
        print("- SIENGE_API_KEY (Bearer Token) OU")
        print("- SIENGE_USERNAME + SIENGE_PASSWORD + SIENGE_SUBDOMAIN (Basic Auth)")
        print("- SIENGE_BASE_URL (padrão: https://api.sienge.com.br)")
        print("")
        print("Exemplo no Windows PowerShell:")
        print('$env:SIENGE_USERNAME="seu_usuario"')
        print('$env:SIENGE_PASSWORD="sua_senha"')
        print('$env:SIENGE_SUBDOMAIN="sua_empresa"')
        print("")
        print("Exemplo no Linux/Mac:")
        print('export SIENGE_USERNAME="seu_usuario"')
        print('export SIENGE_PASSWORD="sua_senha"')
        print('export SIENGE_SUBDOMAIN="sua_empresa"')
    else:
        print("* MCP pronto para uso!")

    mcp.run()


if __name__ == "__main__":
    main()