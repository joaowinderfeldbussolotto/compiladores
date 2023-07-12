import pandas as pd
import xml.etree.ElementTree as ET

# ENTRADAS
entrada = list(open("inputs/entrada.txt"))
codigo = list(open("inputs/codigo.txt"))

parsing = ET.parse('inputs/GoldParser4.xml')
root = parsing.getroot()

# LISTAS 
simbolos = []
estados_finais = []
estados = []
alcancaveis = []
estados_vivos = []
tabela_de_simbolos = []
fita_de_saida = []
fita_de_saida_corrigida = []
escopo = []



redux_simbolos = []
simbolos_sintatico = []
producoes = []
tabela_lalr = []
pilha = ['0']

# DICIONARIOS
gramatica = {}
afnd = {}
indexSimboloRedux = {}


gramaticapd = pd.DataFrame()
count = 0



def tratar_entrada(entrada):
    estado_inicial = ''
    for linha in entrada:
        if '<S> ::=' in linha:
            estado_inicial = linha
        if '::=' in linha:
            tratar_gramatica(linha, estado_inicial)
        else:
            tratar_token(linha)





def tratar_gramatica(linha, estado_inicial):
    """ Faz o tratamento da gramatica, criando as regras e adicionando na gramatica """
    global count
    linha = linha.replace('\n', '')
    
    for i in linha.split(' ::= ')[1].replace('<', '').replace('>', '').split(' | '):
        if i[0] not in simbolos and not i[0].isupper():
            simbolos.append(i[0])
    regra = linha.split(' ::= ')[0].replace('<', '').replace('>', str(count))
    
    print("regra: ", regra)
    
    if regra[0] == 'S':
        count += 1        
        gramatica['S'] += linha.split(' ::= ')[1].replace('>', str(count) + '>').split(' | ')
    else:
        gramatica[regra] = linha.split(' ::= ')[1].replace('>', str(count) + '>').split(' | ')

    if '<S>' in linha.split(' ::= ')[1]:
        criar_inicial_alternativo(estado_inicial)    
    
    


def criar_inicial_alternativo(estado_inicial):
    """ Faz a criação de um estado inicial alternativo """
    global count
    if 'S' + str(count) in gramatica:
        return
    gramatica['S' + str(count)] = estado_inicial.replace('\n', '').split(' ::= ')[1].replace('>', str(count) + '>').split(' | ')
    
    
    
    
def tratar_token(linha):
    """ Faz o tratamento dos tokens, adicionando na gramatica """
    
    linha = linha.replace('\n', '')
    aux = linha
    linha = list(linha)
    
    for i in range(len(linha)):
        
        """ Se o simbolo não estiver na lista de simbolos e não for maiusculo, adiciona na lista de simbolos """
        if linha[i] not in simbolos and not linha[i].isupper():
            simbolos.append(linha[i])
            
        """ Se o tamanho do token for 1, adiciona na gramatica e adiciona o estado final na lista de estados finais """
        if len(linha) == 1:
            inicio_regra = '<' + aux.upper() + '>'
            gramatica['S'] += str(linha[i] + inicio_regra).split() # Adiciona na gramatica no estado inicial
            gramatica[aux.upper()] = []
            estados_finais.append(aux.upper())
                
        elif i == 0 and i != len(linha) - 1: # Se for a primeira posição e não for a ultima
            inicio_regra = '<' + aux.upper() + '1>'
            gramatica['S'] += str(linha[i] + inicio_regra).split()
            
        elif i == len(linha) - 1: # Se for a ultima posição
            final_regra = '<' + aux.upper() + '>'
            gramatica[aux.upper() + str(i)] = str(linha[i] + final_regra).split()
            gramatica[aux.upper()] = []
            estados_finais.append(aux.upper())
        
        else: # Se for uma posição intermediaria
            proxima_regra = '<' + aux.upper() + str(i + 1) + '>'
            gramatica[aux.upper() + str(i)] = str(linha[i] + proxima_regra).split()
            


