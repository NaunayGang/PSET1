"""Routes CRUD page.

Implements Issue #15: List, create, edit and delete Routes via the FastAPI
backend.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from api_client import (
	ApiError,
	create_route,
	delete_route,
	get_route,
	list_routes,
	list_zones,
	update_route,
)


def _format_api_error(err: ApiError) -> str:
	detail = err.detail
	if isinstance(detail, list):
		return "\n".join(str(item) for item in detail)
	return str(detail)


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


def _routes_to_dataframe(
	routes: list[dict[str, Any]],
	*,
	zones_by_id: dict[int, dict[str, Any]] | None = None,
) -> pd.DataFrame:
	if not routes:
		return pd.DataFrame()

	enriched: list[dict[str, Any]] = []
	zones_by_id = zones_by_id or {}
	for route in routes:
		pickup_id = int(route.get("pickup_zone_id", 0) or 0)
		dropoff_id = int(route.get("dropoff_zone_id", 0) or 0)
		pickup_zone = zones_by_id.get(pickup_id, {})
		dropoff_zone = zones_by_id.get(dropoff_id, {})
		enriched.append(
			{
				**route,
				"pickup_zone": pickup_zone.get("zone_name"),
				"dropoff_zone": dropoff_zone.get("zone_name"),
			}
		)

	dataframe = pd.DataFrame(enriched)
	preferred_order = [
		"id",
		"name",
		"active",
		"pickup_zone_id",
		"pickup_zone",
		"dropoff_zone_id",
		"dropoff_zone",
		"created_at",
	]
	columns = [c for c in preferred_order if c in dataframe.columns] + [
		c for c in dataframe.columns if c not in preferred_order
	]
	return dataframe[columns]


def _build_zone_options(zones: list[dict[str, Any]]) -> list[tuple[int, str]]:
	options: list[tuple[int, str]] = []
	for zone in zones:
		zone_id = int(zone.get("id"))
		borough = str(zone.get("borough", "")).strip()
		zone_name = str(zone.get("zone_name", "")).strip()
		label = f"{zone_id} - {borough} / {zone_name}".strip(" -/")
		options.append((zone_id, label))
	options.sort(key=lambda x: x[0])
	return options


def _default_route_name(
	pickup_zone_id: int,
	dropoff_zone_id: int,
	*,
	zones_by_id: dict[int, dict[str, Any]] | None = None,
) -> str:
	zones_by_id = zones_by_id or {}
	pickup_name = zones_by_id.get(pickup_zone_id, {}).get("zone_name")
	dropoff_name = zones_by_id.get(dropoff_zone_id, {}).get("zone_name")
	if pickup_name and dropoff_name:
		return f"{pickup_name} → {dropoff_name}"
	return f"{pickup_zone_id} → {dropoff_zone_id}"


def main() -> None:
	st.set_page_config(page_title="Routes")
	st.title("Routes")
	st.caption("CRUD de rutas (pickup/dropoff) consumiendo el backend vía HTTP.")

	try:
		zones = list_zones()
	except ApiError as err:
		st.error(_format_api_error(err))
		st.stop()
	except Exception:
		st.error(
			"Error de conexión con el backend al obtener las zonas. "
			"Por favor, verifica el servidor e intenta recargar la página."
		)
		st.stop()

	zones_by_id: dict[int, dict[str, Any]] = {}
	for zone in zones:
		try:
			zones_by_id[int(zone.get("id"))] = zone
		except Exception:  # noqa: BLE001
			continue

	zone_options = _build_zone_options(zones)
	if not zone_options:
		st.warning("No hay zonas cargadas. Crea Zones primero para poder crear Routes.")

	with st.expander("Filtros", expanded=True):
		active_filter_enabled = st.checkbox("Filtrar por active", value=False)
		active_value = st.selectbox(
			"active",
			options=[True, False],
			disabled=not active_filter_enabled,
		)

		if zone_options:
			pickup_filter_enabled = st.checkbox("Filtrar por pickup_zone_id", value=False)
			pickup_filter = st.selectbox(
				"pickup_zone_id",
				options=zone_options,
				format_func=lambda o: o[1],
				disabled=not pickup_filter_enabled,
			)

			dropoff_filter_enabled = st.checkbox("Filtrar por dropoff_zone_id", value=False)
			dropoff_filter = st.selectbox(
				"dropoff_zone_id",
				options=zone_options,
				format_func=lambda o: o[1],
				disabled=not dropoff_filter_enabled,
			)
		else:
			pickup_filter_enabled = False
			dropoff_filter_enabled = False
			st.info(
				"No hay zonas disponibles para filtrar por pickup/dropoff. "
				"Crea Zones primero para poder usar estos filtros."
			)

		filters: dict[str, Any] = {}
		if active_filter_enabled:
			filters["active"] = active_value
		if zone_options and pickup_filter_enabled:
			filters["pickup_zone_id"] = int(pickup_filter[0])
		if zone_options and dropoff_filter_enabled:
			filters["dropoff_zone_id"] = int(dropoff_filter[0])

	st.markdown("---")

	col_left, col_right = st.columns([1, 1])

	with col_left:
		st.subheader("Crear Route")
		if not zone_options:
			st.info("Primero crea Zones para poder crear Routes.")
		else:
			with st.form("routes_create_form", clear_on_submit=True):
				pickup = st.selectbox(
					"pickup_zone_id",
					options=zone_options,
					format_func=lambda o: o[1],
				)
				dropoff = st.selectbox(
					"dropoff_zone_id",
					options=zone_options,
					format_func=lambda o: o[1],
				)

				auto_name = st.checkbox("Autogenerar name", value=True)
				default_name = _default_route_name(
					int(pickup[0]),
					int(dropoff[0]),
					zones_by_id=zones_by_id,
				)
				name = st.text_input("name", value=default_name if auto_name else "")
				active = st.checkbox("active", value=True)

				submitted = st.form_submit_button("Crear")
				if submitted:
					pickup_id = int(pickup[0])
					dropoff_id = int(dropoff[0])
					if pickup_id == dropoff_id:
						st.error("pickup_zone_id y dropoff_zone_id deben ser diferentes")
					elif not name.strip():
						st.error("name no puede estar vacío")
					else:
						try:
							created = create_route(
								{
									"id": 1,
									"pickup_zone_id": pickup_id,
									"dropoff_zone_id": dropoff_id,
									"name": name.strip(),
									"active": bool(active),
								}
							)
							st.success(f"Route creada: {created.get('id')}")
						except ApiError as err:
							st.error(_format_api_error(err))
						except Exception as exc:  # noqa: BLE001
							st.error(f"Error conectando con el backend: {exc}")

	with col_right:
		st.subheader("Editar / Eliminar Route")
		edit_route_id = st.number_input(
			"id de la route",
			min_value=1,
			step=1,
			key="edit_route_id",
		)

		fetch_clicked = st.button("Cargar route")
		if fetch_clicked:
			try:
				route_data = get_route(int(edit_route_id))
				st.session_state["loaded_route"] = route_data
			except ApiError as err:
				st.error(_format_api_error(err))
				st.session_state.pop("loaded_route", None)
			except Exception as exc:  # noqa: BLE001
				st.error(f"Error conectando con el backend: {exc}")
				st.session_state.pop("loaded_route", None)

		loaded_route: dict[str, Any] | None = st.session_state.get("loaded_route")
		if loaded_route and int(loaded_route.get("id", 0)) == int(edit_route_id):
			if zone_options:
				with st.form("routes_edit_form"):
					st.caption(
						"El backend requiere que el id del URL coincida con el id del body."
					)

					current_pickup_id = int(loaded_route.get("pickup_zone_id", 0) or 0)
					current_dropoff_id = int(loaded_route.get("dropoff_zone_id", 0) or 0)

					pickup_index = 0
					dropoff_index = 0
					for idx, (zone_id, _) in enumerate(zone_options):
						if zone_id == current_pickup_id:
							pickup_index = idx
						if zone_id == current_dropoff_id:
							dropoff_index = idx

					pickup_edit = st.selectbox(
						"pickup_zone_id",
						options=zone_options,
						format_func=lambda o: o[1],
						index=pickup_index,
					)
					dropoff_edit = st.selectbox(
						"dropoff_zone_id",
						options=zone_options,
						format_func=lambda o: o[1],
						index=dropoff_index,
					)
					name_edit = st.text_input("name", value=str(loaded_route.get("name", "")))
					active_edit = st.checkbox(
						"active",
						value=bool(loaded_route.get("active", True)),
					)

					save_clicked = st.form_submit_button("Guardar cambios")
					if save_clicked:
						pickup_id = int(pickup_edit[0])
						dropoff_id = int(dropoff_edit[0])
						if pickup_id == dropoff_id:
							st.error("pickup_zone_id y dropoff_zone_id deben ser diferentes")
						elif not name_edit.strip():
							st.error("name no puede estar vacío")
						else:
							created_at = _parse_created_at(loaded_route.get("created_at"))
							payload: dict[str, Any] = {
								"id": int(edit_route_id),
								"pickup_zone_id": pickup_id,
								"dropoff_zone_id": dropoff_id,
								"name": name_edit.strip(),
								"active": bool(active_edit),
							}
							if created_at is not None:
								payload["created_at"] = created_at.isoformat()

							try:
								updated = update_route(int(edit_route_id), payload)
								st.success(f"Route actualizada: {updated.get('id')}")
								st.session_state["loaded_route"] = updated
							except ApiError as err:
								st.error(_format_api_error(err))
							except Exception as exc:  # noqa: BLE001
								st.error(f"Error conectando con el backend: {exc}")
			else:
				st.warning(
					"No hay zonas disponibles para editar los campos "
					"'pickup_zone_id' y 'dropoff_zone_id'."
				)

			st.markdown("---")
			delete_confirm = st.checkbox(
				"Confirmo que quiero eliminar esta route",
				value=False,
				key="delete_route_confirm",
			)
			if st.button("Eliminar route", disabled=not delete_confirm):
				try:
					delete_route(int(edit_route_id))
					st.success(f"Route eliminada: {int(edit_route_id)}")
					st.session_state.pop("loaded_route", None)
				except ApiError as err:
					st.error(_format_api_error(err))
				except Exception as exc:  # noqa: BLE001
					st.error(f"Error conectando con el backend: {exc}")

	st.markdown("---")
	st.subheader("Listado de Routes")

	try:
		with st.spinner("Cargando rutas..."):
			routes = list_routes(**filters)
		df = _routes_to_dataframe(routes, zones_by_id=zones_by_id)
		if df.empty:
			st.info("No hay rutas para mostrar con los filtros actuales.")
		else:
			st.dataframe(df, width="stretch", hide_index=True)
	except ApiError as err:
		st.error(_format_api_error(err))
	except Exception as exc:  # noqa: BLE001
		st.error(f"Error conectando con el backend: {exc}")


if __name__ == "__main__":
	main()
