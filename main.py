import streamlit as st
import psycopg2
from psycopg2 import extras
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Folgas - Gilmar Santos", layout="centered")

# --- CONEXÃO COM O BANCO ---
def conectar():
    params = {
        "dbname": "profunda_python",
        "user": "profunda_python_user",
        "password": "UzYpFalRAFMirRh130wkP66Z8eJ3OUwb",
        "host": "://render.com",
        "port": "5432",
        "sslmode": "require"
    }
    try:
        conn = psycopg2.connect(**params)
        conn.set_client_encoding('UTF8')
        return conn
    except:
        return None

# --- LÓGICA DE NEGÓCIO ---
def contar_por_data(data):
    conn = conectar()
    if not conn: return 0
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM folgas WHERE data = %s", (data,))
    count = cur.fetchone()[0]
    conn.close()
    return count

def salvar_folga(nome, data):
    conn = conectar()
    if not conn: return False
    cur = conn.cursor()
    cur.execute("INSERT INTO folgas (nome, data) VALUES (%s, %s)", (nome, data))
    conn.commit()
    conn.close()
    return True

# --- INTERFACE USUÁRIO ---
st.title("📅 Registro de Folgas")
st.subheader("Desenvolvido por Gilmar Santos")

with st.form("form_folga", clear_on_submit=True):
    nome = st.text_input("Nome Completo").strip().upper()
    data = st.date_input("Data da Folga", format="DD/MM/YYYY")
    data_str = data.strftime("%d/%m/%Y")
    
    submit = st.form_submit_button("Salvar Folga")
    
    if submit:
        if " " not in nome:
            st.error("Por favor, digite seu NOME COMPLETO.")
        elif contar_por_data(data_str) >= 2:
            st.error(f"A data {data_str} já possui o limite de 2 funcionários.")
        else:
            if salvar_folga(nome, data_str):
                st.success(f"Folga registrada com sucesso para {nome}!")
            else:
                st.error("Erro ao conectar com o banco. Tente novamente.")

# --- ÁREA ADMINISTRATIVA ---
st.markdown("---")
with st.expander("🔓 Painel Administrativo"):
    senha = st.text_input("Senha Admin", type="password")
    if senha == "admin123":
        conn = conectar()
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT id, nome, data FROM folgas ORDER BY id DESC")
        df = pd.DataFrame(cur.fetchall())
        conn.close()

        if not df.empty:
            st.write("### Lista de Folgas")
            st.dataframe(df[['nome', 'data']], use_container_width=True)
            
            # Exportar CSV
            csv = df[['nome', 'data']].to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Baixar CSV para Excel", csv, "folgas.csv", "text/csv")
        else:
            st.info("Nenhuma folga cadastrada.")

st.caption(f"© {datetime.now().year} Gilmar Santos | Todos os direitos reservados")
