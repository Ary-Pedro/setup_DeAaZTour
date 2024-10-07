import os
import subprocess

def instalar_dependencias():
    """Instala as dependências necessárias para o projeto Django."""
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    except subprocess.CalledProcessError:
        print("Erro ao instalar as dependências.")

def criar_executavel():
    """Cria um executável para inicializar o servidor Django."""
    try:
        subprocess.run(["pyinstaller", "--onefile", "inicializador.py"], check=True)
    except subprocess.CalledProcessError:
        print("Erro ao criar o executável.")

if __name__ == "__main__":
    instalar_dependencias()
    criar_executavel()
