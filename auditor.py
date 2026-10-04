import os
import re
import pandas as pd
import gradio as gr

CAMINHO_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Cadastro_Empresarial.csv")

def inicializar_banco_dados():
    """Garante que a planilha de cadastros exista com o cabeçalho correto."""
    if not os.path.exists(CAMINHO_DATABASE):
        colunas = [
            "Tipo_Cadastro", "Razao_Social_Nome", "Nome_Fantasia", 
            "Documento_Fiscal", "Inscricao_Estadual", "Email_Corporativo", 
            "Telefone_Contato", "Endereco_Completo", "Status_Socio_Economico"
        ]
        df = pd.DataFrame(columns=colunas)
        df.to_csv(CAMINHO_DATABASE, index=False, encoding='utf-8')
inicializar_banco_dados()
def processar_cadastro(tipo, razao, fantasia, documento, inscricao, email, telefone, endereco, status):
    if not razao.strip() or not documento.strip() or not email.strip():
        return "⚠️ ERRO OPERACIONAL: Os campos 'Razão Social/Nome', 'Documento Fiscal' e 'E-mail' são obrigatórios.", CAMINHO_DATABASE
    documento_limpo = re.sub(r'\D', '', documento)
    if tipo == "Pessoa Jurídica (CNPJ)" and len(documento_limpo) != 14:
        return "⚠️ ERRO DE COMPLIANCE: O CNPJ inserido deve conter exatamente 14 dígitos numéricos.", CAMINHO_DATABASE
    elif tipo == "Pessoa Física (CPF)" and len(documento_limpo) != 11:
        return "⚠️ ERRO DE COMPLIANCE: O CPF inserido deve conter exatamente 11 dígitos numéricos.", CAMINHO_DATABASE
    try:
        df_atual = pd.read_csv(CAMINHO_DATABASE, dtype={"Documento_Fiscal": str})
        if documento_limpo in df_atual["Documento_Fiscal"].astype(str).values:
            return f"❌ CONFLITO: O documento '{documento}' já consta na base de dados do sistema.", CAMINHO_DATABASE
        novo_registro = {
            "Tipo_Cadastro": tipo,
            "Razao_Social_Nome": razao.strip(),
            "Nome_Fantasia": fantasia.strip() if fantasia.strip() else "N/A",
            "Documento_Fiscal": documento_limpo,
            "Inscricao_Estadual": inscricao.strip() if inscricao.strip() else "Isento",
            "Email_Corporativo": email.strip().lower(),
            "Telefone_Contato": telefone.strip(),
            "Endereco_Completo": endereco.strip(),
            "Status_Socio_Economico": status
        }
        df_novo = pd.concat([df_atual, pd.DataFrame([novo_registro])], ignore_index=True)
        df_novo.to_csv(CAMINHO_DATABASE, index=False, encoding='utf-8')
        logs = [
            "⚙️ ENGINE DE CADASTRO PROCESSADA COM SUCESSO",
            f"• Tipo de Entrada: {tipo}",
            f"• Beneficiário Mapeado: {razao.upper()}",
            f"• Status de Risco/Crédito: {status}",
            f"\n✅ Registro inserido com sucesso em: {os.path.basename(CAMINHO_DATABASE)}"
        ]
        return "\n".join(logs), CAMINHO_DATABASE
    except Exception as e:
        return f"❌ FALHA CRÍTICA NO MOTOR DE CADASTRO: {str(e)}", CAMINHO_DATABASE
tema_corporativo_claro = gr.themes.Default(
    primary_hue="blue",
    neutral_hue="slate",
)

with gr.Blocks(title="Enterprise Registration System v1.2") as app:
    gr.HTML("<div style='padding: 20px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 25px;'>"
            "<h1 style='color: #0f172a; font-family: sans-serif; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;'>ERP CENTRAL REGISTRATION PIPELINE v1.2</h1>"
            "<p style='color: #64748b; font-family: sans-serif; margin: 4px 0 0 0; font-size: 12px; font-weight: 500;'>MÓDULO INTERNO DE HOMOLOGAÇÃO DE CLIENTES E FORNECEDORES</p>"
            "</div>")
    with gr.Row():
        with gr.Column(scale=5):
            gr.Markdown("### 📋 Informações de Identificação")
            in_tipo = gr.Dropdown(
                choices=["Pessoa Jurídica (CNPJ)", "Pessoa Física (CPF)"], 
                value="Pessoa Jurídica (CNPJ)", 
                label="Natureza Jurídica do Cadastro"
            )
            with gr.Row():
                in_razao = gr.Textbox(label="Razão Social / Nome Completo", placeholder="Nome legal da entidade ou indivíduo")
                in_fantasia = gr.Textbox(label="Nome Fantasia (Opcional)", placeholder="Nome comercial da marca")
            with gr.Row():
                in_documento = gr.Textbox(label="Documento Fiscal (Apenas números)", placeholder="Ex: 00000000000100")
                in_inscricao = gr.Textbox(label="Inscrição Estadual", placeholder="Isento ou numeração fiscal estadual")
            gr.Markdown("### 📍 Contato e Localização")
            with gr.Row():
                in_email = gr.Textbox(label="E-mail Corporativo de Faturamento", placeholder="Ex: faturamento@empresa.com")
                in_telefone = gr.Textbox(label="Telefone do Responsável com DDD", placeholder="Ex: 11999999999")
            in_endereco = gr.Textbox(label="Endereço Comercial Completo", placeholder="Logradouro, número, complemento, cidade e estado")
            in_status = gr.Radio(
                choices=["Ativo / Crédito Aprovado", "Em Análise de Risco", "Bloqueado / Inadimplente"],
                value="Ativo / Crédito Aprovado",
                label="Classificação Operacional e Avaliação de Crédito"
            )           
            btn_cadastrar = gr.Button("⚡ CONSOLIDAR REGISTRO NO BANCO", variant="primary")
        with gr.Column(scale=4):
            gr.Markdown("### 🖥️ Telemetria e Logs do Servidor")
            out_logs = gr.Textbox(
                label="Status de Validação Interna", 
                lines=10, 
                interactive=False
            )
            gr.Markdown("### 📊 Repositório de Dados Consolidado")
            out_arquivo = gr.File(label="Baixar Planilha Unificada (.csv)", value=CAMINHO_DATABASE)
    btn_cadastrar.click(
        fn=processar_cadastro,
        inputs=[in_tipo, in_razao, in_fantasia, in_documento, in_inscricao, in_email, in_telefone, in_endereco, in_status],
        outputs=[out_logs, out_arquivo]
    )
if __name__ == "__main__":
    app.launch(inbrowser=True, theme=tema_corporativo_claro)
