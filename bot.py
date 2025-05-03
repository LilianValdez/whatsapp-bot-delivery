import qrcode
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# configuração: Defina a loja correspondente neste computador
LOJA = "Loja 1" # Altere para "loja 2" conforme necessário, nos outros computadores

#CHAVE PIX DE CADA LOJA
CHAVE_PIX = {
"lOJA 1": "chavepix-loja1@email.com",
"loja 2": "chavepix-loja2@email.com"
} 

# Definir arquivo de pedidos para cada loja
ARQUIVO_PEDIDOS =f"pedidos_{LOJA.replace(' ', '_').lower()}.csv"

    #iniciar o webdriver
driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com/")
input(f"Escaneie o QR Code no WhatsApp Web da {LOJA} e pressione Enter para continuar...")

    # Histórico de pedidos por cliente

histórico_pedidos = {}

    #função para gerar QR Code do Pix
def gerar_qr_code_pix(valor, descricao, nome_cliente):
        chave_pix = CHAVE_PIX[LOJA]
        pix_dados = f"00020101021126530014BR.GOV.BCB.PIX0136{chave_pix}5204000053039865405{valor}5802BR5925{descricao}6009{nome_cliente}62070503***6304"
        qr = qrcode.make(pix_dados)
        qr_path = f"{nome_cliente}_pix_{LOJA.replace('','_').lower()}.png"
        qr.save(qr_path)
        return qr_path

#função para encontrar mensagens não lidas
def encontrar_mensagens():
    try: 
        
        return driver.find_elements(By.CLASS_NAME,
"_21X1U ")
    except:
        print("Erro ao encontrar mensagens")
    return []

# função para responder mensagens
def responder_mensagem(mensagem, resposta):
    try:
         mensagem.click()
         time.sleep(2)
         campo_texto = driver.find_element(By.XPATH, "//div[@title= 'Digite uma mensagem']")
         campo_texto.send_keys(resposta)
         campo_texto.send_keys(Keys.ENTER)
    except:
        # Caso ocorra algum erro ao responder a mensagem
          print("Erro ao responder mensagem")
                
                #Função para salvar pedidos no histórico
    def salvar_pedido(nome, pedido, tipo, pagamento, horário, endereço = ""):
     df = pd.DataFrame([["Nome", "Pedido", "Tipo", "Pagamento", "Horário", "Endereço"]])
     try:
         df_existente = pd.read_csv(ARQUIVO_PEDIDOS[LOJA])
         df = pd.concat([df_existente, df], ignore_index=True) 
     except FileNotFoundError:
             pass
             df.to_csv(ARQUIVO_PEDIDOS[LOJA], index=False)
             if nome not in histórico_pedidos:
                 histórico_pedidos[nome] = []
     histórico_pedidos[nome].append({
                    "pedido": pedido,
                    "tipo": tipo,
                    "pagamento": pagamento,
                    "horário": horário,
                    "endereço": endereço
                })

# loop principal
while True:
     mensagens = encontrar_mensagens()
     for mensagem in mensagens:
        mensagem_texto = mensagem.text.lower()
     nome_cliente = mensagem.find_element(By.CLASS_NAME, "ggj6brxn").text

if "histórico" in mensagem_texto:
    if nome_cliente in histórico_pedidos:
        pedidos_passados = "\n".join(
            f"{p['horario']}: {p['pedido']} {p['tipo']})"
            for p in histórico_pedidos[nome_cliente]
        )
        resposta = f"histórico de pedidos:\n{pedidos_passados}"
    else:
        resposta = "Você não tem pedidos anteriores."
elif "agendar" in mensagem_texto:
    resposta = "Por favor, informe o horário desejado para entrega (ex: 19:30)."
    histórico_pedidos[nome_cliente] = {"status": "aguardando_horario"}

elif (
    nome_cliente in historico_pedidos
    and historico_pedidos[nome_cliente].get("status") == "aguardando_horario"
):
    historico_pedidos[nome_cliente]["horario"] = mensagem_texto
    resposta = f"Pedido agendado para {mensagem_texto}. Obrigado!"
    historico_pedidos[nome_cliente]["status"] = None

elif "pix" in mensagem_texto:
    qr_path = gerar_qr_code_pix("20.00", "Pedido Lanchonete", nome_cliente)
    resposta = f"Aqui está o Qr Code para pagamento via Pix. Faça o pagamento e envie *Pago*.\nArquivo: {qr_path}"

elif "pago" in mensagem_texto:
    resposta = f"Pagamento confirmado! Seu pedido está sendo preparado."

else:
    resposta = f"Olá! Você está falando com a *{LOJA}*. Digite *histórico* para ver seus pedidos anteriores ou *agendar* para marcar um horário."
responder_mensagem(mensagem, resposta)
time.sleep(5)                   

