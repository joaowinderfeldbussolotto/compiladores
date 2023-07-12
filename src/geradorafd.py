import sys
import pandas as pd


possibleRules = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
allRules = []
INITIALSTATE = 'S'


def openFile(fileName):
    """ Abre arquivo e retorna o objeto do arquivo """
    try:
        file = open(fileName, 'r')
        return file
    except:
        print('Erro ao abrir arquivo')




def getParam(arg):
    """ Retorna o parâmetro passado na linha de comando """
    return sys.argv[arg]




def getData(file):
    """ Pega o arquivo e retorna uma lista de linhas """
    data = list()
    for line in file:
        data.append(line)
    return data




def getTokens(data):
    """ Faz a busca dos tokens e retorna uma lista de tokens """
    dirtyTokens = []
    for line in data:
        if line == '\n':
            break
        else:
            dirtyTokens.append(line)
    return dirtyTokens




def getGR(data):
    """ Faz a busca das gramaticas e retorna uma lista de gramaticas """
    data.reverse()
    grs = []
    for line in data:
        if line == '\n':
            break
        else:
            grs.append(line)
    return removeQuebraLinha(grs)




def removeQuebraLinha(data):
    """ Remove quebra de linhas """
    cleaned = []
    for token in data:
        cleaned.append(token.replace('\n', ''))
    return cleaned




def parseTokens(tokens):
    """ Quebra os tokens no menor possível """
    parsed = []
    for token in tokens:
        for char in token:
            parsed.append(char)
    parsed = sorted(set(parsed))
    return parsed




def parseGR(grs):
    """ Faz o parse das gramaticas 
        e retorna uma lista:
        formato : [['<rulename>', ['<rule1>', '<rule2>', '<rule3>']], ['<rulename>', ['<rule1>', '<rule2>']]] """

    parsedGRs = []
    
    for gr in grs:

        completedRule = []
        dirtyRuleName = gr.split('::=')[0]
        ruleName = dirtyRuleName.replace('<','').replace('>','')

        dirtyRules = gr.split('::=')[1]
        rules = dirtyRules.split('|')

        for rule in rules:
            rule = rule.replace(' ','')

        ruleName = ruleName.replace(' ','')

        completedRule.append(ruleName)
        completedRule.append(rules)

        parsedGRs.append(completedRule)

    return parsedGRs




def getGRStokens(gr):
    """ Pega os tokens presentes nas gramáticas """
    grTokens = []

    for rule in gr:
        temp = rule.split('::=')[1]
        temp = temp.split('|')

        for aux in temp:
            aux = aux.split('<')
            grTokens.append(aux[0])
            
    return sorted(set(grTokens))




def removeBlankSpace(data):
    """ remove espaços em branco """
    cleaned = []

    for token in data:
        cleaned.append(token.replace(' ', ''))

    return cleaned




def createTable(tokens, grs):
    """ Faz a criação da tabela"""

    indexes = []
    for rule in grs:
        indexes.append(rule[0])
        allRules.append(rule[0])

    indexes.append('ERR') # adiciona estado de erro
    
    table = pd.DataFrame(index=indexes, columns=tokens)

    return table



def updatePossibleRules():
    """ Faz a atualização da lista de possiveis nomes de regras """
    for rule in allRules:
        if rule not in possibleRules:
            continue
        else:
            possibleRules.remove(rule)
            
            

def removeEpsilon(data):
    """ Remove o simbolo epsilon """
    cleaned = []

    for token in data:
        if token == 'ε' or token == 'Îµ':
            continue
        else:
            cleaned.append(token)
    

    return cleaned




def virouTerminal(table, ruleName):
    """ Torna determinada regra em uma regra terminal """
    nova = '*' + ruleName
    table = table.rename(index = {ruleName:nova})
    return table



def newBlankRow(table, indexName):
    """ Adiciona uma linha em branco dado um nome de regra """
    lista = []
    
    for i in range(len(table.columns)):
        lista.append('')

    table.loc[indexName] = lista
    allRules.append(indexName) # adiciona a regra na lista de regras
    
    return table



