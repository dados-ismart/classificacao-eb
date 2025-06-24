import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from paginas.funcoes import ler_sheets,ler_sheets_cache, registrar, classificar, retornar_indice, atualizar_linha

fuso_horario = pytz.timezone('America/Sao_Paulo')
email = st.user.email 

caixa_classificacao = ['Destaque', 'Pré-Destaque', 'Mediano', 'Atenção', 'Crítico', 'Crítico OP']
caixa_justificativa_classificacao = ['Acadêmico', 'Perfil', 'Familiar', 'Saúde', 'Psicológico', 'Curso não apoiado', 'Curso concorrido', 'Escolha frágil']
caixa_tier = ['2c', '2i', '3c', '3i', '4']

#importar e tratar datasets
bd = ler_sheets_cache('bd')
bd = bd.dropna(subset=['RA - NOME'])
df = ler_sheets('registro')
df_historico = ler_sheets_cache('historico')
bd = bd.merge(df[['RA', 'confirmacao_classificacao_orientadora','conclusao_classificacao_final']], how='left', on='RA')
bd = bd.sort_values(by=['conclusao_classificacao_final','confirmacao_classificacao_orientadora'], ascending = False)
df_login = ler_sheets_cache('login')

orientadora = df_login.loc[df_login['email'] == email, 'Orientadora'].iloc[0]

st.title('Formulário de Classificação')

# filtros
bd_segmentado = bd.query(f"Orientadora == '{orientadora}'")
bd_segmentado = bd_segmentado.query("confirmacao_classificacao_orientadora != 'Não' and confirmacao_classificacao_orientadora != 'Sim'")

col1, col2, col3 = st.columns(3)
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
st.divider()

#Seleção dos alunos
ra_nome_bd = bd_segmentado['RA - NOME']
ra_nome = st.selectbox(
"Seleção dos Alunos",
ra_nome_bd,
index=None,
placeholder="RA")
if 'ra_nome' not in st.session_state:
    st.session_state['ra_nome'] = ra_nome
if st.session_state['ra_nome'] != ra_nome:
    try:
        del st.session_state['classificacao_atual']
        del st.session_state['motivo_atual']
        del st.session_state['confirmacao_alterada']
    except:
        pass
    del st.session_state['ra_nome']

# progresso
alunos_orientadora_total = bd.query(f"Orientadora == '{orientadora}'")
alunos_orientadora_total_registrados = alunos_orientadora_total.query("confirmacao_classificacao_orientadora == 'Não' or confirmacao_classificacao_orientadora == 'Sim'")
try:
    st.progress(alunos_orientadora_total_registrados.shape[0]/alunos_orientadora_total.shape[0], f'Você registrou: **{alunos_orientadora_total_registrados.shape[0]}/{alunos_orientadora_total.shape[0]}**')
except ZeroDivisionError:
    st.error('Zero Resultados')

