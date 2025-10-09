from typing import Dict, Any, Optional, List

from pydantic import conlist
from square_commons.api_utils import make_request_json_output

from square_database_helper.pydantic_models import FiltersV0


class SquareDatabaseHelper:
    def __init__(
        self,
        param_int_square_database_port: int = 10010,
        param_str_square_database_ip: str = "localhost",
        param_str_square_database_protocol: str = "http",
    ):
        try:
            self.global_str_square_database_url_base = (
                f"{param_str_square_database_protocol}://"
                f"{param_str_square_database_ip}:{param_int_square_database_port}"
            )
        except Exception:
            raise

    def _make_request(
        self, method, endpoint, json=None, data=None, params=None, headers=None
    ):
        try:
            return make_request_json_output(
                method=method,
                base_url=self.global_str_square_database_url_base,
                endpoint=endpoint,
                json=json,
                data=data,
                params=params,
                headers=headers,
            )
        except Exception:
            raise

    def insert_rows_v0(
        self,
        data: conlist(Dict[str, Any], min_length=1),
        database_name: str,
        schema_name: str,
        table_name: str,
        skip_conflicts: bool = False,
    ):
        try:
            endpoint = "insert_rows/v0"
            payload = {
                "data": data,
                "database_name": database_name,
                "schema_name": schema_name,
                "table_name": table_name,
                "skip_conflicts": skip_conflicts,
            }
            return self._make_request("POST", endpoint, json=payload)
        except Exception:
            raise

    def get_rows_v0(
        self,
        filters: FiltersV0,
        database_name: str,
        schema_name: str,
        table_name: str,
        apply_filters: bool = True,
        columns: Optional[List[str]] = None,
        order_by: List[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ):
        if order_by is None:
            order_by = []
        try:
            endpoint = "get_rows/v0"
            payload = {
                "database_name": database_name,
                "schema_name": schema_name,
                "table_name": table_name,
                "filters": filters.model_dump(),
                "apply_filters": apply_filters,
                "columns": columns,
                "order_by": order_by,
                "limit": limit,
                "offset": offset,
            }
            return self._make_request("POST", endpoint, json=payload)
        except Exception:
            raise

    def edit_rows_v0(
        self,
        data: Dict[str, Any],
        filters: FiltersV0,
        database_name: str,
        schema_name: str,
        table_name: str,
        apply_filters: bool = True,
    ):
        try:
            endpoint = "edit_rows/v0"
            payload = {
                "data": data,
                "filters": filters.model_dump(),
                "database_name": database_name,
                "schema_name": schema_name,
                "table_name": table_name,
                "apply_filters": apply_filters,
            }
            return self._make_request("PATCH", endpoint, json=payload)
        except Exception:
            raise

    def delete_rows_v0(
        self,
        filters: FiltersV0,
        database_name: str,
        schema_name: str,
        table_name: str,
        apply_filters: bool = True,
    ):
        try:
            endpoint = "delete_rows/v0"
            payload = {
                "filters": filters.model_dump(),
                "database_name": database_name,
                "schema_name": schema_name,
                "table_name": table_name,
                "apply_filters": apply_filters,
            }
            return self._make_request("POST", endpoint, json=payload)
        except Exception:
            raise
