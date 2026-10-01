import streamlit as st   #transforma o código em uma aplicação app web
import pandas as pd     #trabalha com dados organizados em tabelas, pense nela como um excel dentro do python
from datetime import datetime
from database import create_client, Client
from weasyprint import html   #Transforma o código html em PDF


#--integrando supabse--
SUPABASE_URL = "https://hwgczpnloaossmzpnrhc.supabase.co/rest/v1/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3Z2N6cG5sb2Fvc3NtenBucmhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc4NTg2NDYsImV4cCI6MjEwMzQzNDY0Nn0.9MuaOUxzpdzhwxlDFhw8mE9kW1_lmHGSC31Kli2C9n8"

@st.cache_resource #Esse é um decorador do Streamlit."Streamlit, tente reutilizar esse recurso em vez de criar uma nova conexão toda hora."
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(
    page_title="Economy - Controle de Caixa", layout="wide")
st.title("🛡️ BARATAS - Gestão de Caixa & Nuvem") #aqui estamos dando um título ao projeto

#função para gerar o PDF de fechamento
def gerar_pdf_fechamento(data_str, faturamento, custo, sangria, lucro, df_vendas, df_sangrias):
    vendas_html = "" #aqui ela armazena o HTML das vendas.
    if not df_vendas.empty:
        for _, row in df_vendas.iterrows():
            vendas_html += f"""
            <tr>
                <td>{row['produto_nome']}</td>
                <td>{row['quantidade']}</td>
                <td>R$ {float(row['preco_unitario']):.2f}</td>
                <td>R$ {float(row['total_vendido']):.2f}</td>
                <td>R$ {float(row['custo_total']):.2f}</td>
                <td>R$ {float(row['lucro_gerado']):.2f}</td>
            </tr>
            """

        else:
            vendas_html = "<tr><td colspan='6'>Nenhuma venda registrada hoje.</td></tr>"   #Aqui a condição, caso não haja vendas, será exibida essa mensagem.

        sangrias_html = ""
        if not df_sangrias.empty:   #empty verifica se o DataFrame está vazio. Aqui ele diz que não está vazio.
            for _, row in df_sangrias.iterrows():
               sangrias_html += f"""
                <tr>
                     <td>{row['motivo']}</td>
                     <td>R$ {float(row['valor']):.2f}</td>
                </tr>
                """
        else: 
            sangrias_html = "<tr><td colspan='2'>Nenhuma sangria realizada hoje.</td></tr>"  #Aqui a condição, caso não haja sangrias, será exibida essa mensagem.

        #CSS do PDF, aqui ele define o estilo do PDF, como cores, fontes, tamanhos, etc.
        html_str = f"""    
        <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 15mm; background-color: #f8fafc; }}
            body {{ font-family: Arial, sans-serif; color: #1e293b; }}
            .header {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .cards {{ display: table; width: 100%; margin-bottom: 20px; }}
            .card {{ display: table-cell; background: white; padding: 12px; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0; }}
            table {{ width: 100%; border-collapse: collapse; background: white; margin-top: 10px; margin-bottom: 20px; }}
            th, td {{ padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; font-size: 9pt; }}
            th {{ background: #f1f5f9; }}
            .title-sec {{ font-size: 11pt; font-weight: bold; margin-top: 15px; border-left: 4px solid #2563eb; padding-left: 8px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin:0;">📊 Fechamento de Caixa Diário</h1>
            <p style="margin:5px 0 0 0;">Data: {data_str}</p>
        </div>

        <div class="cards">
            <div class="card"><small>FATURAMENTO</small><br><b>R$ {faturamento:.2f}</b></div>
            <div class="card"><small>CUSTO PRODUTOS</small><br><b>R$ {custo:.2f}</b></div>
            <div class="card"><small>SANGRIA</small><br><b style="color:red;">- R$ {sangria:.2f}</b></div>
            <div class="card"><small>LUCRO LÍQUIDO</small><br><b style="color:green;">R$ {lucro:.2f}</b></div>
        </div>

        <div class="title-sec">📦 Vendas Realizadas</div>
        <table>
            <thead>
                <tr><th>Produto</th><th>Qtd</th><th>Unitário</th><th>Total</th><th>Custo</th><th>Lucro</th></tr>
            </thead>
            <tbody>{vendas_html}</tbody>
        </table>

        <div class="title-sec">💸 Sangrias do Dia</div>
        <table>
            <thead>
                <tr><th>Motivo</th><th>Valor</th></tr>
            </thead>
            <tbody>{sangrias_html}</tbody>
        </table>
    </body>
    </html>
    """
    return HTML(string=html_str).write_pdf()


    # --- NAVEGAÇÃO POR ABAS ---
aba1, aba2, aba3, aba4 = st.tabs(["📦 Produtos", "🛒 Vendas do Dia", "💸 Sangrias", "📊 Fechar Caixa & Dashboard"])

# 1. CADASTRO DE PRODUTOS
with aba1:
    st.header("Cadastrar Produto")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nome_p = st.text_input("Nome do Produto")
    with col2:
        custo_p = st.number_input("Preço Custo (R$)", min_value=0.0, step=0.50)
    with col3:
        margem_p = st.number_input("Margem Lucro (%)", min_value=0.0, value=30.0)
    
    venda_sugerida = custo_p * (1 + (margem_p / 100))
    with col4:
        venda_p = st.number_input("Preço Venda Final (R$)", min_value=0.0, value=float(venda_sugerida))

    if st.button("➕ Salvar Produto"):
        if nome_p:
            supabase.table("produtos").insert({
                "nome": nome_p, "preco_custo": custo_p, 
                "margem_lucro": margem_p, "preco_venda": venda_p
            }).execute()
            st.success("Produto salvo no Supabase!")
            st.rerun()

    prods = supabase.table("produtos").select("*").execute().data
    if prods:
        st.dataframe(pd.DataFrame(prods)[["id", "nome", "preco_custo", "margem_lucro", "preco_venda"]], use_container_width=True)
