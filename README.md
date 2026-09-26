# 📄 Copiloto de Documentos RAG (Retrieval-Augmented Generation)

Um assistente inteligente de análise de documentos baseado na técnica **RAG (Retrieval-Augmented Generation)**. A aplicação permite enviar arquivos PDF, processá-los e realizar perguntas interativas diretamente pelo frontend em Streamlit, utilizando o **Google Gemini** para embedding/geração e o **ChromaDB** como banco vetorial local.

---

## 🚀 Teconologias Utilizadas

- **Linguagem:** Python 3.10+
- **Backend Framework:** FastAPI / Uvicorn
- **Frontend UI:** Streamlit
- **Banco Vetorial:** ChromaDB (Persistência local)
- **Provedor de IA:** Google GenAI SDK (`google-genai`)
  - **Modelo de Embedding:** `models/gemini-embedding-001`
  - **Modelo de Geração:** `models/gemini-2.5-flash`
- **Processamento de PDF:** PyPDF

---

## 📁 Estrutura do Projeto

```text
copilot-rag/
├── app/
│   ├── main.py          # Endpoints FastAPI (/upload, /chat)
│   └── rag.py           # Lógica do RAG, integração Gemini e ChromaDB
├── frontend/
│   └── app.py           # Interface gráfica interativa Streamlit
├── data/
│   └── chroma/          # Banco de dados vetorial local (gerado automaticamente)
├── .env                 # Configuração de variáveis de ambiente
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação do projeto
```

---

## 🛠️ Configuração e Instalação

### 1. Requisitos Prévios
- Python instalado (versão 3.10 ou superior).
- Uma chave de API do Google Gemini ([Obtenha sua chave no Google AI Studio](https://aistudio.google.com/)).

### 2. Configuração do Ambiente Virtual
No terminal da raiz do projeto, execute:

```powershell
# Criação do ambiente virtual
python -m venv .venv

# Ativação do ambiente virtual (Windows PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Instalação das Dependências
Instale os pacotes necessários:

```powershell
pip install fastapi uvicorn streamlit chromadb google-genai pypdf python-dotenv
```

### 4. Configuração das Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
GEMINI_API_KEY=sua_chave_api_aqui
```

---

## ⚙️ Como Executar a Aplicação

Para rodar a aplicação completa, é necessário iniciar o backend e o frontend em **dois terminais separados**:

### 🏢 Terminal 1 — Backend (FastAPI)
```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```
> O servidor estará acessível em: `http://127.0.0.1:8000`

### 🖥️ Terminal 2 — Frontend (Streamlit)
```powershell
.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```
> A interface será aberta automaticamente no navegador em: `http://localhost:8501`

---

## 🔄 Fluxo de Funcionamento (RAG)

1. **Upload & Chunking:** O usuário envia um documento PDF no Streamlit. O backend extrai o texto com `PyPDF` e o divide em fragmentos (*chunks*) de 800 caracteres com sobreposição de 100 caracteres.
2. **Embedding & Vetorização:** Cada fragmento é transformado em um vetor denso através da API do Gemini (`models/gemini-embedding-001`) e salvo no **ChromaDB**.
3. **Busca Semântica:** Quando o usuário faz uma pergunta, a dúvida também é convertida em vetor e o ChromaDB recupera os 3 fragmentos de texto mais relevantes.
4. **Geração Resposta:** Um prompt contextualizado contendo os fragmentos resgatados é enviado ao modelo `models/gemini-2.5-flash`, que gera a resposta baseada estritamente no documento.

---

## 🔧 Solução de Problemas Comuns

### 1. Erro de arquivo bloqueado (`chroma.sqlite3`)
Se ocorrer um erro de escrita no Windows ao tentar reindexar documentos ou apagar a pasta `./data/chroma`, encerre os processos Python travados em segundo plano:

```powershell
taskkill /F /IM python.exe
Remove-Item -Recurse -Force ./data/chroma
```

### 2. Erro de porta 8000 ocupada
Caso o Uvicorn informe que a porta 8000 já está em uso:

```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force
```