def criar_afnd():
    
    """ Cria a estrutura do AFND """
    for estado in gramatica:
        afnd[estado] = {}
        estados.append(estado)
        for simbolo in simbolos:
            afnd[estado][simbolo] = []
        afnd[estado]['*'] = []
        
    """ Adiciona as transições no AFND """
    for estado in gramatica:
        for derivacao in gramatica[estado]:
            if len(derivacao) == 1 and derivacao.islower() and estado not in estados_finais:
                estados_finais.append(estado)
            elif derivacao == '*' and estado not in estados_finais:
                estados_finais.append(estado)
            elif derivacao[0] == '<':
                afnd[estado]['*'].append(derivacao.split('<')[1][:-1])
            elif derivacao != '*':
                afnd[estado][derivacao[0]].append(derivacao.split('<')[1][:-1])



def find_eps(estado_transicoes):
    for x in estado_transicoes:
        for y in afnd[x]['*']:
            if y not in estado_transicoes:
                estado_transicoes.append(y)
    return estado_transicoes


def eliminar_epsilon_transicoes():
    for regra in afnd:
        et_set = find_eps(afnd[regra]['*'])
        for state in et_set:
            if state in estados_finais:
                estados_finais.append(regra)
            for simbolo in afnd[state]:
                for transicao in afnd[state][simbolo]:
                    if transicao not in afnd[regra][simbolo]:
                        afnd[regra][simbolo].append(transicao)
        afnd[regra]['*'] = []
            
    
def determinizacao():
    newEstado = []
    for regra in afnd:
        for derivacao in afnd[regra]:
            if len(afnd[regra][derivacao]) > 1:
                new = []
                for state in afnd[regra][derivacao]:
                    if ':' in state:
                        for aux in state.split(':'):
                            if aux not in new:
                                new.append(aux)
                    else:
                        if state not in new:
                            new.append(state)
                if new:
                    new = sorted(new)
                    new = ':'.join(new)

                if new and new not in newEstado and new not in list(afnd.keys()):
                    newEstado.append(new)
                afnd[regra][derivacao] = new.split()
    if newEstado:
        novoEstado(newEstado)


def novoEstado(newState):
    for x in newState:
        afnd[x] = {}
        estados.append(x)
        for y in simbolos:
            afnd[x][y] = []
        afnd[x]['*'] = []
    
    for round in newState:
        agroup = sorted(round.split(':'))
        for x in agroup:
            if x in estados_finais and round not in estados_finais:
                estados_finais.append(round)
            for simbolo in simbolos:
                for transicao in afnd[x][simbolo]:
                    if not afnd[round][simbolo].__contains__(transicao):
                        afnd[round][simbolo].append(transicao)
    determinizacao()
    
    
def find_alcancaveis(estado):
    if estado not in alcancaveis:
        alcancaveis.append(estado)
        for s in afnd[estado]:
            if afnd[estado][s] \
                    and afnd[estado][s][0] not in alcancaveis:
                find_alcancaveis(afnd[estado][s][0])  


def eliminar_estados_inalcancaveis():
    find_alcancaveis('S')
    aux = {}
    aux.update(afnd)
    for regra in aux:
        if regra not in alcancaveis:
            del afnd[regra]



def adiciona_estado_erro():
    afnd['ERR'] = {}
    for s in simbolos:
        afnd['ERR'][s] = []
    afnd['ERR']['*'] = []
    for regra in afnd:
        for s in simbolos:
            if not afnd[regra][s]:
                afnd[regra][s] = ['ERR']
                
                
                
                
                
def buscar_vivos():
    change = False
    
    for regra in afnd:
        for s in afnd[regra]:
            if afnd[regra][s][0] in estados_vivos and regra not in estados_vivos:
                estados_vivos.append(regra)
                change = True
    if change:
        buscar_vivos()
                
                
                
