# publicar Lib pyhton

sempre que for atualizar a lib é necessário excluir a pasta dist que é criada

- python -m pip install build twine wheel
- python -m build
- python -m twine upload dist/*

o nome da pasta src deve ser o nome da lib