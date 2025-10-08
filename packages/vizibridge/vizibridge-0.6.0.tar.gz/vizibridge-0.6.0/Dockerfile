FROM ghcr.io/pyo3/maturin:latest  
ARG PYPI_TOKEN
ENV MATURIN_PYPI_TOKEN=$PYPI_TOKEN
COPY . /io/
RUN maturin publish -i python3.9 --skip-existing
RUN maturin publish -i python3.10 --skip-existing
RUN maturin publish -i python3.11 --skip-existing
RUN maturin publish -i python3.12 --skip-existing
RUN maturin publish -i python3.13 --skip-existing
