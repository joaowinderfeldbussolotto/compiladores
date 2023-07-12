import pandas as pd
import xml.etree.ElementTree as ET


# ENTRADAS 

arquivo = list(open('inputs/entrada.txt'))
codigo  = list(open('inputs/codigo.txt'))
tree = ET.parse('inputs/GoldParsingTable.xml')
root = tree.getroot()


# LISTAS

simbolos = []
estados = []
alcan = []
finais = []
vivos = []
tabela_de_simbolos = []
fitaSaida = []
fita = []
escopo = []
block = []
redux_symbol = []
symbols = []
productions = []
lalr_table = []
pilha  = ['0']



# DICIONARIOS

gramatica = {}
tabela = {}
epTransicao = {}
idxSymbolRedux = {}



# GLOBAIS

repeticao = 0


# LISTAS DE VERIFICAÇÃO

separadores = [' ', '\n', '\t', '+', '-', '{', '}', '~', '.']
espacadores = [' ', '\n', '\t']
operadores  = ['+', '-', '~', '.']


def eliminar_mortos():
    """ Elimina os símbolos mortos da tabela """
    mortos = []
    for x in tabela:
        if x not in vivos and x != '€':
            mortos.append(x)

    for x in mortos:
        del tabela[x]




def buscar_vivos():
    """ Busca os símbolos vivos da tabela para eliminar os mortos"""
    mudou = False

    for regra in tabela:
        for simbolo in tabela[regra]:
            if tabela[regra][simbolo][0] in vivos and regra not in vivos:
                vivos.append(regra)
                mudou = True

    if mudou:
        buscar_vivos()



def elimina():
    """ Elimina os símbolos mortos da tabela """
    loop = {}
    loop.update(tabela)
    for regra in loop:
        if regra not in alcan:
            del tabela[regra]




def busca_alcancaveis(estado):
    """ Busca os alcancaveis da tabela """
    if estado not in alcan:
        alcan.append(estado)
        for simbolo in tabela[estado]:
            if tabela[estado][simbolo] \
                    and tabela[estado][simbolo][0] not in alcan:
                busca_alcancaveis(tabela[estado][simbolo][0])



def encontra_epsilon_transicoes(e_transicoes):
    """ Encontra as epsilon transições """
    for x in e_transicoes:
        for y in tabela[x]['*']:
            if y not in e_transicoes:
                e_transicoes.append(y)
    return e_transicoes



def eliminar_epsilon_transicoes():
    """ Elimina as epsilon transições """
    for regra in tabela:
        et_set = encontra_epsilon_transicoes(tabela[regra]['*'])
        for estado in et_set:
            if estado in finais:
                finais.append(regra)
            for simbolo in tabela[estado]:
                for transicao in tabela[estado][simbolo]:
                    if transicao not in tabela[regra][simbolo]:
                        tabela[regra][simbolo].append(transicao)
        tabela[regra]['*'] = []



def criar_novos(nstates):
    """ Faz o processo de criação de novos estados na etapa de determinização """
    for x in nstates:
        tabela[x] = {}
        estados.append(x)
        for y in simbolos:
            tabela[x][y] = []
        tabela[x]['*'] = []

    for state in nstates:
        estadosjuntar = sorted(state.split(':'))
        for x in estadosjuntar:
            if x in finais and state not in finais:
                finais.append(state)
            for simbolo in simbolos:
                for transition in tabela[x][simbolo]:
                    if not tabela[state][simbolo].__contains__(transition):
                        tabela[state][simbolo].append(transition)
    determinizacao()



def determinizacao():
    """ Faz o processo de determinização no AFND"""
    novosestados = []
    for regra in tabela:
        for producao in tabela[regra]:
            if len(tabela[regra][producao]) > 1:
                novo = []
                for estado in tabela[regra][producao]:
                    if ':' in estado:
                        for aux in estado.split(':'):
                            if aux not in novo:
                                novo.append(aux)
                    else:
                        if estado not in novo:
                            novo.append(estado)

                if novo:
                    novo = sorted(novo)
                    novo = ':'.join(novo)

                if novo and novo not in novosestados and novo not in list(tabela.keys()):
                    novosestados.append(novo)
                tabela[regra][producao] = novo.split()
    if novosestados:
        criar_novos(novosestados)