def criaRegraFinal(table, grName, terminal):
    """ Trata o caso de uma regra ter apenas um terminal
        cria-se uma regra final para o terminal """
    
    if '*' in grName:
        grName = grName.replace('*', '')
    
    updatePossibleRules()
    
    newGrName = possibleRules[0] # próximo nome de regra disponível
    
    if table.loc[grName, terminal] != 'nan':
        table.loc[grName, terminal] += ',' + newGrName
        table = newBlankRow(table, newGrName)
        table = virouTerminal(table, newGrName)
    else:
        table.loc[grName, terminal] = newGrName
        table = newBlankRow(table, newGrName)
        table = virouTerminal(table, newGrName)
    
    updatePossibleRules()
        
    return table
        
    
        
    

def fillWithGRs(table, gramaticas):
    """ Faz o primeiro preenchimento da tabela
        Esse preenchimento é feito pelas gramáticas que foram passadas """

    #print('Preenchendo tabela...', gramaticas)
    
    # Formato : [['A', [' e<A> ', ' i<A> ', '  ε']], ['S', [' e<A> ', ' i<A>']]]

    for gr in gramaticas:
        
        grName = str(gr[0])     # nome da gramatica : 'A'-> ['A', [' e<A> ', ' i<A> ', '  ε']]
        rules = gr[1]           # regras : ' e<A> ', ' i<A> ', '  ε' -> ['A', [' e<A> ', ' i<A> ', '  ε']]

        for rule in rules:

            rule = rule.replace(' ', '').replace('\n', '')

            if "ε" in rule or "Îµ" in rule: # Se tem epislon a regra em questão vira terminal

                #print('Regra:', grName, 'tem epsilon')
                table = virouTerminal(table, grName)

                continue


            elif rule.find('<') == -1: # Se não tem (<) executa :: (É UM TERMINAL)
                
                terminal = rule
                table = criaRegraFinal(table, grName, terminal)

                    
                
                continue

            else: # SE TEM SIMBOLO NÃO-TERMINAL
                
                rule = rule.replace('>', '')
                ruleSplited = rule.split('<')
                token = ruleSplited[0]
                production = str(ruleSplited[1])
                #print(token, production)
                if table.loc[grName, token] == 'nan':
                    table.loc[grName, token] = production
                else:
                    table.loc[grName, token] += ',' + production
                
        
    return ordenaTable(table)




def temRegraNova(table):
    """ Verifica se foram criadas novas regras """
    for index in table.index:
        for token in table.columns:
            if len(table.loc[index, token]) > 1 and table.loc[index, token] not in allRules:
                return True
            else:
                continue
    return False           
    



def ordenaTable(table):
    """ Ordena a tabela e deixa a tabela 'limpa' """
    for index in table.index:
        for token in table.columns:
            if ',' in table.loc[index, token]:
                table.loc[index, token] = table.loc[index, token].replace('-,', '')
                table.loc[index, token] = quebraEordena(table.loc[index, token])
            else:
                continue
    return table




def removeNan(table):
    """ Remove os 'nan's da tabela """
    for index in table.index:
        for token in table.columns:
            if table.loc[index, token] == 'nan':
                table.loc[index, token] = ''
    return table



def quebraEordena(string):
    """ Usada para ordenar cada regra composta """
    
    string = string.split(',')
    string = sorted(set(string))
    newString = ','.join(string)
    
    return newString




def determiniza(afnd, tokens):
    """ Faz a determinização da tabela """

    afd = pd.DataFrame(columns=tokens) # cria a tabela vazia que será a AFD
    
    afd = afd[tokens].astype(str)

    newRules = [] # Guarda as novas regras

    # VERIFICA SE FORAM CRIADAS NOVAS REGRAS
    
    for index in afnd.index:
        for token in afnd.columns:
            #print('BUGGGGG::', index, token,afnd.loc[index, token])


            if len(afnd.loc[index, token]) > 0:

                rule = afnd.loc[index, token]
                if rule[0] == ',':
                    afnd.loc[index, token] = rule[1:]

            if len(afnd.loc[index, token]) > 0 and afnd.loc[index, token] not in allRules: # se é uma regra composta e não está na lista de regras
                #print('Regra:', index, 'tem novas regras', afnd.loc[index, token], '\n')
                newRules.append(quebraEordena(afnd.loc[index, token])) # guarda as novas regras
                allRules.append(quebraEordena(afnd.loc[index, token])) # adiciona no vetor global de regras
                afd.loc[index, token] = afnd.loc[index, token]
            else:
                afd.loc[index, token] = quebraEordena(afnd.loc[index, token])

    
    newRules = sorted(set(newRules))

    for rule in newRules: # Percorre o vetor de novas regras
        #print('Regra:', rule)

        

        dados = dict()

        toSearch = rule.split(',')

        for ruleT in toSearch: # Percorre cada regra das novas regras

            for index in afd.index: # Percorre cada linha da tabela
                
                indexWithout = index.replace('*', '')
                

                if ruleT == indexWithout:  # Se a regra for igual a linha da tabela

                    for token in afd.columns: # Percorre a coluna da tabela

                        if afd.loc[index, token] == 'nan': # se for 'nan', não faz nada
                            continue

                        else:
                            
                            if dados.get(token) == None: # se ja não existe nada no dicionário
                                dados[token] = afd.loc[index, token] # simplesmente adiciona o token no dicionário

                            elif dados.get(token) != None: # se ja existe algum token no dicionário

                                if afd.loc[index, token] not in dados[token]: # se o token que eu quero adicionar não está no dicionário
                                    dados[token] += ',' + afd.loc[index, token] # adiciona o token no dicionário

                                else:
                                    continue

        for token in dados:
            rule = rule.replace('-,', '').replace(',', '')
            afd.loc[rule, token] = dados[token]
            

    return afd




