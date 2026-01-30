"""Zones CRUD page.

Implements Issue #14: List, create, edit and delete Zones via the FastAPI
backend.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from api_client import (
	ApiError,
	create_zone,
	delete_zone,
	get_zone,
	list_zones,
	update_zone,
)


def _format_api_error(err: ApiError) -> str:
	detail = err.detail
	if isinstance(detail, list):
		# Likely FastAPI/Pydantic 422 detail format
		return "\n".join(str(item) for item in detail)
	return str(detail)


def _zones_to_dataframe(zones: list[dict[str, Any]]) -> pd.DataFrame:
	if not zones:
		return pd.DataFrame()
	dataframe = pd.DataFrame(zones)
	preferred_order = [
		"id",
		"borough",
		"zone_name",
		"service_zone",
		"active",
		"created_at",
	]
	columns = [c for c in preferred_order if c in dataframe.columns] + [
		c for c in dataframe.columns if c not in preferred_order
	]
	return dataframe[columns]


def _parse_created_at(value: Any) -> datetime | None:
	if not value:
		return None
	if isinstance(value, datetime):
		return value
	if isinstance(value, str):
		try:
			return datetime.fromisoformat(value.replace("Z", "+00:00"))
		except ValueError:
			return None
	return None


def main() -> None:
	st.set_page_config(page_title="Zones")
	st.title("Zones")

	st.caption("CRUD de zonas (LocationID) consumiendo el backend vía HTTP.")

	with st.expander("Filtros", expanded=True):
		active_filter_enabled = st.checkbox("Filtrar por active", value=False)
		active_value = st.selectbox(
			"active",
			options=[True, False],
			disabled=not active_filter_enabled,
		)
		borough = st.text_input("borough (opcional)", placeholder="Ej: Manhattan")

		filters: dict[str, Any] = {}
		if active_filter_enabled:
			filters["active"] = active_value
		if borough.strip():
			filters["borough"] = borough.strip()

	st.markdown("---")

	col_left, col_right = st.columns([1, 1])

	with col_left:
		st.subheader("Crear Zone")
		with st.form("zones_create_form", clear_on_submit=True):
			zone_id = st.number_input("id (LocationID)", min_value=1, step=1)
			borough_input = st.text_input("borough", placeholder="Ej: Manhattan")
			zone_name = st.text_input("zone_name", placeholder="Ej: Upper East Side")
			service_zone = st.text_input("service_zone", placeholder="Ej: Yellow Zone")
			active = st.checkbox("active", value=True)

			submitted = st.form_submit_button("Crear")

			if submitted:
				if not borough_input.strip() or not zone_name.strip():
					st.error("borough y zone_name no pueden estar vacíos")
				elif not service_zone.strip():
					st.error("service_zone no puede estar vacío")
				else:
					try:
						created = create_zone(
							{
								"id": int(zone_id),
								"borough": borough_input.strip(),
								"zone_name": zone_name.strip(),
								"service_zone": service_zone.strip(),
								"active": bool(active),
							}
						)
						st.success(f"Zone creada: {created.get('id')}")
					except ApiError as err:
						st.error(_format_api_error(err))
					except Exception as exc:  # noqa: BLE001
						st.error(f"Error conectando con el backend: {exc}")

	with col_right:
		st.subheader("Editar / Eliminar Zone")
		edit_zone_id = st.number_input(
			"id de la zona",
			min_value=1,
			step=1,
			key="edit_zone_id",
		)

		fetch_clicked = st.button("Cargar zona")
		if fetch_clicked:
			try:
				zone_data = get_zone(int(edit_zone_id))
				st.session_state["loaded_zone"] = zone_data
			except ApiError as err:
				st.error(_format_api_error(err))
				st.session_state.pop("loaded_zone", None)
			except Exception as exc:  # noqa: BLE001
				st.error(f"Error conectando con el backend: {exc}")
				st.session_state.pop("loaded_zone", None)

		loaded_zone: dict[str, Any] | None = st.session_state.get("loaded_zone")

		if loaded_zone and int(loaded_zone.get("id", 0)) == int(edit_zone_id):
			with st.form("zones_edit_form"):
				st.caption("El backend requiere que el id del URL coincida con el id del body.")

				borough_edit = st.text_input("borough", value=str(loaded_zone.get("borough", "")))
				zone_name_edit = st.text_input(
					"zone_name", value=str(loaded_zone.get("zone_name", ""))
				)
				service_zone_edit = st.text_input(
					"service_zone", value=str(loaded_zone.get("service_zone", ""))
				)
				active_edit = st.checkbox(
					"active",
					value=bool(loaded_zone.get("active", True)),
				)

				save_clicked = st.form_submit_button("Guardar cambios")
				if save_clicked:
					if not borough_edit.strip() or not zone_name_edit.strip():
						st.error("borough y zone_name no pueden estar vacíos")
					elif not service_zone_edit.strip():
						st.error("service_zone no puede estar vacío")
					else:
						created_at = _parse_created_at(loaded_zone.get("created_at"))
						payload: dict[str, Any] = {
							"id": int(edit_zone_id),
							"borough": borough_edit.strip(),
							"zone_name": zone_name_edit.strip(),
							"service_zone": service_zone_edit.strip(),
							"active": bool(active_edit),
						}
						if created_at is not None:
							payload["created_at"] = created_at.isoformat()

						try:
							updated = update_zone(int(edit_zone_id), payload)
							st.success(f"Zone actualizada: {updated.get('id')}")
							st.session_state["loaded_zone"] = updated
						except ApiError as err:
							st.error(_format_api_error(err))
						except Exception as exc:  # noqa: BLE001
							st.error(f"Error conectando con el backend: {exc}")

			st.markdown("---")
			delete_confirm = st.checkbox(
				"Confirmo que quiero eliminar esta zona", value=False, key="delete_confirm"
			)
			if st.button("Eliminar zona", disabled=not delete_confirm):
				try:
					delete_zone(int(edit_zone_id))
					st.success(f"Zone eliminada: {int(edit_zone_id)}")
					st.session_state.pop("loaded_zone", None)
				except ApiError as err:
					st.error(_format_api_error(err))
				except Exception as exc:  # noqa: BLE001
					st.error(f"Error conectando con el backend: {exc}")

	st.markdown("---")
	st.subheader("Listado de Zones")

	try:
		with st.spinner("Cargando zonas..."):
			zones = list_zones(**filters)
		df = _zones_to_dataframe(zones)
		if df.empty:
			st.info("No hay zonas para mostrar con los filtros actuales.")
		else:
			st.dataframe(df, width="stretch", hide_index=True)
	except ApiError as err:
		st.error(_format_api_error(err))
	except Exception as exc:  # noqa: BLE001
		st.error(f"Error conectando con el backend: {exc}")


if __name__ == "__main__":
	main()
