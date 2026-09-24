import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Copiloto de Documentos RAG", page_icon="📄")
st.title("📄 Copiloto de Documentos Inteligente")

# Sidebar para upload de PDFs
st.sidebar.header("1. Upload de Documentos")
uploaded_file = st.sidebar.file_uploader("Envie um PDF", type=["pdf"])

if uploaded_file and st.sidebar.button("Indexar PDF"):
    with st.spinner("Processando e gerando embeddings..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            res = requests.post(f"{API_URL}/upload", files=files)
            if res.status_code == 201:
                chunks = res.json().get("chunks_indexed", 0)
                st.sidebar.success(f"Sucesso! {chunks} blocos indexados.")
            else:
                st.sidebar.error(f"Erro ao processar: {res.text}")
        except Exception as e:
            st.sidebar.error(f"Não foi possível conectar ao servidor backend: {e}")

# Área de Chat
st.header("2. Converse com seu Documento")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico de conversa
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("Ver fontes encontradas no documento"):
                for src in msg["sources"]:
                    st.write(f"- {src}")

# Entrada do usuário
if user_input := st.chat_input("Pergunte algo sobre o documento..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Consultando base vetorial..."):
            try:
                res = requests.post(f"{API_URL}/chat", json={"question": user_input})
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "Sem resposta.")
                    sources = data.get("sources", [])
                    
                    st.write(answer)
                    if sources:
                        with st.expander("Ver fontes encontradas no documento"):
                            for src in sources:
                                st.write(f"- {src}")
                                
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"Erro na API: {res.text}")
            except Exception as e:
                st.error(f"Erro de conexão com a FastAPI: {e}")
                