def criar_af():
    """ Cria o AFND com base na gramática e tokens """
    for x in gramatica:
        tabela[x] = {}
        estados.append(x)
        for y in simbolos:
            tabela[x][y] = []
        tabela[x]['*'] = []

    for regra in gramatica:
        for producao in gramatica[regra]:
            if len(producao) == 1 and producao.islower() and regra not in finais:
                finais.append(regra)
            elif producao == '*' and regra not in finais:
                finais.append(regra)
            elif producao[0] == '<':
                tabela[regra]['*'].append(producao.split('<')[1][:-1])
            elif producao != '*':
                tabela[regra][producao[0]].append(producao.split('<')[1][:-1])




def trata_inicial(s):
    """ Trata a regra inicial da gramática """
    global repeticao
    if 'S' + str(repeticao) in gramatica:
        return
    gramatica['S' + str(repeticao)] = s.replace('\n', '').split(' ::= ')[1].replace('>', str(repeticao) + '>').split(' | ')



def tratar_gramatica(gram, s):
    """ Trata a gramática para a criação do AFND """
    global repeticao
    gram = gram.replace('\n', '')
    for x in gram.split(' ::= ')[1].replace('<', '').replace('>', '').split(' | '):
        if x[0] not in simbolos and not x[0].isupper():
            simbolos.append(x[0])
    regra = gram.split(' ::= ')[0].replace('>', str(repeticao)).replace('<', '')

    if regra[0] == 'S':
        repeticao += 1
        gramatica['S'] += gram.split(' ::= ')[1].replace('>', str(repeticao) + '>').split(' | ')
    else:
        gramatica[regra] = gram.split(' ::= ')[1].replace('>', str(repeticao)+'>').split(' | ')

    if '<S>' in gram.split(' ::= ')[1]:
        trata_inicial(s)



def tratar_token(token):
    """ Trata os tokens para a criação do AFND """
    token = token.replace('\n', '')
    cp_token = token
    token = list(token)
    for x in range(len(token)):
        if token[x] not in simbolos and not token[x].isupper():
            simbolos.append(token[x])

        if len(token) == 1:
            iniregra = '<' + cp_token.upper() + '>'
            gramatica['S'] += str(token[x] + iniregra).split()
            gramatica[cp_token.upper()] = []
            finais.append(cp_token.upper())
        elif x == 0 and x != len(token)-1:
            iniregra = '<' + cp_token.upper() + '1>'
            gramatica['S'] += str(token[x] + iniregra).split()
        elif x == len(token)-1:
            finregra = '<' + cp_token.upper() + '>'
            gramatica[cp_token.upper() + str(x)] = str(token[x] + finregra).split()
            gramatica[cp_token.upper()] = []
            finais.append(cp_token.upper())
        else:
            proxregra = '<' + cp_token.upper() + str(x+1) + '>'
            gramatica[cp_token.upper() + str(x)] = str(token[x] + proxregra).split()



def estado_erro():
    """ Cria o estado de erro no AFD """
    tabela['€'] = {}
    for y in simbolos:
        tabela['€'][y] = []
    tabela['€']['*'] = []
    for regra in tabela:
        for simbolo in tabela[regra]:
            if not tabela[regra][simbolo]:
                tabela[regra][simbolo] = ['€']



