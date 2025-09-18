import re
import random
from collections import defaultdict

# === CARREGAMENTO E PRÉ-PROCESSAMENTO ===
# Carrega o arquivo txt 
# e converte tudo para minúsculas para normalizar o texto
with open("data/maravilha.txt", encoding="utf-8") as f:
    text = f.read().lower()

try:
    text1 = open("data/maravilha_limpo.txt", encoding="utf-8").read().lower()
    text2 = open("data/espelho_limpo.txt", encoding="utf-8").read().lower()
except FileNotFoundError:
    raise FileNotFoundError("Arquivos de texto não encontrados.")

text = (text1 + " " + text2)
    
    # Extrai todas as palavras usando regex
# \b\w+\b captura sequências de caracteres alfanuméricos entre bordas de palavra
words = re.findall(r"\b\w+\b", text)

# === CONSTRUÇÃO DO MODELO MARKOV ===
# Cria um modelo de trigramas ***Markov ordem 2***
# Cada par de palavras (w1, w2) mapeia para uma lista de possíveis palavras seguintes (w3)
markov_model = defaultdict(list)

# Itera através do texto criando trigramas consecutivos
# zip(words, words[1:], words[2:]) cria tuplas de 3 palavras consecutivas
for w1, w2, w3 in zip(words, words[1:], words[2:]):
    # Para cada par (w1, w2), adiciona w3 como possível continuação
    markov_model[(w1, w2)].append(w3)

# === FUNÇÃO DE GERAÇÃO DE TEXTO ===
def generate_text(model, start_words, length=50):
    """
    Gera texto artificial usando o modelo Markov
    
    Args:
        model: dicionário com o modelo Markov construído
        start_words: pode ser uma string (uma palavra) ou tupla (duas palavras)
        length: número total de palavras a gerar
    
    Returns:
        string com o texto gerado
    """
    
    # Se o usuário passou apenas uma palavra, precisa encontrar uma segunda
    if isinstance(start_words, str):
        # Procura todos os pares que começam com a palavra fornecida
        candidates = [pair for pair in model.keys() if pair[0] == start_words]
        if not candidates:
            raise ValueError(f"Não encontrei pares começando com '{start_words}' no texto.")
        # Escolhe aleatoriamente um par válido
        w1, w2 = random.choice(candidates)
    else:
        # Se já recebeu duas palavras, usa diretamente
        w1, w2 = start_words
    
    # Inicializa a saída com as duas primeiras palavras
    output = [w1, w2]
    
    # Gera as palavras restantes
    for _ in range(length - 2):
        # Se o par atual não existe no modelo, para a geração
        if (w1, w2) not in model:
            break
        
        # Escolhe aleatoriamente uma das possíveis palavras seguintes
        w3 = random.choice(model[(w1, w2)])
        output.append(w3)
        
        # Atualiza o contexto: desloca a "janela" de duas palavras
        w1, w2 = w2, w3
    
    return " ".join(output)

# === EXEMPLOS DE USO ===
print(">>> Texto começando com 'alice':")
print(generate_text(markov_model, "alice", 60))

print("\n>>> Texto começando com 'coelho branco':")
print(generate_text(markov_model, ("coelho", "branco"), 60))

print("\n>>> Texto começando com 'rainha':")
print(generate_text(markov_model, "rainha", 60))

# Imprime o modelo completo (pode ser muito grande!)
print(markov_model)