import re
import random
from collections import defaultdict

# Variáveis globais para armazenar o modelo
markov_model = defaultdict(list)
total_words = 0

def load_and_process_text(file_path):
    """
    Carrega um arquivo de texto e constrói o modelo Markov.
    
    Uma cadeia de Markov é um modelo estatístico que prediz o próximo elemento
    de uma sequência baseado apenas nos elementos anteriores imediatos.
    Neste caso, usamos 2 palavras para predizer a terceira (trigramas).
    
    Args:
        file_path (str): Caminho para o arquivo de texto
        
    Returns:
        bool: True se o carregamento foi bem-sucedido, False caso contrário
    """
    global markov_model, total_words
    
    try:
        # Lê o arquivo com encoding UTF-8 para suportar caracteres especiais
        with open(file_path, encoding="utf-8") as f:
            text = f.read().lower()  # Converte para minúsculas para padronizar
        
        # Extrai apenas palavras (remove pontuação e números)
        # \b\w+\b: \b = limite de palavra, \w+ = uma ou mais letras/dígitos
        words = re.findall(r"\b\w+\b", text)
        total_words = len(words)
        
        # Limpa o modelo anterior
        markov_model = defaultdict(list)
        
        # Constrói o modelo de trigramas
        # Para cada sequência de 3 palavras consecutivas (w1, w2, w3),
        # armazena que após o par (w1, w2) pode vir w3
        
        # zip(words, words[1:], words[2:]) cria grupos de 3 palavras consecutivas
        # Exemplo: ["alice", "estava", "muito", "curiosa"] 
        # → [("alice", "estava", "muito"), ("estava", "muito", "curiosa")]
        for w1, w2, w3 in zip(words, words[1:], words[2:]):
            markov_model[(w1, w2)].append(w3)
        
        print(f"Modelo carregado com sucesso!")
        print(f"  - Total de palavras: {total_words:,}")
        print(f"  - Trigramas únicos: {len(markov_model):,}")
        
        return True
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{file_path}' não encontrado.")
        return False
    except Exception as e:
        print(f"Erro ao carregar arquivo: {e}")
        return False

def get_available_words():
    """
    Retorna uma lista das palavras que podem ser usadas como início.
    
    Returns:
        list: Lista ordenada de palavras disponíveis
    """
    # Pega a primeira palavra de cada par (w1, w2) no modelo
    available_words = list(set([pair[0] for pair in markov_model.keys()]))
    return sorted(available_words)

def generate_text(start_word, length=50):
    """
    Gera texto usando o modelo Markov.
    
    O algoritmo funciona assim:
    1. Encontra todos os pares que começam com a palavra escolhida
    2. Escolhe aleatoriamente um par compatível
    3. Para cada nova palavra:
       - Usa o par atual (w1, w2) para encontrar possíveis próximas palavras
       - Escolhe aleatoriamente uma das opções
       - Atualiza o par para (w2, nova_palavra)
    4. Repete até atingir o comprimento desejado
    
    Args:
        start_word (str): Palavra inicial para começar a geração
        length (int): Número de palavras a gerar (padrão: 50)
        
    Returns:
        tuple: (texto_gerado, mensagem_erro)
               Se bem-sucedido: (string, None)
               Se erro: (None, string_com_erro)
    """
    try:
        start_word = start_word.lower().strip()
        
        # Encontra todos os pares que começam com a palavra escolhida
        # Exemplo: se start_word = "alice", encontra todos os pares ("alice", X)
        candidates = [pair for pair in markov_model.keys() if pair[0] == start_word]
        
        if not candidates:
            return None, f"Não encontrei pares começando com '{start_word}' no texto."
        
        # Escolhe aleatoriamente um dos pares compatíveis
        w1, w2 = random.choice(candidates)
        
        # Inicializa o texto de saída com as duas primeiras palavras
        output = [w1, w2]
        
        # Gera o resto do texto palavra por palavra
        for _ in range(length - 2):
            # Verifica se o par atual existe no modelo
            if (w1, w2) not in markov_model:
                # Se não existe, para a geração (chegou a um "beco sem saída")
                break
            
            # Escolhe aleatoriamente a próxima palavra baseada no modelo
            # Todas as palavras que já apareceram após (w1, w2) têm chance igual
            w3 = random.choice(markov_model[(w1, w2)])
            output.append(w3)
            
            # Atualiza o par para a próxima iteração
            # O novo par é (w2, w3) para encontrar a palavra que vem depois
            w1, w2 = w2, w3
        
        return " ".join(output), None
        
    except Exception as e:
        return None, f"Erro ao gerar texto: {e}"

def get_word_suggestions(partial_word, max_suggestions=10):
    """
    Encontra sugestões de palavras baseadas em uma string parcial.
    
    Args:
        partial_word (str): Parte da palavra para buscar
        max_suggestions (int): Número máximo de sugestões
        
    Returns:
        list: Lista de palavras que contêm a string parcial
    """
    available_words = get_available_words()
    # Filtra palavras que contêm a string parcial
    suggestions = [word for word in available_words if partial_word.lower() in word]
    return suggestions[:max_suggestions]

