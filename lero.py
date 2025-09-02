import random
import sys
from collections import defaultdict, Counter

# Carregar os textos
try:
    text1 = open("data/maravilha_limpo.txt", encoding="utf-8").read().lower()
    text2 = open("data/espelho_limpo.txt", encoding="utf-8").read().lower()
except FileNotFoundError:
    raise FileNotFoundError("Arquivos de texto não encontrados.")

# Quebrar em palavras (texto já limpo)
words = (text1 + " " + text2).split()

def build_ngram_model(words, n=3):
    model = defaultdict(list)
    for i in range(len(words) - n + 1):
        context = tuple(words[i:i + n - 1])
        next_word = words[i + n - 1]
        model[context].append(next_word)
    return model

# Função para construir modelo de n-gramas (ordem n-1)
def build_ngram_model(words, n=3):
    if n < 2:
        raise ValueError("n deve ser >= 2")
    model = defaultdict(list)
    for i in range(len(words) - n + 1):
        context = tuple(words[i:i + n - 1])  # n-1 palavras
        next_word = words[i + n - 1]         # palavra seguinte
        model[context].append(next_word)
    return model

# Função para gerar texto com modelo de n-gramas
def generate_text(model, start_words, length=50):

    context_size = len(next(iter(model)))
    if len(start_words) != context_size:
        raise ValueError(f"O modelo espera {context_size} palavras no contexto.")
    
    output = list(start_words)

    for _ in range(length - context_size):
        if tuple(output[-context_size:])  not in model:
            break

        next_words = model[tuple(output[-context_size:])]
        counts = Counter(next_words)
        palavras = list(counts.keys())
        pesos = list(counts.values())

        next_word = random.choices(palavras, weights=pesos, k=1)[0]
        output.append(next_word)

        # Avança a janela
        context = tuple(output[-context_size:])

    return " ".join(output)


if len(sys.argv) < 2:
    n=4
else: n = int(sys.argv[1])
context_size = n - 1

markov_model = build_ngram_model(words, n=n)

#Escolher uma sequência aleatória de n-1 palavras do texto
start_index = random.randint(0, len(words) - context_size)
start_words = tuple(words[start_index:start_index + context_size])

#print("Contexto inicial aleatório:", start_words)
print(generate_text(markov_model, start_words, 53))
