    # interface.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from colors import *
from database import inserir_treino, atualizar_treino, excluir_treino, listar_treinos

id_edicao_atual = None  # Controle de edição

# --------------------- Funções da Interface ----------------------

def salvar_treino():
    global id_edicao_atual

    nome = entrada_nome.get().strip()
    data_treino = entrada_data.get().strip()
    exercicio = entrada_exercicio.get().strip()
    series_str = entrada_series.get().strip()
    reps_str = entrada_reps.get().strip()
    carga_str = entrada_carga.get().strip() or "0"
    obs = texto_obs.get("1.0", tk.END).strip()

    if not nome or not exercicio or not series_str or not reps_str:
        messagebox.showerror("Erro", "Preencha os campos obrigatórios (Nome, Exercício, Séries, Repetições).")
        return

    try:
        series = int(series_str)
        reps = int(reps_str)
        carga = float(carga_str.replace(",", "."))

        if id_edicao_atual is None:
            inserir_treino((nome, data_treino, exercicio, series, reps, carga, obs))
            messagebox.showinfo("Sucesso", "Treino registrado com sucesso!")
        else:
            atualizar_treino((nome, data_treino, exercicio, series, reps, carga, obs, id_edicao_atual))
            messagebox.showinfo("Sucesso", f"Treino ID {id_edicao_atual} atualizado!")
            id_edicao_atual = None
            btn_salvar.config(text="Salvar Treino")

        limpar_campos()
    except ValueError:
        messagebox.showerror("Erro", "Campos numéricos inválidos.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar: {e}")


def limpar_campos(mostrar_msg=False):
    global id_edicao_atual
    entrada_nome.delete(0, tk.END)
    data_var.set(str(date.today()))
    entrada_exercicio.set("Supino")
    entrada_series.delete(0, tk.END)
    entrada_reps.delete(0, tk.END)
    entrada_carga.delete(0, tk.END)
    texto_obs.delete("1.0", tk.END)
    id_edicao_atual = None
    btn_salvar.config(text="Salvar Treino")

    if mostrar_msg:
        messagebox.showinfo("Limpar", "Campos limpos com sucesso!")


def ver_treinos():
    janela_lista = tk.Toplevel()
    janela_lista.title("Treinos Salvos")
    janela_lista.geometry("850x500")
    janela_lista.configure(bg=COR_FUNDO)

    colunas = ("ID", "Nome", "Data", "Exercício", "Séries", "Repetições", "Carga", "Observações")
    tree = ttk.Treeview(janela_lista, columns=colunas, show="headings")

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    tree.column("ID", width=40)
    tree.column("Observações", width=150)
    tree.pack(fill="both", expand=True, pady=10)

    def carregar_dados(filtros=None):
        for item in tree.get_children():
            tree.delete(item)
        for linha in listar_treinos(filtros):
            tree.insert("", "end", values=linha)

    carregar_dados()

    def excluir():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um treino para excluir.")
            return
        valores = tree.item(item)["values"]
        treino_id = valores[0]
        if messagebox.askyesno("Confirmar", f"Excluir treino ID {treino_id}?"):
            excluir_treino(treino_id)
            tree.delete(item)
            messagebox.showinfo("Sucesso", f"Treino {treino_id} excluído.")

    def editar():
        global id_edicao_atual
        item = tree.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um treino para editar.")
            return

        valores = tree.item(item)["values"]
        id_edicao_atual = valores[0]

        limpar_campos()
        entrada_nome.insert(0, valores[1])
        data_var.set(valores[2])
        entrada_exercicio.set(valores[3])
        entrada_series.insert(0, valores[4])
        entrada_reps.insert(0, valores[5])
        entrada_carga.insert(0, valores[6])
        texto_obs.insert("1.0", valores[7])
        btn_salvar.config(text="Atualizar Treino")
        janela_lista.destroy()

    # --- Área de busca ---
    frame_busca = tk.LabelFrame(janela_lista, text="Filtros de busca", bg=COR_FUNDO)
    frame_busca.pack(pady=5, padx=10, fill="x")

    ttk.Label(frame_busca, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    entry_nome = tk.Entry(frame_busca, width=20)
    entry_nome.grid(row=0, column=1, padx=5)
    ttk.Label(frame_busca, text="Data:").grid(row=0, column=2, padx=5)
    entry_data = tk.Entry(frame_busca, width=15)
    entry_data.grid(row=0, column=3, padx=5)
    ttk.Label(frame_busca, text="Exercício:").grid(row=0, column=4, padx=5)
    entry_exercicio = tk.Entry(frame_busca, width=20)
    entry_exercicio.grid(row=0, column=5, padx=5)

    ttk.Button(frame_busca, text="Buscar", command=lambda: carregar_dados({
        "nome": entry_nome.get(),
        "data": entry_data.get(),
        "exercicio": entry_exercicio.get()
    })).grid(row=0, column=6, padx=5)
    ttk.Button(frame_busca, text="Limpar", command=carregar_dados).grid(row=0, column=7, padx=5)

    # --- Botões inferiores ---
    frame_botoes = tk.Frame(janela_lista, bg=COR_FUNDO)
    frame_botoes.pack(pady=10)
    ttk.Button(frame_botoes, text="Editar", command=editar).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botoes, text="Excluir", command=excluir).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botoes, text="Atualizar Lista", command=carregar_dados).grid(row=0, column=2, padx=5)
    ttk.Button(frame_botoes, text="Fechar", command=janela_lista.destroy).grid(row=0, column=3, padx=5)


