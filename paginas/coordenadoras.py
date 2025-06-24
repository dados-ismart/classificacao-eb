import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from paginas.funcoes import ler_sheets, ler_sheets_cache, atualizar_linhas

#set de fuso e conexão com sheets
fuso_horario = pytz.timezone('America/Sao_Paulo')
email = st.user.email 

#importar e tratar datasets
df = ler_sheets('registro')
bd = ler_sheets_cache('bd')
bd = bd.dropna(subset=['RA - NOME'])
df_login = ler_sheets_cache('login')
bd = bd.merge(df[['RA', 'confirmacao_classificacao_orientadora','conclusao_classificacao_final']], how='left', on='RA')
bd = bd.sort_values(by=['conclusao_classificacao_final','confirmacao_classificacao_orientadora'], ascending = False)

st.title('Formulário de Classificação')

# filtros bd
bd_segmentado = bd.query("conclusao_classificacao_final != 'Sim'")
bd_segmentado = bd_segmentado.query("confirmacao_classificacao_orientadora == 'Não' or confirmacao_classificacao_orientadora == 'Sim'")
cidade_login = df_login.query(f'email == "{email}"')["Cidade"].iloc[0]
bd_segmentado = bd_segmentado.query(f'Cidade == "{cidade_login}"')

col1, col2, col3, col4 = st.columns(4)
# Aplique os filtros
valores_segmento = col1.multiselect("Filtro de Segmento", bd_segmentado['Segmento'].unique())
if valores_segmento:
    bd_segmentado = bd_segmentado.query(f"Segmento in {valores_segmento}")
valores_escola = col2.multiselect("Filtro de Escola", bd_segmentado['Escola'].unique())
if valores_escola:
    bd_segmentado = bd_segmentado.query(f"Escola in {valores_escola}")
valores_ano = col3.multiselect("Filtro de Ano", bd_segmentado['Ano'].unique())
if valores_ano:
    bd_segmentado = bd_segmentado.query(f"Ano in {valores_ano}")
selecao_orientadora = col4.multiselect("Filtro Orientadora", bd_segmentado['Orientadora'].unique())
if selecao_orientadora:
    bd_segmentado = bd_segmentado.query(f"Orientadora in {selecao_orientadora}")
st.divider()
ra_nome = None
# progresso
qtd_praca = bd.query(f"Cidade == '{cidade_login}'").shape[0]
qtd_registrados_praca = bd.query(f"Cidade == '{cidade_login}'")
qtd_registrados_praca = qtd_registrados_praca.query("confirmacao_classificacao_orientadora == 'Não' or confirmacao_classificacao_orientadora == 'Sim'").shape[0]
qtd_alunos = bd.shape[0]
qtd_alunos_registrados = bd.query("confirmacao_classificacao_orientadora == 'Não' or confirmacao_classificacao_orientadora == 'Sim'").shape[0]

try:
    st.progress(qtd_alunos_registrados/qtd_alunos, f'Status de Preenchimento das Orientadoras de ***Todas as Praças***: **{qtd_alunos_registrados}/{qtd_alunos}**')
    st.progress(qtd_registrados_praca/qtd_praca, f'Status de Preenchimento das Orientadoras da Praça ***{cidade_login}***: **{qtd_registrados_praca}/{qtd_praca}**')
except ZeroDivisionError:
    st.error('Zero Resultados')

#Primeira Tabela - Confirmação
df_coord = df.query('confirmacao_classificacao_orientadora == "Sim" or confirmacao_classificacao_orientadora == "Não"')
df_coord = df_coord[df_coord['RA'].isin(bd_segmentado['RA'])]

