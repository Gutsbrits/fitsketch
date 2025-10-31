# main.py
import tkinter as tk
from interface import criar_interface_principal

if __name__ == "__main__":
    janela = tk.Tk()
    janela.title("FitSketch - Registro de Treino 🏋️")
    janela.geometry("420x600")
    janela.resizable(False, False)

    criar_interface_principal(janela)

    janela.mainloop()
