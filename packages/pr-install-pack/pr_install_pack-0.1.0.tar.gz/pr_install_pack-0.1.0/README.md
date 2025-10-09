https://chatgpt.com/c/68e55ff6-72c4-8332-b31a-16557791346a

uv build

uv pip install .

Si quieres editable (desarrollo):
uv pip install -e .


uv pip install ..\pr_install_pack\dist\pr_install_pack-0.1.0-py3-none-any.whl
uv pip install ..\pr_install_pack\dist\*.whl --force-reinstall


# con uv pip
Si lo instalaste desde wheel (.whl)
uv build
uv pip install -e ..\pr_install_pack
uv pip install ..\pr_install_pack\dist\pr_install_pack-0.1.0-py3-none-any.whl
uv pip uninstall ..\pr_install_pack\dist\pr_install_pack-0.1.0-py3-none-any.whl


# solo con uv
uv add ..\pr_install_pack\dist\pr_install_pack-0.1.0-py3-none-any.whl
uv add --editable ..\pr_install_pack
uv remove pr_install_pack