df_tabela_editavel = df_coord.query('confirmacao_classificacao_coordenacao != "Sim" and confirmacao_classificacao_coordenacao != "Não"')
df_tabela_editavel['manter_dados_iguais'] = '-' 
df_tabela_editavel = df_tabela_editavel[['manter_dados_iguais','RA','nome','classificacao_final','motivo_final',
                                            'classificacao_automatica','motivo_classificao_automatica','confirmacao_classificacao_orientadora',
                                            'nova_classificacao_orientadora','novo_motivo_classificacao_orientadora','nova_justificativa_classificacao_orientadora',
                                            'reversao','descricao_caso','plano_intervencao','tier','resposta_argumentacao', 'resposta_rotina_estudos',
                                            'resposta_atividades_extracurriculares','resposta_faltas','resposta_respeita_escola',
                                            'resposta_atividades_obrigatorias_ismart','resposta_colaboracao',
                                            'resposta_atividades_nao_obrigatorias_ismart','resposta_networking','resposta_proatividade',
                                            'resposta_questoes_psiquicas','resposta_questoes_familiares','resposta_questoes_saude',
                                            'resposta_ideacao_suicida','resposta_adaptacao_projeto','resposta_seguranca_profissional',
                                            'resposta_curso_apoiado','resposta_nota_condizente']]

df_tabela_editavel = df_tabela_editavel.merge(bd[['RA', 'Orientadora', 'Segmento','Nota Matemática', 'Nota Português', 'Nota História', 'Nota Geografia', 
                                                        'Nota Inglês', 'Nota Francês/Alemão e Outros', 'Nota Espanhol', 'Nota Química', 
                                                        'Nota Física', 'Nota Biologia', 'Nota ENEM', 'Nota PU', 'media_calibrada']]
                                                        , how='left', on='RA')
df_tabela_editavel.sort_values(by=['Segmento', 'nome'])

colunas_nao_editaveis = df_tabela_editavel.columns.to_list()
colunas_nao_editaveis.remove('manter_dados_iguais')

