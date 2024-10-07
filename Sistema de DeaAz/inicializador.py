import os
import subprocess

# Caminho correto para o Python no ambiente virtual
venv_path = r"C:\Users\soust\PycharmProjects\djangoProject2\.venv\Scripts\python.exe"

# Caminho para o projeto Django
project_path = r"C:\Users\soust\PycharmProjects\djangoProject2"

def iniciar_servidor():
    """Inicia o servidor Django."""
    try:
        os.chdir(project_path)  # Mudar para o diretório do projeto
        subprocess.Popen([venv_path, "manage.py", "runserver", "127.0.0.1:8000"])
        print("Servidor Django iniciado em http://127.0.0.1:8000")
        input("Pressione Enter para sair...")  # Pausa para você ver a saída
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        input("Pressione Enter para sair...")  # Pausa em caso de erro

if __name__ == "__main__":
    iniciar_servidor()
