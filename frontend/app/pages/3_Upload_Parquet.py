"""Parquet upload page.

Implements Issue #16: Upload a NYC TLC trips parquet file to the backend and
display the processing summary.
"""

from __future__ import annotations

from typing import Any

import requests
import streamlit as st

from api_client import ApiError, get_api_url, upload_trips_parquet


def _format_api_error(err: ApiError) -> str:
	detail = err.detail
	if isinstance(detail, list):
		return "\n".join(str(item) for item in detail)
	return str(detail)


def _render_result(result: dict[str, Any]) -> None:
	st.subheader("Resultado")

	st.write(f"Archivo: {result.get('file_name')}")

	col1, col2, col3 = st.columns(3)
	col1.metric("Rows read", int(result.get("rows_read", 0) or 0))
	col2.metric("Routes detected", int(result.get("routes_detected", 0) or 0))
	col3.metric("Errores", len(result.get("errors", []) or []))

	col4, col5, col6 = st.columns(3)
	col4.metric("Zones created", int(result.get("zones_created", 0) or 0))
	col5.metric("Zones updated", int(result.get("zones_updated", 0) or 0))
	col6.metric("Routes created", int(result.get("routes_created", 0) or 0))

	st.metric("Routes updated", int(result.get("routes_updated", 0) or 0))

	errors = result.get("errors") or []
	if errors:
		st.subheader("Errores")
		for item in errors:
			st.error(str(item))

	with st.expander("Ver response completo"):
		st.json(result)


def main() -> None:
	st.set_page_config(page_title="Upload Parquet")
	st.title("Upload Parquet")

	st.caption(
		"Sube un archivo .parquet con trips (PULocationID/DOLocationID) para crear/"
		"actualizar Zones y Routes en el backend."
	)

	st.info(f"Backend API: {get_api_url()}")

	uploaded_file = st.file_uploader(
		"Selecciona un archivo .parquet",
		type=["parquet"],
		accept_multiple_files=False,
	)

	col_left, col_right = st.columns([1, 1])

	with col_left:
		mode = st.selectbox("mode", options=["create", "update"], index=0)

	with col_right:
		top_n_routes = st.number_input(
			"top_n_routes",
			min_value=1,
			max_value=500,
			value=50,
			step=1,
		)

	limit_rows = st.number_input(
		"limit_rows",
		min_value=1,
		max_value=1_000_000,
		value=50_000,
		step=1_000,
	)

	st.markdown("---")

	process_disabled = uploaded_file is None
	if st.button("Procesar parquet", disabled=process_disabled):
		try:
			with st.spinner("Subiendo y procesando archivo..."):
				result = upload_trips_parquet(
					filename=str(uploaded_file.name),
					content=uploaded_file.getvalue(),
					mode=str(mode),
					limit_rows=int(limit_rows),
					top_n_routes=int(top_n_routes),
				)
			st.success("Procesamiento completado")
			_render_result(result)
		except ApiError as err:
			st.error(_format_api_error(err))
		except requests.RequestException as exc:
			st.error(f"Error conectando con el backend: {exc}")
		except Exception as exc:  # noqa: BLE001
			st.error(f"Error inesperado: {exc}")

	st.markdown("---")
	st.subheader("Tips")
	st.write(
		"- Si el backend responde `File must be a .parquet file`, verifica la extensión.\n"
		"- Si responde errores por columnas faltantes, el parquet debe incluir "
		"PULocationID y DOLocationID.\n"
		"- El backend guarda datos en memoria: reiniciar el backend limpia Zones/Routes."
	)


if __name__ == "__main__":
	main()