def show_model_info():
    """
    Exibe informações estatísticas sobre o modelo carregado.
    """
    if not markov_model:
        print("Nenhum modelo carregado.")
        return
    
    available_words = get_available_words()
    
    print("\nInformações do Modelo Markov:")
    print("=" * 40)
    print(f"Total de palavras no texto: {total_words:,}")
    print(f"Trigramas únicos: {len(markov_model):,}")
    print(f"Palavras iniciais disponíveis: {len(available_words):,}")
    print(f"Ordem do modelo: 2 (usa 2 palavras para predizer a 3ª)")

def show_examples():
    """
    Mostra alguns exemplos de palavras que podem ser usadas.
    """
    available_words = get_available_words()
    if not available_words:
        print("Nenhuma palavra disponível.")
        return
    
    # Seleciona algumas palavras interessantes como exemplo
    example_words = []
    
    # Tenta encontrar algumas palavras específicas interessantes
    interesting_words = ['alice', 'coelho', 'rainha', 'gato', 'chapeleiro', 
                        'casa', 'tempo', 'mundo', 'vida', 'água']
    
    for word in interesting_words:
        if word in available_words:
            example_words.append(word)
        if len(example_words) >= 5:
            break
    
    # Se não encontrou palavras específicas, usa as primeiras disponíveis
    if len(example_words) < 5:
        example_words.extend(available_words[:5])
        example_words = list(dict.fromkeys(example_words))  # Remove duplicatas
    
    print(f"\nExemplos de palavras disponíveis: {', '.join(example_words[:5])}")

def main():
    """
    Função principal que demonstra o uso do gerador de texto Markoviano.
    
    Cadeia de Markov:
    - É um processo estocástico onde a próxima palavra depende apenas das palavras anteriores
    - Ordem 2 significa que usamos 2 palavras para predizer a próxima
    - Trigramas: sequências de 3 palavras consecutivas (w1, w2, w3)
    - Modelo: dicionário que mapeia pares (w1, w2) → lista de possíveis w3
    """
    print("Gerador de Texto Markoviano")
    print("=" * 50)
    print("Demonstração de Cadeia de Markov para Geração de Texto")
    print("Baseado em 'Alice no País das Maravilhas'")
    print("\nComo funciona:")
    print("1. Analisa o texto e cria trigramas (grupos de 3 palavras)")
    print("2. Para cada par de palavras, guarda quais podem vir depois")
    print("3. Gera texto escolhendo aleatoriamente baseado nos padrões")
    
    # Carrega o arquivo de texto
    file_path = "data/maravilha.txt"  # Arquivo base: Alice no País das Maravilhas
    print(f"\nCarregando arquivo: {file_path}")
    
    if not load_and_process_text(file_path):
        print("Não foi possível carregar o modelo. Verifique o arquivo.")
        return
    
    # Mostra informações do modelo
    show_model_info()
    
    # Mostra exemplos de palavras
    show_examples()
    
    # Loop principal de interação com o usuário
    print("\n" + "=" * 50)
    print("Digite uma palavra para começar a geração")
    print("Comandos especiais: 'info' (estatísticas), 'sair' (terminar)")
    
    while True:
        # Solicita entrada do usuário
        start_word = input("\nPalavra inicial: ").strip()
        
        # Verifica comandos especiais
        if start_word.lower() in ['sair', 'exit', 'quit', '']:
            print("Até logo!")
            break
        elif start_word.lower() == 'info':
            show_model_info()
            show_examples()
            continue
        
        # Solicita o comprimento do texto (opcional)
        try:
            length_input = input("Comprimento (padrão: 50): ").strip()
            length = int(length_input) if length_input else 50
            length = max(10, min(200, length))  # Limita entre 10 e 200 palavras
        except ValueError:
            length = 50
            print("Valor inválido, usando 50 palavras.")
        
        print(f"\nGerando texto de {length} palavras...")
        
        # Gera o texto usando o modelo Markov
        generated_text, error = generate_text(start_word, length)
        
        if error:
            print(error)
            
            # Oferece sugestões se a palavra não foi encontrada
            suggestions = get_word_suggestions(start_word)
            if suggestions:
                print(f"Palavras similares disponíveis: {', '.join(suggestions)}")
            else:
                print("Digite 'info' para ver exemplos de palavras disponíveis.")
        else:
            print("\nTexto Gerado:")
            print("-" * 60)
            # Formata o texto em linhas de aproximadamente 80 caracteres
            words = generated_text.split()
            line = ""
            for word in words:
                if len(line + word) > 80:
                    print(line.strip())
                    line = word + " "
                else:
                    line += word + " "
            if line.strip():  # Imprime a última linha se houver
                print(line.strip())
            print("-" * 60)
            
            # Estatísticas do texto gerado
            print(f"Palavras geradas: {len(words)}")
            
            # Opção de gerar novamente com a mesma palavra
            again = input("\nGerar outro texto com a mesma palavra? (s/n): ")
            if again.lower().startswith('s'):
                continue

if __name__ == "__main__":
    main()