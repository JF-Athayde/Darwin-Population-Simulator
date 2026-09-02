import os
import math
import shutil
import tempfile
from collections import Counter, defaultdict
from html import escape

import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    KeepTogether
)


# ============================================================
# CONFIGURAÇÃO VISUAL
# ============================================================

LARGURA, ALTURA = A4

AZUL = colors.HexColor("#163A5F")
AZUL_ESCURO = colors.HexColor("#0E2942")
AZUL_CLARO = colors.HexColor("#EAF2F8")

VERDE = colors.HexColor("#2E7D5B")
VERDE_CLARO = colors.HexColor("#E8F5EE")

VERMELHO = colors.HexColor("#B84242")
VERMELHO_CLARO = colors.HexColor("#FBECEC")

AMARELO = colors.HexColor("#C99A2E")
AMARELO_CLARO = colors.HexColor("#FFF7DF")

CINZA = colors.HexColor("#F3F5F7")
CINZA_ESCURO = colors.HexColor("#D9DEE3")
CINZA_TEXTO = colors.HexColor("#56616B")

PRETO = colors.HexColor("#20252A")
BRANCO = colors.white


# ============================================================
# CONSTANTES DO MODELO SOCIAL
# ============================================================

PILARES = [
    ("Respeito", "respeito"),
    ("Cidadania", "cidadania"),
    ("Responsabilidade", "responsabilidade"),
    ("Zelo", "zelo"),
    ("Justiça", "justica"),
    ("Sinceridade", "sinceridade"),
]

ACOES = [
    "agir_corretamente",
    "ajudar",
    "ignorar",
    "agir_incorretamente",
]

ACOES_NOMES = {
    "agir_corretamente": "Agir corretamente",
    "ajudar": "Ajudar",
    "ignorar": "Ignorar",
    "agir_incorretamente": "Agir incorretamente",
}

INTERACOES = [
    "positiva",
    "neutra",
    "conflito",
]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def numero(valor, padrao=0.0):
    """
    Converte qualquer valor para float sem quebrar o relatório.
    """
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


def obter(objeto, atributo, padrao=None):
    """
    Obtém um atributo com segurança.
    """
    return getattr(objeto, atributo, padrao)


def chamar(objeto, metodo, padrao=None, *args, **kwargs):
    """
    Executa um método caso ele exista.
    """
    funcao = getattr(objeto, metodo, None)

    if not callable(funcao):
        return padrao

    try:
        return funcao(*args, **kwargs)
    except Exception:
        return padrao


def texto(valor, padrao="Não informado"):
    if valor is None:
        return padrao

    return str(valor)


def texto_seguro(valor, padrao="Não informado"):
    """
    Escapa caracteres que poderiam quebrar Paragraph do ReportLab.
    """
    return escape(texto(valor, padrao))


def limitar(valor, minimo=0, maximo=100):
    return max(
        minimo,
        min(maximo, numero(valor))
    )


# ============================================================
# POPULAÇÃO
# ============================================================

def obter_individuos(population):
    individuos = obter(
        population,
        "individuals",
        []
    )

    if individuos is None:
        return []

    return list(individuos)


# ============================================================
# PILARES
# ============================================================

def obter_pilar(individuo, atributo):
    """
    Obtém um dos seis pilares.
    """
    return limitar(
        obter(
            individuo,
            atributo,
            0
        )
    )


def obter_pilares(individuo):
    """
    Retorna os seis pilares de um indivíduo.
    """

    return {
        atributo: obter_pilar(
            individuo,
            atributo
        )

        for _, atributo in PILARES
    }


def pontuacao_social(individuo):
    """
    Calcula a pontuação social diretamente pelos
    seis pilares.

    Isso evita depender de uma implementação externa
    de social_score().
    """

    valores = [
        obter_pilar(
            individuo,
            atributo
        )

        for _, atributo in PILARES
    ]

    if not valores:
        return 0.0

    return sum(valores) / len(valores)


def ordenar_individuos(population):
    individuos = obter_individuos(population)

    return sorted(
        individuos,
        key=pontuacao_social,
        reverse=True
    )


def media_pilar(population, atributo):
    individuos = obter_individuos(population)

    if not individuos:
        return 0.0

    valores = [
        obter_pilar(
            individuo,
            atributo
        )

        for individuo in individuos
    ]

    return sum(valores) / len(valores)


def medias_pilares(population):
    return {
        atributo: media_pilar(
            population,
            atributo
        )

        for _, atributo in PILARES
    }


# ============================================================
# HISTÓRICO DOS INDIVÍDUOS
# ============================================================

def obter_historico_individuo(individuo):
    """
    Tenta encontrar o histórico de ações do indivíduo.

    Compatível com diferentes nomes que podem existir
    no seu Individual.
    """

    nomes = [
        "action_history",
        "actions_history",
        "history",
        "action_log",
        "social_history",
        "event_history",
    ]

    for nome in nomes:

        historico = obter(
            individuo,
            nome,
            None
        )

        if historico:

            try:
                return list(historico)

            except TypeError:
                continue

    return []


def obter_historico_populacao(population):
    """
    Junta os históricos de todos os indivíduos.
    """

    registros = []

    for individuo in obter_individuos(population):

        historico = obter_historico_individuo(
            individuo
        )

        for registro in historico:

            if isinstance(registro, dict):

                copia = dict(registro)

            else:

                copia = {
                    "raw": registro
                }

            copia["_individual"] = texto(
                obter(
                    individuo,
                    "name",
                    "Indivíduo"
                )
            )

            registros.append(copia)

    return registros


# ============================================================
# AÇÕES
# ============================================================