st.title('Tabela de Confirmação')
with st.form(key='tabela_editavel_cord_confirmacao'):
    edited_df = st.data_editor(
        df_tabela_editavel[['manter_dados_iguais','RA','nome','Orientadora', 'Segmento','classificacao_final'
                            ,'motivo_final','classificacao_automatica','motivo_classificao_automatica','confirmacao_classificacao_orientadora',
                            'nova_classificacao_orientadora','novo_motivo_classificacao_orientadora','nova_justificativa_classificacao_orientadora',
                            'reversao','descricao_caso','plano_intervencao','tier',
                            'resposta_argumentacao','resposta_rotina_estudos','resposta_atividades_extracurriculares','resposta_faltas',
                            'resposta_respeita_escola','resposta_atividades_obrigatorias_ismart','resposta_colaboracao',
                            'resposta_atividades_nao_obrigatorias_ismart','resposta_networking','resposta_proatividade',
                            'resposta_questoes_psiquicas','resposta_questoes_familiares','resposta_questoes_saude','resposta_ideacao_suicida',
                            'resposta_adaptacao_projeto','resposta_seguranca_profissional','resposta_curso_apoiado','resposta_nota_condizente',
                            'Nota Matemática','Nota Português','Nota História','Nota Geografia','Nota Inglês','Nota Francês/Alemão e Outros',
                            'Nota Espanhol','Nota Química','Nota Física','Nota Biologia','Nota ENEM','Nota PU','media_calibrada']],
        column_config={
            "manter_dados_iguais": st.column_config.SelectboxColumn(
                "Manter Dados Iguais?",
                help="Selecione 'Sim' Para Manter e 'Não' Para Alterar",
                options=['Sim', 'Não', '-'],
                required=True
            ),
            "RA": st.column_config.Column(
                "RA",
                required=False
            ),
            "nome": st.column_config.Column(
                "Nome",
                required=False
            ),
            "Orientadora": st.column_config.Column(
                "Orientadora",
                required=False
            ),
            "classificacao_final": st.column_config.Column(
                "Classificação Final",
                required=False
            ),
            "motivo_final": st.column_config.Column(
                "Motivo Classificação Final",
                required=False
            ),
            "classificacao_automatica": st.column_config.Column(
                "Classificação Automatica",
                required=False
            ),
            "motivo_classificao_automatica": st.column_config.Column(
                "Motivo Classificação Automatica",
                required=False
            ),
            "confirmacao_classificacao_orientadora": st.column_config.Column(
                "Orientadora Confirmou a classificação Automatica?",
                required=False
            ),
            "nova_classificacao_orientadora": st.column_config.Column(
                "Classificação da Orientadora",
                required=False
            ),
            "novo_motivo_classificacao_orientadora": st.column_config.Column(
                "Motivo da Orientadora",
                required=False
            ),
            "nova_justificativa_classificacao_orientadora": st.column_config.Column(
                "Justificativa da Orientadora",
                required=False
            ),
            "reversao": st.column_config.Column(
                "Reversão",
                required=False
            ),
            "descricao_caso": st.column_config.Column(
                "Descrição do Caso",
                required=False
            ),
            "plano_intervencao": st.column_config.Column(
                "Plano de Intervenção",
                required=False
            ),
            "tier": st.column_config.Column(
                "Tier",
                required=False
            ),
            "resposta_argumentacao": st.column_config.Column(
                "Resposta - Nivel de Argumentação/Interações",
                required=False
            ),
            "resposta_rotina_estudos": st.column_config.Column(
                "Resposta - Rotina de Estudos Adequada?",
                required=False
            ),
            "resposta_atividades_extracurriculares": st.column_config.Column(
                "Resposta - Atividades Extracurriculares",
                required=False
            ),
            "resposta_faltas": st.column_config.Column(
                "Resposta - Número de Faltas comprometentes?",
                required=False
            ),
            "resposta_respeita_escola": st.column_config.Column(
                "Resposta - Respeita Normas Escolares?",
                required=False
            ),
            "resposta_atividades_obrigatorias_ismart": st.column_config.Column(
                "Resposta - Participa das Atividades Obrigatórias?",
                required=False
            ),
            "resposta_colaboracao": st.column_config.Column(
                "Resposta - É Colaborativo Com Amigos?",
                required=False
            ),
            "resposta_atividades_nao_obrigatorias_ismart": st.column_config.Column(
                "Resposta - Participa das Atividades Não Obrigatórias?",
                required=False
            ),
            "resposta_networking": st.column_config.Column(
                "Resposta - Cultiva Parcerias?",
                required=False
            ),
            "resposta_proatividade": st.column_config.Column(
                "Resposta - É Proativo?",
                required=False
            ),
            "resposta_questoes_psiquicas": st.column_config.Column(
                "Resposta - Apresenta Questões Psíquicas de impacto?",
                required=False
            ),
            "resposta_questoes_familiares": st.column_config.Column(
                "Resposta - Apresenta Questões Familiares de impacto?",
                required=False
            ),
            "resposta_questoes_saude": st.column_config.Column(
                "Resposta - Apresenta Questões Saúde de impacto?",
                required=False
            ),
            "resposta_ideacao_suicida": st.column_config.Column(
                "Resposta - Apresenta Ideação Suicida?",
                required=False
            ),
            "resposta_adaptacao_projeto": st.column_config.Column(
                "Resposta - Se Adaptou ao Projeto?",
                required=False
            ),
            "resposta_seguranca_profissional": st.column_config.Column(
                "Resposta - Tem Segurança Proficional?",
                required=False
            ),
            "resposta_curso_apoiado": st.column_config.Column(
                "Resposta - Deseja Curso Apoiado?",
                required=False
            ),
            "resposta_nota_condizente": st.column_config.Column(
                "Resposta - Nota Condizente Com o Curso Desejado?",
                required=False
            ),
            "Segmento": st.column_config.Column(
                "Segmento",
                required=False
            ),
            "Nota Matemática": st.column_config.NumberColumn(
                "Nota Matemática",
                required=False
            ),
            "Nota Português": st.column_config.NumberColumn(
                "Nota Português",
                required=False
            ),
            "Nota História": st.column_config.NumberColumn(
                "Nota História",
                required=False
            ),
            "Nota Geografia": st.column_config.NumberColumn(
                "Nota Geografia",
                required=False
            ),
            "Nota Inglês": st.column_config.NumberColumn(
                "Nota Inglês",
                required=False
            ),
            "Nota Francês/Alemão e Outros": st.column_config.NumberColumn(
                "Nota Francês/Alemão e Outros",
                required=False
            ),
            "Nota Espanhol": st.column_config.NumberColumn(
                "Nota Espanhol",
                required=False
            ),
            "Nota Química": st.column_config.NumberColumn(
                "Nota Química",                        required=False
            ),        
            "Nota Física": st.column_config.NumberColumn(
                "Nota Física",
                required=False
            ),
            "Nota Biologia": st.column_config.NumberColumn(
                "Nota Biologia",
                required=False
            ),
            "Nota ENEM": st.column_config.NumberColumn(
                "Nota ENEM",
                required=False
            ),
            "Nota PU": st.column_config.NumberColumn(
                "Nota PU",
                required=False
            ),                          
            "media_calibrada": st.column_config.NumberColumn(
                "Média Calibrada",
                required=False
            ),                          
        },
        disabled=colunas_nao_editaveis,
        hide_index=True,
    )
    submit_button = st.form_submit_button(label='REGISTRAR')