def analise_lexica():
    """ Faz a análise léxica do código fonte """
    id = 0
    # + -> soma
    # - -> subtração
    # ~ -> atribuição
    # . -> fim de sentença  
    
    for idx, linha in enumerate(codigo):
        E = 'S' # Estado inicial
        string = ''  # String que será analisada/reconhecida
        for char in linha: # Percorre a linha
            if char in operadores and string: # Se o caractere for um operador e a string não estiver vazia
                if string[-1] not in operadores: # Verifica se o último caractere da string não é um operador
                    if E in finais: # Se o estado atual é final, adiciona a string à tabela de símbolos
                        tabela_de_simbolos.append({'Line': idx, 'State': E, 'Label': string}) 
                        fitaSaida.append(E)
                    else:
                        tabela_de_simbolos.append({'Line': idx, 'State': 'Error', 'Label': string})
                        fitaSaida.append('Error')
                    E = tabela['S'][char][0] # Atualiza o estado atual com base na tabela de transição
                    string = char
                    id += 1
                else: # Se o último caractere da string é um operador
                    string += char
                    if char not in simbolos:
                        E = '€'
                    else:
                        E = tabela[E][char][0] # Atualiza o estado atual com base na tabela de transição
            elif char in separadores and string: # Se o caractere for um separador e a string não estiver vazia
                if E in finais: # Se o estado atual é final, adiciona a string à tabela de símbolos
                    tabela_de_simbolos.append({'Line': idx, 'State': E, 'Label': string})
                    fitaSaida.append(E)
                else:
                    tabela_de_simbolos.append({'Line': idx, 'State': 'Error', 'Label': string})
                    fitaSaida.append('Error')
                E = 'S' # Atualiza o estado atual para o estado inicial
                string = ''
                id += 1
            else: # Se o caractere não for um operador ou separador ou string vazia
                if char in espacadores: # Se o caractere for um espaço, tabulação ou quebra de linha,
                    continue
                if char not in separadores and char not in operadores and string: # Se o caractere não for um separador ou operador ou espacador e a string não estiver vazia
                    if string[-1] in operadores: # Verifica se o último caractere da string é um operador
                        if E in finais: # Se o estado atual é final, adiciona a string à tabela de símbolos
                            tabela_de_simbolos.append({'Line': idx, 'State': E, 'Label': string})
                            fitaSaida.append(E)
                        else:
                            tabela_de_simbolos.append({'Line': idx, 'State': 'Error', 'Label': string})
                            fitaSaida.append('Error')

                        E = 'S' # Atualiza o estado atual para o estado inicial
                        string = ''
                        id += 1
                string += char
                if char not in simbolos:
                    E = '€'
                else:
                    E = tabela[E][char][0] # Atualiza o estado atual com base na tabela de transição


    tabela_de_simbolos.append({'Line': idx, 'State': 'EOF', 'Label': ''})
    fitaSaida.append('EOF')
    
    """ VERIFICAR SE A TABELA DE SÍMBOLOS TEM ERROS """
    erro = False
    for linha in tabela_de_simbolos:
        if linha['State'] == 'Error':
            erro = True
            print('Erro léxico: linha {}, sentença "{}" não reconhecida!'.format(linha['Line']+1, linha['Label']))
    if erro:
        exit()

def corrige_tabela_de_simbolos(symbols):
    """ Remapeia os símbolos da tabela de símbolos para adequar ao formato da tabela de símbolos do LALR """
    symbols_indexes = {}  
    for index, symbol in enumerate(symbols):
        symbols_indexes[symbol['Name']] = str(index)
        idxSymbolRedux[str(index)] = symbol['Name']
    for fta in fitaSaida:
        if fta == 'S1' or fta == 'ENQUANTO1:S1' or fta == 'IGUAL1:S1':
            fta = 'VAR'
        elif fta == 'S2':
            fta = 'NUM'
        elif fta == '$':
            fta = 'EOF'
        fita.append(symbols_indexes[fta])

    for line in tabela_de_simbolos:
        if line['State'] == 'S1' or line['State'] == 'ENQUANTO1:S1' or line['State'] == 'IGUAL1:S1':
            line['State'] = 'VAR'
        elif line['State'] == 'S2':
            line['State'] = 'NUM'
        elif line['State'] == '$':
            line['State'] = 'EOF'


def carrega_da_tabela():
    """ Carrega as informações da tabela LALR do arquivo XML para as variáveis globais """
    xml_symbols = root.iter('Symbol')
    for symbol in xml_symbols:
        symbols.append({
            'Index': symbol.attrib['Index'],
            'Name': symbol.attrib['Name'],
            'Type': symbol.attrib['Type']
        })

    xml_productions = root.iter('Production')
    for production in xml_productions:
        productions.append({
            'NonTerminalIndex': production.attrib['NonTerminalIndex'],
            'SymbolCount': int(production.attrib['SymbolCount']),
        })

    lalr_states = root.iter('LALRState')
    for state in lalr_states:
        lalr_table.append({})
        for action in state:
            lalr_table[int(state.attrib['Index'])][str(action.attrib['SymbolIndex'])] = {
                'Action': action.attrib['Action'],
                'Value': action.attrib['Value']
            }
            
            
