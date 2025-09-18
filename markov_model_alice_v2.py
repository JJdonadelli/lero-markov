import random
from collections import defaultdict, Counter

# Variáveis globais para armazenar dados
words_corpus = []
ngram_model = defaultdict(list)

def load_texts(file1="data/maravilha_limpo.txt", file2="data/espelho_limpo.txt"):
    """
    Carrega e combina textos de dois arquivos.
    
    N-gramas são sequências de N palavras consecutivas usadas para modelar
    a probabilidade de ocorrência de palavras em um texto. Este sistema
    combina dois textos para ter mais dados de treinamento.
    
    Args:
        file1 (str): Caminho para o primeiro arquivo de texto
        file2 (str): Caminho para o segundo arquivo de texto
        
    Returns:
        list: Lista de palavras combinadas dos dois textos, ou None se erro
    """
    global words_corpus
    
    try:
        # Lê o primeiro arquivo
        with open(file1, encoding="utf-8") as f:
            text1 = f.read().lower()
        
        # Lê o segundo arquivo
        with open(file2, encoding="utf-8") as f:
            text2 = f.read().lower()
        
        # Combina os textos e divide em palavras
        # Adiciona espaço entre os textos para separá-los
        combined_text = text1 + " " + text2
        words_corpus = combined_text.split()
        
        print(f"Textos carregados com sucesso!")
        print(f"  - Total de palavras: {len(words_corpus):,}")
        print(f"  - Palavras únicas: {len(set(words_corpus)):,}")
        
        return words_corpus
        
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}")
        return None
    except Exception as e:
        print(f"Erro ao carregar textos: {e}")
        return None

def create_sample_text():
    """
    Cria um texto de exemplo para demonstração quando os arquivos não estão disponíveis.
    
    Returns:
        list: Lista de palavras do texto de exemplo
    """
    sample_text = """
    era uma vez uma princesa muito bonita que vivia em um castelo encantado
    no reino distante havia dragões e cavaleiros corajosos que protegiam a terra sagrada
    os habitantes da vila eram felizes e trabalhavam nos campos verdes sob o sol dourado
    a princesa gostava de passear pelos jardins do castelo onde cresciam flores coloridas
    um dia ela encontrou um livro mágico que continha histórias de terras distantes
    o livro falava sobre aventuras incríveis de heróis que salvavam o mundo
    ela decidiu partir em sua própria aventura para descobrir novos lugares
    """
    
    global words_corpus
    words_corpus = sample_text.lower().split()
    
    print("Usando texto de exemplo para demonstração.")
    print(f"  - Total de palavras: {len(words_corpus):,}")
    
    return words_corpus

def build_ngram_model(words, n=3):
    """
    Constrói um modelo de N-gramas baseado nas palavras fornecidas.
    
    Um N-grama é uma sequência contígua de N palavras. O modelo mapeia
    sequências de (N-1) palavras para listas de palavras que podem vir a seguir.
    
    Exemplo para trigramas (N=3):
    - Texto: "era uma vez uma princesa"
    - Contexto: ("era", "uma") → próxima palavra: "vez"
    - Contexto: ("uma", "vez") → próxima palavra: "uma"
    
    Args:
        words (list): Lista de palavras do corpus
        n (int): Ordem do N-grama (padrão: 3 para trigramas)
        
    Returns:
        dict: Modelo onde chaves são tuplas de (n-1) palavras e valores
              são listas de palavras que podem vir a seguir
              
    Raises:
        ValueError: Se n < 2 (precisa de pelo menos contexto de 1 palavra)
    """
    global ngram_model
    
    if n < 2:
        raise ValueError("n deve ser >= 2 (pelo menos bigramas)")
    
    if len(words) < n:
        raise ValueError(f"Corpus muito pequeno. Precisa de pelo menos {n} palavras.")
    
    # Limpa o modelo anterior
    ngram_model = defaultdict(list)
    
    # Constrói o modelo percorrendo todas as sequências possíveis
    # Para cada posição i, pega n-1 palavras como contexto e a próxima como alvo
    for i in range(len(words) - n + 1):
        # Contexto: sequência de (n-1) palavras
        context = tuple(words[i:i + n - 1])
        
        # Próxima palavra que vem após o contexto
        next_word = words[i + n - 1]
        
        # Adiciona a palavra à lista de possibilidades para este contexto
        ngram_model[context].append(next_word)
    
    print(f"Modelo {n}-grama construído:")
    print(f"  - Contextos únicos: {len(ngram_model):,}")
    print(f"  - Tamanho do contexto: {n-1} palavra(s)")
    
    return ngram_model