if submit_button:
    #Ação de input no sheets
    df_tabela_editavel = edited_df.loc[~edited_df['manter_dados_iguais'].isin(['-'])]
    if df_tabela_editavel.shape[0] == 0:
        st.warning('Revise ao menos um aluno antes de salvar')
    else:
        df_tabela_editavel_sim = df_tabela_editavel.loc[df_tabela_editavel['manter_dados_iguais'].isin(['Sim'])]
        df_tabela_editavel_nao = df_tabela_editavel.loc[df_tabela_editavel['manter_dados_iguais'].isin(['Não'])]
        
        df_tabela_editavel['confirmacao_classificacao_coordenacao'] = df_tabela_editavel['manter_dados_iguais']
        df_tabela_editavel['conclusao_classificacao_final'] = df_tabela_editavel['manter_dados_iguais']
        df_tabela_editavel = df_tabela_editavel[[
            'RA', 'nome', 'resposta_argumentacao', 'resposta_rotina_estudos',
            'resposta_faltas', 'resposta_atividades_extracurriculares', 'resposta_respeita_escola',
            'resposta_atividades_obrigatorias_ismart', 'resposta_colaboracao',
            'resposta_atividades_nao_obrigatorias_ismart', 'resposta_networking',
            'resposta_proatividade', 'resposta_questoes_psiquicas', 'resposta_questoes_familiares',
            'resposta_questoes_saude', 'resposta_ideacao_suicida', 'resposta_adaptacao_projeto',
            'resposta_seguranca_profissional', 'resposta_curso_apoiado', 'resposta_nota_condizente',
            'classificacao_automatica', 'motivo_classificao_automatica',
            'confirmacao_classificacao_orientadora', 'nova_classificacao_orientadora',
            'novo_motivo_classificacao_orientadora', 'nova_justificativa_classificacao_orientadora',
            'reversao', 'descricao_caso', 'plano_intervencao', 'tier', 'confirmacao_classificacao_coordenacao', 
            'classificacao_final', 'motivo_final', 'conclusao_classificacao_final'
        ]]   
        
        df_tabela_editavel['data_submit'] = datetime.now(fuso_horario)
        atualizar_linhas('registro', df_tabela_editavel, 'RA')

#Segunda Tabela - Edição dos Dados                 
df_tabela_editavel = df[df['RA'].isin(bd_segmentado['RA'])]
df_tabela_editavel = df_tabela_editavel.query("conclusao_classificacao_final == 'Não'")
df_tabela_editavel = df_tabela_editavel[['conclusao_classificacao_final','RA','nome','classificacao_final','motivo_final', 'justificativa_classificacao_coord',
                                        'classificacao_automatica','motivo_classificao_automatica','confirmacao_classificacao_orientadora',
                                        'nova_classificacao_orientadora','novo_motivo_classificacao_orientadora','nova_justificativa_classificacao_orientadora',
                                        'reversao','descricao_caso','plano_intervencao','tier','resposta_argumentacao', 'resposta_rotina_estudos',
                                        'resposta_atividades_extracurriculares','resposta_faltas','resposta_respeita_escola',
                                        'resposta_atividades_obrigatorias_ismart','resposta_colaboracao',
                                        'resposta_atividades_nao_obrigatorias_ismart','resposta_networking','resposta_proatividade',
                                        'resposta_questoes_psiquicas','resposta_questoes_familiares','resposta_questoes_saude',
                                        'resposta_ideacao_suicida','resposta_adaptacao_projeto','resposta_seguranca_profissional',
                                        'resposta_curso_apoiado','resposta_nota_condizente', 'confirmacao_classificacao_coordenacao']]
