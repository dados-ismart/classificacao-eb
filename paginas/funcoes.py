import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from time import sleep
from io import BytesIO
from xlsxwriter import Workbook
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime
import hashlib

@st.cache_resource(ttl=7200)
def conn():
    """
    Conecta-se ao Google Sheets usando as credenciais dos secrets
    e retorna o cliente gspread autorizado.
    """
    try:
        # Define os escopos de permissão
        scope = [
            "https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Carrega as credenciais do st.secrets
        creds_dict = st.secrets["connections"]["gsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
        # Autoriza e retorna o cliente gspread
        return gspread.authorize(creds)
    
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
        if st.button('Tentar novamente'):
            st.rerun()

# Chama a função de conexão uma vez e armazena em cache
conn = conn()

def ler_sheets(aba, ttl=1):
    for i in range(0, 10):
        try:
            spreadsheet_name = st.secrets["connections"]["gsheets"]["spreadsheet_name"]
            spreadsheet = conn.open(spreadsheet_name)
            worksheet = spreadsheet.worksheet(aba)
            dados = worksheet.get_all_records()
            return pd.DataFrame(dados)
        except Exception as e:
                st.toast(f'Erro na tentativa {i}/10: {e}', icon="❌")
                sleep(0.2)
    if st.button('Tentar novamente'):
        st.rerun()
    st.stop()

@st.cache_data(show_spinner=False, ttl=7200) 
def ler_sheets_cache(aba):
    for i in range(0, 10):
        try:
            spreadsheet_name = st.secrets["connections"]["gsheets"]["spreadsheet_name"]
            spreadsheet = conn.open(spreadsheet_name)
            worksheet = spreadsheet.worksheet(aba)
            dados = worksheet.get_all_records()
            return pd.DataFrame(dados)
        except Exception as e:
                st.toast(f'Erro na tentativa {i}/10: {e}', icon="❌")
                sleep(0.2)
    st.error('Erro ao conectar com o sheets')
    if st.button('Tentar novamente'):
        st.rerun()
    st.stop()
    
def pontuar(resposta, lista):
    try:
        for index, elemento in enumerate(lista):
            if elemento == resposta:
                return int(index + 1)
    except:
        return st.error('Erro Interno No Formulário')

def classificar(media_calibrada, portugues, matematica, humanas, idiomas, ciencias_naturais, resposta_faltas, ano, caixa_nota_condizente, resposta_adaptacao_projeto , resposta_nota_condizente, resposta_seguranca_profissional, resposta_curso_apoiado , caixa_fragilidade, resposta_questoes_saude, resposta_questoes_familiares, resposta_questoes_psiquicas, resposta_ideacao_suicida , caixa_ideacao_suicida , resposta_argumentacao, resposta_rotina_estudos, resposta_atividades_extracurriculares, resposta_respeita_escola, resposta_atividades_obrigatorias_ismart, resposta_colaboracao, resposta_atividades_nao_obrigatorias_ismart, resposta_networking, resposta_proatividade,caixa_argumentacao,caixa_rotina_estudos,caixa_nao_sim,caixa_atividades_extracurriculares,caixa_nunca_eventualmente_sempre,caixa_networking, caixa_classificacao, caixa_justificativa_classificacao):
    classificacao = ''
    motivo = ''

    #Classificação Psicológico/Questões Familiares/Saúde
        #Psicológico - critico
    if resposta_ideacao_suicida == caixa_ideacao_suicida[1] or resposta_ideacao_suicida == caixa_ideacao_suicida[2]:
        classificacao = 'Crítico'
        motivo += 'Psicológico'+'; '
    elif resposta_questoes_psiquicas == caixa_fragilidade[3]:
        classificacao = 'Crítico'
        motivo += 'Psicológico'+'; '
        #Familiares - critico
    if resposta_questoes_familiares == caixa_fragilidade[3]:
        classificacao = 'Crítico'
        motivo += 'Familiar'+'; '
        #Saúde - critico
    if resposta_questoes_saude == caixa_fragilidade[3]:
        classificacao = 'Crítico'
        motivo += 'Saúde'+'; '
    if classificacao != 'Crítico':
            #Psicológico - Atenção
        if resposta_questoes_psiquicas == caixa_fragilidade[2]:
            classificacao = 'Atenção'
            motivo += 'Psicológico'+'; '
            #Familiares - Atenção
        if resposta_questoes_familiares == caixa_fragilidade[2]:
            classificacao = 'Atenção'
            motivo += 'Familiar'+'; '
            #Saúde - Atenção
        if resposta_questoes_saude == caixa_fragilidade[2]:
            classificacao = 'Atenção'
            motivo += 'Saúde'+'; '
        # opcional 2° ano - Atenção
        if ano == '2º EM':
            if resposta_seguranca_profissional == caixa_nao_sim[0]:
                classificacao = 'Atenção'
                motivo += 'Escolha frágil'+'; '
    # opcional 3° ano - Critico OP
    if classificacao == '':
        if ano == '3º EM':
            if resposta_curso_apoiado == caixa_nao_sim[0]:
                classificacao = 'Crítico OP'
                motivo += 'Curso não apoiado'+'; '
            if resposta_seguranca_profissional == caixa_nao_sim[0]:
                classificacao = 'Crítico OP'
                motivo += 'Escolha frágil'+'; '
            if resposta_nota_condizente == caixa_nota_condizente[0]:
                classificacao = 'Crítico OP'
                motivo += 'Curso concorrido'+'; '
    # Número de faltas
    if classificacao == 'Atenção' or classificacao == 'Crítico' or classificacao == '':
        if resposta_faltas == caixa_nao_sim[1]:
            classificacao = 'Crítico'
            motivo += 'Acadêmico'+'; '
            motivo += 'Perfil'+'; '
            motivo = motivo[:-2]
            return classificacao, motivo

    #Nota escolar
    critico_escolar = 0
    atencao_escolar = 0
    mediano_escolar = 0
    destaque_escolar = 0
    materias = [portugues, matematica, humanas, idiomas, ciencias_naturais]

    #Contagem das matérias
    for i in materias:
        if i < (media_calibrada - 1):
            critico_escolar += 1
        elif (media_calibrada - 1) <= i and i < media_calibrada:
            atencao_escolar += 1
        elif media_calibrada <= i and i < (media_calibrada + 2):
            mediano_escolar += 1
        elif i >= (media_calibrada + 2):
            destaque_escolar += 1


    #status_nota
    if critico_escolar > 0 or atencao_escolar > 2:
        status_nota_escolar = 0
    elif atencao_escolar == 1 or atencao_escolar == 2:
        status_nota_escolar = 1
    elif mediano_escolar > 0 and critico_escolar == 0 and atencao_escolar == 0 and destaque_escolar < 3:
        status_nota_escolar = 2
    elif mediano_escolar >= 1 and destaque_escolar > 2:
        status_nota_escolar = 3
    elif destaque_escolar == 5:
        status_nota_escolar = 4

    #Pontuacao academica
    pontuacao_perfil = 0
    pontuacao_perfil += pontuar(resposta_respeita_escola , caixa_nunca_eventualmente_sempre)
    pontuacao_perfil += pontuar(resposta_atividades_obrigatorias_ismart , caixa_nunca_eventualmente_sempre)
    pontuacao_perfil += pontuar(resposta_colaboracao , caixa_nunca_eventualmente_sempre)
    pontuacao_perfil += pontuar(resposta_atividades_nao_obrigatorias_ismart , caixa_nunca_eventualmente_sempre)
    pontuacao_perfil += pontuar(resposta_networking , caixa_networking)
    pontuacao_perfil += pontuar(resposta_proatividade , caixa_nunca_eventualmente_sempre)
    if pontuacao_perfil < 11:
        status_perfil = 0
    else:
        status_perfil = 1
    #Pontuação Perfil
    pontuacao_academico = 0
    pontuacao_academico += pontuar(resposta_argumentacao, caixa_argumentacao)
    pontuacao_academico += pontuar(resposta_rotina_estudos , caixa_rotina_estudos)
    pontuacao_academico += pontuar(resposta_atividades_extracurriculares , caixa_atividades_extracurriculares)
    if pontuacao_academico < 6:
        status_academico = 0
    else:
        status_academico = 1

    #Classificação notas
    if status_nota_escolar == 0 and (classificacao == 'Crítico' or classificacao == 'Atenção'):
        classificacao = 'Crítico'
        motivo += 'Acadêmico'+'; '
    elif status_nota_escolar == 1 and classificacao == 'Atenção':
        motivo += 'Acadêmico'+'; '
    elif classificacao == '':
        if status_nota_escolar == 0 or (status_nota_escolar == 1 and status_perfil == 0 and status_academico == 0):
            classificacao = 'Crítico'
            motivo = 'Acadêmico'+'; '
            if status_perfil == 0:
                motivo += 'Perfil'+'; '
        elif status_nota_escolar == 1 or (status_nota_escolar == 2 and status_perfil ==0 and status_academico == 0):
            classificacao = 'Atenção'
            motivo = 'Acadêmico'+'; '
            if status_perfil == 0:
                motivo += 'Perfil'+'; '
        elif status_nota_escolar == 2:
            classificacao = 'Mediano'
            motivo = 'Acadêmico'+'; '
            if status_perfil == 0:
                motivo += 'Perfil'+'; '
        elif status_nota_escolar == 3:
            if status_perfil == 1:
                classificacao = 'Pré-Destaque'
                motivo = 'Acadêmico'+'; '
                if status_academico == 1:
                    motivo += 'Perfil'+'; '
            else:
                classificacao = 'Atenção'
                motivo = 'Perfil'+'; '
        elif status_nota_escolar == 4:
            if status_perfil == 1:
                classificacao = 'Destaque'
                motivo = 'Acadêmico'+'; '
                if status_academico == 1:
                    motivo += 'Perfil'+'; '
            else:
                classificacao = 'Atenção'
                motivo = 'Perfil'+'; '

    motivo = motivo[:-2]
    return classificacao, motivo

def registrar_substituindo_df(df_insert, aba, coluna_apoio, remover_registros_anteriores=True):
    #Leitura da aba registro e checa se é nula
    for i in range(0, 2):
        df = ler_sheets(aba)
        if df.shape[0] == 0:
            sleep(3)
            continue
        else: 
            break

    #Limpar linhas duplicadas (registros_anteriores)
    if remover_registros_anteriores:
        ra = df_insert['RA'].to_list()
        if isinstance(ra, list) and ra: 
            df = df[~df['RA'].isin(ra)]

    #REGISTRAR
    for a in range(1, 4):
        try:
            updared_df = pd.concat([df, df_insert], ignore_index=True)
            conn.update(worksheet=aba, data=updared_df, append=True)
            sleep(0.2)
            st.success('Sucesso!')
            sleep(0.5)
            break
        except:
            sleep(0.2)
            df = ler_sheets(aba)
            if type(ra) != list:
                if not df.query(f'RA == {ra} and {coluna_apoio} == {coluna_apoio}').empty:
                    st.success('Sucesso!')
                    break
                else:
                    st.warning('Erro')
                    sleep(1)
                    continue
            else:
                if not df.query(f'RA == {ra[0]} and {coluna_apoio} == {coluna_apoio}').empty:
                    st.success('Sucesso!')
                    break
                else:
                    st.warning('Erro')
                    sleep(1)
                    continue
    st.rerun()

def registrar(df_insert, aba, rerun=True):
    """
    Registra um DataFrame no Google Sheets, garantindo que a ordem das colunas
    corresponda exatamente à da planilha, preenchendo colunas ausentes com
    valores vazios.
    """
    st.toast(f"🔄 Registrando dados na aba '{aba}'...")
    df_copy = df_insert.copy()
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    for a in range(1, 4):
        try:
            # ... (lógica de conexão, reindex, etc. continua a mesma) ...
            spreadsheet = conn.open(st.secrets["connections"]["gsheets"]["spreadsheet_name"])
            worksheet = spreadsheet.worksheet(aba)
            headers = worksheet.row_values(1)
            df_final = df_copy.reindex(columns=headers).fillna('')
            dados_para_append = df_final.values.tolist()
            worksheet.append_rows(dados_para_append, value_input_option='USER_ENTERED')
            
            st.toast("Registrado com sucesso!", icon="✅")
            sleep(1)
            if rerun:
                st.rerun()
            else:
                return True  

        except Exception as e:
            st.toast(f'Erro na tentativa {a}/3: {e}', icon="❌")
            sleep(2)

    st.toast("Falha ao registrar dados após 3 tentativas.")
    return False  

def atualizar_linha(aba: str, valor_id, novos_dados: dict):
    """
    Atualiza uma linha específica com a ordem de operações correta e
    todas as verificações de segurança.
    """
    st.toast("Tentando atualizar...", icon="🔄")
    try:
        # PASSO 1: Preparar os dados de entrada
        # Sanitiza as datas no dicionário 'novos_dados' antes de qualquer outra coisa.
        for coluna, valor_novo in list(novos_dados.items()):
            if isinstance(valor_novo, (datetime, pd.Timestamp)):
                novos_dados[coluna] = valor_novo.strftime('%Y-%m-%d %H:%M:%S')

        # PASSO 2: Conectar e encontrar a linha
        # Primeiro, conectamos à planilha e à aba.
        spreadsheet = conn.open(st.secrets["connections"]["gsheets"]["spreadsheet_name"])
        worksheet = spreadsheet.worksheet(aba)
        
        # Depois, encontramos a célula para saber qual linha modificar.
        cell = worksheet.find(str(valor_id))

        # PASSO 3: Ler e preparar os dados da planilha
        # Agora que temos a linha, lemos os valores dela e do cabeçalho.
        headers = worksheet.row_values(1)
        valores_antigos = worksheet.row_values(cell.row)

        # Garante que a linha de valores tenha o mesmo tamanho do cabeçalho
        if valores_antigos is None:
            valores_antigos = []
        if len(valores_antigos) < len(headers):
            valores_antigos.extend([''] * (len(headers) - len(valores_antigos)))

        # PASSO 4: Mesclar os dados antigos com os novos
        novos_valores = list(valores_antigos)
        for coluna, valor_novo in novos_dados.items():
            if coluna in headers:
                col_index = headers.index(coluna)
                novos_valores[col_index] = valor_novo
            else:
                st.toast(f"A coluna '{coluna}' não foi encontrada no cabeçalho e será ignorada.")

        # PASSO 5: Escrever os dados de volta com uma única chamada
        range_to_update = f'A{cell.row}'
        worksheet.update(range_to_update, [novos_valores], value_input_option='USER_ENTERED')
        
        st.toast("Registro atualizado com sucesso!", icon="✅")
        sleep(2) 
        st.rerun()
    except Exception as e:
        st.toast(f"Ocorreu um erro inesperado ao atualizar: {e}", icon="❌")
        sleep(2)

def atualizar_linhas(aba: str, df_updates: pd.DataFrame, id_column: str):
    """
    Atualiza múltiplas linhas usando uma estratégia de travamento otimista (hash/checksum)
    para prevenir condições de corrida sem usar uma célula de lock.
    """
    st.toast("Iniciando atualização em lote...", icon="🔄")

    if df_updates.empty:
        st.toast("Nenhum dado para atualizar.", icon="ℹ️")
        sleep(2)
        st.rerun()

    try:
        # ETAPA 1: LEITURA INICIAL E CRIAÇÃO DO "FINGERPRINT" (HASH)
        spreadsheet = conn.open(st.secrets["connections"]["gsheets"]["spreadsheet_name"])
        worksheet = spreadsheet.worksheet(aba)
        
        st.write("Lendo o estado inicial da planilha...")
        df_sheet_initial = pd.DataFrame(worksheet.get_all_records(expected_headers=worksheet.row_values(1)))
        
        # Cria um hash do estado inicial. to_json() cria uma representação de texto consistente.
        hash_inicial = hashlib.sha256(df_sheet_initial.to_json().encode()).hexdigest()

        # ETAPA 2: ATUALIZAÇÃO LOCAL (LÓGICA DO PANDAS)
        # (Esta parte é a mesma da função anterior)
        df_sheet_initial[id_column] = df_sheet_initial[id_column].astype(str)
        df_updates[id_column] = df_updates[id_column].astype(str)

        for col in df_updates.columns:
            if pd.api.types.is_datetime64_any_dtype(df_updates[col]):
                df_updates[col] = df_updates[col].dt.strftime('%Y-%m-%d %H:%M:%S')

        df_sheet_indexed = df_sheet_initial.set_index(id_column)
        df_updates_indexed = df_updates.set_index(id_column)
        df_sheet_indexed.update(df_updates_indexed)
        df_final = df_sheet_indexed.reset_index()

        # ETAPA 3: LEITURA DE VERIFICAÇÃO E NOVO "FINGERPRINT"
        st.toast("Verificando se houve alterações externas...")
        df_sheet_atual = pd.DataFrame(worksheet.get_all_records(expected_headers=worksheet.row_values(1)))
        hash_atual = hashlib.sha256(df_sheet_atual.to_json().encode()).hexdigest()

        # ETAPA 4: COMPARAÇÃO E ESCRITA SEGURA
        if hash_inicial == hash_atual:
            # Os hashes são iguais! Ninguém mexeu. É seguro escrever.
            st.toast("Nenhuma alteração detectada. Escrevendo dados na planilha...")
            dados_para_escrever = [df_final.columns.tolist()] + df_final.values.tolist()
            worksheet.clear()
            worksheet.update('A1', dados_para_escrever, value_input_option='USER_ENTERED')
            
            st.toast("Registros atualizados com sucesso!", icon="🎉")
            st.balloons()
            sleep(2)
            st.rerun()
        else:
            # Os hashes são diferentes! Alguém alterou a planilha. Abortar.
            st.toast("A planilha foi modificada por outro processo enquanto você trabalhava. Sua atualização foi cancelada para evitar perda de dados. Por favor, tente novamente.", icon="⚠️")
            return False

    except Exception as e:
        st.toast(f"Ocorreu um erro inesperado durante a atualização: {e}", icon="❌")
        return False

def int_para_letra_coluna(n: int) -> str:
    """
    Converte um número de coluna (1-based) para sua letra correspondente no Excel/Sheets.
    Ex: 1 -> 'A', 27 -> 'AA'.
    """
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def esvaziar_aba(aba: str):
    """
    Limpa o conteúdo de todas as células de uma aba a partir da segunda linha,
    sem depender de gspread.utils.
    """
    st.toast(f"Iniciando limpeza da aba '{aba}'...")
    
    for i in range(1, 4):
        try:
            # Conecta à planilha e seleciona a aba
            spreadsheet = conn.open(st.secrets["connections"]["gsheets"]["spreadsheet_name"])
            worksheet = spreadsheet.worksheet(aba)

            # Pega todos os valores para saber as dimensões da planilha
            all_data = worksheet.get_all_values()
            num_rows = len(all_data)
            
            if num_rows <= 1:
                st.toast(f"Aba '{aba}' já está vazia.", icon="ℹ️")
                st.cache_data.clear()
                return True

            num_cols = len(all_data[0]) if num_rows > 0 else 0
            if num_cols == 0:
                st.toast(f"Aba '{aba}' não tem colunas.", icon="ℹ️")
                return True

            # --- MUDANÇA PRINCIPAL AQUI ---
            # Usa nossa própria função para obter a letra da última coluna
            last_col_letter = int_para_letra_coluna(num_cols)
            range_to_clear = f'A2:{last_col_letter}{num_rows}'
            
            st.toast(f"Limpando o intervalo {range_to_clear}...")

            # O resto da lógica continua a mesma
            worksheet.batch_clear([range_to_clear])
            
            st.toast(f"Aba '{aba}' limpa com sucesso!", icon="✅")
            st.cache_data.clear()
            sleep(1)
            return True # Sucesso!

        except Exception as e:
            st.toast(f"Erro ao limpar a aba na tentativa {i}/3: {e}", icon="❌")
            sleep(2)

    st.toast(f"Não foi possível limpar a aba '{aba}' após 3 tentativas.")
    return False

def retornar_indice(lista, variavel):
    if variavel == None:
        return None
    try:
        for indice, valor in enumerate(lista):
            if valor == variavel:
                return indice
    except:
        return None

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    processed_data = output.getvalue()
    return processed_data

def enviar_email(contatos, assunto, mensagem):
    #Configurações de login
    EMAIL_ADDRESS = st.secrets["email"]
    EMAIL_PASSWORD = st.secrets["senha_email"]
    
    cont = 0
    barra_progresso = st.progress(cont/len(contatos), f'Envios: **{cont}/{len(contatos)}**')
    for contato in contatos:
        barra_progresso.progress(cont/len(contatos), f'Envios: **{cont}/{len(contatos)}**')
        mail = EmailMessage()

        # tópico
        mail['Subject'] = assunto

        #De
        mail['From'] = EMAIL_ADDRESS
        #para
        mail['To'] = contato

        #email pode ter texto e html e encode utf-8
        mail.set_content(mensagem)

        contexto_ssl = ssl.create_default_context()

        #Servidor smtp + nome do servidor
        # Enviar o email
        cont += 1
        try:
            # Inicia a conexão na porta 587
            with smtplib.SMTP('smtp.office365.com', 587) as email:
                email.ehlo()
                email.starttls(context=contexto_ssl)
                email.ehlo()
                email.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                email.send_message(mail)
                st.toast(f"E-mail enviado com sucesso para {contato}", icon="✅")
        except Exception as e:
            st.toast(f"Erro ao enviar e-mail para {contato}: {e}", icon="❌")
        sleep(1)
    st.toast("Envio concluio!", icon="✅")
    st.rerun()
