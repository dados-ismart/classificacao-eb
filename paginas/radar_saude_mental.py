import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

from paginas.funcoes import (
    ler_roster,          # precisa aceitar 'radar_respostas'
    ler_sheets_cache,    # precisa aceitar 'radar_alunos'
    registrar_saude_mental            # registrar(df, 'radar_respostas')
)

# =========================
# Configurações & Helpers
# =========================
TZ = pytz.timezone('America/Sao_Paulo')

COLS_ROSTER = [
    "Nome + RA dx alunx", "Colégio", "Ano", "Gênero",
    "Praça", "Cor/raça", "Orientador Tag", "Orientador Responsável"
]

PROGRESSO_OPCOES = [
    "Segue necessitando de acompanhamento",
    "Novo encaminhamento",
    "Não necessita mais de acompanhamento",
]
IDEACAO_OPCOES = [
    "Não Identificada",
    "Ideação Suicida - Pensamento Suicida",
    "Ideação Suicida - Planejamento",
    "Ideação Suicida - Tentativa",
]
CLASSIFICACAO_OPCOES = ["Camada 2", "Camada 3", "Camada 4"]

def mes_referencia_anterior_str(agora: datetime) -> str:
    """Retorna YYYY-MM do mês anterior ao atual (ex.: '2025-08')."""
    ano = agora.year
    mes = agora.month
    if mes == 1:
        return f"{ano-1}-12"
    return f"{ano}-{mes-1:02d}"

