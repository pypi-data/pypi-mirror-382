"""MCP server exposing the Buscador de CNPJ API via FastMCP."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from collections.abc import Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Optional

import aiohttp
from aiohttp import ClientError
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from pydantic import BaseModel, ConfigDict, Field, field_validator

load_dotenv()

LOGGER = logging.getLogger(__name__)
if not LOGGER.handlers:
    logging.basicConfig(level=logging.INFO)

API_KEY_ENV_VARS = (
    "CNPJ_API_KEY",
    "CNPJ_API_TOKEN",
    "BUSCADOR_CNPJ_API_KEY",
    "API_KEY",
)
BASE_URL = "https://api.buscadordecnpj.com"
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=30)
DEFAULT_HEADERS = {"Accept": "application/json"}
META_HEADERS = (
    "X-Credits-Charged",
    "X-Credits-Remaining",
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "X-RateLimit-Reset",
    "X-Cache",
)


class MissingAPIKeyError(RuntimeError):
    """Raised when a premium endpoint is requested without an API key."""

    def __init__(self) -> None:
        message = (
            "Uma chave de API é obrigatória para este endpoint premium. "
            "Configure uma das variáveis: "
            f"{', '.join(API_KEY_ENV_VARS)}. "
            "As chaves podem ser obtidas em https://buscadordecnpj.com."
        )
        super().__init__(message)


class APIError(RuntimeError):
    """Wraps HTTP errors returned by the Buscador de CNPJ API."""

    def __init__(self, status_code: int, payload: Any) -> None:
        message = "Erro na API do Buscador de CNPJ"
        details = payload if isinstance(payload, (str, bytes)) else json.dumps(payload, ensure_ascii=False)
        super().__init__(f"{message} (status {status_code}): {details}")
        self.status_code = status_code
        self.payload = payload


class NetworkError(RuntimeError):
    """Raised when a network-level error occurs while calling the API."""


def find_api_key() -> Optional[str]:
    """Return the first configured API key, if any."""

    for env_var in API_KEY_ENV_VARS:
        value = os.getenv(env_var)
        if value:
            return value.strip()
    return None


def normalize_cnpj(value: str) -> str:
    """Return only digits from a CNPJ and ensure it contains 14 characters."""

    digits = re.sub(r"\D", "", value)
    if len(digits) != 14:
        raise ValueError(f"CNPJ deve conter 14 dígitos. Recebido '{value}'.")
    return digits


class QueryModel(BaseModel):
    """Base model enabling passthrough of arbitrary filters for search endpoints."""

    model_config = ConfigDict(extra="allow")

    def to_params(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in self.model_dump(exclude_none=True).items()
        }


class CNPJLookupInput(BaseModel):
    """Arguments for CNPJ lookup endpoints."""

    cnpj: str = Field(..., description="CNPJ da empresa (aceita máscara ou apenas números)")

    @field_validator("cnpj", mode="before")
    @classmethod
    def validate_cnpj(cls, value: str) -> str:
        return normalize_cnpj(value)


class CNPJBulkLookupInput(BaseModel):
    """Arguments for bulk CNPJ lookups."""

    cnpjs: Sequence[str] = Field(..., min_length=1, description="Lista de CNPJs (máscara opcional)")
    uf: Optional[str] = Field(
        default=None,
        description="UF opcional para segmentar a busca (use mesma UF da busca prévia)",
    )
    situacao_cadastral: Optional[int] = Field(
        default=None,
        ge=0,
        description="Código da situação cadastral (ex: 2 = ATIVA)",
    )

    @field_validator("cnpjs", mode="before")
    @classmethod
    def validate_cnpjs(cls, values: Sequence[str]) -> list[str]:
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            raise TypeError("'cnpjs' deve ser uma sequência de strings")
        normalized = [normalize_cnpj(item) for item in values]
        if len(normalized) > 500:
            raise ValueError("Máximo de 500 CNPJs por requisição.")
        return normalized

    @field_validator("uf", mode="before")
    @classmethod
    def normalize_uf(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().upper()
        if len(value) != 2:
            raise ValueError("UF deve ter 2 caracteres.")
        return value


class SearchInput(QueryModel):
    """Arguments for `/search` queries."""

    term: Optional[str] = Field(
        default=None,
        description="Termo textual. Aceita curingas como *padaria*",
    )
    pagina: int = Field(default=1, ge=1, description="Página de resultados (default 1)")
    limite: Optional[int] = Field(
        default=None,
        ge=1,
        le=10000,
        description="Resultados por página (1-10000)",
    )
    ordenarPor: Optional[str] = Field(default=None, description="Campo para ordenação")
    ordenacaoDesc: Optional[bool] = Field(default=None, description="True para ordem descendente")


class SearchCsvInput(SearchInput):
    """Arguments for `/search/csv` queries."""

    pagina_inicio: Optional[int] = Field(default=1, ge=1, description="Página inicial para exportação")
    pagina_fim: Optional[int] = Field(default=1, ge=1, description="Página final para exportação")


class BuscadorCNPJClient:
    """HTTP client wrapping the Buscador de CNPJ API."""

    def __init__(self, base_url: str = BASE_URL, *, api_key: Optional[str] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or find_api_key()
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT, headers=DEFAULT_HEADERS)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def lookup_public(self, cnpj: str) -> dict[str, Any]:
        path = f"/cnpj/public/{normalize_cnpj(cnpj)}"
        return await self._request("GET", path)

    async def lookup(self, cnpj: str) -> dict[str, Any]:
        path = f"/cnpj/{normalize_cnpj(cnpj)}"
        return await self._request("GET", path, require_api_key=True)

    async def lookup_bulk(
        self,
        cnpjs: Sequence[str],
        *,
        uf: Optional[str] = None,
        situacao_cadastral: Optional[int] = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "cnpjs": [normalize_cnpj(item) for item in cnpjs],
        }
        if uf:
            payload["uf"] = uf
        if situacao_cadastral is not None:
            payload["situacao_cadastral"] = situacao_cadastral
        return await self._request("POST", "/cnpj/list", json_body=payload, require_api_key=True)

    async def search(self, params: Mapping[str, Any]) -> dict[str, Any]:
        return await self._request("GET", "/search/", params=params, require_api_key=True)

    async def search_estimate(self, params: Mapping[str, Any]) -> dict[str, Any]:
        return await self._request("GET", "/search/estimate", params=params, require_api_key=True)

    async def search_csv(self, params: Mapping[str, Any]) -> dict[str, Any]:
        return await self._request("GET", "/search/csv", params=params, require_api_key=True)

    async def search_csv_estimate(self, params: Mapping[str, Any]) -> dict[str, Any]:
        return await self._request("GET", "/search/csv/estimate", params=params, require_api_key=True)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
        require_api_key: bool = False,
    ) -> dict[str, Any]:
        if require_api_key and not self.api_key:
            raise MissingAPIKeyError()

        await self.start()
        assert self._session is not None

        url = f"{self.base_url}{path}"
        query = self._prepare_params(params)

        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        try:
            async with self._session.request(
                method,
                url,
                params=query,
                json=json_body,
                headers=headers,
            ) as response:
                parsed = await self._parse_response(response)
                if response.status >= 400:
                    raise APIError(response.status, parsed)
                meta = self._extract_meta(response)
                return {"data": parsed, "meta": meta}
        except ClientError as exc:
            raise NetworkError(f"Falha ao acessar {url}: {exc}") from exc

    def _prepare_params(self, params: Optional[Mapping[str, Any]]) -> Optional[dict[str, Any]]:
        if not params:
            return None
        prepared: dict[str, Any] = {}
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, bool):
                prepared[key] = "true" if value else "false"
            else:
                prepared[key] = value
        return prepared

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Any:
        content_type = response.headers.get("Content-Type", "").lower()
        text = await response.text()
        if "application/json" in content_type:
            return json.loads(text) if text else {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text or None

    def _extract_meta(self, response: aiohttp.ClientResponse) -> dict[str, Any]:
        meta: dict[str, Any] = {"status_code": response.status}
        for header in META_HEADERS:
            if header in response.headers:
                meta_key = header.lower().replace("-", "_")
                meta[meta_key] = response.headers[header]
        return meta


@dataclass
class AppContext:
    """Holds shared dependencies for MCP tools during a session."""

    client: BuscadorCNPJClient


@asynccontextmanager
async def lifespan(_: FastMCP):
    client = BuscadorCNPJClient()
    await client.start()
    try:
        yield AppContext(client=client)
    finally:
        await client.close()


mcp = FastMCP(
    name="Buscador de CNPJ",
    instructions=(
        "Ferramentas para consultar dados de empresas brasileiras através do "
        "https://buscadordecnpj.com. Use 'cnpj_public_lookup' para dados "
        "gratuitos e as ferramentas premium quando houver chave de API configurada."
    ),
    lifespan=lifespan,
)


ToolContext = Context[ServerSession, AppContext]


def _client_from_ctx(ctx: ToolContext) -> BuscadorCNPJClient:
    return ctx.request_context.lifespan_context.client


@mcp.resource("buscadordecnpj://status")
def get_status() -> dict[str, Any]:
    """Return runtime status information for the server."""

    api_key = find_api_key()
    return {
        "base_url": BASE_URL,
        "api_key_present": bool(api_key),
        "api_key_preview": f"***{api_key[-4:]}" if api_key else None,
        "api_key_env_candidates": API_KEY_ENV_VARS,
    }


@mcp.resource("buscadordecnpj://docs/endpoints")
def get_endpoint_overview() -> dict[str, Any]:
    """Summaries of the main Buscador de CNPJ endpoints served by this MCP."""

    return {
        "cnpj_public_lookup": {
            "method": "GET",
            "path": "/cnpj/public/{cnpj}",
            "authentication": "optional",
            "credits": "0",
            "description": (
                "Retorna dados públicos básicos (sem telefone/email) para um CNPJ. "
                "Ideal quando não há chave de API ou para consultas rápidas."
            ),
        },
        "cnpj_lookup": {
            "method": "GET",
            "path": "/cnpj/{cnpj}",
            "authentication": "x-api-key",
            "credits": "1 por CNPJ encontrado, grátis quando em cache",
            "description": (
                "Entrega o dossiê completo de um CNPJ, incluindo dados sensíveis "
                "quando autorizado. Útil para análises detalhadas."
            ),
        },
        "cnpj_bulk_lookup": {
            "method": "POST",
            "path": "/cnpj/list",
            "authentication": "x-api-key",
            "credits": "1 a cada 20 CNPJs enviados",
            "description": (
                "Consulta em lote para enriquecer listas. Respeite os filtros de UF e "
                "situação cadastral usados em buscas anteriores para consistência."
            ),
        },
        "cnpj_search": {
            "method": "GET",
            "path": "/search/",
            "authentication": "x-api-key",
            "credits": "2 por requisição",
            "description": (
                "Busca avançada via Manticore com dezenas de filtros textuais, "
                "numéricos e de data. Aceita curingas com *."
            ),
        },
        "cnpj_search_csv": {
            "method": "GET",
            "path": "/search/csv",
            "authentication": "x-api-key",
            "credits": "2 por página (primeira gratuita)",
            "description": (
                "Exporta resultados da busca avançada em CSV completo com todos os campos."
            ),
        },
        "estimates": {
            "search_estimate": {
                "method": "GET",
                "path": "/search/estimate",
                "credits": "0",
                "description": "Retorna contagem estimada de resultados para ajustar filtros antes da busca.",
            },
            "search_csv_estimate": {
                "method": "GET",
                "path": "/search/csv/estimate",
                "credits": "0",
                "description": (
                    "Calcula custo esperado de créditos para exportações CSV com base nas páginas solicitadas."
                ),
            },
        },
    }


@mcp.resource("buscadordecnpj://docs/credits")
def get_credit_policy() -> str:
    """Explain credit consumption rules for the main endpoints."""

    return dedent(
        """
        Política de créditos do Buscador de CNPJ:

        • cnpj_public_lookup: gratuito (dados básicos)
        • cnpj_lookup: 1 crédito por CNPJ retornado (sem custo quando o resultado vem do cache)
        • cnpj_bulk_lookup: 1 crédito a cada bloco de 20 CNPJs enviados (independente do resultado)
        • cnpj_search: 2 créditos por requisição
        • cnpj_search_csv: 2 créditos por página exportada (a primeira página é gratuita)
        • search_estimate e search_csv_estimate: gratuitos, úteis para planejar custos

        Dicas:
        - Configure a chave em uma das variáveis aceitas (CNPJ_API_KEY, CNPJ_API_TOKEN, BUSCADOR_CNPJ_API_KEY ou API_KEY).
        - Use os endpoints de estimativa antes de exportar CSVs grandes para evitar gastos inesperados.
        - Reaproveite filtros de UF e situação cadastral entre /search e /cnpj/list para evitar "not_found" falsos.
        """
    ).strip()


@mcp.tool()
async def cnpj_public_lookup(args: CNPJLookupInput, ctx: ToolContext) -> dict[str, Any]:
    """Consulta pública de CNPJ (dados básicos sem necessidade de API key)."""

    client = _client_from_ctx(ctx)
    return await client.lookup_public(args.cnpj)


@mcp.tool()
async def cnpj_lookup(args: CNPJLookupInput, ctx: ToolContext) -> dict[str, Any]:
    """Consulta detalhada de CNPJ (requer API key)."""

    client = _client_from_ctx(ctx)
    return await client.lookup(args.cnpj)


@mcp.tool()
async def cnpj_bulk_lookup(args: CNPJBulkLookupInput, ctx: ToolContext) -> dict[str, Any]:
    """Consulta múltiplos CNPJs em uma única requisição (requer API key)."""

    client = _client_from_ctx(ctx)
    return await client.lookup_bulk(args.cnpjs, uf=args.uf, situacao_cadastral=args.situacao_cadastral)


@mcp.tool()
async def cnpj_search(args: SearchInput, ctx: ToolContext) -> dict[str, Any]:
    """Busca avançada com filtros estruturados (requer API key)."""

    client = _client_from_ctx(ctx)
    return await client.search(args.to_params())


@mcp.tool()
async def cnpj_search_estimate(args: SearchInput, ctx: ToolContext) -> dict[str, Any]:
    """Estima a quantidade de resultados para uma busca avançada (requer API key)."""

    client = _client_from_ctx(ctx)
    return await client.search_estimate(args.to_params())


@mcp.tool()
async def cnpj_search_csv(args: SearchCsvInput, ctx: ToolContext) -> dict[str, Any]:
    """Exporta resultados de busca avançada para CSV (requer API key)."""

    client = _client_from_ctx(ctx)
    return await client.search_csv(args.to_params())


@mcp.tool()
async def cnpj_search_csv_estimate(args: SearchCsvInput, ctx: ToolContext) -> dict[str, Any]:
    """Estima créditos necessários para exportação CSV (requer API key)."""

    client = _client_from_ctx(ctx)
    return await client.search_csv_estimate(args.to_params())


@mcp.prompt()
def prompt_company_profile(cnpj: str, detalhado: bool = True) -> str:
    """Gera um template de análise de empresa com base em um CNPJ."""

    return dedent(
        f"""
        Objetivo: produzir um resumo executivo sobre a empresa de CNPJ {cnpj}.

        Passos sugeridos:
        1. Tentar `{ 'cnpj_lookup' if detalhado else 'cnpj_public_lookup' }`.
           - Caso receba erro de chave ausente e ainda precise de detalhes confidenciais, solicite ao usuário uma chave de API válida.
           - Se a consulta detalhada falhar e não houver chave, use `cnpj_public_lookup` como fallback.
        2. Estruturar a resposta com:
           - Razão social, nome fantasia, data de abertura e situação cadastral
           - Atividade principal (CNAE) e atividades secundárias relevantes
           - Endereço completo e contatos disponíveis
           - Indicadores financeiros (capital social, faixa de faturamento) quando presentes
        3. Evidenciar riscos: situação cadastral ≠ ATIVA, pendências, desenquadramentos de Simples/MEI ou data de baixa.
        4. Se houver filiais, listar CNPJs relacionados.

        Produza a resposta em português claro, com bullets quando fizer sentido e destaque alertas importantes.
        """
    ).strip()


@mcp.prompt()
def prompt_targeted_search(
    termo: str,
    uf: Optional[str] = None,
    situacao: Optional[int] = None,
    exportar_csv: bool = False,
) -> str:
    """Guia a execução de uma busca avançada e, opcionalmente, exportação CSV."""

    filtro_uf = f"UF={uf}" if uf else "UF não informado"
    filtro_situacao = (
        f"situação cadastral={situacao}"
        if situacao is not None
        else "situação cadastral não informada"
    )
    return dedent(
        f"""
        Objetivo: localizar empresas relacionadas a "{termo}". Filtros: {filtro_uf}, {filtro_situacao}.

        1. Use `cnpj_search` com os filtros adequados.
           - Combine `term`, `uf` e `situacao_cadastral` quando disponíveis.
           - Se o volume esperado for alto, execute antes `cnpj_search_estimate` para saber a contagem e planejar custos.
        2. Resuma os resultados principais (razão social, CNAE, município, situação).
        3. {"Caso precise exportar CSV, consulte `cnpj_search_csv_estimate` e depois chame `cnpj_search_csv`." if exportar_csv else "Se o usuário solicitar exportação, confirme antes."}
        4. Oriente o usuário sobre créditos consumidos (ver recurso `buscadordecnpj://docs/credits`).

        Apresente conclusões em português e cite quantos resultados foram encontrados ou exportados.
        """
    ).strip()


@mcp.prompt()
def prompt_bulk_enrichment(descricao_lista: str, total_cnpjs: int) -> str:
    """Instrui como enriquecer uma lista de CNPJs em lote."""

    return dedent(
        f"""
        Objetivo: enriquecer {total_cnpjs} CNPJs ({descricao_lista}).

        1. Confirme se o usuário tem chave de API ativa (necessário para `cnpj_bulk_lookup`).
        2. Garanta que cada CNPJ tenha 14 dígitos; normalize se necessário.
        3. Se os CNPJs vierem de uma busca filtrada por UF/situação, mantenha os mesmos filtros ao chamar `cnpj_bulk_lookup`.
        4. Informe sobre consumo de créditos: 1 crédito a cada 20 CNPJs enviados.
        5. Depois da consulta, destaque:
           - CNPJs encontrados vs não encontrados (campo `not_found`)
           - Dados principais de cada empresa (razão social, situação, CNAE)
           - Alertas para status não ativos ou dados inconsistentes

        Entregue a análise em português, com tabela ou bullets conforme o volume.
        """
    ).strip()


async def main() -> None:
    """Run the MCP server over stdio."""

    await mcp.run_stdio_async()


def cli_main() -> None:
    """CLI entry point used by the package's console script."""

    asyncio.run(main())