def elimina_mortos():
    estados_vivos.extend(estados_finais)
    buscar_vivos()
    dead = []
    for regra in afnd:
        if regra not in estados_vivos and regra != 'ERR':
            dead.append(regra)
    
    for regra in dead:
        del afnd[regra]
    
    
def print_af():
    dataframe = pd.DataFrame(afnd)
    dataframe = dataframe.T
    print(dataframe)
    

def analise_lexica():
    separadores = [' ', '\n', '\t', '+', '-', '{', '}', '~', '.', ''],
    espacos = [' ', '\n', '\t', '']    
    operacoes = ['+', '-', '~', '.']
    # + -> soma
    # - -> subtração
    # ~ -> atribuição
    # . -> fim de sentença    
    count = 0
    #print(estados_finais)
    #print(simbolos)
    for nro_linha, linha in enumerate(codigo):  # Percorre as linhas do código de entrada
        #print('Linha: ', nro_linha)
        #print('Conteúdo: ', linha)
        estado = 'S'                                    # Estado inicial
        string = ''                                     # String que será reconhecida
        for char in linha:                              # Percorre os caracteres da linha
            #print('Caracter: ', char)
            #print('String: ', string)
            if char in operacoes and string:            # Se o caracter for uma OPERAÇÃO e a string não estiver vazia
                if string[-1] not in operacoes:         # Se o último caracter da string não for uma OPERAÇÃO
                    if estado in estados_finais:        # Se o estado atual for final
                        fita_de_saida.append(estado)    # Adiciona o estado atual na fita de saída
                        tabela_de_simbolos.append({'Linha': nro_linha, 'State': estado, 'Conteudo': string}) # Adiciona na tabela de símbolos
                    else:                               # Se o estado atual não for final então é um ERRO
                        fita_de_saida.append('ERR')    # Adiciona o estado ERRO na fita de saída
                        tabela_de_simbolos.append({'Linha': nro_linha, 'State': 'ERR', 'Conteudo': string}) # Adiciona na tabela de símbolos
                    estado = afnd['S'][char][0] # Estado atual recebe o próximo estado 
                    string = char              # String recebe o caracter atual
                    count += 1
                else:                              # Se o último caracter da string for uma OPERAÇÃO
                    string += char                  # Adiciona o caracter atual na string
                    if char not in simbolos:        # Se o caracter atual não for um símbolo
                        estado = 'ERR'                     # Estado atual recebe o estado de erro
                    else:                       # Se o caracter atual for um símbolo
                        estado = afnd[estado][char][0]  # Estado atual recebe o próximo estado
            elif char == ' ' and string:        # Se o caracter for um ESPAÇO e a string não estiver vazia
                if estado in estados_finais:    # Se o estado atual for final
                    fita_de_saida.append(estado) # Adiciona o estado atual na fita de saída >RECONHECIDO<
                    tabela_de_simbolos.append({'Linha': nro_linha, 'State': estado, 'Conteudo': string}) # Adiciona na tabela de símbolos
                else:                           # Se o estado atual não for final então é um ERRO
                    fita_de_saida.append('ERRO') # Adiciona o estado ERRO na fita de saída >ERRO<
                    tabela_de_simbolos.append({'Linha': nro_linha, 'State': 'ERR', 'Conteudo': string}) # Adiciona na tabela de símbolos
                estado = 'S'                    # Estado atual recebe o estado inicial
                string = ''                     # String recebe vazio
                count += 1
            elif char in separadores and string: # Se o caracter for um SEPARADOR e a string não estiver vazia
                if estado in estados_finais:    # Se o estado atual for final
                    fita_de_saida.append(estado) # Adiciona o estado atual na fita de saída >RECONHECIDO<
                    tabela_de_simbolos.append({'Linha': nro_linha, 'State': estado, 'Conteudo': string}) # Adiciona na tabela de símbolos
                else:                           # Se o estado atual não for final então é um ERRO
                    fita_de_saida.append('ERR') # Adiciona o estado ERRO na fita de saída >ERRO<
                    tabela_de_simbolos.append({'Linha': nro_linha, 'State': 'ERR', 'Conteudo': string}) # Adiciona na tabela de símbolos
                estado = 'S'                    # Estado atual recebe o estado inicial
                string = ''                     # String recebe vazio
                count += 1
            else: # por fim, se o caracter não for uma OPERAÇÃO ou um SEPARADOR (ele é um caractere comum)
                if char in espacos:
                    continue
                if char not in separadores and char not in operacoes and string: # Se o caracter não for um SEPARADOR e não for um OPERADOR e a string não estiver vazia
                    if string[-1] in operacoes:
                        if estado in estados_finais:
                            fita_de_saida.append(estado)
                            tabela_de_simbolos.append({'Linha': nro_linha, 'State': estado, 'Conteudo': string})
                        else: # deu erro
                            fita_de_saida.append('ERRO')
                            tabela_de_simbolos.append({'Linha': nro_linha, 'State': 'ERR', 'Conteudo': string})
                        estado = 'S' # volta pro estado inicial
                        string = '' # limpa a string
                        count += 1
                string += char # adiciona o caracter atual na string
                if char not in simbolos:
                    estado = 'ERR'
                else:
                    estado = afnd[estado][char][0]
    tabela_de_simbolos.append({'Linha': nro_linha, 'State': 'EOF', 'Conteudo': ''})
    fita_de_saida.append('EOF')
    erros = False
    for linha in tabela_de_simbolos:
        if linha['State'] == 'ERR':
            erros = True
            print('Erro léxico encontrado: Linha {}, Sentença "{}" não reconhecida'.format(linha['Linha']+1, linha['Conteudo']))
    if erros:
        exit()
                    
                    