def generate_text(model, start_words, length=50):
    """
    Gera texto usando o modelo de N-gramas com seleção ponderada.
    
    O algoritmo funciona assim:
    1. Começa com as palavras iniciais fornecidas
    2. Usa as últimas (n-1) palavras como contexto
    3. Encontra todas as palavras que podem vir após este contexto
    4. Escolhe uma palavra baseada na frequência (palavras mais comuns têm maior chance)
    5. Adiciona a palavra escolhida ao texto e atualiza o contexto
    6. Repete até atingir o comprimento desejado
    
    Args:
        model (dict): Modelo de N-gramas construído por build_ngram_model()
        start_words (tuple): Tupla com palavras iniciais
        length (int): Número total de palavras a gerar
        
    Returns:
        str: Texto gerado
        
    Raises:
        ValueError: Se o número de palavras iniciais não corresponde ao modelo
    """
    # Verifica se temos pelo menos um contexto no modelo para determinar o tamanho
    if not model:
        raise ValueError("Modelo vazio. Construa o modelo primeiro.")
    
    # Pega o tamanho do contexto do primeiro item do modelo
    context_size = len(next(iter(model)))
    
    # Verifica se as palavras iniciais têm o tamanho correto
    if len(start_words) != context_size:
        raise ValueError(f"O modelo espera {context_size} palavra(s) inicial(is), "
                        f"mas {len(start_words)} foi(ram) fornecida(s).")
    
    # Inicializa a saída com as palavras iniciais
    output = list(start_words)
    
    # Gera o restante do texto
    for _ in range(length - context_size):
        # Pega o contexto atual (últimas context_size palavras)
        current_context = tuple(output[-context_size:])
        
        # Verifica se o contexto existe no modelo
        if current_context not in model:
            # Se não existe, para a geração (chegou a um beco sem saída)
            print(f"Parada antecipada: contexto '{' '.join(current_context)}' não encontrado.")
            break
        
        # Pega todas as palavras que podem vir após este contexto
        next_words = model[current_context]
        
        # Conta a frequência de cada palavra para seleção ponderada
        # Palavras que aparecem mais vezes após este contexto têm maior probabilidade
        word_counts = Counter(next_words)
        words_list = list(word_counts.keys())
        weights_list = list(word_counts.values())
        
        # Escolhe uma palavra baseada nos pesos (frequências)
        # random.choices() permite seleção ponderada
        next_word = random.choices(words_list, weights=weights_list, k=1)[0]
        
        # Adiciona a palavra escolhida ao texto
        output.append(next_word)
    
    return " ".join(output)

def get_random_start_words(words, context_size):
    """
    Escolhe uma sequência aleatória de palavras iniciais do corpus.
    
    Isso é útil quando o usuário não quer especificar as palavras iniciais
    e prefere deixar o sistema escolher aleatoriamente.
    
    Args:
        words (list): Lista de palavras do corpus
        context_size (int): Número de palavras iniciais necessárias
        
    Returns:
        tuple: Tupla com as palavras iniciais escolhidas aleatoriamente
    """
    if len(words) < context_size:
        raise ValueError(f"Corpus muito pequeno. Precisa de pelo menos {context_size} palavras.")
    
    # Escolhe um índice aleatório, garantindo que há palavras suficientes após ele
    max_start_index = len(words) - context_size
    start_index = random.randint(0, max_start_index)
    
    # Retorna a sequência de palavras começando no índice escolhido
    return tuple(words[start_index:start_index + context_size])

def show_word_statistics(words, top_n=10):
    """
    Mostra estatísticas das palavras mais comuns no corpus.
    
    Args:
        words (list): Lista de palavras
        top_n (int): Número de palavras mais comuns a mostrar
    """
    word_counts = Counter(words)
    
    print(f"\nPalavras mais comuns (top {top_n}):")
    print("-" * 30)
    
    for word, count in word_counts.most_common(top_n):
        percentage = (count / len(words)) * 100
        print(f"{word:<15} {count:>5} ({percentage:.1f}%)")

def get_available_contexts(model, context_size):
    """
    Retorna uma lista de contextos disponíveis no modelo para o usuário escolher.
    
    Args:
        model (dict): Modelo de N-gramas
        context_size (int): Tamanho do contexto
        
    Returns:
        list: Lista de contextos (tuplas) disponíveis
    """
    return list(model.keys())

def suggest_contexts(model, partial_context, max_suggestions=5):
    """
    Sugere contextos que começam com as palavras fornecidas.
    
    Args:
        model (dict): Modelo de N-gramas
        partial_context (tuple): Contexto parcial fornecido pelo usuário
        max_suggestions (int): Número máximo de sugestões
        
    Returns:
        list: Lista de contextos sugeridos
    """
    suggestions = []
    partial_len = len(partial_context)
    
    for context in model.keys():
        # Verifica se o contexto começa com as palavras parciais
        if context[:partial_len] == partial_context:
            suggestions.append(context)
            if len(suggestions) >= max_suggestions:
                break
    
    return suggestions