def cleanTable(table):
    """ ADICIONA OS ESTADOS DE ERRO E AS CHAVES """
    
    for index in table.index:
        #print( 'O INDICEEE:',index)

        for token in table.columns:
            if ',' in table.loc[index, token]:
                table.loc[index, token] = '[' + table.loc[index, token].replace(',', '') + ']'
            elif '-' in table.loc[index, token]:
                table.loc[index, token] = 'ERR'
            elif len(table.loc[index, token]) == 0:
                table.loc[index, token] = 'ERR'
    
    # PARA ALTERAR O NOME DO INDICE DA TABELA
    # df  =  df.rename(index = {'antigo':'novo'})
    for index in table.index:
        if 'S' in index:
            novo = '->' + index
            table = table.rename(index = {index:novo})
        elif '*' in index or len(index) == 1 or index == 'ERR':
            continue
        
        else:
            novo = '[' + index + ']'
            table = table.rename(index = {index:novo})
            



    return table




def carregaTokens(afnd, tokens):
    """ formato <tokens> :: ['se\n', 'ex\n', 'sa\n']"""
    
    
    for i in range(len(tokens)):
        tokens[i] = tokens[i].replace('\n', '')
    
    #print('Carregando tokens...', tokens)
    
    #print('\n', afnd, '\n')
    
    for word in tokens: # 'se'
        initial = True
        last = word[-1:] # pega o último caractere
        #print('last:', last)
        updatePossibleRules()
        count = 0
        for token in word:  # 's'
            
            
            
            if initial: # se for o primeiro caractere
                
                for col in afnd.columns:
                    if token == col:
                        novaRegra = str(possibleRules[count])
                        #print('INITIAL::', token, col, possibleRules[count], novaRegra, count,'\n')
                        if len(afnd.loc[INITIALSTATE, token]) > 0:
                            afnd.loc[INITIALSTATE, token] += ',' + novaRegra
                            afnd = newBlankRow(afnd, novaRegra)
                            initial = False
                            count += 1
                        else:
                            afnd.loc[INITIALSTATE, token] = novaRegra
                            afnd = newBlankRow(afnd, novaRegra)
                            initial = False
                            count += 1
                    else:
                        continue
            elif token == last: # o estado criado tem que se tornar um estado final
                
                for col in afnd.columns:
                    if token == col:
                        
                        novaRegra = str(possibleRules[count])
                        regraAnterior = str(possibleRules[count-1])
                        #print('LAST::', token, col, possibleRules[count], novaRegra, regraAnterior, count,'\n')
                        #verificar se já não existe uma regra
                        if len(afnd.loc[regraAnterior, token]) > 0: # tem regra já
                            afnd.loc[regraAnterior, token] += ',' + novaRegra
                            afnd = newBlankRow(afnd, novaRegra)
                            afnd = virouTerminal(afnd, novaRegra)
                        else:
                            afnd.loc[regraAnterior, token] = novaRegra
                            afnd = newBlankRow(afnd, novaRegra)
                            afnd = virouTerminal(afnd, novaRegra)
                    else:
                        continue

            else:
                #lógica para criar os estados intermediários
                # utilizaremos o count para saber qual estado criar
                for col in afnd.columns:
                    if token == col:
                        novaRegra = str(possibleRules[count])
                        regraAnterior = str(possibleRules[count-1])
                        #print('MIDDLE::', token, col, possibleRules[count], novaRegra, regraAnterior, '\n')
                        if len(afnd.loc[regraAnterior, token]) > 0:
                            afnd.loc[regraAnterior, token] += ',' + novaRegra
                            afnd = newBlankRow(afnd, novaRegra)
                            count += 1
                        else:
                            afnd.loc[regraAnterior, token] = novaRegra
                            afnd = newBlankRow(afnd, novaRegra)
                            count += 1
                    else:
                        continue
                
                
        
    return afnd