def carrega_da_tabela():
    
    xml_simbolos = root.iter('Symbol') # Carrega os símbolos da tabela
    for simbolo in xml_simbolos:
        simbolos_sintatico.append({
            'Index': simbolo.attrib['Index'],
            'Name': simbolo.attrib['Name'],
            'Type': simbolo.attrib['Type']
        })
    
    xml_producoes = root.iter('Production') # Carrega as produções da tabela
    for producao in xml_producoes:
        producoes.append({
            'NonTerminalIndex': producao.attrib['NonTerminalIndex'],
            'SymbolCount': int(producao.attrib['SymbolCount']),
        })

    estados_tabela_lalr = root.iter('LALRState') # Carrega os estados da tabela LALR
    for estado in estados_tabela_lalr:
        tabela_lalr.append({}) # Adiciona um novo estado vazio (por ora) na tabela LALR
        for acao in estado:
            tabela_lalr[int(estado.attrib['Index'])][str(acao.attrib['SymbolIndex'])] = {
                'Action': acao.attrib['Action'],
                'Value': acao.attrib['Value']
            }
    
                        
                        
def corrige_ts(simb):
    indexes = {}
    for index, simbolo in enumerate(simb):
        indexes[simbolo['Name']] = str(index)
        indexSimboloRedux[str(index)] = simbolo['Name']
    for aux in fita_de_saida:
        if aux == 'S1' or aux == 'WHILE1:S1' or aux == 'SAME1:S1':
            aux = 'VAR'
        elif aux == 'S2':
            aux = 'NUM'
        elif aux == '$':
            aux = 'EOF'
        fita_de_saida_corrigida.append(indexes[aux])
        
    for linha in tabela_de_simbolos:
        if linha['State'] == 'S1' or linha['State'] == 'WHILE1:S1' or linha['State'] == 'SAME1:S1':
            linha['State'] = 'VAR'
        elif linha['State'] == 'S2':
            linha['State'] = 'NUM'
        elif linha['State'] == '$':
            linha['State'] = 'EOF'
        linha['State'] = indexes[linha['State']]
        