def criar_interface_principal(root):
    global entrada_nome, data_var, entrada_data, entrada_exercicio, entrada_series, entrada_reps, entrada_carga, texto_obs, btn_salvar

    root.configure(bg=COR_FUNDO)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TLabel", background=COR_FUNDO, foreground=COR_TEXTO, font=("Segoe UI", 10))
    style.configure("TButton", background=COR_BOTAO, foreground="white", font=("Segoe UI", 10, "bold"))
    style.map("TButton", background=[("active", COR_BOTAO_HOVER)])

    # --- Título ---
    ttk.Label(root, text="Registro de Treino", font=("Segoe UI", 16, "bold"), anchor="center").pack(pady=(20, 10))

    frame = ttk.Frame(root)
    frame.pack(pady=10, padx=20, fill="x")
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="w")
    entrada_nome = ttk.Entry(frame)
    entrada_nome.grid(row=0, column=1, sticky="ew")

    ttk.Label(frame, text="Data:").grid(row=1, column=0, sticky="w")
    data_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
    entrada_data = ttk.Entry(frame, textvariable=data_var)
    entrada_data.grid(row=1, column=1, sticky="ew")

    ttk.Label(frame, text="Exercício:").grid(row=2, column=0, sticky="w")
    exercicios = ["Supino", "Agachamento", "Levantamento Terra", "Remada Curvada", "Desenvolvimento", "Rosca Direta", "Tríceps Pulley", "Abdominal", "Corrida"]
    entrada_exercicio = ttk.Combobox(frame, values=exercicios)
    entrada_exercicio.grid(row=2, column=1, sticky="ew")
    entrada_exercicio.set("Supino")

    ttk.Label(frame, text="Séries:").grid(row=3, column=0, sticky="w")
    entrada_series = ttk.Entry(frame)
    entrada_series.grid(row=3, column=1, sticky="ew")

    ttk.Label(frame, text="Repetições:").grid(row=4, column=0, sticky="w")
    entrada_reps = ttk.Entry(frame)
    entrada_reps.grid(row=4, column=1, sticky="ew")

    ttk.Label(frame, text="Carga (kg):").grid(row=5, column=0, sticky="w")
    entrada_carga = ttk.Entry(frame)
    entrada_carga.grid(row=5, column=1, sticky="ew")

    ttk.Label(frame, text="Observações:").grid(row=6, column=0, sticky="nw")
    texto_obs = tk.Text(frame, width=25, height=4)
    texto_obs.grid(row=6, column=1, sticky="ew")

    frame_botoes = ttk.Frame(root)
    frame_botoes.pack(pady=20, padx=20, fill="x")
    frame_botoes.columnconfigure((0, 1), weight=1)

    btn_salvar = ttk.Button(frame_botoes, text="Salvar Treino", command=salvar_treino)
    btn_salvar.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=5)

    ttk.Button(frame_botoes, text="Limpar", command=limpar_campos).grid(row=1, column=0, sticky="ew", padx=(0, 5), ipady=5)
    ttk.Button(frame_botoes, text="Ver Treinos", command=ver_treinos).grid(row=1, column=1, sticky="ew", padx=(5, 0), ipady=5)

    ttk.Label(root, text="FitSketch v0.3", font=("Segoe UI", 9), foreground="gray").pack(side="bottom", pady=10)