def contar_acoes(population):
    """
    Conta as ações registradas nos históricos.
    """

    contador = Counter()

    registros = obter_historico_populacao(
        population
    )

    for registro in registros:

        acao = registro.get(
            "action",
            registro.get(
                "acao",
                None
            )
        )

        if acao:
            contador[str(acao)] += 1

    return contador


def total_acoes(population):
    contador = contar_acoes(population)

    return sum(
        contador.values()
    )


# ============================================================
# EVENTOS
# ============================================================

def obter_eventos(population):
    """
    Procura eventos em diferentes estruturas
    para manter compatibilidade com o projeto.
    """

    nomes = [
        "events",
        "event_history",
        "event_log",
        "events_history",
    ]

    for nome in nomes:

        eventos = obter(
            population,
            nome,
            None
        )

        if eventos:

            try:
                return list(eventos)

            except TypeError:
                pass

    social = obter(
        population,
        "social",
        None
    )

    if social:

        for nome in nomes:

            eventos = obter(
                social,
                nome,
                None
            )

            if eventos:

                try:
                    return list(eventos)

                except TypeError:
                    pass

    return []


# ============================================================
# INTERAÇÕES
# ============================================================

def obter_interacoes(population):
    social = obter(
        population,
        "social",
        None
    )

    if social is None:
        return []

    nomes = [
        "interactions",
        "interaction_history",
        "history",
    ]

    for nome in nomes:

        interacoes = obter(
            social,
            nome,
            None
        )

        if interacoes:

            try:
                return list(interacoes)

            except TypeError:
                pass

    return []


def contar_interacoes(population):
    contador = Counter()

    for interacao in obter_interacoes(
        population
    ):

        if isinstance(interacao, dict):

            tipo = interacao.get(
                "type",
                "desconhecida"
            )

            contador[
                str(tipo)
            ] += 1

    return contador


# ============================================================
# HISTÓRICO DE EVOLUÇÃO
# ============================================================

def extrair_evolucao_individuo(individuo):
    """
    Extrai uma série temporal dos pilares a partir
    do histórico de ações.

    Espera registros semelhantes a:

    {
        "day": 10,
        "pillar": "respeito",
        "score_after": 55
    }

    """

    historico = obter_historico_individuo(
        individuo
    )

    if not historico:
        return []

    pontos = []

    for registro in historico:

        if not isinstance(
            registro,
            dict
        ):
            continue

        dia = registro.get(
            "day",
            registro.get(
                "dia",
                None
            )
        )

        pilar = registro.get(
            "pillar",
            registro.get(
                "pilar",
                None
            )
        )

        score = registro.get(
            "score_after",
            registro.get(
                "after",
                None
            )
        )

        if (
            dia is None
            or pilar is None
            or score is None
        ):
            continue

        pontos.append(
            {
                "day": numero(dia),
                "pillar": str(pilar).lower(),
                "score": numero(score),
            }
        )

    return sorted(
        pontos,
        key=lambda x: x["day"]
    )


# ============================================================
# ESTILOS
# ============================================================

def criar_estilos():

    estilos = getSampleStyleSheet()

    estilos.add(
        ParagraphStyle(
            name="TituloCapa",
            parent=estilos["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=32,
            textColor=BRANCO,
            alignment=TA_LEFT,
            spaceAfter=12,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="SubtituloCapa",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=19,
            textColor=colors.HexColor(
                "#DDEAF5"
            ),
            alignment=TA_LEFT,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="TituloSecao",
            parent=estilos["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=AZUL,
            spaceBefore=4,
            spaceAfter=12,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="Subtitulo",
            parent=estilos["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=PRETO,
            spaceBefore=8,
            spaceAfter=6,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="Texto",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=CINZA_TEXTO,
            spaceAfter=8,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="TextoDestaque",
            parent=estilos["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=15,
            textColor=PRETO,
            spaceAfter=6,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="NumeroGrande",
            parent=estilos["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=24,
            textColor=AZUL,
            alignment=TA_CENTER,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="LegendaNumero",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=CINZA_TEXTO,
            alignment=TA_CENTER,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="Pequeno",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=CINZA_TEXTO,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="Centralizado",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=CINZA_TEXTO,
        )
    )

    return estilos


# ============================================================
# CABEÇALHO / RODAPÉ
# ============================================================

def desenhar_pagina(canvas, doc):

    canvas.saveState()

    # Linha superior
    canvas.setFillColor(
        AZUL
    )

    canvas.rect(
        0,
        ALTURA - 0.22 * cm,
        LARGURA,
        0.22 * cm,
        fill=1,
        stroke=0,
    )

    # Rodapé
    canvas.setStrokeColor(
        CINZA_ESCURO
    )

    canvas.line(
        2 * cm,
        1.25 * cm,
        LARGURA - 2 * cm,
        1.25 * cm,
    )

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.setFillColor(
        CINZA_TEXTO
    )

    canvas.drawString(
        2 * cm,
        0.75 * cm,
        "Darwin Population • Relatório da Simulação",
    )

    canvas.drawRightString(
        LARGURA - 2 * cm,
        0.75 * cm,
        f"Página {doc.page}",
    )

    canvas.restoreState()


# ============================================================
# COMPONENTES
# ============================================================

def caixa_indicador(
    numero_valor,
    legenda,
    estilos
):

    tabela = Table(
        [
            [
                Paragraph(
                    texto(
                        numero_valor
                    ),
                    estilos["NumeroGrande"]
                )
            ],
            [
                Paragraph(
                    texto_seguro(
                        legenda
                    ),
                    estilos["LegendaNumero"]
                )
            ],
        ],
        colWidths=[
            5.0 * cm
        ],
        rowHeights=[
            0.9 * cm,
            0.6 * cm
        ],
    )

    tabela.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    CINZA
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    CINZA_ESCURO
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
            ]
        )
    )

    return tabela


def criar_caixa_texto(
    titulo,
    conteudo,
    estilos,
    fundo=CINZA
):

    tabela = Table(
        [
            [
                Paragraph(
                    f"<b>{texto_seguro(titulo)}</b>",
                    estilos["TextoDestaque"]
                )
            ],
            [
                Paragraph(
                    texto_seguro(conteudo),
                    estilos["Texto"]
                )
            ],
        ],
        colWidths=[
            15.5 * cm
        ],
    )

    tabela.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    fundo
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    CINZA_ESCURO
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
            ]
        )
    )

    return tabela