def main():
    """
    Função principal que implementa a interface de linha de comando
    para o gerador de texto com N-gramas.
    
    N-gramas são uma técnica de processamento de linguagem natural que
    modela sequências de palavras para gerar texto que segue padrões
    estatísticos similares ao texto original.
    """
    print("Gerador de Texto com Modelos N-Gramas")
    print("=" * 50)
    print("Sistema de geração de texto baseado em cadeias de Markov")
    print("Usa N-gramas para modelar sequências de palavras")
    
    # Tenta carregar os arquivos de texto
    print(f"\nCarregando textos...")
    words = load_texts()
    
    # Se não conseguiu carregar, oferece texto de exemplo
    if words is None:
        print("\nArquivos não encontrados. Opções:")
        print("1. Use texto de exemplo")
        print("2. Sair")
        
        choice = input("\nEscolha uma opção (1-2): ").strip()
        if choice == "1":
            words = create_sample_text()
        else:
            print("Programa encerrado.")
            return
    
    # Mostra estatísticas básicas
    show_word_statistics(words)
    
    print(f"\n" + "=" * 50)
    print("Comandos disponíveis:")
    print("- 'stats': mostra estatísticas do corpus")
    print("- 'sair': encerra o programa")
    
    while True:
        print(f"\n" + "-" * 30)
        
        # Solicita parâmetros do modelo
        try:
            n_input = input("Ordem do N-grama (2-6, padrão: 3): ").strip()
            n = int(n_input) if n_input else 3
            n = max(2, min(6, n))  # Limita entre 2 e 6
        except ValueError:
            n = 3
            print("Valor inválido, usando n=3 (trigramas).")
        
        try:
            length_input = input("Comprimento do texto (10-200, padrão: 50): ").strip()
            length = int(length_input) if length_input else 50
            length = max(10, min(200, length))  # Limita entre 10 e 200
        except ValueError:
            length = 50
            print("Valor inválido, usando comprimento=50.")
        
        # Constrói o modelo
        print(f"\nConstruindo modelo {n}-grama...")
        try:
            model = build_ngram_model(words, n=n)
        except ValueError as e:
            print(f"Erro: {e}")
            continue
        
        context_size = n - 1
        
        # Escolhe palavras iniciais
        print(f"\nMétodo para palavras iniciais:")
        print("1. Aleatório")
        print("2. Manual")
        
        method = input("Escolha (1-2, padrão: 1): ").strip()
        
        if method == "2":
            # Entrada manual
            print(f"\nDigite {context_size} palavra(s) inicial(is):")
            manual_input = input("Palavras (separadas por espaço): ").strip().lower()
            
            if manual_input == "sair":
                print("Programa encerrado.")
                break
            elif manual_input == "stats":
                show_word_statistics(words, 15)
                continue
            
            if not manual_input:
                print("Nenhuma palavra fornecida. Usando método aleatório.")
                start_words = get_random_start_words(words, context_size)
            else:
                manual_words = manual_input.split()
                if len(manual_words) != context_size:
                    print(f"Erro: esperava {context_size} palavra(s), "
                          f"recebeu {len(manual_words)}.")
                    continue
                start_words = tuple(manual_words)
                
                # Verifica se o contexto existe
                if start_words not in model:
                    print(f"Aviso: contexto '{' '.join(start_words)}' não encontrado no modelo.")
                    # Sugere contextos similares
                    suggestions = suggest_contexts(model, start_words[:1])
                    if suggestions:
                        print("Sugestões de contextos disponíveis:")
                        for i, suggestion in enumerate(suggestions[:5], 1):
                            print(f"{i}. {' '.join(suggestion)}")
                    continue
        else:
            # Método aleatório
            start_words = get_random_start_words(words, context_size)
        
        print(f"\nPalavras iniciais escolhidas: {' '.join(start_words)}")
        print("Gerando texto...")
        
        # Gera o texto
        try:
            generated_text = generate_text(model, start_words, length)
            
            print(f"\nTexto Gerado (n={n}, comprimento={length}):")
            print("=" * 60)
            
            # Formata o texto em linhas de ~80 caracteres
            words_list = generated_text.split()
            line = ""
            for word in words_list:
                if len(line + word) > 80:
                    print(line.strip())
                    line = word + " "
                else:
                    line += word + " "
            if line.strip():  # Imprime a última linha
                print(line.strip())
            
            print("=" * 60)
            print(f"Palavras geradas: {len(words_list)}")
            
            # Destaca as palavras iniciais
            initial_words = ' '.join(words_list[:context_size])
            print(f"Contexto inicial: [{initial_words}]")
            
        except Exception as e:
            print(f"Erro ao gerar texto: {e}")
        
        # Pergunta se quer continuar
        continue_choice = input("\nGerar outro texto? (s/n): ").strip().lower()
        if not continue_choice.startswith('s'):
            break
    
    print("Obrigado por usar o Gerador de Texto N-Gramas!")

if __name__ == "__main__":
    main()