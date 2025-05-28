import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from models import BancoDeDados
import matplotlib.pyplot as plt
import os

# --- Abstração e Herança ---


class BaseApp(ABC):
    def __init__(self, root):
        self._root = root
        self._root.title("Dashboard Financeiro Base")
        self._root.configure(bg="#f0f8ff")
        self._root.geometry("700x650")
        self._root.resizable(False, False)
        if os.path.exists("favicon.ico"):
            self._root.iconbitmap("favicon.ico")

        self._db = BancoDeDados()

        self._configurar_estilo()

        self.criar_widgets()
        self.atualizar_lista()

    def _configurar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",
                        rowheight=30,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#4CAF50",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.configure("TButton",
                        font=("Segoe UI", 10),
                        padding=8,
                        relief="flat",
                        background="#4CAF50",
                        foreground="white")
        style.map("TButton", background=[("active", "#45a049")])

    @abstractmethod
    def criar_widgets(self):
        """Método abstrato para criar widgets na interface."""

    @abstractmethod
    def atualizar_lista(self):
        """Método abstrato para atualizar a lista de transações."""

    @abstractmethod
    def mostrar_grafico(self):
        """Método abstrato para mostrar gráfico de despesas."""

# --- Classe concreta que herda da BaseApp ---


class App(BaseApp):
    def __init__(self, root):
        super().__init__(root)
        self._root.title("Dashboard Financeiro")

    def criar_widgets(self):
        tk.Label(self._root, text="Bem-vindo ao seu painel financeiro! Aqui você pode acompanhar suas entradas, saídas, categorias de gastos e gerar gráficos mensais automaticamente.",
                wraplength=680, font=("Arial", 10, "italic"), bg="#e6f2ff", fg="#333").pack(pady=5)

        label_titulo = tk.Label(self._root, text="\ud83d\udcb0 Dashboard Financeiro", font=(
            "Segoe UI", 20, "bold"), bg="#f0f8ff")
        label_titulo.pack(pady=10)

        frame_form = tk.Frame(self._root, bg="#f0f8ff", pady=10)
        frame_form.pack(pady=5)

        fields = [
            ("Tipo (Entrada/Saída):",
            ttk.Combobox(frame_form, values=["Entrada", "Saída"])),
            ("Categoria:", tk.Entry(frame_form)),
            ("Valor:", tk.Entry(frame_form)),
            ("Data (DD/MM/AAAA):", tk.Entry(frame_form)),
            ("Descrição:", tk.Entry(frame_form)),
        ]

        self._tipo_entry, self._categoria_entry, self._valor_entry, self._data_entry, self._descricao_entry = [
            f[1] for f in fields]

        for i, (label, widget) in enumerate(fields):
            tk.Label(frame_form, text=label, bg="#f0f8ff", font=("Segoe UI", 10)).grid(
                row=i, column=0, sticky="e", padx=5, pady=5)
            widget.grid(row=i, column=1, sticky="ew", padx=5, pady=5)

        frame_form.columnconfigure(1, weight=1)

        ttk.Button(frame_form, text="Adicionar", command=self.adicionar_transacao).grid(
            row=5, columnspan=2, pady=10, sticky="ew")
        ttk.Button(frame_form, text="Gráfico de Despesas", command=self.mostrar_grafico).grid(
            row=6, columnspan=2, pady=5, sticky="ew")
        ttk.Button(frame_form, text="Gráfico de Entradas", command=self.mostrar_grafico_entradas).grid(
            row=7, columnspan=2, pady=5, sticky="ew")
        ttk.Button(frame_form, text="Resumo Financeiro", command=self.mostrar_resumo).grid(
            row=8, columnspan=2, pady=5, sticky="ew")

        self._tree = ttk.Treeview(self._root, columns=(
            "tipo", "categoria", "valor", "data", "descricao"), show="headings")
        for col in self._tree["columns"]:
            self._tree.heading(col, text=col.capitalize())
        self._tree.pack(padx=10, pady=10, fill="both", expand=True)

    def adicionar_transacao(self):
        try:
            tipo = self._tipo_entry.get()
            categoria = self._categoria_entry.get()
            valor = float(self._valor_entry.get())
            data = self._data_entry.get()
            descricao = self._descricao_entry.get()

            self._db.inserir_transacao(tipo, categoria, valor, data, descricao)
            self.atualizar_lista()

            self._tipo_entry.set("")
            self._categoria_entry.delete(0, tk.END)
            self._valor_entry.delete(0, tk.END)
            self._data_entry.delete(0, tk.END)
            self._descricao_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Digite um número.")

    def atualizar_lista(self):
        for row in self._tree.get_children():
            self._tree.delete(row)

        for idx, transacao in enumerate(self._db.listar_transacoes()):
            tag = 'odd' if idx % 2 else 'even'
            self._tree.insert("", tk.END, values=transacao[1:], tags=(tag,))

        self._tree.tag_configure('odd', background='#f0f0ff')
        self._tree.tag_configure('even', background='#ffffff')

    # --- Polimorfismo: método sobrescrito ---

    def mostrar_grafico(self):
        transacoes = self._db.listar_transacoes()
        categorias = {}
        for t in transacoes:
            tipo, categoria, valor = t[1], t[2], t[3]
            if tipo == "Saída":
                categorias[categoria] = categorias.get(categoria, 0) + valor

        if categorias:
            fig, axs = plt.subplots(1, 2, figsize=(12, 5))
            axs[0].bar(categorias.keys(), categorias.values(), color='salmon')
            axs[0].set_title("Despesas por Categoria")
            axs[0].set_xlabel("Categoria")
            axs[0].set_ylabel("Total Gasto (R$)")
            axs[0].tick_params(axis='x', rotation=45)

            axs[1].pie(categorias.values(), labels=categorias.keys(),
                    autopct='%1.1f%%', startangle=140)
            axs[1].set_title("Distribuição Percentual de Despesas")

            plt.tight_layout()
            plt.show()
        else:
            messagebox.showinfo(
                "Info", "Nenhuma transação de saída para exibir no gráfico.")

    def mostrar_grafico_entradas(self):
        transacoes = self._db.listar_transacoes()
        categorias = {}
        for t in transacoes:
            tipo, categoria, valor = t[1], t[2], t[3]
            if tipo == "Entrada":
                categorias[categoria] = categorias.get(categoria, 0) + valor

        if categorias:
            fig, axs = plt.subplots(1, 2, figsize=(12, 5))
            axs[0].bar(categorias.keys(), categorias.values(),
                    color='lightgreen')
            axs[0].set_title("Entradas por Categoria")
            axs[0].set_xlabel("Categoria")
            axs[0].set_ylabel("Total Recebido (R$)")
            axs[0].tick_params(axis='x', rotation=45)

            axs[1].pie(categorias.values(), labels=categorias.keys(),
                    autopct='%1.1f%%', startangle=140)
            axs[1].set_title("Distribuição Percentual de Entradas")

            plt.tight_layout()
            plt.show()
        else:
            messagebox.showinfo(
                "Info", "Nenhuma transação de entrada para exibir no gráfico.")

    def mostrar_resumo(self):
        transacoes = self._db.listar_transacoes()
        total_entrada = sum(t[3] for t in transacoes if t[1] == "Entrada")
        total_saida = sum(t[3] for t in transacoes if t[1] == "Saída")

        if total_entrada + total_saida == 0:
            lucro_perc = despesa_perc = 0
        else:
            lucro_perc = (total_entrada - total_saida) / \
                total_entrada * 100 if total_entrada != 0 else 0
            despesa_perc = (total_saida / total_entrada) * \
                100 if total_entrada != 0 else 100

        msg = (
            f"Total Recebido: R$ {total_entrada:.2f}\n"
            f"Total Gasto: R$ {total_saida:.2f}\n"
            f"Lucro Líquido: R$ {total_entrada - total_saida:.2f}\n"
            f"% Lucro: {lucro_perc:.1f}%\n"
            f"% Despesas: {despesa_perc:.1f}%"
        )

        messagebox.showinfo("Resumo Financeiro", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