def faz_analise_sintatica():
    index = 0
    
    while True:
        last = fita_de_saida_corrigida[0]
        try:
            acao = tabela_lalr[int(pilha[0])][last]
        except:
            print('Erro sintático: Linha {}, Sentença "{}" não reconhecida'.format(tabela_de_simbolos[index]['Linha']+1, tabela_de_simbolos[index]['Conteudo']))
            exit()
            break
        
        if acao['Action'] == '1': # Equivale a SHIFT
            pilha.insert(0, fita_de_saida_corrigida.pop(0))
            pilha.insert(0, acao['Value'])
            index += 1
        elif acao['Action'] == '2': # Equivale a REDUCE
            lenght = producoes[int(acao['Value'])]['SymbolCount'] * 2 # Quantidade de símbolos da produção * 2 (porque cada símbolo é representado por um estado e um símbolo)
            while lenght: # Enquanto a quantidade de símbolos da produção não for 0
                pilha.pop(0)
                lenght -= 1
            redux_simbolos.append(producoes[int(acao['Value'])]['NonTerminalIndex']) # Adiciona o símbolo reduzido na lista de símbolos reduzidos
            pilha.insert(0, producoes[int(acao['Value'])]['NonTerminalIndex']) # Adiciona o símbolo reduzido na pilha
            pilha.insert(0, tabela_lalr[int(pilha[1])][pilha[0]]['Value']) # Adiciona o estado da tabela LALR na pilha
        elif acao['Action'] == '3': # Equivale a ACCEPT
            print('Salto')
        elif acao['Action'] == '4': # Equivale a ERROR
            break
        
def captura():
    aux = [1]
    id = 1
    for simbolo in redux_simbolos:
        if indexSimboloRedux[simbolo] == 'CONDS':
            id+=1
            aux.insert(0, id)
        elif indexSimboloRedux[simbolo] == 'REP' or indexSimboloRedux[simbolo]  == 'COND':
            aux.pop(0)
        elif indexSimboloRedux[simbolo] == 'RVAR':
            escopo.append(aux[0])


def completa_tabela_de_simbolos():
    for token in tabela_de_simbolos:
        if token['State'] == 'VAR':
            token['Scope'] = escopo.pop(0)
        
        
            
        
                        
                
def analise_sintatica():
    carrega_da_tabela() # Carrega a tabela LALR e suas informações
    corrige_ts(simbolos_sintatico) # Corrige a tabela de símbolos substituindo os estados pelos símbolos corretos
    faz_analise_sintatica()
    captura()
    completa_tabela_de_simbolos()
                
                
    # print('tabela de simbolos: ', tabela_de_simbolos)
    # print('fita de saida: ', fita_de_saida)
    # print('fita: ', fita_de_saida_corrigida)
    # print('tabela lalr: ', tabela_lalr)
    # print('producoes: ', producoes)
    # print('simbolos: ', simbolos_sintatico)
    
                
    
    
    
    
    


def main():
    gramatica['S'] = []
    tratar_entrada(entrada)
    
    criar_afnd()
    
    print('----------AFND CRIADO--------------')    
    print_af()
    
    eliminar_epsilon_transicoes()
    
    print('----------EPSILON TRANSICOES ELIMINADAS--------------')
    print_af()
    
    determinizacao()
    
    print('------------DETERMINIZADO------------')
    print_af()
    
    eliminar_estados_inalcancaveis()
    
    print('------------ELIMINOU INALCANCAVEIS------------')
    print_af()
    
    adiciona_estado_erro()
    
    print('------------ADICIONOU ESTADO DE ERRO------------')
    print_af()
    
    elimina_mortos() 
    
    print('------------ELIMINOU MORTOS------------')
    print_af()
    
    print("\n"* 60)
    print('------------ANALISE LEXICA------------')
    
    
    analise_lexica()
    
    print('------------FIM DA ANALISE LEXICA------------')
    
    analise_sintatica()

    
if __name__ == '__main__':
    main()