def normaliza_str(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

# =========================
# Contexto do usuário
# =========================
email = st.user.email if hasattr(st, "user") else None
df_login = ler_sheets_cache('login')

try:
    orientadora = df_login.loc[df_login['email'] == email, 'Orientadora'].iloc[0]
except Exception:
    st.error("Não foi possível identificar a orientadora a partir do login.")
    st.stop()

st.title("Radar de Saúde Mental — Atualização Mensal")

# Badge do mês de referência (mês anterior)
agora = datetime.now(TZ)
mes_ref = mes_referencia_anterior_str(agora)
st.caption(f"**Mês de referência:** `{mes_ref}`  •  (**preencha 1x por aluno a cada mês**)")

st.divider()

# =========================
# 1) Ler roster (Sheets 1) e filtrar por orientadora
# =========================
try:
    cfg = st.secrets.get("sheets", {})
    url_radar = cfg.get("radar")
    radar_header = int(cfg.get("radar_header_row", 1))
    roster = ler_roster(url_radar, header_row=radar_header)
except Exception as e:
    st.error("Não foi possível carregar a base de alunos do radar.")
    st.stop()

# Garantir colunas essenciais
missing_cols = [c for c in COLS_ROSTER if c not in roster.columns]
if missing_cols:
    st.error(f"As seguintes colunas estão ausentes: {missing_cols}")
    st.stop()

# Normalizações leves
roster = roster[COLS_ROSTER].copy()
for c in COLS_ROSTER:
    roster[c] = roster[c].apply(normaliza_str)

# Filtro por orientadora (case-insensitive) via "Orientador Tag"
orientadora_norm = normaliza_str(orientadora).lower()
roster['__tag_norm'] = roster['Orientador Tag'].str.lower()

roster_orientadora = roster.loc[roster['__tag_norm'] == orientadora_norm].drop(columns='__tag_norm')

total_atribuido = roster_orientadora.shape[0]

if total_atribuido == 0:
    st.info("Você não possui alunos atribuídos no radar para este mês.")
    st.markdown(
        "Para adicionar novos alunos ao radar, use o formulário: "
        "[Abrir formulário de inclusão](https://docs.google.com/forms/d/e/1FAIpQLSfRKeUPUaJfbqzqezSdpdatzD6gbdyjAePC742c6REnCu1Meg/viewform)"
    )
    st.stop()

# =========================
# 2) Ler respostas já enviadas (Sheets 2) e ocultar alunos já preenchidos no mês
# =========================
try:
    url_respostas = cfg.get("respostas")
    respostas = ler_roster(url_respostas)
except Exception:
    # Se a planilha de respostas ainda não existe ou está vazia, continuamos com DF vazio
    respostas = pd.DataFrame(columns=[
        "Data/Hora da resposta", "Nome + RA dx alunx", "Colégio", "Ano", "Gênero", "Praça",
        "Cor/raça", "Orientador Responsável", "Progresso", "Comentário",
        "Ideação Suicida Identificada?", "Classificação", "Documentos", "Mês referência"
    ])

# Normaliza possíveis colunas
for c in ["Nome + RA dx alunx", "Mês referência"]:
    if c in respostas.columns:
        respostas[c] = respostas[c].apply(normaliza_str)

# Quem já foi respondido no mês de referência?
respondidos_mes = set(
    respostas.loc[respostas["Mês referência"] == mes_ref, "Nome + RA dx alunx"].dropna().unique().tolist()
)

# Opções de alunos pendentes
roster_orientadora["__nome_ra"] = roster_orientadora["Nome + RA dx alunx"]
pendentes_df = roster_orientadora.loc[~roster_orientadora["__nome_ra"].isin(respondidos_mes)].copy()

preenchidos = total_atribuido - pendentes_df.shape[0]
try:
    st.progress(preenchidos / total_atribuido, f"Progresso mensal: **{preenchidos}/{total_atribuido}** alunos registrados")
except ZeroDivisionError:
    st.progress(0, "Sem alunos atribuídos")

if pendentes_df.empty:
    st.success("Tudo certo! Você já registrou **todos** os seus alunos neste mês de referência. ✅")
    st.markdown(
        "Se precisar incluir novos alunos no radar, utilize o formulário: "
        "[Adicionar novos alunos](https://docs.google.com/forms/d/e/1FAIpQLSfRKeUPUaJfbqzqezSdpdatzD6gbdyjAePC742c6REnCu1Meg/viewform)"
    )
    st.stop()

st.divider()

# =========================
# 3) Seleção do aluno pendente
# =========================
st.subheader("Selecionar aluno")
aluno_escolhido = st.selectbox(
    "Nome + RA",
    options=pendentes_df["__nome_ra"].tolist(),
    index=None,
    placeholder="Escolha um aluno para registrar o mês"
)

if not aluno_escolhido:
    st.stop()

registro_aluno = pendentes_df.loc[pendentes_df["__nome_ra"] == aluno_escolhido].iloc[0]

# Mostrar contexto rápido do aluno
with st.expander("Dados do aluno"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Colégio", registro_aluno["Colégio"], border=True)
    c2.metric("Ano", registro_aluno["Ano"], border=True)
    c3.metric("Praça", registro_aluno["Praça"], border=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Gênero", registro_aluno["Gênero"], border=True)
    c2.metric("Cor/raça", registro_aluno["Cor/raça"], border=True)
    c3.metric("Orientador Responsável", registro_aluno["Orientador Responsável"], border=True)

st.divider()

# =========================
# 4) Formulário de registro
# =========================
with st.form("form_radar_saude_mental"):
    st.subheader("Registro do mês")

    progresso = st.radio("**Progresso** *", PROGRESSO_OPCOES, index=None)
    comentario = st.text_area(
        "**Comentário** *",
        placeholder=(
            "Comente pontos importantes para os próximos passos (fatores além da demanda) "
            "e ganhos/progressos desde a última anotação. "
            "Pense no que alguém precisaria saber ao ler este caso pela primeira vez."
        ),
        height=140
    )
    ideacao = st.radio("**Ideação Suicida Identificada?** *", IDEACAO_OPCOES, index=None, horizontal=False)
    classificacao = st.radio("**Classificação** *", CLASSIFICACAO_OPCOES, index=None, horizontal=True)

    st.write("")
    st.markdown("**Documentos** (links de Drive, até 5 itens)")
    documentos_links = st.text_input(
        "Cole links de arquivos/pastas no Drive (separe por ponto-e-vírgula ; )",
        placeholder="https://drive.google.com/...; https://drive.google.com/..."
    )
    st.caption(
        "💡 Para manter simples e seguro, armazene os documentos no Google Drive da equipe e cole os **links** aqui. "
        "O link para a pasta do Google Drive é: https://drive.google.com/drive/folders/1WDH1VGB8b9voQgcQAhPUm1RKjhqZPFj7"
    )

    st.write("")
    enviar = st.form_submit_button("Salvar / Enviar relatório", use_container_width=True)

st.markdown(
    "Para **adição de novos alunos** no radar de saúde mental, acesse: "
    "[este formulário](https://docs.google.com/forms/d/e/1FAIpQLSfRKeUPUaJfbqzqezSdpdatzD6gbdyjAePC742c6REnCu1Meg/viewform)"
)

if enviar:
    # Validação dos obrigatórios
    faltando = []
    if not progresso: faltando.append("Progresso")
    if not comentario or not comentario.strip(): faltando.append("Comentário")
    if not ideacao: faltando.append("Ideação Suicida Identificada?")
    if not classificacao: faltando.append("Classificação")

    if faltando:
        st.warning(f"Preencha os campos obrigatórios: {', '.join(faltando)}.")
        st.stop()

    # Checagem de duplicidade (defensiva): não registrar duas vezes no mesmo mês para o mesmo aluno
    ja_existe = False
    if not respostas.empty:
        filtro_dup = (respostas["Nome + RA dx alunx"] == registro_aluno["Nome + RA dx alunx"]) & \
                     (respostas["Mês referência"] == mes_ref)
        ja_existe = bool(respostas.loc[filtro_dup].shape[0] > 0)

    if ja_existe:
        st.info("Este aluno já possui registro para o mês de referência. A lista será atualizada.")
        st.rerun()

    # Montar linha para Sheets 2 com todas as colunas solicitadas
    agora_dt = datetime.now(TZ)
    linha = {
        "Data/Hora da resposta": agora_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Nome + RA dx alunx": registro_aluno["Nome + RA dx alunx"],
        "Colégio": registro_aluno["Colégio"],
        "Ano": registro_aluno["Ano"],
        "Gênero": registro_aluno["Gênero"],
        "Praça": registro_aluno["Praça"],
        "Cor/raça": registro_aluno["Cor/raça"],
        "Orientador Responsável": registro_aluno["Orientador Responsável"],
        "Progresso": progresso,
        "Comentário": comentario.strip(),
        "Ideação Suicida Identificada?": ideacao,
        "Classificação": classificacao,
        "Documentos": documentos_links.strip() if documentos_links else "",
        "Mês referência": mes_ref
    }

    ok = registrar_saude_mental(linha)
    if ok:
        st.success("Registro salvo com sucesso! ✅")
        st.rerun()
    else:
        st.info("Respostas NÃO foram enviadas ao Google Sheets.")
