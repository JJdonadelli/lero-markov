import re
import random
from collections import defaultdict, Counter

def ler_arquivos():
    """Lê os dois arquivos de texto e retorna o conteúdo combinado."""
    try:
        with open('data/maravilha.txt', 'r', encoding='utf-8') as f:
            maravilha = f.read()
    except FileNotFoundError:
        print("Arquivo 'data/maravilha.txt' não encontrado!")
        return ""
    
    try:
        with open('data/espelho.txt', 'r', encoding='utf-8') as f:
            espelho = f.read()
    except FileNotFoundError:
        print("Arquivo 'data/espelho.txt' não encontrado!")
        return ""
    
    return maravilha + " " + espelho

def preprocessar_texto(texto):
    """Preprocessa o texto removendo caracteres especiais e convertendo para minúsculas."""
    # Remove quebras de linha excessivas e caracteres especiais
    texto = re.sub(r'\n+', ' ', texto)
    texto = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', texto)
    
    # Converte para minúsculas
    texto = texto.lower()
    
    # Remove espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()

def tokenizar(texto):
    """Tokeniza o texto em palavras."""
    # Divide por espaços e remove tokens vazios
    tokens = [token for token in texto.split() if token]
    return tokens

def criar_ngramas(tokens, n):
    """Cria um dicionário de n-gramas a partir dos tokens."""
    ngramas = defaultdict(list)
    
    for i in range(len(tokens) - n + 1):
        # Chave: n-1 palavras anteriores
        chave = tuple(tokens[i:i+n-1])
        # Valor: próxima palavra
        proxima_palavra = tokens[i+n-1]
        ngramas[chave].append(proxima_palavra)
    
    return ngramas

def encontrar_palavras_interessantes(tokens):
    """Encontra palavras interessantes e relevantes para começar o texto."""
    # Lista de palavras relacionadas às fábulas da Alice
    palavras_alice = [
        'alice', 'coelho', 'chapeleiro', 'gato', 'rainha', 'rei', 'carta', 'cartas',
        'chá', 'mesa', 'jardim', 'buraco', 'toca', 'relógio', 'tempo', 'mundo',
        'país', 'maravilhas', 'espelho', 'sonho', 'dormindo', 'acordar',
        'pequena', 'grande', 'crescer', 'diminuir', 'poção', 'beber', 'comer',
        'porta', 'chave', 'curiosa', 'estranha', 'estranho', 'medo', 'coragem'
    ]
    
    # Conta a frequência das palavras
    contador = Counter(tokens)
    
    # Encontra palavras interessantes que aparecem no texto
    palavras_disponiveis = []
    for palavra in palavras_alice:
        if palavra in contador and contador[palavra] > 5:  # Só palavras com frequência > 5
            palavras_disponiveis.append(palavra)
    
    # Adiciona algumas palavras mais frequentes do texto
    palavras_frequentes = [palavra for palavra, freq in contador.most_common(50) 
                          if len(palavra) > 3 and palavra.isalpha()]
    
    # Combina as listas removendo duplicatas
    todas_palavras = list(set(palavras_disponiveis + palavras_frequentes[:20]))
    
    return sorted(todas_palavras)

def escolher_palavra_inicial(palavras_interessantes):
    """Permite ao usuário escolher uma palavra inicial."""
    print("\nPalavras interessantes disponíveis:")
    for i, palavra in enumerate(palavras_interessantes, 1):
        print(f"{i:2d}. {palavra}")
    
    while True:
        try:
            escolha = input(f"\nEscolha uma palavra (1-{len(palavras_interessantes)}) ou digite uma palavra: ").strip()
            
            if escolha.isdigit():
                idx = int(escolha) - 1
                if 0 <= idx < len(palavras_interessantes):
                    return palavras_interessantes[idx]
                else:
                    print("Número inválido!")
            else:
                if escolha.lower():
                    return escolha.lower()
                else:
                    print("Palavra inválida!")
        except (ValueError, KeyboardInterrupt):
            print("Entrada inválida!")