def main():
    # Pega os dados do arquivo de entrada e coloca em um vetor
    allData = getData(openFile(getParam(1)))

    # Cria um vetor com todos os tokens
    tokens = getTokens(allData)               

    # Parseia os tokens e cria uma espécie de alfabeto da linguagem
    parsedTokens = parseTokens(removeQuebraLinha(tokens))

    # Pega os vetor gerado e coloca as regras em um vetor
    grs = getGR(allData)

    # Pega os tokens presentes nas regras e coloca em um vetor
    tokensFromGRS = getGRStokens(grs)  

    # Faz uma junção dos tokens (das regras e os fornecidos na entrada) -> forma um alfabeto total da linguagem
    allTokens = removeBlankSpace(parsedTokens) + removeBlankSpace(tokensFromGRS) 
    allTokens = sorted(set(allTokens))
    allTokens = removeEpsilon(allTokens)


    # Pega o vetor gerado e coloca as regras parseadas em um vetor
    parsedGRs = parseGR(grs)                  


    # cria a tabela (dataframe) para o AFND
    afnd = createTable(allTokens, parsedGRs)    
    afnd = afnd[allTokens].astype(str)

    # preenche a tabela com as regras
    afnd = fillWithGRs(afnd, parsedGRs)         
    afnd = removeNan(afnd)# remove os 'nan's

    print('\nITERAÇÃO - PREENCHE COM GRAMÁTICAS ----\n\n', afnd)             
    print('\n---------------------------------------------')

    #print('antes de carregar\n',allRules,'\n',afnd,'\n')

    # função para carregar os tokens na afd
    afnd = carregaTokens(afnd, tokens)          

    print('\nITERAÇÃO - PREENCHE COM TOKENS ----\n\n', afnd)             
    print('\n---------------------------------------------')


    # DETERMINIZAÇÃO --------------------------------------------------------------
    # determiniza o afnd + remove os 'nan' + ordena a tabela e normaliza


    afd = determiniza(afnd, allTokens)      
    afd = removeNan(afd)                        
    afd = ordenaTable(afd)         
    print('\nITERAÇÃO 0 - DETERMINIZAÇÃO ----\n\n', afd)             
    print('\n---------------------------------------------')


    # verifica se há novas regras geradas a partir das regras já determinizadas
    time = 1
    while temRegraNova(afd):                
        afd = determiniza(afd, allTokens)   # determiniza o afnd
        afd = ordenaTable(afd)              # ordena a tabela e normaliza
        #print('\nITERAÇÃO 0 - DETERMINIZAÇÃO ----\n')
        print(f'\n ITERAÇÃO {time} - DETERMINIZAÇÃO ----\n\n',afd)                          # printa a tabela a cada etapa
        print('\n---------------------------------------------')
        time += 1                            # incrementa o tempo de execução


    # printa a tabela afnd final
    print('--------------------------------AFND--------------------------------')
    #afnd = cleanTable(afnd)
    print(afnd)
    print('------------------------------------------------------------------')


    # printa a tabela afd final
    print('--------------------------------AFD--------------------------------')
    afd = cleanTable(afd)
    print(afd)
    print('------------------------------------------------------------------')

    # print('TESTE ACESSO AO DATAFRAME:  ')

    # print(afd.loc['B', 'e'])

    # for index in afd.index:
    #     print(index)
    #     for col in afd.columns:
    #         print(afd.loc[index, col])
    #     print('---------------------')

    # print(afd.index.values)
    # print(afd.columns.values)
        
        
    afnd.to_csv('outputs/afnd.csv', index=True, header=True)
    afd.to_csv('outputs/afd.csv', index=True, header=True)

    # PARA ALTERAR O NOME DO INDICE DA TABELA
    # df  =  df.rename(index = {'antigo':'novo'})



# Modularizar o código
if __name__ == "__main__":  
    main()

