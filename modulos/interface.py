from datetime import datetime
import customtkinter as ctk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from tkinter import filedialog

from modulos.persistencia import carregar_dados, salvar_dados


# =========================
# CONFIGURAÇÕES
# =========================

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

SENHA_RESPONSAVEL = "1234"
responsavel_autorizado = False


# =========================
# CORES
# =========================

COR_PRINCIPAL = ("#2563EB", "#3B82F6")
COR_PRINCIPAL_HOVER = ("#1D4ED8", "#2563EB")

COR_FUNDO = ("#F4F6F8", "#111827")
COR_CARD = ("#FFFFFF", "#1F2937")

COR_TEXTO = ("#1F2937", "#F9FAFB")
COR_TEXTO_SECUNDARIO = ("#6B7280", "#9CA3AF")

COR_BORDA = ("#E5E7EB", "#374151")
COR_HOVER = ("#EFF6FF", "#374151")

COR_PENDENTE = ("#F59E0B", "#FBBF24")
COR_RESOLVIDA = ("#16A34A", "#22C55E")
COR_ERRO = ("#DC2626", "#F87171")

COR_NEUTRO = ("#E5E7EB", "#374151")
COR_NEUTRO_HOVER = ("#D1D5DB", "#4B5563")
COR_NEUTRO_TEXTO = ("#1F2937", "#F9FAFB")


# =========================
# FUNÇÕES
# =========================

def mudar_tema(novo_tema):
    ctk.set_appearance_mode(novo_tema)


def gerar_id(dados):
    maior_id = 0

    for item in dados:
        id_item = item.get("id", "")

        if id_item.startswith("PEN-"):
            try:
                numero = int(id_item.replace("PEN-", ""))
                if numero > maior_id:
                    maior_id = numero
            except ValueError:
                pass

    return f"PEN-{maior_id + 1:03d}"


def cadastrar():
    produto = entrada_produto.get().strip()
    operador = entrada_operador.get().strip()
    natureza = entrada_natureza.get().strip()

    if not produto or not operador or not natureza:
        resultado_cadastro.configure(
            text="Preencha todos os campos.",
            text_color=COR_ERRO
        )
        return

    dados = carregar_dados()

    agora = datetime.now()

    nova_pendencia = {
        "id": gerar_id(dados),
        "produto": produto,
        "operador": operador,
        "natureza": natureza,
        "data": agora.strftime("%d/%m/%Y"),
        "hora": agora.strftime("%H:%M:%S"),
        "status": "Pendente"
    }

    dados.append(nova_pendencia)

    if salvar_dados(dados):
        resultado_cadastro.configure(
            text=f"Pendência {nova_pendencia['id']} cadastrada com sucesso!",
            text_color=COR_RESOLVIDA
        )

        entrada_produto.delete(0, "end")
        entrada_operador.delete(0, "end")
        entrada_natureza.delete(0, "end")

        atualizar_resumo()
    else:
        resultado_cadastro.configure(
            text="Erro ao salvar a pendência.",
            text_color=COR_ERRO
        )


def resolver():
    id_resolver = entrada_id_resolver.get().strip().upper()

    if not id_resolver:
        resultado_resolver.configure(
            text="Digite o ID da pendência.",
            text_color=COR_ERRO
        )
        return

    dados = carregar_dados()

    encontrou = False

    for item in dados:
        if item.get("id", "").upper() == id_resolver:
            encontrou = True

            if item.get("status") == "Resolvida":
                resultado_resolver.configure(
                    text="Essa pendência já está resolvida.",
                    text_color=COR_PENDENTE
                )
                return

            item["status"] = "Resolvida"

            if salvar_dados(dados):
                resultado_resolver.configure(
                    text=f"Pendência {id_resolver} resolvida com sucesso!",
                    text_color=COR_RESOLVIDA
                )

                entrada_id_resolver.delete(0, "end")
                atualizar_resumo()
            else:
                resultado_resolver.configure(
                    text="Erro ao salvar a alteração.",
                    text_color=COR_ERRO
                )

            return

    if not encontrou:
        resultado_resolver.configure(
            text="Pendência não encontrada.",
            text_color=COR_ERRO
        )


