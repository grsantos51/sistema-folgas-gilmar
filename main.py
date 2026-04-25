import streamlit as st
import psycopg2
from psycopg2 import extras
from datetime import datetime
import pandas as pd

# --- CONEXÃO COM O BANCO ---
def conectar():
    params = {
        "dbname": "profunda_python",
        "user": "profunda_python_user",
        "password": "UzYpFalRAFMirRh130wkP66Z8eJ3OUwb",
        "host": "://render.com",
        "port": "5432",
        "sslmode": "require",
        "connect_timeout": 15
    }
    try:
        conn = psycopg2.connect(**params)
        conn.set_client_encoding('UTF8')
        return conn
    except:
        return None

# --- INTERFACE ---
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
        else:
            conn = conectar()
            if conn:
                cur = conn.cursor()
                # Verifica limite de 2 por data
                cur.execute("SELECT COUNT(*) FROM folgas WHERE data = %s", (data_str,))
                if cur.fetchone()[0] >= 2:
                    st.error(f"A data {data_str} já possui o limite de 2 funcionários.")
                else:
                    cur.execute("INSERT INTO folgas (nome, data) VALUES (%s, %s)", (nome, data_str))
                    conn.commit()
                    st.success(f"Folga registrada para {nome}!")
                conn.close()
            else:
                st.error("Banco de dados fora do ar. Tente novamente em 30 segundos.")

# --- ADMIN ---
st.markdown("---")
with st.expander("🔓 Painel Administrativo"):
    senha = st.text_input("Senha Admin", type="password")
    if senha == "admin123":
        conn = conectar()
        if conn:
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT nome, data FROM folgas ORDER BY id DESC")
            df = pd.DataFrame(cur.fetchall())
            conn.close()

            if not df.empty:
                # Ajuste solicitado pelo Streamlit: width='stretch'
                st.dataframe(df[['nome', 'data']], width='stretch')
                csv = df[['nome', 'data']].to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Baixar CSV", csv, "folgas.csv", "text/csv")
            else:
                st.info("Nenhuma folga cadastrada.")

st.caption(f"© {datetime.now().year} Gilmar Santos | Todos os direitos reservados")
