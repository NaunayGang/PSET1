"""Streamlit Home page for the Demand Prediction Service.

Implements Issue #13 (Streamlit App Shell):
- Reads the backend API URL from the API_URL environment variable.
- Calls the /health endpoint to verify backend status.
- Shows basic description and navigation hints for the app.
"""

import streamlit as st

from api_client import get_api_url, get_health


def show_backend_status() -> None:
	"""Display the current status of the backend API on the page."""

	st.subheader("Backend status")

	try:
		health = get_health()
		status = health.get("status")
		api_url = get_api_url()

		if status == "ok":
			st.success(f"Backend OK ({api_url})")
		else:
			st.warning(f"Backend respondió algo inesperado: {health}")
	except Exception as exc:  # noqa: BLE001
		st.error(
			"No se pudo conectar al backend. "
			"Verifica que el servicio FastAPI esté corriendo.",
		)
		st.caption(str(exc))


def main() -> None:
	"""Render the main Home page."""

	st.set_page_config(page_title="Demand Prediction Service")

	st.title("Demand Prediction Service")
	st.write(
		"Sistema de gestión de zonas y rutas de NYC TLC, "
		"incluyendo carga de datos desde archivos Parquet.",
	)

	show_backend_status()

	st.markdown("---")
	st.subheader("Navegación de la aplicación")
	st.write(
		"Usa el menú de páginas de Streamlit (barra lateral) para acceder "
		"a las distintas secciones:",
	)
	st.markdown("- **Zones**: CRUD completo de zonas.")
	st.markdown(
		"- **Routes**: CRUD de rutas utilizando zonas de origen y destino.",
	)
	st.markdown(
		"- **Upload Parquet**: Carga de archivos .parquet para crear o "
		"actualizar zonas y rutas.",
	)


if __name__ == "__main__":
	main()

