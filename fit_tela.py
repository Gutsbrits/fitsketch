# Cores padrão do sistema
COR_FUNDO = "#ECECEC"       # Cinza claro
COR_BOTAO = "#0078D7"       # Azul principal
COR_BOTAO_HOVER = "#005A9E" # Azul mais escuro para hover
COR_TEXTO = "#333333"       # Cinza escuro para textos
COR_BORDA = "#CCCCCC"      # Cinza para bordas

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sqlite3

def inicializar_db():
    """Inicializa o banco de dados e cria a tabela se não existir."""
    conn = sqlite3.connect("fit.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        data TEXT,
        exercicio TEXT,
        series INTEGER,
        repeticoes INTEGER,
        carga REAL,
        observacoes TEXT
    )
    """)
    conn.commit()
    return conn, cursor

# Conexão com banco de dados
conn, cursor = inicializar_db()

# Variável para controlar o ID do treino em edição
id_edicao_atual = None

# --- Funções do Banco de Dados ---

def salvar_treino():
    global id_edicao_atual

    nome = entrada_nome.get().strip()
    data_treino = entrada_data.get().strip()
    exercicio = entrada_exercicio.get().strip()
    series_str = entrada_series.get().strip()
    reps_str = entrada_reps.get().strip()
    carga_str = entrada_carga.get().strip() or "0" # Padrão para 0 se vazio
    obs = texto_obs.get("1.0", tk.END).strip()

    # Verifica se os campos principais estão preenchidos
    if not nome or not exercicio or not series_str or not reps_str:
        messagebox.showerror("Erro", "Preencha os campos obrigatórios (Nome, Exercício, Séries, Repetições).")
        return

    try:
        # Validação de tipos numéricos
        series = int(series_str)
        reps = int(reps_str)
        carga = float(carga_str.replace(",", ".")) # Aceita vírgula como decimal

        if id_edicao_atual is None:
            # Inserir novo treino
            cursor.execute("""
                INSERT INTO treinos (nome, data, exercicio, series, repeticoes, carga, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome, data_treino, exercicio, series, reps, carga, obs))
            messagebox.showinfo("Sucesso", "Treino registrado com sucesso!")
        else:
            # Atualizar treino existente
            cursor.execute("""
                UPDATE treinos SET nome=?, data=?, exercicio=?, series=?, repeticoes=?, carga=?, observacoes=?
                WHERE id=?
            """, (nome, data_treino, exercicio, series, reps, carga, obs, id_edicao_atual))
            messagebox.showinfo("Sucesso", f"Treino ID {id_edicao_atual} atualizado!")

        conn.commit()
        limpar_campos()
    except ValueError:
        messagebox.showerror("Erro de Formato", "Os campos 'Séries', 'Repetições' e 'Carga' devem ser números.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível salvar o treino.\n{e}")

