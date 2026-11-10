"""Interface gráfica inicial do aplicativo inSPECT.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import queue
import threading
import math

TAGS_DURACAO = {
    "(0018,9073)": (0x0018, 0x9073),
    "(0018,9220)": (0x0018, 0x9220),
    "(0018,1242)": (0x0018, 0x1242),
    "(0018,1063)": (0x0018, 0x1063),
    "(0018,1065)": (0x0018, 0x1065),
    "(0011,100B)": (0x0011, 0x100B),
}

class AplicativoSPECT(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("inSPECT - Controle de Qualidade de Sistemas SPECT")
        self.geometry("1100x700")
        self.minsize(850, 550)

        pasta_app = os.path.dirname(os.path.abspath(__file__))
        self.diretorio_saida = tk.StringVar(
            value=os.path.join(pasta_app, "resultados")
        )

        self.tags_duracao_estatica = {
            tag: tk.BooleanVar(value=(tag == "(0018,1242)"))
            for tag in TAGS_DURACAO
        }
        self.tags_duracao_dinamica = {
            tag: tk.BooleanVar(value=(tag == "(0011,100B)"))
            for tag in TAGS_DURACAO
        }
        self.tag_duracao_estatica = "(0018,1242)"
        self.tag_duracao_dinamica = "(0011,100B)"

        self.pipeline_analise = None
        self._fila_resultados = queue.Queue()
        self._calculo_em_andamento = False
        self._figuras_por_painel = {}

        self._criar_estilos()
        self._criar_menu_superior()
        self._criar_conteudo()

    def _criar_estilos(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 11, "bold"))
        estilo.configure("Acao.TButton", font=("Segoe UI", 10, "bold"))

    def _criar_menu_superior(self):
        barra = ttk.Frame(self, padding=(12, 10))
        barra.pack(fill="x")
        ttk.Label(barra, text="inSPECT", font=("Segoe UI", 15, "bold")).pack(
            side="left", padx=(0, 25)
        )
        ttk.Button(barra, text="Configurações", command=self._configuracoes).pack(
            side="left", padx=4
        )
        ttk.Button(barra, text="Ajuda", command=self._ajuda).pack(side="left", padx=4)
        self.botao_nova_analise = ttk.Button(
            barra,
            text="Iniciar Nova Análise",
            command=self._voltar_para_entrada,
            state="disabled",
        )
        self.botao_nova_analise.pack(side="left", padx=4)
        ttk.Button(
            barra,
            text="Contato",
            command=self._mostrar_contato,
        ).pack(side="left", padx=4)

    def _criar_conteudo(self):
        principal = ttk.Frame(self, padding=(12, 0, 12, 12))
        principal.pack(fill="both", expand=True)
        principal.columnconfigure(0, weight=1)
        principal.columnconfigure(1, weight=2)
        principal.rowconfigure(0, weight=1)
        principal.rowconfigure(1, weight=1, uniform="aquisicoes")
        principal.rowconfigure(2, weight=1, uniform="aquisicoes")

        self.entrada_frame = ttk.LabelFrame(
            principal, text="Arquivos de aquisição", padding=12
        )
        entrada = self.entrada_frame
        entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        entrada.columnconfigure(1, weight=1)

        self.arquivo_estatico = self._campo_arquivo(
            entrada, "Arquivo Aquisição Estática", 0
        )
        self.arquivo_dinamico = self._campo_arquivo(
            entrada, "Arquivo Aquisição Dinâmica", 2
        )

        self.aquisicao_intrinseca = tk.BooleanVar(value=False)
        self.aquisicao_extrinseca = tk.BooleanVar(value=False)

        tipo_aquisicao = ttk.LabelFrame(
            entrada, text="Tipo de aquisição", padding=8
        )
        tipo_aquisicao.grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        ttk.Checkbutton(
            tipo_aquisicao,
            text="Aquisição Intrínseca",
            variable=self.aquisicao_intrinseca,
            command=self._atualizar_tipo_aquisicao,
        ).pack(anchor="w", pady=2)
        ttk.Checkbutton(
            tipo_aquisicao,
            text="Aquisição Extrínseca",
            variable=self.aquisicao_extrinseca,
            command=self._atualizar_tipo_aquisicao,
        ).pack(anchor="w", pady=2)

        opcoes = ttk.Frame(entrada)
        opcoes.grid(row=5, column=0, columnspan=2, sticky="w", pady=(14, 12))
        self.salvar_imagens = tk.BooleanVar(value=False)
        self.salvar_relatorio = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opcoes, text="Salvar Imagens", variable=self.salvar_imagens
        ).pack(anchor="w", pady=3)
        ttk.Checkbutton(
            opcoes, text="Salvar Relatório", variable=self.salvar_relatorio
        ).pack(anchor="w", pady=3)

        self.botao_calcular = ttk.Button(
            entrada,
            text="Calcular",
            style="Acao.TButton",
            command=self._calcular,
        )
        self.botao_calcular.grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(18, 0)
        )

        self.resultados_frame = ttk.LabelFrame(
            principal, text="Resultados", padding=10
        )
        resultados = self.resultados_frame
        resultados.grid(row=0, column=1, sticky="nsew")
        resultados.columnconfigure(0, weight=3, minsize=280)
        resultados.columnconfigure(1, weight=2)
        resultados.columnconfigure(2, weight=2)
        resultados.rowconfigure(1, weight=1)

        ttk.Label(resultados, text="Texto", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )

        texto_frame = ttk.Frame(resultados)
        texto_frame.grid(
            row=1, column=0, sticky="nsew", padx=(0, 8)
        )
        texto_frame.columnconfigure(0, weight=1)
        texto_frame.rowconfigure(0, weight=1)

        self.resultado_texto = tk.Text(
            texto_frame, width=38, wrap="word", state="disabled"
        )
        self.resultado_texto.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(
            texto_frame,
            orient="vertical",
            command=self.resultado_texto.yview,
        )
        barra.grid(row=0, column=1, sticky="ns")
        self.resultado_texto.configure(yscrollcommand=barra.set)

        self.area_imagem_estatica = self._criar_area_imagem(
            resultados, "Aquisição Estática", 1, 1
        )
        self.area_imagem_dinamica = self._criar_area_imagem(
            resultados, "Aquisição Dinâmica", 1, 2
        )

    def _campo_arquivo(self, pai, rotulo, linha):
        ttk.Label(pai, text=rotulo).grid(row=linha, column=0, columnspan=2, sticky="w")
        variavel = tk.StringVar()
        ttk.Entry(pai, textvariable=variavel).grid(
            row=linha + 1, column=0, sticky="ew", pady=(4, 14)
        )
        ttk.Button(
            pai, text="Procurar...", command=lambda: self._selecionar_arquivo(variavel)
        ).grid(row=linha + 1, column=1, padx=(6, 0), pady=(4, 14))
        return variavel

    def _criar_area_imagem(self, pai, titulo, linha, coluna=0):
        quadro = ttk.LabelFrame(pai, text=titulo, padding=6)
        quadro.grid(
            row=linha, column=coluna, sticky="nsew", pady=(0, 8)
        )
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)
        return quadro

    def _selecionar_arquivo(self, variavel):
        caminho_atual = variavel.get().strip()
        diretorio_inicial = (
            os.path.dirname(caminho_atual)
            if caminho_atual and os.path.isdir(os.path.dirname(caminho_atual))
            else os.getcwd()
        )

        caminho = filedialog.askopenfilename(
            parent=self,
            title="Selecionar arquivo de aquisição",
            initialdir=diretorio_inicial,
            filetypes=[
                ("Arquivos DICOM", "*.dcm *.dicom"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if caminho:
            variavel.set(caminho)

    def _configuracoes(self):
        janela = tk.Toplevel(self)
        janela.title("Configurações")
        janela.transient(self)
        janela.grab_set()

        for coluna in range(2):
            janela.columnconfigure(coluna, weight=1)

        ttk.Label(
            janela,
            text="Nome do diretório onde os dados serão salvos",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 4))

        ttk.Entry(janela, textvariable=self.diretorio_saida, width=55).grid(
            row=1, column=0, sticky="ew", padx=(12, 6), pady=(0, 12)
        )
        ttk.Button(
            janela,
            text="Procurar...",
            command=self._selecionar_diretorio_saida,
        ).grid(row=1, column=1, padx=(0, 12), pady=(0, 12))

        grupos = (
            (
                "Tag de Duração de Aquisição Estática",
                2,
                self.tags_duracao_estatica,
                "estatica",
            ),
            (
                "Tag de Duração de Aquisição Dinâmica",
                3,
                self.tags_duracao_dinamica,
                "dinamica",
            ),
        )

        for titulo, linha, variaveis, tipo in grupos:
            grupo = ttk.LabelFrame(janela, text=titulo, padding=8)
            grupo.grid(
                row=linha, column=0, columnspan=2, sticky="ew",
                padx=12, pady=(0, 8),
            )
            for tag, variavel in variaveis.items():
                ttk.Checkbutton(
                    grupo,
                    text=tag,
                    variable=variavel,
                    command=lambda t=tipo, k=tag, v=variavel:
                        self._selecionar_tag_duracao(t, k, v),
                ).pack(anchor="w")

        ttk.Button(janela, text="OK", command=janela.destroy).grid(
            row=4, column=0, columnspan=2, pady=(0, 12)
        )

    def _selecionar_tag_duracao(self, tipo, tag_selecionada, variavel):
        # Mantém exatamente uma checkbox marcada em cada grupo.
        if not variavel.get():
            variavel.set(True)
            return

        if tipo == "estatica":
            variaveis = self.tags_duracao_estatica
            self.tag_duracao_estatica = tag_selecionada
        elif tipo == "dinamica":
            variaveis = self.tags_duracao_dinamica
            self.tag_duracao_dinamica = tag_selecionada
        else:
            return

        for tag, outra_variavel in variaveis.items():
            outra_variavel.set(tag == tag_selecionada)

    def _selecionar_diretorio_saida(self):
        pasta = filedialog.askdirectory(
            title="Selecionar diretório de saída",
            initialdir=self.diretorio_saida.get() or os.getcwd(),
        )
        if pasta:
            self.diretorio_saida.set(pasta)

    def _ajuda(self):
        janela = tk.Toplevel(self)
        janela.title("Ajuda")
        janela.transient(self)
        janela.grab_set()
        janela.resizable(False, False)

        ttk.Label(
            janela,
            text=(
                "Instruções de uso\n\n"
                "1. Com base na marca e no modelo do equipamento SPECT, "
                "selecione a tag que armazena a duração da aquisição do exame "
                "em Configurações > Tags.\n\n"
                "2. Selecione os arquivos das aquisições estática e dinâmica. "
                "Digite o caminho do arquivo ou use o botão Procurar.\n\n"
                "3. Marque Aquisição Intrínseca (sem colimador) ou "
                "Aquisição Extrínseca (com colimador).\n\n"
                "4. Escolha se deseja salvar as imagens e o relatório. "
                "O diretório de saída pode ser definido em Configurações.\n\n"
                "5. Clique em Calcular.\n\n"
                "6. Para realizar outra análise, clique em "
                "“Iniciar Nova Análise” no menu superior."
            ),
            justify="left",
            wraplength=520,
            padding=16,
        ).pack(fill="both", expand=True)

        ttk.Button(
            janela, text="Fechar", command=janela.destroy
        ).pack(pady=(0, 12))
    
    def _mostrar_contato(self):
        janela = tk.Toplevel(self)
        janela.title("Contato")
        janela.transient(self)
        janela.grab_set()
        janela.resizable(False, False)

        ttk.Label(
            janela,
            text=(
                "Aplicativo desenvolvido por Emilie Chen para projeto de "
                "Iniciação Científica da Universidade Federal do ABC, "
                "São Bernardo do Campo, Brasil.\n\n"
                "Envie feedback e bugs para:\n"
                "inspect.cq@gmail.com"
            ),
            justify="left",
            wraplength=420,
            padding=16,
        ).pack(fill="both", expand=True)

        ttk.Button(janela, text="Fechar", command=janela.destroy).pack(
            pady=(0, 12)
        )

    def _atualizar_tipo_aquisicao(self):
        if self.aquisicao_intrinseca.get():
            self.aquisicao_extrinseca.set(False)
            self.pipeline_analise = "run_analysis_pipeline_intrinsico"
        elif self.aquisicao_extrinseca.get():
            self.aquisicao_intrinseca.set(False)
            self.pipeline_analise = "run_analysis_pipeline_extrinsico"
        else:
            self.pipeline_analise = None

    def _calcular(self):
        if self._calculo_em_andamento:
            return

        pipeline = self.pipeline_analise
        if pipeline is None:
            self._definir_texto(
                "Selecione Aquisição Intrínsica ou Aquisição Extrínsica."
            )
            return

        caminho_estatico = self.arquivo_estatico.get().strip()
        caminho_dinamico = self.arquivo_dinamico.get().strip()

        if not caminho_estatico and not caminho_dinamico:
            self._definir_texto("Selecione pelo menos um arquivo DICOM.")
            return

        for nome, caminho in (
            ("Aquisição Estática", caminho_estatico),
            ("Aquisição Dinâmica", caminho_dinamico),
        ):
            if caminho and not os.path.isfile(caminho):
                self._definir_texto(f"Arquivo não encontrado ({nome}): {caminho}")
                return

        self._calculo_em_andamento = True
        self.botao_calcular.configure(state="disabled")
        self._definir_texto("Processando aquisições...")
        self.update_idletasks()

        argumentos = (
            pipeline,
            caminho_estatico,
            caminho_dinamico,
            self.salvar_imagens.get(),
            self.salvar_relatorio.get(),
            self.diretorio_saida.get().strip(),
            TAGS_DURACAO[self.tag_duracao_estatica],
            TAGS_DURACAO[self.tag_duracao_dinamica],
        )
        threading.Thread(
            target=self._executar_calculo,
            args=argumentos,
            daemon=True,
        ).start()
        self.after(100, self._verificar_resultado)

    def _executar_calculo(
        self, pipeline, caminho_estatico, caminho_dinamico,
        salvar_imagens, salvar_relatorio, output_dir,
        tag_duracao_estatica, tag_duracao_dinamica
    ):
        try:
            import funções_para_app as funcoes

            funcao = getattr(funcoes, pipeline, None)
            if funcao is None:
                raise AttributeError(f"A função {pipeline} não foi encontrada.")

            textos = []
            figuras = []

            for nome, caminho in (
                ("Aquisição Estática", caminho_estatico),
                ("Aquisição Dinâmica", caminho_dinamico),
            ):
                if not caminho:
                    figuras.append((None, None))
                    continue

                try:
                    resultado = funcao(
                        caminho,
                        save_images=salvar_imagens,
                        save_report=salvar_relatorio,
                        output_dir=output_dir,
                    )
                    if not resultado or resultado[0] is None:
                        figuras.append((None, None))
                        textos.append(f"{nome}: nenhum pixel válido foi encontrado.")
                        continue

                    indice = 2 if pipeline == "run_analysis_pipeline_intrinsico" else 3
                    figuras.append(resultado[indice])
                    textos.append(f"{nome}: análise concluída.")
                except Exception as erro:
                    figuras.append((None, None))
                    textos.append(f"{nome}: erro na análise — {erro}")

            if caminho_estatico and caminho_dinamico:
                pipeline_tempo = getattr(
                    funcoes, "pipeline_temporzacao", None
                )
                if pipeline_tempo is None:
                    textos.append("Teste de temporização: função não encontrada.")
                else:
                    try:
                        texto_tempo = pipeline_tempo(
                            caminho_estatico,
                            caminho_dinamico,
                            save_report=salvar_relatorio,
                            output_dir=output_dir,
                            tag_duracao_estatica=tag_duracao_estatica,
                            tag_duracao_dinamica=tag_duracao_dinamica,
                        )
                        textos.extend(
                            ["Teste de temporização:", str(texto_tempo)]
                        )
                    except Exception as erro:
                        textos.append(
                            f"Erro no teste de temporização: {erro}"
                        )
            else:
                textos.append(
                    "O teste de temporização precisa de uma aquisição "
                    "estática e uma aquisição dinâmica"
                )

            self._fila_resultados.put(("\n\n".join(textos), figuras))
        except Exception as erro:
            self._fila_resultados.put(
                (f"Erro ao executar a análise: {erro}", [(None, None), (None, None)])
            )

    def _voltar_para_entrada(self):
        self._mostrar_figuras(self.area_imagem_estatica, None)
        self._mostrar_figuras(self.area_imagem_dinamica, None)
        self._definir_texto("")

        self.arquivo_estatico.set("")
        self.arquivo_dinamico.set("")

        self.resultados_frame.grid_configure(column=1, columnspan=1)
        self.entrada_frame.grid()
        self.botao_nova_analise.configure(state="disabled")

    def _verificar_resultado(self):
        try:
            texto, figuras = self._fila_resultados.get_nowait()
        except queue.Empty:
            self.after(100, self._verificar_resultado)
            return

        try:
            self._mostrar_figuras(self.area_imagem_estatica, figuras[0])
            self._mostrar_figuras(self.area_imagem_dinamica, figuras[1])
        except Exception as erro:
            texto += f"\nErro ao exibir as imagens: {erro}"
        finally:
            self._definir_texto(texto)
            self._calculo_em_andamento = False
            self.botao_calcular.configure(state="normal")
            self.botao_nova_analise.configure(state="normal")
            self.entrada_frame.grid_remove()
            self.resultados_frame.grid_configure(column=0, columnspan=2)

    def _mostrar_figuras(self, painel, figuras):
        for figura in self._figuras_por_painel.pop(painel, []):
            plt.close(figura)

        for widget in painel.winfo_children():
            widget.destroy()

        if not figuras:
            ttk.Label(painel, text="Nenhuma imagem disponível.", anchor="center").pack(
                fill="both", expand=True
            )
            return

        titulos = ("Histograma", "Phantom / ROI")
        disponiveis = []
        if len(figuras) > 1 and figuras[1] is not None:
            disponiveis.append(("Phantom / ROI", figuras[1]))
        if figuras[0] is not None:
            disponiveis.append(("Histograma", figuras[0]))

        if not disponiveis:
            ttk.Label(
                painel, text="Nenhuma imagem disponível.", anchor="center"
            ).pack(fill="both", expand=True)
            return

        figuras_ativas = []
        for titulo, figura in disponiveis:
            subpainel = ttk.LabelFrame(painel, text=titulo, padding=2)
            subpainel.pack(fill="both", expand=True, side="top", pady=2)

            figura.set_size_inches(6.4, 2.5, forward=True)
            canvas = FigureCanvasTkAgg(figura, master=subpainel)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            figuras_ativas.append(figura)

        self._figuras_por_painel[painel] = figuras_ativas

    def _definir_texto(self, texto):
        self.resultado_texto.configure(state="normal")
        self.resultado_texto.delete("1.0", "end")
        self.resultado_texto.insert("1.0", texto)
        self.resultado_texto.configure(state="disabled")        

if __name__ == "__main__":
    AplicativoSPECT().mainloop()