# ============================================================
# RANKING
# ============================================================

def tabela_ranking(
    individuos,
    estilos,
    limite=10
):

    dados = [
        [
            "#",
            "Indivíduo",
            "Score social",
        ]
    ]

    for posicao, individuo in enumerate(
        individuos[:limite],
        1
    ):

        nome = texto(
            obter(
                individuo,
                "name",
                f"Indivíduo {posicao}"
            )
        )

        dados.append(
            [
                f"{posicao}º",
                nome,
                f"{pontuacao_social(individuo):.2f}",
            ]
        )

    tabela = Table(
        dados,
        colWidths=[
            1.2 * cm,
            9.5 * cm,
            4.8 * cm,
        ],
        repeatRows=1,
    )

    tabela.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    AZUL
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    BRANCO
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (0, -1),
                    "CENTER"
                ),
                (
                    "ALIGN",
                    (2, 0),
                    (2, -1),
                    "CENTER"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TEXTCOLOR",
                    (0, 1),
                    (-1, -1),
                    PRETO
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [BRANCO, CINZA]
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    CINZA_ESCURO
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ]
        )
    )

    return tabela


# ============================================================
# GRÁFICO 1 — RANKING
# ============================================================

def grafico_ranking(
    individuos,
    caminho
):

    dados = individuos[:10]

    if not dados:
        return False

    nomes = [
        texto(
            obter(
                individuo,
                "name",
                f"Indivíduo {i + 1}"
            )
        )

        for i, individuo in enumerate(dados)
    ]

    valores = [
        pontuacao_social(
            individuo
        )

        for individuo in dados
    ]

    nomes.reverse()
    valores.reverse()

    plt.figure(
        figsize=(8, 4.8)
    )

    plt.barh(
        nomes,
        valores
    )

    plt.xlabel(
        "Pontuação social"
    )

    plt.title(
        "Ranking dos indivíduos"
    )

    plt.xlim(
        0,
        100
    )

    plt.grid(
        axis="x",
        alpha=0.2
    )

    plt.tight_layout()

    plt.savefig(
        caminho,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    return True


# ============================================================
# GRÁFICO 2 — OS 6 PILARES
# ============================================================

def grafico_pilares(
    population,
    caminho
):

    medias = medias_pilares(
        population
    )

    nomes = [
        nome

        for nome, _ in PILARES
    ]

    valores = [
        medias[atributo]

        for _, atributo in PILARES
    ]

    if not valores:
        return False

    plt.figure(
        figsize=(8, 4.8)
    )

    barras = plt.bar(
        nomes,
        valores
    )

    plt.ylabel(
        "Média da população"
    )

    plt.title(
        "Estado dos seis pilares sociais"
    )

    plt.ylim(
        0,
        100
    )

    plt.xticks(
        rotation=20
    )

    plt.grid(
        axis="y",
        alpha=0.2
    )

    for barra, valor in zip(
        barras,
        valores
    ):

        plt.text(
            barra.get_x()
            + barra.get_width() / 2,
            valor + 2,
            f"{valor:.1f}",
            ha="center",
            fontsize=9
        )

    plt.tight_layout()

    plt.savefig(
        caminho,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    return True


# ============================================================
# GRÁFICO 3 — AÇÕES
# ============================================================

def grafico_acoes(
    population,
    caminho
):

    contador = contar_acoes(
        population
    )

    if not contador:
        return False

    nomes = []
    valores = []

    for acao in ACOES:

        valor = contador.get(
            acao,
            0
        )

        nomes.append(
            ACOES_NOMES.get(
                acao,
                acao
            )
        )

        valores.append(
            valor
        )

    if sum(valores) == 0:
        return False

    plt.figure(
        figsize=(8, 4.8)
    )

    plt.bar(
        nomes,
        valores
    )

    plt.title(
        "Distribuição das ações"
    )

    plt.ylabel(
        "Quantidade"
    )

    plt.xticks(
        rotation=18
    )

    plt.grid(
        axis="y",
        alpha=0.2
    )

    plt.tight_layout()

    plt.savefig(
        caminho,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    return True


# ============================================================
# GRÁFICO 4 — INTERAÇÕES
# ============================================================

def grafico_interacoes(
    population,
    caminho
):

    contador = contar_interacoes(
        population
    )

    valores = [
        contador.get(
            tipo,
            0
        )

        for tipo in INTERACOES
    ]

    if sum(valores) == 0:
        return False

    nomes = [
        "Positivas",
        "Neutras",
        "Conflitos",
    ]

    plt.figure(
        figsize=(7, 4.5)
    )

    plt.bar(
        nomes,
        valores
    )

    plt.title(
        "Tipos de interação social"
    )

    plt.ylabel(
        "Quantidade"
    )

    plt.grid(
        axis="y",
        alpha=0.2
    )

    plt.tight_layout()

    plt.savefig(
        caminho,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    return True


# ============================================================
# GRÁFICO 5 — PERFIL DO DESTAQUE
# ============================================================

def grafico_individuo(
    individuo,
    caminho
):

    nomes = [
        nome

        for nome, _ in PILARES
    ]

    valores = [
        obter_pilar(
            individuo,
            atributo
        )

        for _, atributo in PILARES
    ]

    if not valores:
        return False

    plt.figure(
        figsize=(8, 4.5)
    )

    barras = plt.bar(
        nomes,
        valores
    )

    plt.ylim(
        0,
        100
    )

    plt.ylabel(
        "Pontuação"
    )

    nome = texto(
        obter(
            individuo,
            "name",
            "Indivíduo destaque"
        )
    )

    plt.title(
        f"Perfil social de {nome}"
    )

    plt.xticks(
        rotation=20
    )

    plt.grid(
        axis="y",
        alpha=0.2
    )

    for barra, valor in zip(
        barras,
        valores
    ):

        plt.text(
            barra.get_x()
            + barra.get_width() / 2,
            valor + 2,
            f"{valor:.1f}",
            ha="center",
            fontsize=9
        )

    plt.tight_layout()

    plt.savefig(
        caminho,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    return True


# ============================================================
# GRÁFICO 6 — EVOLUÇÃO DOS PILARES
# ============================================================

def grafico_evolucao(
    individuo,
    caminho
):

    registros = extrair_evolucao_individuo(
        individuo
    )

    if not registros:
        return False

    por_pilar = defaultdict(list)

    for registro in registros:

        por_pilar[
            registro["pillar"]
        ].append(
            (
                registro["day"],
                registro["score"]
            )
        )

    if not por_pilar:
        return False

    plt.figure(
        figsize=(8, 5)
    )

    for nome, atributo in PILARES:

        pontos = por_pilar.get(
            atributo,
            []
        )

        if not pontos:
            continue

        pontos.sort()

        dias = [
            ponto[0]
            for ponto in pontos
        ]

        scores = [
            ponto[1]
            for ponto in pontos
        ]

        plt.plot(
            dias,
            scores,
            marker="o",
            linewidth=1.6,
            markersize=3,
            label=nome
        )

    plt.title(
        "Evolução dos pilares ao longo da simulação"
    )

    plt.xlabel(
        "Dia"
    )

    plt.ylabel(
        "Pontuação"
    )

    plt.ylim(
        0,
        100
    )

    plt.grid(
        alpha=0.2
    )

    plt.legend(
        fontsize=8
    )

    plt.tight_layout()

    plt.savefig(
        caminho,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    return True


# ============================================================
# DESCRIÇÃO DE EVENTOS
# ============================================================

def descrever_evento(evento):

    if isinstance(
        evento,
        str
    ):

        return texto_seguro(
            evento
        )

    if isinstance(
        evento,
        dict
    ):

        dia = evento.get(
            "day",
            evento.get(
                "dia",
                "?"
            )
        )

        nome = evento.get(
            "name",
            evento.get(
                "event",
                evento.get(
                    "type",
                    "Acontecimento"
                )
            )
        )

        descricao = evento.get(
            "description",
            evento.get(
                "descricao",
                ""
            )
        )

        pilar = evento.get(
            "pillar",
            evento.get(
                "pilar",
                None
            )
        )

        resultado = (
            f"<b>Dia {escape(texto(dia))}"
            f" — {escape(texto(nome))}</b>"
        )

        if pilar:
            resultado += (
                f"<br/><font size='8'>"
                f"Pilar: {escape(texto(pilar))}"
                f"</font>"
            )

        if descricao:
            resultado += (
                f"<br/>{escape(texto(descricao))}"
            )

        return resultado

    return texto_seguro(
        evento
    )


# ============================================================
# DESCRIÇÃO DE INTERAÇÕES
# ============================================================

def descrever_interacao(
    interacao
):

    if not isinstance(
        interacao,
        dict
    ):

        return texto_seguro(
            interacao
        )

    dia = interacao.get(
        "day",
        interacao.get(
            "dia",
            "?"
        )
    )

    origem = interacao.get(
        "individual_a",
        interacao.get(
            "source",
            "Indivíduo"
        )
    )

    destino = interacao.get(
        "individual_b",
        interacao.get(
            "target",
            "Outro"
        )
    )

    tipo = interacao.get(
        "type",
        interacao.get(
            "action",
            "interação"
        )
    )

    score = interacao.get(
        "score",
        None
    )

    texto_interacao = (
        f"<b>Dia {escape(texto(dia))}</b> — "
        f"{escape(texto(origem))} ↔ "
        f"{escape(texto(destino))} "
        f"({escape(texto(tipo))})"
    )

    if score is not None:

        texto_interacao += (
            f" — Score: "
            f"<b>{numero(score):.2f}</b>"
        )

    return texto_interacao


# ============================================================
# ANÁLISES AUTOMÁTICAS
# ============================================================

def faixa_score(score):

    if score >= 80:
        return "muito alto"

    if score >= 65:
        return "alto"

    if score >= 50:
        return "moderado"

    if score >= 35:
        return "baixo"

    return "muito baixo"


def gerar_analise_pilares(
    population
):

    medias = medias_pilares(
        population
    )

    maior = max(
        medias.items(),
        key=lambda x: x[1]
    )

    menor = min(
        medias.items(),
        key=lambda x: x[1]
    )

    nomes = {
        atributo: nome

        for nome, atributo in PILARES
    }

    return (
        f"O pilar com melhor resultado médio foi "
        f"<b>{escape(nomes[maior[0]])}</b>, "
        f"com <b>{maior[1]:.2f}</b> pontos. "
        f"O menor resultado médio foi observado em "
        f"<b>{escape(nomes[menor[0]])}</b>, "
        f"com <b>{menor[1]:.2f}</b> pontos."
    )


def gerar_analise_acoes(
    population
):

    contador = contar_acoes(
        population
    )

    total = sum(
        contador.values()
    )

    if total == 0:
        return (
            "Não há registros de ações suficientes "
            "para realizar uma análise comportamental."
        )

    melhor = (
        contador.get(
            "agir_corretamente",
            0
        )
        + contador.get(
            "ajudar",
            0
        )
    )

    ruins = contador.get(
        "agir_incorretamente",
        0
    )

    positivas = (
        melhor / total
    ) * 100

    negativas = (
        ruins / total
    ) * 100

    return (
        f"Foram registradas <b>{total}</b> ações. "
        f"As ações associadas a comportamento construtivo "
        f"(agir corretamente + ajudar) representaram "
        f"<b>{positivas:.1f}%</b> dos registros, enquanto "
        f"ações incorretas representaram "
        f"<b>{negativas:.1f}%</b>."
    )


def gerar_analise_interacoes(
    population
):

    contador = contar_interacoes(
        population
    )

    total = sum(
        contador.values()
    )

    if total == 0:

        return (
            "Não foram encontradas interações "
            "suficientes para análise."
        )

    positivas = contador.get(
        "positiva",
        0
    )

    conflitos = contador.get(
        "conflito",
        0
    )

    neutras = contador.get(
        "neutra",
        0
    )

    return (
        f"Foram registradas <b>{total}</b> interações: "
        f"<b>{positivas}</b> positivas, "
        f"<b>{neutras}</b> neutras e "
        f"<b>{conflitos}</b> conflitos."
    )


def gerar_conclusao(
    population,
    individuos,
    dias
):

    quantidade = len(
        individuos
    )

    if quantidade == 0:

        return (
            "A simulação não possui indivíduos "
            "suficientes para gerar uma conclusão."
        )

    vencedor = individuos[0]

    nome = texto(
        obter(
            vencedor,
            "name",
            "Indivíduo destaque"
        )
    )

    score = pontuacao_social(
        vencedor
    )

    media = (
        sum(
            pontuacao_social(
                individuo
            )

            for individuo in individuos
        )
        / quantidade
    )

    interacoes = len(
        obter_interacoes(
            population
        )
    )

    eventos = len(
        obter_eventos(
            population
        )
    )

    return (
        f"A simulação acompanhou "
        f"<b>{quantidade} indivíduos</b>"

        + (
            f" durante <b>{dias} dias</b>."
            if dias is not None
            else "."
        )

        + f" Foram registrados "
        f"<b>{eventos} acontecimentos</b> e "
        f"<b>{interacoes} interações sociais</b>. "

        f"A pontuação social média da população foi "
        f"<b>{media:.2f}</b>, enquanto o indivíduo "
        f"<b>{escape(nome)}</b> apresentou o maior "
        f"resultado, com <b>{score:.2f}</b>. "

        f"O resultado demonstra que a dinâmica social "
        f"emerge da combinação entre características "
        f"individuais, percepção de eventos, decisões "
        f"e interações entre os membros da população."
    )


# ============================================================
# CRIAÇÃO DO PDF
# ============================================================

def create_pdf(
    population,
    arquivo="relatorio_darwin_population.pdf",
    dias=None
):

    """
    Gera um relatório completo da população.

    Exemplo:

        population.simulate(200)

        create_pdf(
            population,
            "relatorio.pdf",
            200
        )
    """

    estilos = criar_estilos()

    individuos = ordenar_individuos(
        population
    )

    quantidade = len(
        individuos
    )

    vencedor = (
        individuos[0]
        if individuos
        else None
    )

    eventos = obter_eventos(
        population
    )

    interacoes = obter_interacoes(
        population
    )

    registros = obter_historico_populacao(
        population
    )

    # ========================================================
    # DIRETÓRIO TEMPORÁRIO
    # ========================================================

    pasta_temp = tempfile.mkdtemp(
        prefix="darwin_report_"
    )

    ranking_png = os.path.join(
        pasta_temp,
        "ranking.png"
    )

    pilares_png = os.path.join(
        pasta_temp,
        "pilares.png"
    )

    acoes_png = os.path.join(
        pasta_temp,
        "acoes.png"
    )

    interacoes_png = os.path.join(
        pasta_temp,
        "interacoes.png"
    )

    vencedor_png = os.path.join(
        pasta_temp,
        "vencedor.png"
    )

    evolucao_png = os.path.join(
        pasta_temp,
        "evolucao.png"
    )

    # ========================================================
    # GRÁFICOS
    # ========================================================

    tem_ranking = grafico_ranking(
        individuos,
        ranking_png
    )

    tem_pilares = grafico_pilares(
        population,
        pilares_png
    )

    tem_acoes = grafico_acoes(
        population,
        acoes_png
    )

    tem_interacoes = grafico_interacoes(
        population,
        interacoes_png
    )

    tem_vencedor = False

    tem_evolucao = False

    if vencedor:

        tem_vencedor = grafico_individuo(
            vencedor,
            vencedor_png
        )

        tem_evolucao = grafico_evolucao(
            vencedor,
            evolucao_png
        )

    # ========================================================
    # DOCUMENTO
    # ========================================================

    documento = SimpleDocTemplate(
        arquivo,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=1.7 * cm,
        title=(
            "Darwin Population — "
            "Relatório da Simulação"
        ),
        author="Darwin Population",
    )

    story = []

    # ========================================================
    # CAPA
    # ========================================================

    capa = Table(
        [
            [
                [
                    Spacer(
                        1,
                        2.5 * cm
                    ),

                    Paragraph(
                        "DARWIN<br/>POPULATION",
                        estilos["TituloCapa"]
                    ),

                    Paragraph(
                        "Relatório da evolução "
                        "social da população",
                        estilos["SubtituloCapa"]
                    ),

                    Spacer(
                        1,
                        1.0 * cm
                    ),

                    Paragraph(
                        "SIMULAÇÃO SOCIAL",
                        ParagraphStyle(
                            "CapaPequeno",
                            parent=estilos[
                                "SubtituloCapa"
                            ],
                            fontName="Helvetica-Bold",
                            fontSize=9,
                        )
                    ),

                    Spacer(
                        1,
                        4.2 * cm
                    ),

                    Paragraph(
                        "Percepção • Decisão • "
                        "Comportamento • Interação",
                        ParagraphStyle(
                            "CapaFinal",
                            parent=estilos[
                                "SubtituloCapa"
                            ],
                            fontSize=10,
                            leading=15,
                        )
                    ),
                ]
            ]
        ],
        colWidths=[
            17 * cm
        ],
        rowHeights=[
            23 * cm
        ],
    )

    capa.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    AZUL
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.2 * cm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.2 * cm
                ),
            ]
        )
    )

    story.append(capa)
    story.append(PageBreak())

    # ========================================================
    # 01 — RESUMO EXECUTIVO
    # ========================================================

    story.append(
        Paragraph(
            "01 / RESUMO EXECUTIVO",
            estilos["TituloSecao"]
        )
    )

    story.append(
        Paragraph(
            "Visão geral da sociedade simulada",
            estilos["Subtitulo"]
        )
    )

    story.append(
        Paragraph(
            "O modelo acompanha uma população formada por "
            "indivíduos que percebem acontecimentos, tomam "
            "decisões, executam ações e interagem entre si. "
            "O comportamento coletivo é resultado da evolução "
            "dessas decisões ao longo do tempo.",
            estilos["Texto"]
        )
    )

    media_social = 0

    if individuos:

        media_social = (
            sum(
                pontuacao_social(
                    individuo
                )

                for individuo in individuos
            )
            / len(individuos)
        )

    indicadores = Table(
        [
            [
                caixa_indicador(
                    quantidade,
                    "Indivíduos",
                    estilos
                ),

                caixa_indicador(
                    dias
                    if dias is not None
                    else "—",
                    "Dias simulados",
                    estilos
                ),

                caixa_indicador(
                    len(eventos),
                    "Acontecimentos",
                    estilos
                ),
            ],

            [
                caixa_indicador(
                    len(interacoes),
                    "Interações",
                    estilos
                ),

                caixa_indicador(
                    len(registros),
                    "Decisões registradas",
                    estilos
                ),

                caixa_indicador(
                    f"{media_social:.2f}",
                    "Média social",
                    estilos
                ),
            ],
        ],
        colWidths=[
            5.2 * cm,
            5.2 * cm,
            5.2 * cm,
        ],
    )

    indicadores.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
            ]
        )
    )

    story.append(
        indicadores
    )

    story.append(
        Spacer(
            1,
            0.5 * cm
        )
    )

    story.append(
        criar_caixa_texto(
            "Leitura inicial",
            (
                f"A pontuação média atual da população é "
                f"{media_social:.2f}, classificada como "
                f"{faixa_score(media_social)}. "
                f"{gerar_analise_pilares(population).replace('<b>', '').replace('</b>', '')}"
            ),
            estilos,
            AZUL_CLARO
        )
    )

    # ========================================================
    # 02 — PILARES
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "02 / PILARES DA SOCIEDADE",
            estilos["TituloSecao"]
        )
    )

    story.append(
        Paragraph(
            "Os seis pilares fundamentais",
            estilos["Subtitulo"]
        )
    )

    story.append(
        Paragraph(
            "Cada indivíduo possui seis dimensões sociais: "
            "respeito, cidadania, responsabilidade, zelo, "
            "justiça e sinceridade. O resultado apresentado "
            "aqui corresponde à média desses atributos na "
            "população.",
            estilos["Texto"]
        )
    )

    if tem_pilares:

        story.append(
            Image(
                pilares_png,
                width=15.5 * cm,
                height=8.8 * cm
            )
        )

    story.append(
        Spacer(
            1,
            0.4 * cm
        )
    )

    dados_pilares = [
        [
            "Pilar",
            "Média",
            "Classificação",
        ]
    ]

    medias = medias_pilares(
        population
    )

    for nome, atributo in PILARES:

        valor = medias[atributo]

        dados_pilares.append(
            [
                nome,
                f"{valor:.2f}",
                faixa_score(valor).capitalize(),
            ]
        )

    tabela = Table(
        dados_pilares,
        colWidths=[
            7.5 * cm,
            4 * cm,
            4 * cm,
        ],
        repeatRows=1,
    )

    tabela.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    AZUL
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    BRANCO
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [BRANCO, CINZA]
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    CINZA_ESCURO
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ]
        )
    )

    story.append(
        tabela
    )

    story.append(
        Spacer(
            1,
            0.4 * cm
        )
    )

    story.append(
        Paragraph(
            gerar_analise_pilares(
                population
            ),
            estilos["Texto"]
        )
    )

    # ========================================================
    # 03 — RANKING
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "03 / RANKING SOCIAL",
            estilos["TituloSecao"]
        )
    )

    story.append(
        Paragraph(
            "Quem apresentou o melhor desempenho?",
            estilos["Subtitulo"]
        )
    )

    story.append(
        Paragraph(
            "O ranking considera a média dos seis pilares "
            "sociais de cada indivíduo. Isso cria uma visão "
            "geral do comportamento social observado.",
            estilos["Texto"]
        )
    )

    if tem_ranking:

        story.append(
            Image(
                ranking_png,
                width=15.5 * cm,
                height=8.5 * cm
            )
        )

    story.append(
        Spacer(
            1,
            0.3 * cm
        )
    )

    story.append(
        tabela_ranking(
            individuos,
            estilos,
            limite=10
        )
    )

    # ========================================================
    # 04 — AÇÕES
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "04 / COMPORTAMENTO",
            estilos["TituloSecao"]
        )
    )

    story.append(
        Paragraph(
            "Como os indivíduos responderam aos eventos?",
            estilos["Subtitulo"]
        )
    )

    story.append(
        Paragraph(
            "O sistema de decisão pode produzir quatro tipos "
            "de resposta: agir corretamente, ajudar, ignorar "
            "ou agir incorretamente. A distribuição dessas "
            "ações permite observar o comportamento coletivo.",
            estilos["Texto"]
        )
    )

    if tem_acoes:

        story.append(
            Image(
                acoes_png,
                width=15.5 * cm,
                height=8.7 * cm
            )
        )

        story.append(
            Spacer(
                1,
                0.3 * cm
            )
        )

    story.append(
        criar_caixa_texto(
            "Interpretação",
            (
                "A análise das ações mostra como a população "
                "transforma percepção em comportamento. "
                "A presença de diferentes respostas é importante "
                "porque impede que todos os indivíduos se comportem "
                "de maneira idêntica."
            ),
            estilos,
            CINZA
        )
    )

    story.append(
        Spacer(
            1,
            0.3 * cm
        )
    )

    story.append(
        Paragraph(
            gerar_analise_acoes(
                population
            ),
            estilos["Texto"]
        )
    )

    # ========================================================
    # 05 — INTERAÇÕES
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "05 / INTERAÇÕES SOCIAIS",
            estilos["TituloSecao"]
        )
    )

    story.append(
        Paragraph(
            "Indivíduo × indivíduo",
            estilos["Subtitulo"]
        )
    )

    story.append(
        Paragraph(
            "Além dos eventos externos, os indivíduos também "
            "interagem entre si. Essas relações podem ser "
            "positivas, neutras ou gerar conflitos.",
            estilos["Texto"]
        )
    )

    if tem_interacoes:

        story.append(
            Image(
                interacoes_png,
                width=15.5 * cm,
                height=8.5 * cm
            )
        )

    story.append(
        Spacer(
            1,
            0.3 * cm
        )
    )

    story.append(
        Paragraph(
            gerar_analise_interacoes(
                population
            ),
            estilos["Texto"]
        )
    )

    story.append(
        Spacer(
            1,
            0.2 * cm
        )
    )

    if interacoes:

        dados = [
            [
                Paragraph(
                    "<b>Dia</b>",
                    estilos["Pequeno"]
                ),

                Paragraph(
                    "<b>Relação</b>",
                    estilos["Pequeno"]
                ),
            ]
        ]

        for interacao in interacoes[-15:]:

            dia = (
                interacao.get(
                    "day",
                    interacao.get(
                        "dia",
                        "?"
                    )
                )

                if isinstance(
                    interacao,
                    dict
                )

                else "?"
            )

            dados.append(
                [
                    Paragraph(
                        escape(
                            texto(dia)
                        ),
                        estilos["Pequeno"]
                    ),

                    Paragraph(
                        descrever_interacao(
                            interacao
                        ),
                        estilos["Pequeno"]
                    ),
                ]
            )

        tabela_interacoes = Table(
            dados,
            colWidths=[
                2 * cm,
                13.5 * cm,
            ],
            repeatRows=1,
        )

        tabela_interacoes.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        AZUL_CLARO
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.3,
                        CINZA_ESCURO
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                ]
            )
        )

        story.append(
            tabela_interacoes
        )

    # ========================================================
    # 06 — ACONTECIMENTOS
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "06 / ACONTECIMENTOS",
            estilos["TituloSecao"]
        )
    )

    story.append(
        Paragraph(
            "Situações que movimentaram a população",
            estilos["Subtitulo"]
        )
    )

    story.append(
        Paragraph(
            "Os acontecimentos são os estímulos que provocam "
            "percepção e tomada de decisão. O mesmo evento "
            "pode ser interpretado de maneiras diferentes "
            "por indivíduos diferentes.",
            estilos["Texto"]
        )
    )

    if eventos:

        for evento in eventos[:20]:

            bloco = Table(
                [
                    [
                        Paragraph(
                            descrever_evento(
                                evento
                            ),
                            estilos["Texto"]
                        )
                    ]
                ],
                colWidths=[
                    15.5 * cm
                ],
            )

            bloco.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            CINZA
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            CINZA_ESCURO
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            10
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            10
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            8
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            8
                        ),
                    ]
                )
            )

            story.append(
                bloco
            )

            story.append(
                Spacer(
                    1,
                    0.15 * cm
                )
            )

    else:

        story.append(
            Paragraph(
                "Nenhum acontecimento foi encontrado "
                "no histórico disponível.",
                estilos["Texto"]
            )
        )

    # ========================================================
    # 07 — INDIVÍDUO DESTAQUE
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "07 / INDIVÍDUO DESTAQUE",
            estilos["TituloSecao"]
        )
    )

    if vencedor:

        nome = texto(
            obter(
                vencedor,
                "name",
                "Indivíduo destaque"
            )
        )

        score = pontuacao_social(
            vencedor
        )

        destaque = Table(
            [
                [
                    Paragraph(
                        "★",
                        ParagraphStyle(
                            "Estrela",
                            parent=estilos[
                                "NumeroGrande"
                            ],
                            fontSize=32,
                            textColor=AMARELO,
                        )
                    ),

                    [
                        Paragraph(
                            escape(nome),
                            ParagraphStyle(
                                "NomeVencedor",
                                parent=estilos[
                                    "TituloSecao"
                                ],
                                fontSize=21,
                            )
                        ),

                        Paragraph(
                            f"Pontuação social: "
                            f"<b>{score:.2f}</b>",
                            estilos["TextoDestaque"]
                        ),

                        Paragraph(
                            "Este indivíduo apresentou "
                            "o maior resultado social da "
                            "população analisada.",
                            estilos["Texto"]
                        ),
                    ],
                ]
            ],
            colWidths=[
                2 * cm,
                13.5 * cm
            ],
        )

        destaque.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        VERDE_CLARO
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        VERDE
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        12
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        12
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        12
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        12
                    ),
                ]
            )
        )

        story.append(
            destaque
        )

        story.append(
            Spacer(
                1,
                0.5 * cm
            )
        )

        if tem_vencedor:

            story.append(
                Image(
                    vencedor_png,
                    width=15.5 * cm,
                    height=8.7 * cm
                )
            )

        # ====================================================
        # TABELA DOS PILARES DO DESTAQUE
        # ====================================================

        dados_destaque = [
            [
                "Pilar",
                "Valor"
            ]
        ]

        for nome_pilar, atributo in PILARES:

            valor = obter_pilar(
                vencedor,
                atributo
            )

            dados_destaque.append(
                [
                    nome_pilar,
                    f"{valor:.2f}"
                ]
            )

        tabela_destaque = Table(
            dados_destaque,
            colWidths=[
                11 * cm,
                4.5 * cm,
            ],
            repeatRows=1,
        )

        tabela_destaque.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        AZUL
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        BRANCO
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [BRANCO, CINZA]
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.3,
                        CINZA_ESCURO
                    ),
                    (
                        "ALIGN",
                        (1, 0),
                        (1, -1),
                        "CENTER"
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                ]
            )
        )

        story.append(
            Spacer(
                1,
                0.2 * cm
            )
        )

        story.append(
            tabela_destaque
        )

        # ====================================================
        # EVOLUÇÃO
        # ====================================================

        if tem_evolucao:

            story.append(
                Spacer(
                    1,
                    0.5 * cm
                )
            )

            story.append(
                Paragraph(
                    "Evolução ao longo da simulação",
                    estilos["Subtitulo"]
                )
            )

            story.append(
                Image(
                    evolucao_png,
                    width=15.5 * cm,
                    height=9 * cm
                )
            )

        relatorio = chamar(
            vencedor,
            "show_full_report",
            None
        )

        if relatorio:

            story.append(
                Spacer(
                    1,
                    0.3 * cm
                )
            )

            story.append(
                Paragraph(
                    "Relatório individual",
                    estilos["Subtitulo"]
                )
            )

            story.append(
                Paragraph(
                    escape(
                        str(relatorio)
                    ).replace(
                        "\n",
                        "<br/>"
                    ),
                    estilos["Texto"]
                )
            )

    else:

        story.append(
            Paragraph(
                "Não foi possível identificar "
                "um indivíduo destaque.",
                estilos["Texto"]
            )
        )

    # ========================================================
    # 08 — CONCLUSÃO
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "08 / CONCLUSÃO",
            estilos["TituloSecao"]
        )
    )

    story.append(
        Paragraph(
            "O que a simulação mostra?",
            estilos["Subtitulo"]
        )
    )

    story.append(
        Paragraph(
            gerar_conclusao(
                population,
                individuos,
                dias
            ),
            estilos["Texto"]
        )
    )

    story.append(
        Spacer(
            1,
            0.4 * cm
        )
    )

    story.append(
        criar_caixa_texto(
            "IDEIA CENTRAL",
            (
                "O comportamento de uma sociedade não é "
                "determinado por uma única característica. "
                "Ele emerge da combinação entre os valores "
                "dos indivíduos, sua percepção dos acontecimentos, "
                "suas decisões e as interações estabelecidas "
                "com outras pessoas."
            ),
            estilos,
            AZUL_CLARO
        )
    )

    story.append(
        Spacer(
            1,
            0.5 * cm
        )
    )

    story.append(
        Paragraph(
            "Síntese comportamental",
            estilos["Subtitulo"]
        )
    )

    story.append(
        Paragraph(
            gerar_analise_pilares(
                population
            ),
            estilos["Texto"]
        )
    )

    story.append(
        Paragraph(
            gerar_analise_acoes(
                population
            ),
            estilos["Texto"]
        )
    )

    story.append(
        Paragraph(
            gerar_analise_interacoes(
                population
            ),
            estilos["Texto"]
        )
    )

    # ========================================================
    # PALAVRAS-CHAVE
    # ========================================================

    story.append(
        Spacer(
            1,
            0.4 * cm
        )
    )

    story.append(
        Paragraph(
            "Palavras-chave",
            estilos["Subtitulo"]
        )
    )

    palavras = (
        "Comportamento • Sociedade • Percepção • "
        "Decisão • Respeito • Cidadania • "
        "Responsabilidade • Zelo • Justiça • "
        "Sinceridade • Interação • Evolução"
    )

    story.append(
        Paragraph(
            palavras,
            estilos["Texto"]
        )
    )

    # ========================================================
    # BUILD
    # ========================================================

    try:

        documento.build(
            story,
            onFirstPage=desenhar_pagina,
            onLaterPages=desenhar_pagina,
        )

    finally:

        shutil.rmtree(
            pasta_temp,
            ignore_errors=True
        )

    print(
        "\n" +
        "=" * 60 +
        "\nRELATÓRIO GERADO COM SUCESSO" +
        "\n" +
        "=" * 60
    )

    print(
        f"Arquivo: {arquivo}"
    )

    return arquivo


# ============================================================
# ALIAS
# ============================================================

PopulationReport = create_pdf


# ============================================================
# EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":

    print(
        "Este arquivo deve receber uma Population já criada."
    )

    print(
        "\nExemplo:"
    )

    print(
        "\n"
        "from darwin.population import Population\n"
        "from create_pdf import create_pdf\n"
        "\n"
        "population = Population(100)\n"
        "population.simulate(200)\n"
        "\n"
        "create_pdf(\n"
        "    population,\n"
        "    'relatorio.pdf',\n"
        "    200\n"
        ")"
    )

