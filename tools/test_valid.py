from python_validator import PythonValidator

validator = PythonValidator(
    workspace_dir="workspace/python"
)


result = validator.validate("main.py")


print("========== VALIDATION ==========")
print("OK:", result["ok"])
print("File:", result["file"])
print("Return code:", result["return_code"])

print("\n========== STDOUT ==========")
print(result["stdout"])

print("\n========== STDERR ==========")
print(result["stderr"])