#Painel Micro
if ra_nome is not None:
    #Transformação do RA
    try:
        st.session_state["ra"] = bd.loc[bd['RA - NOME'] == ra_nome, 'RA'].iloc[0]
        ra = None
        ra = st.session_state["ra"]
    except IndexError:
        st.warning('Aluno não encontrado na base.')
        st.stop()

    #Variaveis e calulo de Materias escolares
    nome = bd.loc[bd['RA'] == ra, 'Nome'].iloc[0]
    segmento = bd.loc[bd['RA'] == ra, 'Segmento'].iloc[0]
    ano = bd.loc[bd['RA'] == ra, 'Ano'].iloc[0]

    matematica = bd.loc[bd['RA'] == ra, 'Nota Matemática'].iloc[0]
    ingles = bd.loc[bd['RA'] == ra, 'Nota Inglês'].iloc[0]
    portugues = bd.loc[bd['RA'] == ra, 'Nota Português'].iloc[0]
    outras_linguas = bd.loc[bd['RA'] == ra, 'Nota Francês/Alemão e Outros'].iloc[0]
    historia = bd.loc[bd['RA'] == ra, 'Nota História'].iloc[0]
    espanhol = bd.loc[bd['RA'] == ra, 'Nota Espanhol'].iloc[0]
    geografia = bd.loc[bd['RA'] == ra, 'Nota Geografia'].iloc[0]
    biologia = bd.loc[bd['RA'] == ra, 'Nota Biologia'].iloc[0]
    quimica = bd.loc[bd['RA'] == ra, 'Nota Química'].iloc[0]
    fisica = bd.loc[bd['RA'] == ra, 'Nota Física'].iloc[0]
    enem = bd.loc[bd['RA'] == ra, 'Nota ENEM'].iloc[0]
    pu = bd.loc[bd['RA'] == ra, 'Nota PU'].iloc[0]

    media_calibrada = bd.loc[bd['RA'] == ra, 'media_calibrada'].iloc[0]
    if media_calibrada == '#N/D': 
        st.error('Escola do aluno não encontrada na planilha')
        st.stop()

    if matematica == '-':
        matematica = media_calibrada
    if portugues == '-':
        portugues = media_calibrada

    qtd_somas_ciencias_naturais = 0
    ciencias_naturais = 0
    if fisica != '-':
        ciencias_naturais += fisica
        qtd_somas_ciencias_naturais += 1
    if quimica != '-':
        ciencias_naturais += quimica
        qtd_somas_ciencias_naturais += 1
    if biologia != '-':
        ciencias_naturais += biologia
        qtd_somas_ciencias_naturais += 1
    try:
        ciencias_naturais = ciencias_naturais/qtd_somas_ciencias_naturais
    except:
        ciencias_naturais = media_calibrada

    qtd_somas_idiomas = 0
    idiomas = 0
    if ingles != '-':
        idiomas += ingles
        qtd_somas_idiomas += 1
    if outras_linguas != '-':
        idiomas += outras_linguas
        qtd_somas_idiomas += 1
    if espanhol != '-':
        idiomas += espanhol
        qtd_somas_idiomas += 1

    try:
        idiomas = idiomas/qtd_somas_idiomas
    except:
        idiomas = media_calibrada

    qtd_somas_humanas = 0
    humanas = 0
    if geografia != '-':
        humanas += geografia
        qtd_somas_humanas += 1
    if historia != '-':
        humanas += historia
        qtd_somas_humanas += 1

    try:
        humanas = humanas/qtd_somas_humanas
    except:
        humanas = media_calibrada

    #Painel
    st.title('Aluno')
    col1, col2 = st.columns([2, 5])
    col1.metric("RA", ra, border=True)
    col2.metric("Nome", nome, border=True)
    st.metric("Segmento", segmento, border=True)
    st.divider()
    st.header('Notas')
    st.subheader(f'Média calibrada: {media_calibrada:.2f}')
    col1, col2, col3 = st.columns(3)
    col1.metric("Matemática", f'{matematica:.2f}', border=True)
    col2.metric("Português", f'{portugues:.2f}', border=True)
    try:
        col3.metric("Humanas", f"{humanas:.2f}", border=True)
    except:
        col3.metric("Humanas", f"{0}", border=True)
    col1, col2, col3 = st.columns(3)
    try:
        col1.metric("Idiomas", f"{idiomas:.2f}", border=True)
    except:
        col1.metric("Idiomas", f"{0}", border=True)
    col2.metric("Ciências Naturais", f'{ciencias_naturais:.2f}', border=True)
    with st.expander("Notas detalhadas"):
        st.subheader('Ciências Naturais')
        col1, col2, col3 = st.columns(3)
        try:
            col1.metric('Biologia', f'{biologia:.2f}', border=True)
        except:
            col1.metric('Biologia', biologia, border=True)
        try:
            col2.metric('Química', f'{quimica:.2f}', border=True)
        except:
            col2.metric('Química', quimica, border=True)
        try:
            col3.metric('Física', f'{fisica:.2f}', border=True)
        except:
            col3.metric('Física', fisica, border=True)
        st.subheader('Idiomas')
        col1, col2, col3 = st.columns(3)
        try:
            col1.metric('Inglês', f'{ingles:.2f}', border=True)
        except:
            col1.metric('Inglês', ingles, border=True)
        try:
            col2.metric('Outras Línguas', f'{outras_linguas:.2f}', border=True)
        except:
            col2.metric('Outras Línguas', outras_linguas, border=True)
        try:
            col3.metric('Espanhol', f'{espanhol:.2f}', border=True)
        except:
            col3.metric('Espanhol', espanhol, border=True)
        st.subheader('Humanas')
        col1, col2 = st.columns(2)
        try:
            col1.metric('Geografia', f'{geografia:.2f}', border=True)
        except:
            col1.metric('Geografia', geografia, border=True)
        try:
            col2.metric('História', f'{historia:.2f}', border=True)
        except:
            col2.metric('História', historia, border=True)

    col1, col2 = st.columns(2)
    try:
        col1.metric("ENEM", f'{enem:.2f}', border=True)
    except:
        col1.metric("ENEM", f"{enem}", border=True)
    try:
        col2.metric("PU", f'{pu:.2f}', border=True)
    except:
        col2.metric("PU", f"{pu}", border=True)


    #formulario
    st.divider()
    caixa_sim_nao = ['Não', 'Sim']
    caixa_reversao = ["Alta", "Média", "Baixa"]
    #Variaveis Registro
    if df.query(f'RA == {ra}').empty:
        if not df_historico.query(f'RA == {ra}').empty:
            registro_resposta_argumentacao = df_historico.loc[df_historico['RA'] == ra, 'resposta_argumentacao'].iloc[0]
            registro_resposta_rotina_estudos = df_historico.loc[df_historico['RA'] == ra, 'resposta_rotina_estudos'].iloc[0]
            registro_resposta_faltas = df_historico.loc[df_historico['RA'] == ra, 'resposta_faltas'].iloc[0]
            registro_resposta_atividades_extracurriculares = df_historico.loc[df_historico['RA'] == ra, 'resposta_atividades_extracurriculares'].iloc[0]
            registro_resposta_respeita_escola = df_historico.loc[df_historico['RA'] == ra, 'resposta_respeita_escola'].iloc[0]
            registro_resposta_atividades_obrigatorias_ismart = df_historico.loc[df_historico['RA'] == ra, 'resposta_atividades_obrigatorias_ismart'].iloc[0]
            registro_resposta_colaboracao = df_historico.loc[df_historico['RA'] == ra, 'resposta_colaboracao'].iloc[0]
            registro_resposta_atividades_nao_obrigatorias_ismart = df_historico.loc[df_historico['RA'] == ra, 'resposta_atividades_nao_obrigatorias_ismart'].iloc[0]
            registro_resposta_networking = df_historico.loc[df_historico['RA'] == ra, 'resposta_networking'].iloc[0]
            registro_resposta_proatividade = df_historico.loc[df_historico['RA'] == ra, 'resposta_proatividade'].iloc[0]
            registro_resposta_questoes_psiquicas = df_historico.loc[df_historico['RA'] == ra, 'resposta_questoes_psiquicas'].iloc[0]
            registro_resposta_questoes_familiares = df_historico.loc[df_historico['RA'] == ra, 'resposta_questoes_familiares'].iloc[0]
            registro_resposta_questoes_saude = df_historico.loc[df_historico['RA'] == ra, 'resposta_questoes_saude'].iloc[0]
            registro_resposta_ideacao_suicida = df_historico.loc[df_historico['RA'] == ra, 'resposta_ideacao_suicida'].iloc[0]
            registro_resposta_adaptacao_projeto = df_historico.loc[df_historico['RA'] == ra, 'resposta_adaptacao_projeto'].iloc[0]
            registro_resposta_seguranca_profissional = df_historico.loc[df_historico['RA'] == ra, 'resposta_seguranca_profissional'].iloc[0]
            registro_resposta_curso_apoiado = df_historico.loc[df_historico['RA'] == ra, 'resposta_curso_apoiado'].iloc[0]
            registro_resposta_nota_condizente = df_historico.loc[df_historico['RA'] == ra, 'resposta_nota_condizente'].iloc[0]
        else:
            registro_resposta_argumentacao = None
            registro_resposta_rotina_estudos = None
            registro_resposta_faltas = None
            registro_resposta_atividades_extracurriculares = None
            registro_resposta_respeita_escola = None
            registro_resposta_atividades_obrigatorias_ismart = None
            registro_resposta_colaboracao = None
            registro_resposta_atividades_nao_obrigatorias_ismart = None
            registro_resposta_networking = None
            registro_resposta_proatividade = None
            registro_resposta_questoes_psiquicas = None
            registro_resposta_questoes_familiares = None
            registro_resposta_questoes_saude = None
            registro_resposta_ideacao_suicida = None
            registro_resposta_adaptacao_projeto = None
            registro_resposta_seguranca_profissional = None
            registro_resposta_curso_apoiado = None
            registro_resposta_nota_condizente = None
    else:
        registro_resposta_argumentacao = df.loc[df['RA'] == ra, 'resposta_argumentacao'].iloc[0]
        registro_resposta_rotina_estudos = df.loc[df['RA'] == ra, 'resposta_rotina_estudos'].iloc[0]
        registro_resposta_faltas = df.loc[df['RA'] == ra, 'resposta_faltas'].iloc[0]
        registro_resposta_atividades_extracurriculares = df.loc[df['RA'] == ra, 'resposta_atividades_extracurriculares'].iloc[0]
        registro_resposta_respeita_escola = df.loc[df['RA'] == ra, 'resposta_respeita_escola'].iloc[0]
        registro_resposta_atividades_obrigatorias_ismart = df.loc[df['RA'] == ra, 'resposta_atividades_obrigatorias_ismart'].iloc[0]
        registro_resposta_colaboracao = df.loc[df['RA'] == ra, 'resposta_colaboracao'].iloc[0]
        registro_resposta_atividades_nao_obrigatorias_ismart = df.loc[df['RA'] == ra, 'resposta_atividades_nao_obrigatorias_ismart'].iloc[0]
        registro_resposta_networking = df.loc[df['RA'] == ra, 'resposta_networking'].iloc[0]
        registro_resposta_proatividade = df.loc[df['RA'] == ra, 'resposta_proatividade'].iloc[0]
        registro_resposta_questoes_psiquicas = df.loc[df['RA'] == ra, 'resposta_questoes_psiquicas'].iloc[0]
        registro_resposta_questoes_familiares = df.loc[df['RA'] == ra, 'resposta_questoes_familiares'].iloc[0]
        registro_resposta_questoes_saude = df.loc[df['RA'] == ra, 'resposta_questoes_saude'].iloc[0]
        registro_resposta_ideacao_suicida = df.loc[df['RA'] == ra, 'resposta_ideacao_suicida'].iloc[0]
        registro_resposta_adaptacao_projeto = df.loc[df['RA'] == ra, 'resposta_adaptacao_projeto'].iloc[0]
        registro_resposta_seguranca_profissional = df.loc[df['RA'] == ra, 'resposta_seguranca_profissional'].iloc[0]
        registro_resposta_curso_apoiado = df.loc[df['RA'] == ra, 'resposta_curso_apoiado'].iloc[0]
        registro_resposta_nota_condizente = df.loc[df['RA'] == ra, 'resposta_nota_condizente'].iloc[0]

    with st.form(key='formulario'):
        #listas do formulario
        caixa_argumentacao = ['Superficial - apenas reproduz',
                            'Argumenta e se posiciona, trazendo sua opinião de forma consistente',
                            'Sempre traz elementos além dos solicitados']
        caixa_rotina_estudos = ['Não', 'Precisa melhorar', 'Sim']
        caixa_atividades_extracurriculares = ['Nenhuma', 'Uma', 'Mais de uma']
        caixa_nunca_eventualmente_sempre = ['Nunca', 'Eventualmente', 'Sempre']
        caixa_networking = ['Tem dificuldade', 'Sim (dentro da escola)', 'Sim, (além da escola)']
        caixa_fragilidade = ['Não',
                            'Sim, com baixa probabilidade de impacto',
                            'Sim, com média probabilidade de impacto',
                            'Sim, com alta probabilidade de impacto']
        caixa_ideacao_suicida = ['Não', 'Sim, estável', 'Sim, em risco']
        caixa_coerencia_enem = ['Sim', 'Não', 'Sim para ser recomendado pelo Ismart para cursinho Med']
        caixa_nota_condizente = ['Não', 'Sim', 'Sim para ser recomendado pelo Ismart para cursinho Med']
        #Preenchimento
        st.header('Preencha o formulário')
    
        st.divider()
        st.subheader('Acadêmico')
        resposta_argumentacao = st.radio('**O aluno traz conteúdos consistentes nas suas argumentações/interações (com orientadoras, escola parceira, outros)?**', caixa_argumentacao, index=retornar_indice(lista=caixa_argumentacao,variavel=registro_resposta_argumentacao))
        resposta_rotina_estudos = st.radio('**O aluno tem uma rotina de estudos adequada as suas necessidades?**', caixa_rotina_estudos, index=retornar_indice(lista=caixa_rotina_estudos,variavel=registro_resposta_rotina_estudos), horizontal=True)
        resposta_atividades_extracurriculares = st.radio('**O aluno faz atividades acadêmicas extracurriculares com vias a desenvolver seu talento acadêmico? (olimpiadas, projetos de iniciação cientifica, programação, Cultura inglesa/Inglês/Prep)**', caixa_atividades_extracurriculares, index=retornar_indice(lista=caixa_atividades_extracurriculares,variavel=registro_resposta_atividades_extracurriculares), horizontal=True)
        resposta_faltas = st.radio('**O aluno está com número de faltas e/ou atrasos que compromete o seu desempenho acadêmico?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_faltas), horizontal=True)
        
        st.divider()
        st.subheader('Perfil')
        resposta_respeita_escola = st.radio('**O aluno respeita as normas da escola parceira?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_respeita_escola), horizontal=True)
        resposta_atividades_obrigatorias_ismart = st.radio('**O aluno aproveita as atividades obrigatórias oferecidas pelo Ismart? Qualidade do envolvimento nas atividades (pressupõe participação em 100% das atividades)**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_atividades_obrigatorias_ismart), horizontal=True)
        resposta_colaboracao = st.radio('**É colaborativo com os amigos? Oferece ajuda?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_colaboracao), horizontal=True)
        resposta_atividades_nao_obrigatorias_ismart = st.radio('**O aluno aproveita e participa das atividades não obrigatórias do Ismart?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_atividades_nao_obrigatorias_ismart), horizontal=True)
        resposta_networking = st.radio('**O aluno cultiva relação na escola parceira e em outros contextos que a escola possibilita?**', caixa_networking, index=retornar_indice(lista=caixa_networking,variavel=registro_resposta_networking), horizontal=True)
        resposta_proatividade = st.radio('**O aluno é pró-ativo, ou seja, traz questionamentos críticos, sugestões, problemas, soluções, dúvidas?**', caixa_nunca_eventualmente_sempre, index=retornar_indice(lista=caixa_nunca_eventualmente_sempre,variavel=registro_resposta_proatividade), horizontal=True)
        
        st.divider()
        st.subheader('Psicológico/Questões Familiares/Saúde')
        resposta_questoes_psiquicas = st.radio('**O aluno apresenta questões psíquicas que podem vir a impactar seu desenvolvimento no projeto?**', caixa_fragilidade, index=retornar_indice(lista=caixa_fragilidade,variavel=registro_resposta_questoes_psiquicas))
        resposta_questoes_familiares = st.radio('**O aluno apresenta questões familiares que podem vir a impactar seu desenvolvimento no projeto?**', caixa_fragilidade, index=retornar_indice(lista=caixa_fragilidade,variavel=registro_resposta_questoes_familiares))
        resposta_questoes_saude = st.radio('**O aluno apresenta questões de saúde que podem vir a impactar seu desenvolvimento no projeto?**', caixa_fragilidade, index=retornar_indice(lista=caixa_fragilidade,variavel=registro_resposta_questoes_saude))
        resposta_ideacao_suicida = st.radio('**O aluno apresenta ideação suicida?**', caixa_ideacao_suicida, index=retornar_indice(lista=caixa_ideacao_suicida,variavel=registro_resposta_ideacao_suicida), horizontal=True)
    
        if ano == '8º EF' or ano == '1º EM':
            st.divider()
            st.subheader('Questão de 8°/1° ano')
            resposta_adaptacao_projeto = st.radio('**O aluno conseguiu se adaptar bem ao projeto?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_adaptacao_projeto))
        else:
            resposta_adaptacao_projeto = '-'

        if ano == '2º EM':
            st.divider()
            st.subheader('Questão de 2° ano')
            resposta_seguranca_profissional = st.radio('**O aluno está seguro em seu processo de escolha profissional?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_seguranca_profissional))
        else:
            resposta_seguranca_profissional = '-'

        if ano == '3º EM':
            st.divider()
            st.subheader('Questões de 3° ano')
            resposta_curso_apoiado = st.radio('**O aluno escolheu um curso apoiado pelo Ismart?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_curso_apoiado))
            resposta_nota_condizente = st.radio('**O aluno tem desempenho acadêmico e demais notas (ENEM e Prova Única) condizentes com sua estratégia de vestibulares?**', caixa_nota_condizente, index=retornar_indice(lista=caixa_nota_condizente,variavel=registro_resposta_nota_condizente))
            resposta_seguranca_profissional = st.radio('**O aluno está seguro com a escolha profissional?**', caixa_sim_nao, index=retornar_indice(lista=caixa_sim_nao,variavel=registro_resposta_seguranca_profissional))
        else:
            resposta_curso_apoiado = '-'
            resposta_nota_condizente = '-'
            if ano != '2º EM':
                resposta_seguranca_profissional = '-'

        submit_button = st.form_submit_button(label='SALVAR')
        if submit_button:
            # ação de input no sheets
            if not resposta_argumentacao or not resposta_rotina_estudos or not resposta_atividades_extracurriculares or not resposta_faltas:
                st.warning('Questões em **Acadêmico** do formulário não estão preenchidas')
                st.stop()
            if not resposta_respeita_escola or not resposta_atividades_obrigatorias_ismart or not resposta_colaboracao or not resposta_atividades_nao_obrigatorias_ismart or not resposta_networking or not resposta_proatividade:
                st.warning('Questões em **Perfil** do formulário não estão preenchidas')
                st.stop()
            if not resposta_questoes_psiquicas or not resposta_questoes_familiares or not resposta_questoes_saude or not resposta_ideacao_suicida:
                st.warning('Questões em **Psicológico/Questões Familiares/Saúde** do formulário não estão preenchidas')
                st.stop()
            if not resposta_adaptacao_projeto or not resposta_seguranca_profissional or not resposta_curso_apoiado or not resposta_nota_condizente:
                st.warning('**Questões de ano** do formulário não estão preenchidas')
                st.stop()
            else:
                df_insert = pd.DataFrame([{
                                        'RA': ra,
                                        'nome': nome,
                                        'data_submit': datetime.now(fuso_horario),
                                        'resposta_argumentacao': resposta_argumentacao,
                                        'resposta_rotina_estudos': resposta_rotina_estudos,
                                        'resposta_faltas': resposta_faltas,
                                        'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,
                                        'resposta_respeita_escola': resposta_respeita_escola,
                                        'resposta_atividades_obrigatorias_ismart': resposta_atividades_obrigatorias_ismart,
                                        'resposta_colaboracao': resposta_colaboracao,
                                        'resposta_atividades_nao_obrigatorias_ismart': resposta_atividades_nao_obrigatorias_ismart,
                                        'resposta_networking': resposta_networking,
                                        'resposta_proatividade': resposta_proatividade,
                                        'resposta_questoes_psiquicas': resposta_questoes_psiquicas,
                                        'resposta_questoes_familiares': resposta_questoes_familiares,
                                        'resposta_questoes_saude': resposta_questoes_saude,
                                        'resposta_ideacao_suicida': resposta_ideacao_suicida,
                                        'resposta_adaptacao_projeto': resposta_adaptacao_projeto,
                                        'resposta_seguranca_profissional': resposta_seguranca_profissional,
                                        'resposta_curso_apoiado': resposta_curso_apoiado,
                                        'resposta_nota_condizente': resposta_nota_condizente,
                                        'classificacao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0],
                                        'motivo_classificao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1],
                                        }])
                if df.query(f"RA == {ra}").empty:
                    registrar(df_insert, 'registro')
                else:
                    df_insert = df_insert.to_dict(orient='records')[0]
                    atualizar_linha('registro', ra, df_insert)

    if not df.query(f"RA == {ra} and classificacao_automatica == classificacao_automatica").empty:
        #Variaveis do sheets
        classificacao_automatica = df.loc[df['RA'] == ra, 'classificacao_automatica'].iloc[0]
        motivo_classificao_automatica = df.loc[df['RA'] == ra, 'motivo_classificao_automatica'].iloc[0]
        nova_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_classificacao_orientadora'].iloc[0]
        novo_motivo_classificacao_orientadora = df.loc[df['RA'] == ra, 'novo_motivo_classificacao_orientadora'].iloc[0]
        nova_justificativa_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_justificativa_classificacao_orientadora'].iloc[0]
        descricao_caso = df.loc[df['RA'] == ra, 'descricao_caso'].iloc[0]
        plano_intervencao = df.loc[df['RA'] == ra, 'plano_intervencao'].iloc[0]
        confirmacao_classificacao_coordenacao = df.loc[df['RA'] == ra, 'confirmacao_classificacao_coordenacao'].iloc[0]
        classificacao_final = df.loc[df['RA'] == ra, 'classificacao_final'].iloc[0]
        motivo_final = df.loc[df['RA'] == ra, 'motivo_final'].iloc[0]

        #
        if 'confirmacao_alterada' not in st.session_state:
            st.session_state['confirmacao_alterada'] = 'Não'

        if st.session_state['confirmacao_alterada'] == 'Não':
            st.session_state['classificacao_atual'] = classificacao_automatica
            st.session_state['motivo_atual'] = motivo_classificao_automatica

        st.title('Confirmar classificação')
        st.metric("Classificação", st.session_state['classificacao_atual'], border=True)
        st.metric("Motivo", st.session_state['motivo_atual'], border=True)

        if st.session_state['confirmacao_alterada'] == 'Sim':
            resposta_confirmar_classificacao = 'Não'
        else:
            resposta_confirmar_classificacao = st.selectbox("Confirma classificação?",caixa_sim_nao,index=1,placeholder="Confirma classificação?")

        if resposta_confirmar_classificacao == 'Não' and st.session_state['confirmacao_alterada'] == 'Não':
            with st.form(key='formulario_registrar_orientadora'):
                resposta_nova_classificacao_orientadora = st.selectbox("Nova classificação",caixa_classificacao,index=None,placeholder="Nova classificação")
                resposta_novo_motivo_classificacao_orientadora_lista = st.multiselect("Novo motivo da classificação",caixa_justificativa_classificacao,placeholder="Novo motivo da classificação")
                resposta_novo_motivo_classificacao_orientadora = ''
                for i in resposta_novo_motivo_classificacao_orientadora_lista:
                    resposta_novo_motivo_classificacao_orientadora += f'{i}; '
                resposta_novo_motivo_classificacao_orientadora = resposta_novo_motivo_classificacao_orientadora[:-2]
                resposta_nova_justificativa_classificacao_orientadora = st.text_area(placeholder='Justifique a mudança de classificação', label='Justifique a mudança de classificação')
                resposta_nova_justificativa_classificacao_orientadora = resposta_nova_justificativa_classificacao_orientadora.strip()
                submit_button = st.form_submit_button(label='ALTERAR')
                if submit_button:
                    if not resposta_nova_classificacao_orientadora or not resposta_novo_motivo_classificacao_orientadora or not resposta_nova_justificativa_classificacao_orientadora:
                        st.warning('Preencha os dados de classificação')
                        st.stop()
                    else:
                        st.session_state['classificacao_atual'] = resposta_nova_classificacao_orientadora
                        st.session_state['motivo_atual'] = resposta_novo_motivo_classificacao_orientadora
                        st.session_state['confirmacao_alterada'] = 'Sim'
                        df_insert = pd.DataFrame([{
                                                'RA': ra,
                                                'nome': nome,
                                                'data_submit': datetime.now(fuso_horario),
                                                'resposta_argumentacao': resposta_argumentacao,
                                                'resposta_rotina_estudos': resposta_rotina_estudos,
                                                'resposta_faltas': resposta_faltas,
                                                'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,
                                                'resposta_respeita_escola': resposta_respeita_escola,
                                                'resposta_atividades_obrigatorias_ismart': resposta_atividades_obrigatorias_ismart,
                                                'resposta_colaboracao': resposta_colaboracao,
                                                'resposta_atividades_nao_obrigatorias_ismart': resposta_atividades_nao_obrigatorias_ismart,
                                                'resposta_networking': resposta_networking,
                                                'resposta_proatividade': resposta_proatividade,
                                                'resposta_questoes_psiquicas': resposta_questoes_psiquicas,
                                                'resposta_questoes_familiares': resposta_questoes_familiares,
                                                'resposta_questoes_saude': resposta_questoes_saude,
                                                'resposta_ideacao_suicida': resposta_ideacao_suicida,
                                                'resposta_adaptacao_projeto': resposta_adaptacao_projeto,
                                                'resposta_seguranca_profissional': resposta_seguranca_profissional,
                                                'resposta_curso_apoiado': resposta_curso_apoiado,
                                                'resposta_nota_condizente': resposta_nota_condizente,
                                                'classificacao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0],
                                                'motivo_classificao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1],
                                                'confirmacao_classificacao_orientadora': '',
                                                'nova_classificacao_orientadora' : resposta_nova_classificacao_orientadora,
                                                'novo_motivo_classificacao_orientadora': resposta_novo_motivo_classificacao_orientadora,
                                                'nova_justificativa_classificacao_orientadora': resposta_nova_justificativa_classificacao_orientadora,
                                                'classificacao_final': resposta_nova_classificacao_orientadora,
                                                'motivo_final': resposta_novo_motivo_classificacao_orientadora
                                                }]).to_dict(orient='records')[0]
                        atualizar_linha('registro', ra, df_insert)
        else:
            with st.form(key='formulario_descricao'):
                resposta_nova_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_classificacao_orientadora'].iloc[0]
                resposta_novo_motivo_classificacao_orientadora = df.loc[df['RA'] == ra, 'novo_motivo_classificacao_orientadora'].iloc[0]
                resposta_nova_justificativa_classificacao_orientadora = df.loc[df['RA'] == ra, 'nova_justificativa_classificacao_orientadora'].iloc[0]

                if st.session_state['classificacao_atual'] == 'Crítico' or st.session_state['classificacao_atual'] == 'Crítico OP':
                    try:
                        reversao = df_historico.loc[df_historico['RA'] == ra, 'reversao'].iloc[0]
                    except:
                        reversao = None
                    resposta_reversao = st.radio('**Reversão**', caixa_reversao, index=retornar_indice(lista=caixa_reversao,variavel=reversao), horizontal=True)
                    try:
                        historico_descricao_caso = df_historico.loc[df_historico['RA'] == ra, 'descricao_caso'].iloc[0]
                    except:
                        historico_descricao_caso = None
                    resposta_descricao_caso = st.text_area(placeholder='Descrição do caso', label='Descrição do caso', value=historico_descricao_caso)
                    resposta_descricao_caso = resposta_descricao_caso.strip()
                    try:
                        historico_plano_intervencao = df_historico.loc[df_historico['RA'] == ra, 'plano_intervencao'].iloc[0]
                    except:
                        historico_plano_intervencao = None
                    resposta_plano_intervencao = st.text_area(placeholder='Plano de intervenção', label='Plano de intervenção', value=historico_plano_intervencao).strip()
                    resposta_plano_intervencao = resposta_plano_intervencao.strip()
                elif st.session_state['classificacao_atual'] == 'Atenção':
                    resposta_reversao = '-'
                    resposta_descricao_caso = '-'
                    try:
                        historico_plano_intervencao = df_historico.loc[df_historico['RA'] == ra, 'plano_intervencao'].iloc[0]
                    except:
                        historico_plano_intervencao = None
                    resposta_plano_intervencao = st.text_area(placeholder='Plano de intervenção', label='Plano de intervenção', value=historico_plano_intervencao).strip()
                    resposta_plano_intervencao = resposta_plano_intervencao.strip()
                else:
                    resposta_reversao = '-'
                    resposta_descricao_caso = '-'
                    resposta_plano_intervencao = '-'
                df_login = ler_sheets_cache('login')
                cidade_login = df_login.query(f'email == "{email}"')["Cidade"].iloc[0]
                if cidade_login == 'SP':
                    try:
                        registro_resposta_tier = df_historico.loc[df_historico['RA'] == ra, 'tier'].iloc[0]
                        lista_default_tier = [item.strip() for item in registro_resposta_tier.split(';')]
                        resposta_tier = st.multiselect('Deseja Indicar Tiers?', caixa_tier, placeholder="Tiers", default=lista_default_tier)
                    except:
                        resposta_tier = st.multiselect('Deseja Indicar Tiers?', caixa_tier, placeholder="Tiers")
                    tier = ''

                    for i in resposta_tier:
                        tier += f'{i}; '
                    tier = tier[:-2]

                else:
                    tier = '-'
                submit_button = st.form_submit_button(label='REGISTRAR')
                if submit_button:
                    if not resposta_reversao:
                        st.warning('Preencha os dados da reversão')
                        st.stop()
                    elif not resposta_plano_intervencao:
                        st.warning('Preencha os dados da intervenção')
                        st.stop()
                    else:
                        if resposta_confirmar_classificacao == 'Sim':
                            df_insert = pd.DataFrame([{
                                                'RA': ra,
                                                'nome': nome,
                                                'data_submit': datetime.now(fuso_horario),
                                                'resposta_argumentacao': resposta_argumentacao,
                                                'resposta_rotina_estudos': resposta_rotina_estudos,
                                                'resposta_faltas': resposta_faltas,
                                                'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,
                                                'resposta_respeita_escola': resposta_respeita_escola,
                                                'resposta_atividades_obrigatorias_ismart': resposta_atividades_obrigatorias_ismart,
                                                'resposta_colaboracao': resposta_colaboracao,
                                                'resposta_atividades_nao_obrigatorias_ismart': resposta_atividades_nao_obrigatorias_ismart,
                                                'resposta_networking': resposta_networking,
                                                'resposta_proatividade': resposta_proatividade,
                                                'resposta_questoes_psiquicas': resposta_questoes_psiquicas,
                                                'resposta_questoes_familiares': resposta_questoes_familiares,
                                                'resposta_questoes_saude': resposta_questoes_saude,
                                                'resposta_ideacao_suicida': resposta_ideacao_suicida,
                                                'resposta_adaptacao_projeto': resposta_adaptacao_projeto,
                                                'resposta_seguranca_profissional': resposta_seguranca_profissional,
                                                'resposta_curso_apoiado': resposta_curso_apoiado,
                                                'resposta_nota_condizente': resposta_nota_condizente,
                                                'classificacao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0],
                                                'motivo_classificao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1],
                                                'confirmacao_classificacao_orientadora': resposta_confirmar_classificacao,
                                                'nova_classificacao_orientadora' : '-',
                                                'novo_motivo_classificacao_orientadora': '-',
                                                'nova_justificativa_classificacao_orientadora': '-',
                                                'reversao': resposta_reversao,
                                                'descricao_caso': resposta_descricao_caso,
                                                'plano_intervencao': resposta_plano_intervencao,
                                                'tier': tier,
                                                'confirmacao_classificacao_coordenacao': '-',
                                                'justificativa_classificacao_coord': '-',
                                                'classificacao_final': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0],
                                                'motivo_final': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1]
                                                }]).to_dict(orient='records')[0]
                            atualizar_linha('registro', ra, df_insert)
                        elif resposta_confirmar_classificacao == 'Não':
                            df_insert = pd.DataFrame([{
                                                'RA': ra,
                                                'nome': nome,
                                                'data_submit': datetime.now(fuso_horario),
                                                'resposta_argumentacao': resposta_argumentacao,
                                                'resposta_rotina_estudos': resposta_rotina_estudos,
                                                'resposta_faltas': resposta_faltas,
                                                'resposta_atividades_extracurriculares': resposta_atividades_extracurriculares,
                                                'resposta_respeita_escola': resposta_respeita_escola,
                                                'resposta_atividades_obrigatorias_ismart': resposta_atividades_obrigatorias_ismart,
                                                'resposta_colaboracao': resposta_colaboracao,
                                                'resposta_atividades_nao_obrigatorias_ismart': resposta_atividades_nao_obrigatorias_ismart,
                                                'resposta_networking': resposta_networking,
                                                'resposta_proatividade': resposta_proatividade,
                                                'resposta_questoes_psiquicas': resposta_questoes_psiquicas,
                                                'resposta_questoes_familiares': resposta_questoes_familiares,
                                                'resposta_questoes_saude': resposta_questoes_saude,
                                                'resposta_ideacao_suicida': resposta_ideacao_suicida,
                                                'resposta_adaptacao_projeto': resposta_adaptacao_projeto,
                                                'resposta_seguranca_profissional': resposta_seguranca_profissional,
                                                'resposta_curso_apoiado': resposta_curso_apoiado,
                                                'resposta_nota_condizente': resposta_nota_condizente,
                                                'classificacao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[0],
                                                'motivo_classificao_automatica': classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_sim_nao,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao)[1],
                                                'confirmacao_classificacao_orientadora': resposta_confirmar_classificacao,
                                                'nova_classificacao_orientadora' : nova_classificacao_orientadora,
                                                'novo_motivo_classificacao_orientadora': novo_motivo_classificacao_orientadora,
                                                'nova_justificativa_classificacao_orientadora': nova_justificativa_classificacao_orientadora,
                                                'reversao': resposta_reversao,
                                                'descricao_caso': resposta_descricao_caso,
                                                'plano_intervencao': resposta_plano_intervencao,
                                                'tier': tier,
                                                'classificacao_final': nova_classificacao_orientadora,
                                                'motivo_final': novo_motivo_classificacao_orientadora

                                                }]).to_dict(orient='records')[0]
                            atualizar_linha('registro', ra, df_insert)
else:
    #Tabela De Confirmação
    # Filtro personalizado no histórico
    df_historico_filtrado = df_historico[~df_historico['RA'].isin(df['RA'])]
    df_historico_filtrado = df_historico_filtrado[df_historico_filtrado['RA'].isin(bd_segmentado['RA'])]
    df_historico_filtrado = df_historico_filtrado.query("confirmacao_classificacao_orientadora.notna()")    
    df_historico_filtrado.sort_values(by='data_submit', ascending = False, inplace=True)
    df_historico_filtrado = df_historico_filtrado.drop_duplicates('RA')
    df_historico_filtrado['manter_dados_iguais'] = '-' 
    df_historico_filtrado = df_historico_filtrado[['manter_dados_iguais','RA','nome','Segmento','data_submit',
                                                    'classificacao_final','motivo_final','confirmacao_classificacao_coordenacao',
                                                    'justificativa_classificacao_coord','classificacao_automatica','motivo_classificao_automatica',
                                                    'confirmacao_classificacao_orientadora','nova_classificacao_orientadora',
                                                    'novo_motivo_classificacao_orientadora','nova_justificativa_classificacao_orientadora',
                                                    'reversao','descricao_caso','plano_intervencao','tier','resposta_argumentacao','resposta_rotina_estudos',
                                                    'resposta_atividades_extracurriculares','resposta_faltas','resposta_respeita_escola',
                                                    'resposta_atividades_obrigatorias_ismart','resposta_colaboracao',
                                                    'resposta_atividades_nao_obrigatorias_ismart','resposta_networking','resposta_proatividade',
                                                    'resposta_questoes_psiquicas','resposta_questoes_familiares','resposta_questoes_saude',
                                                    'resposta_ideacao_suicida','resposta_adaptacao_projeto','resposta_seguranca_profissional',
                                                    'resposta_curso_apoiado','resposta_nota_condizente']]

    df_historico_filtrado = df_historico_filtrado.merge(bd[['RA', 'Nota Matemática', 'Nota Português', 'Nota História', 'Nota Geografia', 
                                                            'Nota Inglês', 'Nota Francês/Alemão e Outros', 'Nota Espanhol', 'Nota Química', 
                                                            'Nota Física', 'Nota Biologia', 'Nota ENEM', 'Nota PU', 'media_calibrada']]
                                                            , how='left', on='RA')
    df_historico_filtrado.sort_values(by=['Segmento', 'nome'])

    #Colunas Não Editaveis
    colunas_nao_editaveis = df_historico_filtrado.columns.to_list()
    colunas_nao_editaveis.remove('manter_dados_iguais')

    with st.form(key='tabela_editavel2'):
        # Configure o data editor
        edited_df = st.data_editor(
            df_historico_filtrado[['manter_dados_iguais','RA','nome','Segmento','data_submit','classificacao_final'
                                    ,'motivo_final','confirmacao_classificacao_coordenacao','justificativa_classificacao_coord',
                                    'classificacao_automatica','motivo_classificao_automatica','confirmacao_classificacao_orientadora',
                                    'nova_classificacao_orientadora','novo_motivo_classificacao_orientadora',
                                    'nova_justificativa_classificacao_orientadora','reversao','descricao_caso','plano_intervencao','tier',
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
                    help="Selecione Sim Para Confirmar Que Os Dados Estão Corretos ",
                    options=['Sim', '-'],
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
                "data_submit": st.column_config.Column(
                    "Data de Registro",
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
                "confirmacao_classificacao_coordenacao": st.column_config.Column(
                    "Coordenação Confirmou a Classificação?",
                    required=False
                ),
                "justificativa_classificacao_coord": st.column_config.Column(
                    "Justificativa da Coordenação",
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
        #filtrar do df_tabela_editavel aqueles com confirmar
        df_tabela_editavel = edited_df.loc[edited_df['manter_dados_iguais'].isin(['Sim'])]

        if df_tabela_editavel.shape[0] == 0:
            st.warning('Revise ao menos um aluno antes de salvar')
        else:
            df_insert = df_tabela_editavel[[
                                'RA', 'nome', 'data_submit', 'resposta_argumentacao', 'resposta_rotina_estudos',
                                'resposta_faltas', 'resposta_atividades_extracurriculares', 'resposta_respeita_escola',
                                'resposta_atividades_obrigatorias_ismart', 'resposta_colaboracao',
                                'resposta_atividades_nao_obrigatorias_ismart', 'resposta_networking',
                                'resposta_proatividade', 'resposta_questoes_psiquicas', 'resposta_questoes_familiares',
                                'resposta_questoes_saude', 'resposta_ideacao_suicida', 'resposta_adaptacao_projeto',
                                'resposta_seguranca_profissional', 'resposta_curso_apoiado', 'resposta_nota_condizente',
                                'classificacao_automatica', 'motivo_classificao_automatica',
                                'confirmacao_classificacao_orientadora', 'nova_classificacao_orientadora',
                                'novo_motivo_classificacao_orientadora', 'nova_justificativa_classificacao_orientadora',
                                'reversao', 'descricao_caso', 'plano_intervencao', 'tier', 'justificativa_classificacao_coord', 'classificacao_final', 'motivo_final'
                            ]]                                                                                                                                                                                                                                                          
            df_insert['data_submit'] = datetime.now(fuso_horario)
            df_insert['data_submit'] = df_insert['data_submit'].dt.strftime('%Y-%m-%d %H:%M:%S')
            registrar(df_insert, 'registro')