def buscar():
    termo = entrada_busca.get().strip().lower()

    dados = carregar_dados()

    caixa_consulta.configure(state="normal")
    caixa_consulta.delete("1.0", "end")

    resultados = []

    for item in dados:
        campos = [
            str(item.get("id", "")),
            str(item.get("produto", "")),
            str(item.get("operador", "")),
            str(item.get("natureza", "")),
            str(item.get("status", ""))
        ]

        if not termo or any(termo in campo.lower() for campo in campos):
            resultados.append(item)

    if not resultados:
        caixa_consulta.insert(
            "end",
            "Nenhuma pendência encontrada."
        )
    else:
        for item in resultados:
            caixa_consulta.insert(
                "end",
                f"ID: {item.get('id', '')}\n"
                f"Produto: {item.get('produto', '')}\n"
                f"Operador: {item.get('operador', '')}\n"
                f"Natureza: {item.get('natureza', '')}\n"
                f"Data: {item.get('data', '')}\n"
                f"Hora: {item.get('hora', '')}\n"
                f"Status: {item.get('status', '')}\n"
                f"{'-' * 50}\n"
            )

    caixa_consulta.configure(state="disabled")


def atualizar_resumo():
    dados = carregar_dados()

    total = len(dados)
    pendentes = sum(
        1 for item in dados
        if item.get("status") == "Pendente"
    )
    resolvidas = sum(
        1 for item in dados
        if item.get("status") == "Resolvida"
    )

    lbl_total.configure(text=str(total))
    lbl_pendentes.configure(text=str(pendentes))
    lbl_resolvidas.configure(text=str(resolvidas))


def exportar_pdf():
    dados = carregar_dados()

    if not dados:
        resultado_exportacao.configure(
            text="Não há dados para exportar.",
            text_color=COR_ERRO
        )
        return

    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Arquivo PDF", "*.pdf")]
    )

    if not caminho:
        return

    try:
        arquivo_pdf = canvas.Canvas(caminho, pagesize=A4)

        largura, altura = A4
        y = altura - 50

        arquivo_pdf.setFont("Helvetica-Bold", 16)
        arquivo_pdf.drawString(
            50,
            y,
            "SCPP - CONTROLE DE PENDÊNCIAS"
        )

        y -= 35

        arquivo_pdf.setFont("Helvetica", 10)

        for item in dados:

            texto = (
                f"ID: {item.get('id', '')} | "
                f"Produto: {item.get('produto', '')} | "
                f"Operador: {item.get('operador', '')}"
            )

            arquivo_pdf.drawString(50, y, texto)
            y -= 15

            arquivo_pdf.drawString(
                50,
                y,
                f"Natureza: {item.get('natureza', '')} | "
                f"Data: {item.get('data', '')} | "
                f"Hora: {item.get('hora', '')}"
            )

            y -= 15

            arquivo_pdf.drawString(
                50,
                y,
                f"Status: {item.get('status', '')}"
            )

            y -= 25

            if y < 60:
                arquivo_pdf.showPage()
                y = altura - 50
                arquivo_pdf.setFont("Helvetica", 10)

        arquivo_pdf.save()

        resultado_exportacao.configure(
            text="PDF exportado com sucesso!",
            text_color=COR_RESOLVIDA
        )

    except Exception:
        resultado_exportacao.configure(
            text="Erro ao exportar PDF.",
            text_color=COR_ERRO
        )


def exportar_excel():
    dados = carregar_dados()

    if not dados:
        resultado_exportacao.configure(
            text="Não há dados para exportar.",
            text_color=COR_ERRO
        )
        return

    caminho = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Arquivo Excel", "*.xlsx")]
    )

    if not caminho:
        return

    try:
        planilha = Workbook()
        aba = planilha.active
        aba.title = "Pendências"

        cabecalho = [
            "ID",
            "Produto",
            "Operador",
            "Natureza",
            "Data",
            "Hora",
            "Status"
        ]

        aba.append(cabecalho)

        for item in dados:
            aba.append([
                item.get("id", ""),
                item.get("produto", ""),
                item.get("operador", ""),
                item.get("natureza", ""),
                item.get("data", ""),
                item.get("hora", ""),
                item.get("status", "")
            ])

        planilha.save(caminho)

        resultado_exportacao.configure(
            text="Excel exportado com sucesso!",
            text_color=COR_RESOLVIDA
        )

    except Exception:
        resultado_exportacao.configure(
            text="Erro ao exportar Excel.",
            text_color=COR_ERRO
        )


def verificar_senha():
    global responsavel_autorizado

    senha = campo_senha.get()

    if senha == SENHA_RESPONSAVEL:
        responsavel_autorizado = True

        janela_senha.destroy()
        mostrar_tela(tela_resolver)

    else:
        mensagem_senha.configure(
            text="Senha incorreta.",
            text_color=COR_ERRO
        )


