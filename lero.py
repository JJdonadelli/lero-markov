import random
import sys
from collections import defaultdict, Counter

# === CARREGAMENTO DOS TEXTOS ===
# Carrega dois textos de Alice no País das Maravilhas
# (provavelmente versões diferentes ou livros relacionados)
try:
    text1 = open("data/maravilha_limpo.txt", encoding="utf-8").read().lower()
    text2 = open("data/espelho_limpo.txt", encoding="utf-8").read().lower()
except FileNotFoundError:
    raise FileNotFoundError("Arquivos de texto não encontrados.")

# Combina os dois textos e quebra em palavras
# Assume que os textos já estão limpos (sem pontuação, etc.)
words = (text1 + " " + text2).split()

# === FUNÇÃO PARA CONSTRUIR MODELO DE N-GRAMAS ===
def build_ngram_model(words, n=3):
    """
    Constrói um modelo de n-gramas (Markov de ordem n-1)
    
    Args:
        words: lista de palavras do texto
        n: tamanho do n-grama (3 = trigramas, 4 = 4-gramas, etc.)
    
    Returns:
        dicionário onde cada chave é um contexto de (n-1) palavras
        e o valor é uma lista de possíveis palavras seguintes
    """
    if n < 2:
        raise ValueError("n deve ser >= 2")
    
    model = defaultdict(list)
    
    # Percorre o texto criando n-gramas
    for i in range(len(words) - n + 1):
        # Contexto: (n-1) palavras
        context = tuple(words[i:i + n - 1])
        # Palavra que segue o contexto
        next_word = words[i + n - 1]
        # Adiciona a palavra ao contexto
        model[context].append(next_word)
    
    return model

# === FUNÇÃO PARA GERAR TEXTO ===
def generate_text(model, start_words, length=50):
    """
    Gera texto usando o modelo de n-gramas com seleção ponderada
    
    Args:
        model: modelo de n-gramas construído
        start_words: tupla com palavras iniciais
        length: número total de palavras a gerar
    
    Returns:
        string com o texto gerado
    """
    # Determina o tamanho do contexto baseado no modelo
    context_size = len(next(iter(model)))
    
    # Verifica se o número de palavras iniciais está correto
    if len(start_words) != context_size:
        raise ValueError(f"O modelo espera {context_size} palavras no contexto.")
    
    # Inicializa a saída com as palavras iniciais
    output = list(start_words)
    
    # Gera as palavras restantes
    for _ in range(length - context_size):  # CORREÇÃO: era "* in range"
        # Pega o contexto atual (últimas n-1 palavras)
        current_context = tuple(output[-context_size:])
        
        # Se o contexto não existe no modelo, para a geração
        if current_context not in model:
            break
        
        # Pega todas as possíveis palavras seguintes
        next_words = model[current_context]
        
        # Conta a frequência de cada palavra (seleção ponderada)
        counts = Counter(next_words)
        palavras = list(counts.keys())
        pesos = list(counts.values())
        
        # Escolhe uma palavra baseada na frequência (mais frequentes têm maior chance)
        next_word = random.choices(palavras, weights=pesos, k=1)[0]
        output.append(next_word)
    
    return " ".join(output)

# === CONFIGURAÇÃO E EXECUÇÃO ===
# Permite definir o tamanho do n-grama via linha de comando
if len(sys.argv) < 2:
    n = 4  # Padrão: 4-gramas (Markov ordem 3)
else:
    n = int(sys.argv[1])

context_size = n - 1

# Constrói o modelo
markov_model = build_ngram_model(words, n=n)

# Escolhe um contexto inicial aleatório do texto original
start_index = random.randint(0, len(words) - context_size)
start_words = tuple(words[start_index:start_index + context_size])

# Opcionalmente mostra o contexto inicial
# print("Contexto inicial aleatório:", start_words)

# Gera e imprime o texto
print(generate_text(markov_model, start_words, 53))