df_tabela_editavel = df_tabela_editavel.merge(bd[['RA', 'Orientadora', 'Segmento','Nota Matemática', 'Nota Português', 'Nota História', 'Nota Geografia', 
                                                        'Nota Inglês', 'Nota Francês/Alemão e Outros', 'Nota Espanhol', 'Nota Química', 
                                                        'Nota Física', 'Nota Biologia', 'Nota ENEM', 'Nota PU', 'media_calibrada']]
                                                        , how='left', on='RA')
df_tabela_editavel.sort_values(by=['Segmento', 'nome'])

colunas_nao_editaveis = df_tabela_editavel.columns.to_list()
colunas_nao_editaveis = [col for col in colunas_nao_editaveis if col not in ['conclusao_classificacao_final', 'justificativa_classificacao_coord', 
                                                                                'classificacao_final', 'motivo_final', 'tier', 'plano_intervencao',
                                                                                'descricao_caso', 'reversao', 
                                                                            ]]
df_tabela_editavel['justificativa_classificacao_coord'] = df_tabela_editavel['justificativa_classificacao_coord'].astype(str)
df_tabela_editavel['conclusao_classificacao_final'] = '-'

st.title('Tabela de Edição')
with st.form(key='tabela_editavel_cord_edicao'):
    edited_df = st.data_editor(
        df_tabela_editavel[['conclusao_classificacao_final','RA','nome','classificacao_final', 'motivo_final','justificativa_classificacao_coord',
                            'reversao','descricao_caso','plano_intervencao','tier', 'Orientadora', 'Segmento',
                            'classificacao_automatica','motivo_classificao_automatica', 'confirmacao_classificacao_orientadora','nova_classificacao_orientadora',
                            'novo_motivo_classificacao_orientadora','nova_justificativa_classificacao_orientadora',
                            'resposta_argumentacao','resposta_rotina_estudos','resposta_atividades_extracurriculares','resposta_faltas',
                            'resposta_respeita_escola','resposta_atividades_obrigatorias_ismart','resposta_colaboracao',
                            'resposta_atividades_nao_obrigatorias_ismart','resposta_networking','resposta_proatividade',
                            'resposta_questoes_psiquicas','resposta_questoes_familiares','resposta_questoes_saude','resposta_ideacao_suicida',
                            'resposta_adaptacao_projeto','resposta_seguranca_profissional','resposta_curso_apoiado','resposta_nota_condizente',
                            'Nota Matemática','Nota Português','Nota História','Nota Geografia','Nota Inglês','Nota Francês/Alemão e Outros',
                            'Nota Espanhol','Nota Química','Nota Física','Nota Biologia','Nota ENEM','Nota PU','media_calibrada']],
        column_config={
            "conclusao_classificacao_final": st.column_config.SelectboxColumn(
                "Confirmar Classificação Final?",
                help='Selecione "Sim" ou "Não" Para Finalizar As Alterações. ' \
                '"Sim" Se você Manteve a Classificação Igual e "Não" no Contrário',
                options=['Sim', 'Não', '-'],
                required=True
            ),
            "justificativa_classificacao_coord": st.column_config.TextColumn(
                "Justificativa da Coordenadora",
                required=False
            ),
            "RA": st.column_config.Column(
                "RA",
                required=False
            ),
            "nome": st.column_config.Column(
                "Nome",
                required=False
            ),
            "Orientadora": st.column_config.Column(
                "Orientadora",
                required=False
            ),
            "classificacao_final": st.column_config.SelectboxColumn(
                "Classificação Final",
                options=['Destaque', 'Pré-Destaque', 'Mediano', 'Atenção', 'Crítico', 'Crítico OP'],
                required=False
            ),
            "motivo_final": st.column_config.Column(
                "Motivo Classificação Final",
                help='Acadêmico; Perfil; Familiar; Saúde; Psicológico; Curso não apoiado; Curso concorrido; Escolha frágil',
                required=False
            ),
            "classificacao_automatica": st.column_config.Column(
                "Classificação Automatica",
                required=False
            ),
            "motivo_classificao_automatica": st.column_config.Column(
                "Motivo Classificação Automatica",
                required=False
            ),
            "confirmacao_classificacao_orientadora": st.column_config.Column(
                "Orientadora Confirmou a classificação Automatica?",
                required=False
            ),
            "nova_classificacao_orientadora": st.column_config.Column(
                "Classificação da Orientadora",
                required=False
            ),
            "novo_motivo_classificacao_orientadora": st.column_config.Column(
                "Motivo da Orientadora",
                help='Acadêmico; Perfil; Familiar; Saúde; Psicológico; Curso não apoiado; Curso concorrido; Escolha frágil',
                required=False
            ),
            "nova_justificativa_classificacao_orientadora": st.column_config.Column(
                "Justificativa da Orientadora",
                required=False
            ),
            "reversao": st.column_config.SelectboxColumn(
                "Reversão",
                options=["Alta", "Média", "Baixa", '-'],
                required=False
            ),
            "descricao_caso": st.column_config.Column(
                "Descrição do Caso",
                required=False
            ),
            "plano_intervencao": st.column_config.Column(
                "Plano de Intervenção",
                required=False
            ),
            "tier": st.column_config.Column(
                "Tier",
                help='2c; 2i; 3c; 3i; 4',
                required=False
            ),
            "resposta_argumentacao": st.column_config.Column(
                "Resposta - Nivel de Argumentação/Interações",
                required=False
            ),
            "resposta_rotina_estudos": st.column_config.Column(
                "Resposta - Rotina de Estudos Adequada?",
                required=False
            ),
            "resposta_atividades_extracurriculares": st.column_config.Column(
                "Resposta - Atividades Extracurriculares",
                required=False
            ),
            "resposta_faltas": st.column_config.Column(
                "Resposta - Número de Faltas comprometentes?",
                required=False
            ),
            "resposta_respeita_escola": st.column_config.Column(
                "Resposta - Respeita Normas Escolares?",
                required=False
            ),
            "resposta_atividades_obrigatorias_ismart": st.column_config.Column(
                "Resposta - Participa das Atividades Obrigatórias?",
                required=False
            ),
            "resposta_colaboracao": st.column_config.Column(
                "Resposta - É Colaborativo Com Amigos?",
                required=False
            ),
            "resposta_atividades_nao_obrigatorias_ismart": st.column_config.Column(
                "Resposta - Participa das Atividades Não Obrigatórias?",
                required=False
            ),
            "resposta_networking": st.column_config.Column(
                "Resposta - Cultiva Parcerias?",
                required=False
            ),
            "resposta_proatividade": st.column_config.Column(
                "Resposta - É Proativo?",
                required=False
            ),
            "resposta_questoes_psiquicas": st.column_config.Column(
                "Resposta - Apresenta Questões Psíquicas de impacto?",
                required=False
            ),
            "resposta_questoes_familiares": st.column_config.Column(
                "Resposta - Apresenta Questões Familiares de impacto?",
                required=False
            ),
            "resposta_questoes_saude": st.column_config.Column(
                "Resposta - Apresenta Questões Saúde de impacto?",
                required=False
            ),
            "resposta_ideacao_suicida": st.column_config.Column(
                "Resposta - Apresenta Ideação Suicida?",
                required=False
            ),
            "resposta_adaptacao_projeto": st.column_config.Column(
                "Resposta - Se Adaptou ao Projeto?",
                required=False
            ),
            "resposta_seguranca_profissional": st.column_config.Column(
                "Resposta - Tem Segurança Proficional?",
                required=False
            ),
            "resposta_curso_apoiado": st.column_config.Column(
                "Resposta - Deseja Curso Apoiado?",
                required=False
            ),
            "resposta_nota_condizente": st.column_config.Column(
                "Resposta - Nota Condizente Com o Curso Desejado?",
                required=False
            ),
            "Segmento": st.column_config.Column(
                "Segmento",
                required=False
            ),
            "Nota Matemática": st.column_config.NumberColumn(
                "Nota Matemática",
                required=False
            ),
            "Nota Português": st.column_config.NumberColumn(
                "Nota Português",
                required=False
            ),
            "Nota História": st.column_config.NumberColumn(
                "Nota História",
                required=False
            ),
            "Nota Geografia": st.column_config.NumberColumn(
                "Nota Geografia",
                required=False
            ),
            "Nota Inglês": st.column_config.NumberColumn(
                "Nota Inglês",
                required=False
            ),
            "Nota Francês/Alemão e Outros": st.column_config.NumberColumn(
                "Nota Francês/Alemão e Outros",
                required=False
            ),
            "Nota Espanhol": st.column_config.NumberColumn(
                "Nota Espanhol",
                required=False
            ),
            "Nota Química": st.column_config.NumberColumn(
                "Nota Química",                        required=False
            ),        
            "Nota Física": st.column_config.NumberColumn(
                "Nota Física",
                required=False
            ),
            "Nota Biologia": st.column_config.NumberColumn(
                "Nota Biologia",
                required=False
            ),
            "Nota ENEM": st.column_config.NumberColumn(
                "Nota ENEM",
                required=False
            ),
            "Nota PU": st.column_config.NumberColumn(
                "Nota PU",
                required=False
            ),                          
            "media_calibrada": st.column_config.NumberColumn(
                "Média Calibrada",
                required=False
            ),                          
        },
        disabled=colunas_nao_editaveis,
        hide_index=True,
    )
    submit_button = st.form_submit_button(label='REGISTRAR')