def abrir_resolver():
    global janela_senha
    global campo_senha
    global mensagem_senha

    if responsavel_autorizado:
        mostrar_tela(tela_resolver)
        return

    janela_senha = ctk.CTkToplevel(janela)
    janela_senha.title("Acesso do responsável")
    janela_senha.geometry("350x220")
    janela_senha.resizable(False, False)

    titulo_senha = ctk.CTkLabel(
        janela_senha,
        text="Acesso do responsável",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    titulo_senha.pack(pady=(25, 15))

    campo_senha = ctk.CTkEntry(
        janela_senha,
        placeholder_text="Digite a senha",
        show="*",
        width=250
    )
    campo_senha.pack(pady=10)

    botao_senha = ctk.CTkButton(
        janela_senha,
        text="Entrar",
        command=verificar_senha,
        fg_color=COR_PRINCIPAL,
        hover_color=COR_PRINCIPAL_HOVER
    )
    botao_senha.pack(pady=10)

    mensagem_senha = ctk.CTkLabel(
        janela_senha,
        text=""
    )
    mensagem_senha.pack()


def mostrar_tela(tela):
    tela_cadastro.pack_forget()
    tela_consulta.pack_forget()
    tela_resolver.pack_forget()

    tela.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )


# =========================
# JANELA PRINCIPAL
# =========================

janela = ctk.CTk()

janela.title("PENDENCY CONTROL - Dashboard")
janela.geometry("1100x650")
janela.minsize(950, 600)

janela.configure(fg_color=COR_FUNDO)


# =========================
# SIDEBAR
# =========================

sidebar = ctk.CTkFrame(
    janela,
    width=210,
    corner_radius=0,
    fg_color=COR_CARD,
    border_width=1,
    border_color=COR_BORDA
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


logo = ctk.CTkLabel(
    sidebar,
    text="SCPP",
    font=ctk.CTkFont(
        size=32,
        weight="bold"
    ),
    text_color=COR_PRINCIPAL
)

logo.pack(pady=(35, 5))


logo_subtitulo = ctk.CTkLabel(
    sidebar,
    text="CONTROLE DE\nPENDÊNCIAS",
    font=ctk.CTkFont(
        size=12,
        weight="bold"
    ),
    text_color=COR_TEXTO_SECUNDARIO
)

logo_subtitulo.pack(pady=(0, 35))


botao_cadastro = ctk.CTkButton(
    sidebar,
    text="CADASTRAR",
    height=42,
    command=lambda: mostrar_tela(tela_cadastro),
    fg_color=COR_PRINCIPAL,
    hover_color=COR_PRINCIPAL_HOVER
)

botao_cadastro.pack(
    fill="x",
    padx=20,
    pady=6
)


botao_consulta = ctk.CTkButton(
    sidebar,
    text="CONSULTAR",
    height=42,
    command=lambda: mostrar_tela(tela_consulta),
    fg_color=COR_NEUTRO,
    hover_color=COR_NEUTRO_HOVER,
    text_color=COR_NEUTRO_TEXTO
)

botao_consulta.pack(
    fill="x",
    padx=20,
    pady=6
)


botao_resolver = ctk.CTkButton(
    sidebar,
    text="RESOLVER",
    height=42,
    command=abrir_resolver,
    fg_color=COR_NEUTRO,
    hover_color=COR_NEUTRO_HOVER,
    text_color=COR_NEUTRO_TEXTO
)

botao_resolver.pack(
    fill="x",
    padx=20,
    pady=6
)


# =========================
# ÁREA CENTRAL
# =========================

area_principal = ctk.CTkFrame(
    janela,
    fg_color=COR_FUNDO,
    corner_radius=0
)

area_principal.pack(
    side="left",
    fill="both",
    expand=True
)


# =========================
# CABEÇALHO
# =========================

cabecalho = ctk.CTkFrame(
    area_principal,
    fg_color="transparent"
)

cabecalho.pack(
    fill="x",
    padx=25,
    pady=(20, 5)
)


titulo = ctk.CTkLabel(
    cabecalho,
    text="PENDENCY CONTROL",
    font=ctk.CTkFont(
        size=26,
        weight="bold"
    ),
    text_color=COR_TEXTO
)

titulo.pack(side="left")


subtitulo = ctk.CTkLabel(
    cabecalho,
    text="Sistema de Controle de Pendências",
    font=ctk.CTkFont(size=13),
    text_color=COR_TEXTO_SECUNDARIO
)

subtitulo.pack(
    side="left",
    padx=15,
    pady=(8, 0)
)


seletor_tema = ctk.CTkOptionMenu(
    cabecalho,
    values=["Light", "Dark", "System"],
    command=mudar_tema,
    width=100
)

seletor_tema.set("Light")

seletor_tema.pack(side="right")


# =========================
# ÁREA DE CONTEÚDO
# =========================

conteudo = ctk.CTkFrame(
    area_principal,
    fg_color="transparent"
)

conteudo.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=15
)