# --- Funções da Interface ---

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

        sql = "SELECT * FROM treinos WHERE 1=1"
        valores = []

        # Adiciona filtros conforme preenchido
        if filtros:
            if filtros.get("nome"):
                sql += " AND nome LIKE ?"
                valores.append("%" + filtros["nome"] + "%")
            if filtros.get("data"):
                sql += " AND data LIKE ?"
                valores.append("%" + filtros["data"] + "%")
            if filtros.get("exercicio"):
                sql += " AND exercicio LIKE ?"
                valores.append("%" + filtros["exercicio"] + "%")

        sql += " ORDER BY id DESC"
        cursor.execute(sql, valores)
        registros = cursor.fetchall()
        for linha in registros:
            tree.insert("", "end", values=linha)

    carregar_dados()

    # --- Função Excluir ---
    def excluir_treino():
        item = tree.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um treino para excluir.")
            return
        valores = tree.item(item)["values"]
        treino_id = valores[0]
        confirm = messagebox.askyesno("Confirmar", f"Deseja excluir o treino ID {treino_id}?")
        if not confirm:
            return
        cursor.execute("DELETE FROM treinos WHERE id=?", (treino_id,))
        conn.commit()
        tree.delete(item)
        messagebox.showinfo("Sucesso", f"Treino {treino_id} excluído.")

    # --- Função Editar ---
    def editar_treino():
        item = tree.selection()
        global id_edicao_atual

        if not item:
            messagebox.showwarning("Atenção", "Selecione um treino para editar.")
            return
        
        valores = tree.item(item)["values"]
        id_edicao_atual = valores[0]

        # Limpa campos antes de preencher
        limpar_campos(mostrar_msg=False)

        # Preenche os campos da janela principal
        entrada_nome.insert(0, valores[1])
        data_var.set(valores[2])
        entrada_exercicio.set(valores[3])
        entrada_series.insert(0, valores[4])
        entrada_reps.insert(0, valores[5])
        entrada_carga.insert(0, valores[6])
        texto_obs.insert("1.0", valores[7])

        btn_salvar.config(text="Atualizar Treino")
        janela_lista.destroy()

    # --- Área de busca avançada ---
    frame_busca = tk.LabelFrame(janela_lista, text="Filtros de busca")
    frame_busca.pack(pady=5, padx=10, fill="x")

    ttk.Label(frame_busca, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    entry_nome = tk.Entry(frame_busca, width=20)
    entry_nome.grid(row=0, column=1, padx=5)

    tk.Label(frame_busca, text="Data:").grid(row=0, column=2, padx=5)
    entry_data = tk.Entry(frame_busca, width=15)
    entry_data.grid(row=0, column=3, padx=5)

    ttk.Label(frame_busca, text="Exercício:").grid(row=0, column=4, padx=5)
    entry_exercicio = tk.Entry(frame_busca, width=20)
    entry_exercicio.grid(row=0, column=5, padx=5)

    def buscar():
        filtros = {
            "nome": entry_nome.get().strip(),
            "data": entry_data.get().strip(),
            "exercicio": entry_exercicio.get().strip()
        }
        carregar_dados(filtros)

    def limpar():
        entry_nome.delete(0, tk.END)
        entry_data.delete(0, tk.END)
        entry_exercicio.delete(0, tk.END)
        carregar_dados()

    ttk.Button(frame_busca, text="Buscar", command=buscar, style="TButton").grid(row=0, column=6, padx=5)
    ttk.Button(frame_busca, text="Limpar", command=limpar, style="TButton").grid(row=0, column=7, padx=5)

    # --- Botões inferiores ---
    frame_botoes = tk.Frame(janela_lista)
    frame_botoes.pack(pady=10)

    ttk.Button(frame_botoes, text="Editar", command=editar_treino, style="TButton").grid(row=0, column=0, padx=5)
    ttk.Button(frame_botoes, text="Excluir", command=excluir_treino, style="TButton").grid(row=0, column=1, padx=5)
    ttk.Button(frame_botoes, text="Atualizar Lista", command=carregar_dados, style="TButton").grid(row=0, column=2, padx=5)
    ttk.Button(frame_botoes, text="Fechar", command=janela_lista.destroy, style="TButton").grid(row=0, column=3, padx=5)

def limpar_campos(mostrar_msg=False):
    global id_edicao_atual

    # Limpa os campos de entrada
    entrada_nome.delete(0, tk.END) # Limpa o nome também
    data_var.set(str(date.today()))
    entrada_exercicio.set("Supino")
    entrada_series.delete(0, tk.END)
    entrada_reps.delete(0, tk.END)
    entrada_carga.delete(0, tk.END)
    texto_obs.delete("1.0", tk.END)

    # Reseta o estado de edição e o texto do botão
    id_edicao_atual = None
    btn_salvar.config(text="Salvar Treino")

    if mostrar_msg:
        messagebox.showinfo("Limpar", "Campos limpos com sucesso!")

def criar_interface_principal(root):
    """Cria e configura todos os widgets da janela principal."""
    global entrada_nome, data_var, entrada_data, entrada_exercicio, entrada_series, entrada_reps, entrada_carga, texto_obs, btn_salvar

    root.configure(bg=COR_FUNDO)

    # Estilo TTK
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TLabel", background=COR_FUNDO, foreground=COR_TEXTO, font=("Segoe UI", 10))
    style.configure("TButton", background=COR_BOTAO, foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, focusthickness=3, focuscolor='none')
    style.map("TButton", background=[("active", COR_BOTAO_HOVER)])
    style.configure("TEntry", bordercolor=COR_BORDA, lightcolor=COR_BORDA, darkcolor=COR_BORDA, fieldbackground="white")
    style.configure("TCombobox", bordercolor=COR_BORDA, lightcolor=COR_BORDA, darkcolor=COR_BORDA, fieldbackground="white", selectbackground="white", selectforeground=COR_TEXTO)

    # Título
    titulo = ttk.Label(root, text="Registro de Treino", font=("Segoe UI", 16, "bold"), anchor="center")
    titulo.pack(pady=(20, 10), fill="x")

    # Frame principal
    frame = ttk.Frame(root, style="TFrame")
    frame.pack(pady=10, padx=20, fill="x")
    frame.columnconfigure(1, weight=1)

    # --- Campos de Entrada ---
    label_opts = {"padx": 5, "pady": 8} # Removido 'sticky' daqui
    entry_opts = {"sticky": "ew", "pady": 8}

    ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="w", **label_opts)
    entrada_nome = ttk.Entry(frame, width=30)
    entrada_nome.grid(row=0, column=1, **entry_opts)

    ttk.Label(frame, text="Data:").grid(row=1, column=0, sticky="w", **label_opts)
    data_var = tk.StringVar(value=str(date.today()))
    entrada_data = ttk.Entry(frame, textvariable=data_var, width=30)
    entrada_data.grid(row=1, column=1, **entry_opts)

    ttk.Label(frame, text="Exercício:").grid(row=2, column=0, sticky="w", **label_opts)
    exercicios = ["Supino", "Agachamento", "Levantamento Terra", "Remada Curvada", "Desenvolvimento", "Rosca Direta", "Tríceps Pulley", "Abdominal", "Corrida"]
    entrada_exercicio = ttk.Combobox(frame, values=exercicios, width=27)
    entrada_exercicio.grid(row=2, column=1, **entry_opts)
    entrada_exercicio.set("Supino")

    ttk.Label(frame, text="Séries:").grid(row=3, column=0, sticky="w", **label_opts)
    entrada_series = ttk.Entry(frame, width=30)
    entrada_series.grid(row=3, column=1, **entry_opts)

    ttk.Label(frame, text="Repetições:").grid(row=4, column=0, sticky="w", **label_opts)
    entrada_reps = ttk.Entry(frame, width=30)
    entrada_reps.grid(row=4, column=1, **entry_opts)

    ttk.Label(frame, text="Carga (kg):").grid(row=5, column=0, sticky="w", **label_opts)
    entrada_carga = ttk.Entry(frame, width=30)
    entrada_carga.grid(row=5, column=1, **entry_opts)

    ttk.Label(frame, text="Observações:").grid(row=6, column=0, sticky="nw", **label_opts) # Agora 'sticky="nw"' é o único valor para sticky
    texto_obs = tk.Text(frame, width=23, height=4, relief="solid", borderwidth=1, font=("Segoe UI", 10))
    texto_obs.grid(row=6, column=1, **entry_opts)

    # --- Botões ---
    frame_botoes = ttk.Frame(root)
    frame_botoes.pack(pady=20, padx=20, fill="x")
    frame_botoes.columnconfigure((0, 1), weight=1)

    btn_salvar = ttk.Button(frame_botoes, text="Salvar Treino", command=salvar_treino, style="TButton")
    btn_salvar.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=5, pady=(0, 10))

    btn_limpar = ttk.Button(frame_botoes, text="Limpar", command=limpar_campos, style="TButton")
    btn_limpar.grid(row=1, column=0, sticky="ew", padx=(0, 5), ipady=5)

    btn_ver = ttk.Button(frame_botoes, text="Ver Treinos", command=ver_treinos, style="TButton")
    btn_ver.grid(row=1, column=1, sticky="ew", padx=(5, 0), ipady=5)

    # Rodapé
    rodape = ttk.Label(root, text="FitSketch v0.2", font=("Segoe UI", 9), foreground="gray", anchor="center")
    rodape.pack(side="bottom", pady=10, fill="x")

if __name__ == "__main__":
    janela = tk.Tk()
    janela.title("FitSketch - Registro de Treino 🏋️")
    janela.geometry("420x600")
    janela.resizable(False, False)

    criar_interface_principal(janela)

    janela.mainloop()

    # Fecha a conexão com o banco ao sair
    conn.close()