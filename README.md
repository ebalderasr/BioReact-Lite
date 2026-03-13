# BioReact-Lite 🧪

Simulador interactivo de biorreactores continuos desarrollado para el análisis de dinámica, estabilidad y control de bioprocesos.

## Características
- **Cinética de Monod**: Cálculo de la velocidad específica de crecimiento.
- **Integración Numérica**: Implementación de Runge-Kutta de 4to orden (RK4).
- **Análisis de Estabilidad**: Cálculo de la Matriz Jacobiana, Eigenvalores y Eigenvectores basados en el primer método de Lyapunov.
- **Visualización**: Series de tiempo y plano de fase interactivos.

## Requisitos
- Python 3.10+
- Streamlit, Plotly, Scipy, Numpy, Pandas

## Instalación y Uso
1. Clonar el repositorio.
2. Crear un entorno virtual: `python3 -m venv venv`
3. Activar: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Ejecutar: `streamlit run app.py`

---
**Autor:** Emiliano Balderas Ramírez  
*PhD en Bioquímica · Instituto de Biotecnología, UNAM*