# =========================
# TELA CADASTRO
# =========================

tela_cadastro = ctk.CTkFrame(
    conteudo,
    fg_color=COR_CARD,
    corner_radius=12,
    border_width=1,
    border_color=COR_BORDA
)


titulo_cadastro = ctk.CTkLabel(
    tela_cadastro,
    text="Cadastrar Pendência",
    font=ctk.CTkFont(
        size=22,
        weight="bold"
    ),
    text_color=COR_TEXTO
)

titulo_cadastro.pack(
    anchor="w",
    padx=30,
    pady=(30, 20)
)


entrada_produto = ctk.CTkEntry(
    tela_cadastro,
    placeholder_text="Produto",
    height=40
)

entrada_produto.pack(
    fill="x",
    padx=30,
    pady=8
)


entrada_operador = ctk.CTkEntry(
    tela_cadastro,
    placeholder_text="Operador",
    height=40
)

entrada_operador.pack(
    fill="x",
    padx=30,
    pady=8
)


entrada_natureza = ctk.CTkEntry(
    tela_cadastro,
    placeholder_text="Natureza da pendência",
    height=40
)

entrada_natureza.pack(
    fill="x",
    padx=30,
    pady=8
)


botao_cadastrar = ctk.CTkButton(
    tela_cadastro,
    text="CADASTRAR PENDÊNCIA",
    height=42,
    command=cadastrar,
    fg_color=COR_PRINCIPAL,
    hover_color=COR_PRINCIPAL_HOVER
)

botao_cadastrar.pack(
    padx=30,
    pady=(20, 10)
)


resultado_cadastro = ctk.CTkLabel(
    tela_cadastro,
    text="",
    font=ctk.CTkFont(size=13)
)

resultado_cadastro.pack(
    padx=30,
    pady=10
)


# =========================
# TELA CONSULTA
# =========================

tela_consulta = ctk.CTkFrame(
    conteudo,
    fg_color=COR_CARD,
    corner_radius=12,
    border_width=1,
    border_color=COR_BORDA
)


titulo_consulta = ctk.CTkLabel(
    tela_consulta,
    text="Consultar Pendências",
    font=ctk.CTkFont(
        size=22,
        weight="bold"
    ),
    text_color=COR_TEXTO
)

titulo_consulta.pack(
    anchor="w",
    padx=30,
    pady=(30, 15)
)


entrada_busca = ctk.CTkEntry(
    tela_consulta,
    placeholder_text="Digite ID, produto, operador, natureza ou status",
    height=40
)

entrada_busca.pack(
    fill="x",
    padx=30,
    pady=8
)


botao_buscar = ctk.CTkButton(
    tela_consulta,
    text="BUSCAR",
    height=40,
    command=buscar,
    fg_color=COR_PRINCIPAL,
    hover_color=COR_PRINCIPAL_HOVER
)

botao_buscar.pack(
    padx=30,
    pady=10
)


caixa_consulta = ctk.CTkTextbox(
    tela_consulta,
    height=350,
    fg_color=COR_FUNDO,
    text_color=COR_TEXTO
)

caixa_consulta.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(10, 30)
)

caixa_consulta.configure(state="disabled")


# =========================
# TELA RESOLVER
# =========================

tela_resolver = ctk.CTkFrame(
    conteudo,
    fg_color=COR_CARD,
    corner_radius=12,
    border_width=1,
    border_color=COR_BORDA
)


titulo_resolver = ctk.CTkLabel(
    tela_resolver,
    text="Resolver Pendência",
    font=ctk.CTkFont(
        size=22,
        weight="bold"
    ),
    text_color=COR_TEXTO
)

titulo_resolver.pack(
    anchor="w",
    padx=30,
    pady=(30, 15)
)


entrada_id_resolver = ctk.CTkEntry(
    tela_resolver,
    placeholder_text="Digite o ID da pendência (ex.: PEN-001)",
    height=40
)

entrada_id_resolver.pack(
    fill="x",
    padx=30,
    pady=8
)


