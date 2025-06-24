import streamlit as st
from paginas.funcoes import ler_sheets_cache
import time
from PIL import Image

logo = Image.open('imagens/logo_ismart.png')

st.set_page_config(
                page_title='Ismart - Classificação',
                page_icon=logo,
                layout="wide",
                initial_sidebar_state="collapsed")

st.logo(logo, icon_image=logo)

def check_microsoft_login():
    """Autenticação via login da Microsoft e verificação do domínio."""
    # if not st.user.is_logged_in:   #Esta versão não está disponível no streamlit utilizado para deploy
    if not st.user.is_logged_in:
        st.markdown("<div style='text-align: center; font-size: 32px; font-weight: bold;'>🔐 Bem-vinda(o) a Plataforma de Classificação</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 18px;'>Para acessar as informações, faça login com sua conta institucional.</div>", unsafe_allow_html=True)
        st.write("")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.write("")
            st.button("🔓 Acessar com minha conta Microsoft", 
                      on_click=st.login, 
                      help="Clique para entrar com seu e-mail do Ismart",
                      use_container_width=True)
            st.write("")
        st.stop()

    # usuario = st.user
    usuario = st.user
    email_usuario = usuario.email

    # if not email_usuario.endswith("@ismart.org.br"):
    #     col1, col2, col3 = st.columns([1, 1.5, 1])
    #     with col2:
    #         st.markdown("<div style='text-align: center; font-size: 20px; font-weight: bold;'>⛔ Acesso não autorizado</div>", unsafe_allow_html=True)
    #         st.markdown("<div style='text-align: center; font-size: 16px;'>Apenas usuários com e-mail institucional (@ismart.org.br) podem acessar este dashboard.</div>", unsafe_allow_html=True)
    #         st.markdown("<div style='text-align: center; font-size: 14px;'>Caso precise de ajuda, entre em contato com o <b>time de dados</b>!</div>", unsafe_allow_html=True)
    #         st.write("")
    #         st.button("↩️ Tentar novamente", on_click=st.logout, use_container_width=True)
    #     st.stop()

    return True

def logout():
    """Realiza logout da conta Microsoft e limpa a sessão."""
    if st.user.is_logged_in:
        st.logout()
    
    # Limpa variáveis da sessão
    keys_to_remove = ["auth_success_shown", "autenticado"]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.toast("🔒 Você foi desconectado com sucesso!", icon="🔒")
    time.sleep(0.5)

# --- PAGE SETUP ---
pagina_inicial_coordenadora = st.Page(
    "paginas/coordenadoras.py",
    title= "Classificação",
    icon= "⚖️",
    default=True,
)

pagina_inicial_orientadora = st.Page(
    "paginas/orientadoras.py",
    title= "Classificação",
    icon= "⚖️",
    default=True,
)

dash = st.Page(
    "paginas/dash.py",
    title= "Visualização",
    icon= "📊"
)

dash_status_preenchimento = st.Page(
    "paginas/dash_status_preenchimento.py",
    title= "Status de Preenchimento",
    icon= "🕔"
)

tutorial = st.Page(
    "paginas/tutorial.py",
    title= "Tutorial",
    icon= "🎥"
)

# --- NAVIGATION SETUP [WITH SECTIONS]---
if check_microsoft_login():
    if "auth_success_shown" not in st.session_state:
        st.toast("Autenticação realizada com sucesso!", icon="✅")
        st.session_state.auth_success_shown = True 
    df_login = ler_sheets_cache('login')
    
    email = st.user.email 
    if df_login.query(f'email == "{email}"')["cargo"].iloc[0] == "coordenação":
        pg = st.navigation({
            "Páginas": [pagina_inicial_coordenadora, dash, dash_status_preenchimento, tutorial],
        }, position='top')    
    else:
        pg = st.navigation({
            "Páginas": [pagina_inicial_orientadora, dash, dash_status_preenchimento, tutorial],
        }, position='top')  

    with st.sidebar:
        if st.button("🚪 **Sair da conta**", 
                    type="secondary", 
                    help="Clique para desconectar-se completamente",
                    use_container_width=True):
            logout()
            st.rerun() 
        if st.button('Limpar Cache'):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()

else:
    st.stop()
# --- RUN NAVIGATION ---
pg.run()
