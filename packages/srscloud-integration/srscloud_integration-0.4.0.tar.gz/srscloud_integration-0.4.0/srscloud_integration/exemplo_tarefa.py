####### exemplo de integração com SRSCloud ##########
# utilize a biblioteca SRSCloud_Integration
#pip install srscloud-integration
from srscloud_integration import SRS
import sys
from datetime import datetime

# defina os parametros de configuração do seu sistema:
srs = SRS(token='',maquina='',workflow='',tarefa='')

# se precisar setar proxy: (se o SrsBot estiver instalado na maquina, a configuração é automatica)
#### DICA: coloque a senha de proxy nas variaveis de ambiente criptografada e descriptografe aqui
srs.proxy(server='', user='', password='')

# Inicie a execução: 
entrada = srs.execucaoIniciar() 
try:
    parametrosConfiguracao = entrada['Parametros'] #json com os parametros de configuração

    #criar log
    log = srs.log(statusId=2, mensagem="escreva sua mensagem de log") #registro de logs (2) ou Alertas (3)
    #Se precisar, pode enviar um arquivo de evidencia ou print de tela adicionando 2 parametros: arquivo='path do arquivo' 
    #logs são uteis para acompanhar o andamento da execução, use-o em momentos chave da sua aplicação, mas lembre-se que seu usuário estará acessando estes registros, não insira senhas nem crie um log muito detalhado e técnico demais. Isso deixa a plicação mais lenta e muito mais dificil de entender. 
    if not log['Autorizado']: #problemas com a execução!
        sys.exit()

    #######Filas #######

    #fila inserir
    referencia = 'Texto identificador do item' #procure combinar informações que sirvam de identificador unico deste item para seu cliente
    parametrosEntrada = {
        'Parametro': 'Valor', #parametros gerais
        'Lista': ['a','c'], #parametros tipo checkbox
        'Aniversario': '2025-01-01 00:00:00', #parametros tipo data precisam ser enviados neste formato, inclusive com HH:mm:ss 
        'Planilha': srs.formatar_arquivo('path do arquivo') #melhor forma de enviar arquivos 
    }#verifique os parametros corretos da sua tarefa no Portal SRS 

    fila = srs.filaInserir(referencia=referencia, 
                parametrosEntrada=parametrosEntrada, 
                workflow='WorkflowAlias', tarefa='TarefaAlias') #use-o para criar novos itens a serem processados, 
    ##Dicas:##
    # - Voce pode criar itens em filas de outros Workflows ou tarefas, permitindo assim que uma atividade flua por várias etapas representadas pelas tarefas pelas quais ela passou. 
    # - São raras as exceções onde voce deve criar um item de fila e consumi-lo na mesma tarefa. O caminho mais comum é uma tarefa criar itens para outra do mesmo workflow realizar 

    fila = srs.filaProximo() #recebe o proximo item a ser processado

    if fila['Autorizado']: #significa que existem dados para processar, insira aqui a parte do código para preparar o ambiente para seu robo
        
        ##############credencial de acesso ##################
        credencial = srs.credencialObter(sistema='Alias do sistema') #informações de acesso aos sistemas 
        print('Dados de acesso:', credencial)
        if credencial['Autorizado']: #Determina se este Workflow ainda tem acesso e se o Sistema possui alguma credencial válida e disponível. 
            print('Parametros da credencial como Login e Senha', credencial['CredencialParametro'])
            caminho = credencial['Sistema']['Caminho'] #Url, path ou caminho de acesso do sistema 
            ResponsavelSistema = {'Nome': credencial['Sistema']['RespTecNome'], 
                        'Email': credencial['Sistema']['RespTecEmail']}  #dados do contato em caso de sistema forma do ar
            ResponsavelCredencial = {'Nome': credencial['Credencial']['RespNome'], 
                        'Email': credencial['Credencial']['RespEmail']}  #dados do contato em caso de senha invalida ou prestes a expirar

            cred_expira_em = datetime.strptime(credencial['Credencial']['ExpiraEm'], '%Y-%m-%d')
            intervalo = (cred_expira_em - datetime.today()).days
            if intervalo < 3: # caso o sistema precise trocar a senha periodicamente, voce pode verificar a data de vencimento e tomar uma ação... 
                if credencial['Credencial']['GerarSenha'] == 1: #Esta credencial pode ser alterada pelo robo
                    ##### insira aqui a sequencia de passos para acessar o sistema e alterar a senha da credencial ### 
                    credUpd = srs.credencialAlterar(credencialId=credencial['Credencial']['CredenciaId'], 
                                                    expiraEm='NovaData', parametro='NomeParametro', 
                                                    valorAntigo='Valor atual do parametro', valorNovo='Novo valor do parametro', ativo=1)
                else: # a senha vai vencer, mas o robo não pode gerar senha sozinho
                    #### envie uma mensagem para o ResponsavelCredencial
                    mensagem = f""" Atenção, a senha da credencial {credencial['Credencial']['NomeCredencial']} do sistema {credencial['Sistema']['NomeSistema']} expirará em: {credencial['Credencial']['ExpiraEm']}. """
        

    while fila['Autorizado']: # Autorizado = False pode significar que não tem mais filas ou que o item enviado não está mais disponivel
        filaId = fila['Fila'][0]['FilaId'] #recebe ou confirma o FilaId que esta sendo processado
        print('filaId=',filaId, '\nReferencia:', fila['Fila'][0]['Referencia'], '\nParametrosEntrada', fila['Fila'][0]['ParametrosEntrada'])

        ######### inicio do código do seu robo para processar o item
        # aqui é o recheio do bolo, insira aqui o código do seu robo! 
        ######### inicio do código do seu robo para processar o item

        #se precisar pode contar com nossos serviços prontos, já deixamos pronto a integração com os mais usados, mas voce pode verificar na nossa BotStore outros serviços para voce usar
        captcha = srs.bsQuebraCaptcha(imagemCaptcha='c:/Automate Brasil/captcha.png') # por padrão chamamos todos os serviços da botstore com as iniciais bs... fique atento, alguns destes serviços são cobrados

        ######### Finalize o item de fila enviando informações para seu usuário
        arquivo = srs.formatar_arquivo('path do arquivo') # se precisar anexar um arquivo aos parametros, use a função de formação primeiro
        parametrosSaida = {'Empresa': 'Automate Brasil', 'Telefone': '11 2653-2649', 'Status': 'Ativo', 'Logo':arquivo}
        statusId=2 # 2 significa finalizado com sucesso, 3 finalizado com erro 
        proximo=1 # 0 apenas atualiza o item, 1 já retorna o proximo item da fila automaticamente para seguir com o loop
        mensagem='Empresa identificada e ativa' #a mensagem ajuda seus usuários a acompanhar o processamento da fila. 
        filaProximo = srs.filaAtualizar(parametrosSaida=parametrosSaida, statusId=statusId, proximo=proximo, mensagem=mensagem)
        
        if filaProximo['Autorizado']: 
            fila=filaProximo['Proximo'] #já pega os dados do proximo item de fila
        else: 
            print(fila) #Alguma coisa deu errado na atualização do seu item de fila
            break

    ##### Encerra a execução, insira aqui seu código de finalização para fechar sistemas e enviar comunicados

    comunicado = srs.enviarNotificacao(destino=[{'Token':srs.token}], canal=['Email', 'Portal'], assunto='Exemplo', mensagem='Enviando mensagem')

    fim = srs.execucaoFinalizar(mensagem='Execução finalizada com sucesso', status='Ok')
    print('finalizado:', fim)
except Exception as ex:#tratamento de erro na execução
    erro = {'Msg': 'Erro', 'type': type(ex).__name__, 'message': str(ex), 'lineo': ex.__traceback__.tb_lineno}
    mensagem = f'Erro de execução:{erro}'
    print(mensagem)    
    srs.logMaquina('alert', mensagem)
    fim = srs.execucaoFinalizar(mensagem=mensagem, status='Erro')