botao_resolver_pendencia = ctk.CTkButton(
    tela_resolver,
    text="RESOLVER PENDÊNCIA",
    height=42,
    command=resolver,
    fg_color=COR_RESOLVIDA,
    hover_color=("#15803D", "#16A34A")
)

botao_resolver_pendencia.pack(
    padx=30,
    pady=15
)


resultado_resolver = ctk.CTkLabel(
    tela_resolver,
    text="",
    font=ctk.CTkFont(size=13)
)

resultado_resolver.pack(
    padx=30,
    pady=10
)


# =========================
# PAINEL DE RESUMO
# =========================

painel_resumo = ctk.CTkFrame(
    janela,
    width=190,
    corner_radius=0,
    fg_color=COR_CARD,
    border_width=1,
    border_color=COR_BORDA
)

painel_resumo.pack(
    side="right",
    fill="y"
)

painel_resumo.pack_propagate(False)


titulo_resumo = ctk.CTkLabel(
    painel_resumo,
    text="RESUMO",
    font=ctk.CTkFont(
        size=18,
        weight="bold"
    ),
    text_color=COR_TEXTO
)

titulo_resumo.pack(pady=(35, 25))


# Total

ctk.CTkLabel(
    painel_resumo,
    text="TOTAL",
    font=ctk.CTkFont(
        size=11,
        weight="bold"
    ),
    text_color=COR_TEXTO_SECUNDARIO
).pack(pady=(5, 0))


lbl_total = ctk.CTkLabel(
    painel_resumo,
    text="0",
    font=ctk.CTkFont(
        size=28,
        weight="bold"
    ),
    text_color=COR_TEXTO
)

lbl_total.pack(pady=(0, 20))


# Pendentes

ctk.CTkLabel(
    painel_resumo,
    text="PENDENTES",
    font=ctk.CTkFont(
        size=11,
        weight="bold"
    ),
    text_color=COR_PENDENTE
).pack(pady=(5, 0))


lbl_pendentes = ctk.CTkLabel(
    painel_resumo,
    text="0",
    font=ctk.CTkFont(
        size=28,
        weight="bold"
    ),
    text_color=COR_PENDENTE
)

lbl_pendentes.pack(pady=(0, 20))


# Resolvidas

ctk.CTkLabel(
    painel_resumo,
    text="RESOLVIDAS",
    font=ctk.CTkFont(
        size=11,
        weight="bold"
    ),
    text_color=COR_RESOLVIDA
).pack(pady=(5, 0))


lbl_resolvidas = ctk.CTkLabel(
    painel_resumo,
    text="0",
    font=ctk.CTkFont(
        size=28,
        weight="bold"
    ),
    text_color=COR_RESOLVIDA
)

lbl_resolvidas.pack(pady=(0, 25))


# =========================
# EXPORTAÇÃO
# =========================

ctk.CTkLabel(
    painel_resumo,
    text="EXPORTAR",
    font=ctk.CTkFont(
        size=11,
        weight="bold"
    ),
    text_color=COR_TEXTO_SECUNDARIO
).pack(pady=(10, 8))


botao_pdf = ctk.CTkButton(
    painel_resumo,
    text="PDF",
    height=36,
    command=exportar_pdf,
    fg_color=COR_NEUTRO,
    hover_color=COR_NEUTRO_HOVER,
    text_color=COR_NEUTRO_TEXTO
)

botao_pdf.pack(
    fill="x",
    padx=20,
    pady=5
)


botao_excel = ctk.CTkButton(
    painel_resumo,
    text="EXCEL",
    height=36,
    command=exportar_excel,
    fg_color=COR_NEUTRO,
    hover_color=COR_NEUTRO_HOVER,
    text_color=COR_NEUTRO_TEXTO
)

botao_excel.pack(
    fill="x",
    padx=20,
    pady=5
)


resultado_exportacao = ctk.CTkLabel(
    painel_resumo,
    text="",
    wraplength=150,
    font=ctk.CTkFont(size=11)
)

resultado_exportacao.pack(
    padx=15,
    pady=10
)


# =========================
# ATALHOS DO TECLADO
# =========================

janela.bind(
    "<Control-Return>",
    lambda event: cadastrar()
)

janela.bind(
    "<Escape>",
    lambda event: mostrar_tela(tela_cadastro)
)


# =========================
# INICIALIZAÇÃO
# =========================

mostrar_tela(tela_cadastro)
atualizar_resumo()


def iniciar_programa():
    janela.mainloop()