def gerar_texto(ngramas_dict, palavra_inicial, n, tamanho=51):
    """Gera texto usando cadeias de Markov com n-gramas progressivos."""
    resultado = [palavra_inicial]
    
    # Para n > 2, começamos com 2-gramas e aumentamos gradualmente
    for tamanho_atual in range(2, n + 1):
        if len(resultado) >= tamanho:
            break
            
        # Usa os n-gramas do tamanho atual
        ngramas_atuais = ngramas_dict[tamanho_atual]
        
        # Pega o contexto necessário (últimas tamanho_atual-1 palavras)
        contexto_size = tamanho_atual - 1
        
        while len(resultado) < tamanho:
            if len(resultado) < contexto_size:
                # Não temos contexto suficiente, para por aqui
                break
                
            contexto = tuple(resultado[-contexto_size:])
            
            if contexto in ngramas_atuais and ngramas_atuais[contexto]:
                # Escolhe aleatoriamente a próxima palavra
                proxima = random.choice(ngramas_atuais[contexto])
                resultado.append(proxima)
            else:
                # Se não encontrar o contexto, tenta um contexto menor
                if contexto_size > 1:
                    contexto_menor = contexto[1:]  # Remove a primeira palavra
                    if contexto_menor in ngramas_atuais and ngramas_atuais[contexto_menor]:
                        proxima = random.choice(ngramas_atuais[contexto_menor])
                        resultado.append(proxima)
                    else:
                        break
                else:
                    break
    
    return resultado[:tamanho]

def main():
    print("=== Gerador de Texto com N-gramas de Markov - Livros da Alice ===\n")
    
    # Lê os arquivos
    print("Lendo arquivos...")
    texto_completo = ler_arquivos()
    
    if not texto_completo:
        print("Erro ao ler os arquivos!")
        return
    
    # Preprocessa o texto
    print("Preprocessando texto...")
    texto_limpo = preprocessar_texto(texto_completo)
    tokens = tokenizar(texto_limpo)
    
    print(f"Total de palavras processadas: {len(tokens)}")
    
    # Parâmetros
    while True:
        try:
            n = int(input("\nDigite o valor de n (2-6): "))
            if 2 <= n <= 6:
                break
            else:
                print("n deve estar entre 2 e 6!")
        except ValueError:
            print("Digite um número válido!")
    
    tamanho = input("Digite o tamanho do texto (padrão 51): ").strip()
    tamanho = int(tamanho) if tamanho.isdigit() else 51
    
    # Cria n-gramas para todos os tamanhos de 2 até n
    print(f"\nCriando n-gramas de 2 até {n}...")
    ngramas_dict = {}
    for i in range(2, n + 1):
        ngramas_dict[i] = criar_ngramas(tokens, i)
        print(f"  {i}-gramas: {len(ngramas_dict[i])} combinações únicas")
    
    # Encontra palavras interessantes
    palavras_interessantes = encontrar_palavras_interessantes(tokens)
    
    # Permite escolher palavra inicial
    palavra_inicial = escolher_palavra_inicial(palavras_interessantes)
    
    # Gera o texto
    print(f"\nGerando texto com {n}-gramas, começando com '{palavra_inicial}'...")
    texto_gerado = gerar_texto(ngramas_dict, palavra_inicial, n, tamanho)
    
    # Exibe o resultado
    print(f"\n{'='*60}")
    print("TEXTO GERADO:")
    print(f"{'='*60}")
    
    texto_final = ' '.join(texto_gerado)
    
    # Quebra em linhas para melhor legibilidade
    palavras = texto_final.split()
    linhas = []
    linha_atual = []
    
    for palavra in palavras:
        linha_atual.append(palavra)
        if len(' '.join(linha_atual)) > 70:  # Quebra linha a cada ~70 caracteres
            linhas.append(' '.join(linha_atual))
            linha_atual = []
    
    if linha_atual:
        linhas.append(' '.join(linha_atual))
    
    for linha in linhas:
        print(linha)
    
    print(f"\n{'='*60}")
    print(f"Estatísticas: {len(texto_gerado)} palavras geradas usando {n}-gramas")
    print(f"Palavra inicial: '{palavra_inicial}'")

if __name__ == "__main__":
    main()