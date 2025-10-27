FROM fenics/dolfinx:latest

RUN pip install --no-cache-dir jupyterlab pyvista matplotlib

CMD ["jupyter-lab", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
