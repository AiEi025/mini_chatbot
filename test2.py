from tools.python_validator import PythonValidator
from pathlib import Path
workspace_dir = Path(__file__).resolve().parent /'workspace'
result = PythonValidator(workspace_dir = workspace_dir/'python/').validate(file_path='test_53366ec1')
print('fjdlksjafdsaf'+'ffffffjdklsajfdksa')
print(result)