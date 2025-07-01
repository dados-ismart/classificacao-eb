# Plataforma de Classificação de Alunos - Ismart

![Logo do Ismart](https://raw.githubusercontent.com/dados-ismart/classificacao-eb/main/imagens/logo_ismart.png)

Uma aplicação web desenvolvida com Streamlit para centralizar e otimizar o processo de classificação de alunos, integrando dados quantitativos (notas) e avaliações qualitativas da equipe pedagógica.

---

## 📖 Sobre o Projeto

Esta plataforma foi criada para resolver a necessidade de um sistema unificado para a classificação periódica de alunos. Ela utiliza o Google Sheets como um banco de dados para ler informações dos alunos, notas e registrar as classificações, garantindo que os dados estejam sempre centralizados e acessíveis.

O sistema possui um fluxo de trabalho claro com diferentes níveis de permissão, permitindo que orientadoras e coordenadoras colaborem de forma eficiente no processo de avaliação de cada aluno.

---

## ✨ Funcionalidades Principais

* **🔐 Autenticação Segura:** Login integrado com o Microsoft Entra (Azure AD), permitindo acesso apenas para usuários com e-mail institucional (`@ismart.org.br`).
* **👤 Perfis de Acesso:**
    * **Orientadoras:** Preenchem um formulário detalhado sobre cada aluno, visualizam uma classificação automática sugerida e podem propor alterações com justificativas.
    * **Coordenação:** Têm uma visão geral, podem revisar, alterar e confirmar as classificações enviadas pelas orientadoras, finalizando o processo.
* **🤖 Classificação Automática:** Um algoritmo inicial classifica os alunos com base em seu desempenho acadêmico (notas em relação à média da escola), fornecendo um ponto de partida para a avaliação.
* **📝 Formulário de Avaliação Detalhado:** Coleta informações sobre múltiplos aspectos do aluno, incluindo desempenho acadêmico, perfil comportamental, questões psicossociais, familiares e de saúde.
* **📊 Dashboard Interativo:** Uma página de visualização de dados (`Visualização`) com gráficos e tabelas que resumem as classificações atuais. Permite filtrar os dados por segmento, escola, ano e orientadora.
* **📈 Controle de Preenchimento:** Um painel (`Status de Preenchimento`) que mostra o progresso do preenchimento dos formulários em tempo real, tanto de forma geral quanto por unidade (praça) e por orientadora.
* **⚙️ Funções Administrativas:**
    * **Encerramento de Ciclo:** Uma função protegida por senha que arquiva os registros do mês atual para um histórico e limpa a base para o próximo ciclo de classificação.
    * **Envio de Lembretes:** Funcionalidade para enviar e-mails automáticos para as orientadoras que ainda não concluíram seus registros.
* **📥 Exportação de Dados:** Possibilidade de baixar todos os dados de classificação atuais em um arquivo Excel.

---

## 🛠️ Tecnologias Utilizadas

* **Backend & Frontend:** [Python](https://www.python.org/) com [Streamlit](https://streamlit.io/)
* **Manipulação de Dados:** [Pandas](https://pandas.pydata.org/)
* **Banco de Dados:** [Google Sheets](https://www.google.com/sheets/about/)
* **Conexão com Google Sheets:** [gspread](https://docs.gspread.org/en/latest/) e a conexão nativa do Streamlit.
* **Envio de E-mail:** `smtplib` para conexão com servidor SMTP (Office 365).
* **Autenticação:** Módulo `st.user` do Streamlit para login com a Microsoft.

---

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e executar o projeto em sua máquina.

### Pré-requisitos

* [Python 3.8+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/)

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/dados-ismart/classificacao-eb.git](https://github.com/dados-ismart/classificacao-eb.git)
    ```

2.  **Navegue até o diretório do projeto:**
    ```bash
    cd seu-projeto
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    venv\Scripts\activate
    ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuração de Credenciais

Este projeto utiliza o `st.secrets` para gerenciar informações sensíveis. Crie um arquivo chamado `secrets.toml` dentro de uma pasta `.streamlit` na raiz do seu projeto.

**Estrutura do diretório:**
```
seu-projeto/
├── .streamlit/
│   └── secrets.toml
├── paginas/
│   └── ...
└── main.py
```

**Conteúdo do arquivo `.streamlit/secrets.toml`:**

```toml
# Credenciais para envio de e-mail e funções administrativas
email = "seu-email@ismart.org.br"
senha_email = "sua-senha-de-aplicativo"

# Credenciais para conexão com o Google Sheets
# Siga este tutorial para obter seu arquivo JSON: https://docs.streamlit.io/knowledge-base/tutorials/databases/g-sheets
[connections.gsheets]
spreadsheet_name = "nome-da-sua-planilha"
type = "service_account"
project_id = "seu-project-id-do-gcp"
private_key_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n...\n-----END PRIVATE KEY-----\n"
client_email = "nome-da-sua-conta-de-servico@seu-projeto-id.iam.gserviceaccount.com"
client_id = "12345678901234567890"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/sua-conta-de-servico%40seu-projeto-id.iam.gserviceaccount.com"
universe_domain = "googleapis.com"

# Credenciais para autenticação com Microsoft Entra ID (OAuth)
[auth]
redirect_uri = "https://seu-app.streamlit.app/oauth2callback"
cookie_secret = "gere-uma-string-aleatoria-e-longa-aqui"
client_id = "seu-client-id-do-azure-ad"
client_secret = "seu-client-secret-do-azure-ad"
server_metadata_url = "https://login.microsoftonline.com/SEU_TENANT_ID/v2.0/.well-known/openid-configuration"
```

> **IMPORTANTE:** O arquivo `secrets.toml` **NUNCA** deve ser enviado para o repositório do GitHub. Certifique-se de que `.streamlit/secrets.toml` está no seu arquivo `.gitignore`.

### Executando a Aplicação

Com o ambiente virtual ativado e o arquivo de segredos configurado, execute o seguinte comando no terminal:

```bash
streamlit run main.py
```

A aplicação será aberta no seu navegador padrão.

---

## 🗂️ Estrutura do Projeto

```
├── main.py                     # Ponto de entrada, login e navegação principal
├── paginas/
│   ├── funcoes.py              # Funções utilitárias (conexão, CRUD no Sheets, lógica de classificação)
│   ├── orientadoras.py         # Página de classificação para o perfil "Orientadora"
│   ├── coordenadoras.py        # Página de revisão e aprovação para o perfil "Coordenação"
│   ├── dash.py                 # Página do dashboard com gráficos e tabelas
│   ├── dash_status_preenchimento.py # Página para acompanhar o progresso
│   └── tutorial.py             # Página com o tutorial e regras de negócio
├── imagens/
│   └── logo_ismart.png         # Logo da aplicação
├── requirements.txt            # Dependências do Python
└── README.md                   # Este arquivo
```

---

## ✍️ Autor

Feito com ❤️ por [Felipe Rios do Amaral](https://github.com/Felipe2312).