# Ver os tokens estão escritos na ordem correta
def faz_analise_sintatica():
    idx = 0
    while True: # Enquanto a fita não estiver vazia
        ultimo_fita = fita[0] # Último símbolo da fita (i.e o próximo a ser lido) (estado)
        try:
            action = lalr_table[int(pilha[0])][ultimo_fita] # Ação a ser tomada de acordo com a tabela LALR, se não existir, erro sintático
        except:

            # print(pd.DataFrame(lalr_table))
   
            print('Erro sintático: linha {}, sentença "{}" não reconhecida!'.format(tabela_de_simbolos[idx]['Line']+1, tabela_de_simbolos[idx]['Label']))
            exit()
            

        if action['Action'] == '1': # Empilhamento ou shift
            pilha.insert(0, fita.pop(0))
            pilha.insert(0, action['Value'])
            idx += 1
        elif action['Action'] == '2': # Redução
            size = productions[int(action['Value'])]['SymbolCount'] * 2 # Recupera o número de símbolos da produção
            while size: # Desempilha os símbolos da produção
                pilha.pop(0)
                size -= 1
            # redux_symbol.append(productions[int(action['Value'])]['NonTerminalIndex'])
            #Após a redução, ocorre um salto (fica um numero(salto) no topo da pilha)
            pilha.insert(0, productions[int(action['Value'])]['NonTerminalIndex'])
            pilha.insert(0, lalr_table[int(pilha[1])][pilha[0]]['Value'])
        elif action['Action'] == '3':  
            print('salto')
            # Mude para o próximo estado indicado na célula correspondente do símbolo não-terminal
            # pilha.insert(0, lalr_table[int(pilha[0])][action['Value']]['Value'])
        elif action['Action'] == '4': # Aceite
            break
        
        
        
        
def captura_demais():
    pilha_aux = [1]
    id = 1
    for symbol in redux_symbol:
        if idxSymbolRedux[symbol] == 'CONDS':
            id += 1
            pilha_aux.insert(0, id)
            block.append(pilha_aux[1])
        elif idxSymbolRedux[symbol] == 'REP' or idxSymbolRedux[symbol] == 'COND':
            pilha_aux.pop(0)
        elif idxSymbolRedux[symbol] == 'RVAR':
            escopo.append(pilha_aux[0])
            
            
            
            
def completa_tabela_de_simbolos():
    for token in tabela_de_simbolos:
        if token['State'] == 'VAR':
            token['Scope'] = escopo.pop(0)



def analisador_sintatico():
    carrega_da_tabela() # Carrega a tabela do GoldParser e coloca em diversas listas
    corrige_tabela_de_simbolos(symbols) # Corrige a tabela de simbolos para o formato do GoldParser
    faz_analise_sintatica() # Faz a análise sintática em si
    # captura_demais() # Captura os blocos e escopos
    # completa_tabela_de_simbolos()  # Completa a tabela de simbolos com os escopos

def print_af():
    dataframe = pd.DataFrame(tabela)
    dataframe = dataframe.T
    print(dataframe)


def elimina_inalcancaveis():
    busca_alcancaveis('S')
    elimina()
    
    
def elimina_mortos():
    vivos.extend(finais)
    buscar_vivos()
    eliminar_mortos()
    


def parte_LFA():
    

    
    gramatica['S'] = []
    estadoinicial = ''
    for x in arquivo:
        if '<S> ::=' in x: 
            estadoinicial = x # define o estado inicial
        if '::=' in x: # se for uma regra de produção
            tratar_gramatica(x, estadoinicial)
        else: # se for um token
            tratar_token(x)
    
    
            
    criar_af() # cria o afnd        
    # print('---------- AFND CRIADO --------------')    
    # print_af()
    
    
    eliminar_epsilon_transicoes() # elimina as epsilon transições
    # print('---------- EPSILON TRANSICOES ELIMINADAS --------------')    
    # print_af()
    
    
    determinizacao() # determiniza o afnd
    # print('---------- AFND DETERMINIZADO / GEROU AFD --------------')    
    # print_af()
    
    
    elimina_inalcancaveis() # elimina estados inalcançaveis
    # print('---------- ESTADOS INALCANÇAVEIS ELIMINADOS --------------')
    # print_af()
    
    
    estado_erro() # cria o estado de erro
    # print('---------- ESTADO DE ERRO CRIADO --------------')
    # print_af()
    

    elimina_mortos() # elimina estados mortos
    print('---------- ESTADOS MORTOS ELIMINADOS --------------')
    print_af()


def main():
    
    parte_LFA() # parte do CCR de LFA 
    analise_lexica() # parte do CCR de Compiladores
    analisador_sintatico() # parte do CCR de Compiladores
    
    print('Código compilado sem erros!')



if __name__ == '__main__':
    main()