if submit_button:
    #Ação de input no sheets
    df_tabela_editavel = edited_df.query("conclusao_classificacao_final == 'Sim' or conclusao_classificacao_final == 'Não'")
    if df_tabela_editavel.shape[0] > 0:
        df_tabela_editavel = df_tabela_editavel[[
            'RA', 'nome', 'resposta_argumentacao', 'resposta_rotina_estudos',
            'resposta_faltas', 'resposta_atividades_extracurriculares', 'resposta_respeita_escola',
            'resposta_atividades_obrigatorias_ismart', 'resposta_colaboracao',
            'resposta_atividades_nao_obrigatorias_ismart', 'resposta_networking',
            'resposta_proatividade', 'resposta_questoes_psiquicas', 'resposta_questoes_familiares',
            'resposta_questoes_saude', 'resposta_ideacao_suicida', 'resposta_adaptacao_projeto',
            'resposta_seguranca_profissional', 'resposta_curso_apoiado', 'resposta_nota_condizente',
            'classificacao_automatica', 'motivo_classificao_automatica',
            'confirmacao_classificacao_orientadora', 'nova_classificacao_orientadora',
            'novo_motivo_classificacao_orientadora', 'nova_justificativa_classificacao_orientadora',
            'reversao', 'descricao_caso', 'plano_intervencao', 'tier', 'justificativa_classificacao_coord',
            'classificacao_final', 'motivo_final', 'conclusao_classificacao_final'
        ]]   
        df_tabela_editavel['data_submit'] = datetime.now(fuso_horario)
        df_tabela_editavel['confirmacao_classificacao_coordenacao'] = df_tabela_editavel['conclusao_classificacao_final']
        df_tabela_editavel['conclusao_classificacao_final'] = 'Sim'
        atualizar_linhas('registro', df_tabela_editavel, 'RA')
    else:
        st.warning('Revise ao menos um aluno antes de registrar')
