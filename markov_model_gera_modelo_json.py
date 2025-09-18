## Gera o modello para a versão html
import json
import re
from collections import defaultdict, Counter
import os

def preprocessar_texto(texto):
    """Preprocessa o texto removendo caracteres especiais e convertendo para minúsculas."""
    if not texto:
        return ""
    
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
    tokens = [token for token in texto.split() if token]
    return tokens

def criar_ngramas(tokens, n):
    """Cria um dicionário de n-gramas a partir dos tokens."""
    ngramas = defaultdict(list)
    
    for i in range(len(tokens) - n + 1):
        # Chave: n-1 palavras anteriores
        chave = ' '.join(tokens[i:i+n-1])  # Usar string em vez de tuple para JSON
        # Valor: próxima palavra
        proxima_palavra = tokens[i+n-1]
        ngramas[chave].append(proxima_palavra)
    
    return dict(ngramas)

def encontrar_palavras_interessantes(tokens):
    """Encontra palavras interessantes e relevantes para começar o texto."""
    palavras_alice = [
        'alice', 'coelho', 'chapeleiro', 'gato', 'rainha', 'rei', 'carta', 'cartas',
        'chá', 'mesa', 'jardim', 'buraco', 'toca', 'relógio', 'tempo', 'mundo',
        'país', 'maravilhas', 'espelho', 'sonho', 'dormindo', 'acordar',
        'pequena', 'grande', 'crescer', 'diminuir', 'poção', 'beber', 'comer',
        'porta', 'chave', 'curiosa', 'estranha', 'estranho', 'medo', 'coragem'
    ]
    
    contador = Counter(tokens)
    
    palavras_disponiveis = []
    for palavra in palavras_alice:
        if palavra in contador and contador[palavra] > 3:
            palavras_disponiveis.append(palavra)
    
    palavras_frequentes = [palavra for palavra, freq in contador.most_common(30) 
                          if len(palavra) > 3 and palavra.isalpha()]
    
    todas_palavras = list(set(palavras_disponiveis + palavras_frequentes[:15]))
    
    return sorted(todas_palavras)

def main():
    # Lê os arquivos
    print("Lendo arquivos...")
    maravilha = ""
    espelho = ""
    
    # Ajuste os caminhos conforme necessário
    if os.path.exists('public_html/estocastico/markov_lero/data/maravilha-limpo.txt'):
        with open('public_html/estocastico/markov_lero/data/maravilha-limpo.txt', 'r', encoding='utf-8') as f:
            maravilha = f.read()
    elif os.path.exists('data/maravilha-limpo.txt'):
        with open('data/maravilha-limpo.txt', 'r', encoding='utf-8') as f:
            maravilha = f.read()
    else:
        print("Arquivo maravilha-limpo.txt não encontrado!")
        return
    
    if os.path.exists('public_html/estocastico/markov_lero/data/espelho-limpo.txt'):
        with open('public_html/estocastico/markov_lero/data/espelho-limpo.txt', 'r', encoding='utf-8') as f:
            espelho = f.read()
    elif os.path.exists('data/espelho-limpo.txt'):
        with open('data/espelho-limpo.txt', 'r', encoding='utf-8') as f:
            espelho = f.read()
    else:
        print("Arquivo espelho-limpo.txt não encontrado!")
        return
    
    texto_completo = maravilha + " " + espelho
    print(f"Texto completo carregado: {len(texto_completo)} caracteres")
    
    # Preprocessa o texto
    print("Preprocessando texto...")
    texto_limpo = preprocessar_texto(texto_completo)
    tokens = tokenizar(texto_limpo)
    print(f"Tokens gerados: {len(tokens)}")
    
    # Encontra palavras interessantes
    print("Encontrando palavras interessantes...")
    palavras_interessantes = encontrar_palavras_interessantes(tokens)
    print(f"Palavras interessantes: {len(palavras_interessantes)}")
    
    # Gera n-gramas para diferentes ordens
    print("Gerando n-gramas...")
    todos_ngramas = {}
    
    for n in range(2, 7):  # 2-gramas até 6-gramas
        print(f"  Processando {n}-gramas...")
        ngramas = criar_ngramas(tokens, n)
        todos_ngramas[str(n)] = ngramas
        print(f"    {len(ngramas)} {n}-gramas únicos")
    
    # Prepara dados para salvar
    dados_completos = {
        'tokens': tokens,
        'palavras_interessantes': palavras_interessantes,
        'ngramas': todos_ngramas,
        'estatisticas': {
            'total_tokens': len(tokens),
            'tokens_unicos': len(set(tokens)),
            'palavras_alice': len([p for p in palavras_interessantes 
                                 if p in ['alice', 'coelho', 'chapeleiro', 'gato', 'rainha']])
        }
    }
    
    # Salva arquivo principal (pode ser grande)
    print("Salvando arquivo completo...")
    with open('markov_data_complete.json', 'w', encoding='utf-8') as f:
        json.dump(dados_completos, f, ensure_ascii=False, separators=(',', ':'))
    
    # Salva versão compacta (só metadados e palavras)
    print("Salvando arquivo compacto...")
    dados_compactos = {
        'palavras_interessantes': palavras_interessantes,
        'estatisticas': dados_completos['estatisticas'],
        'sample_ngramas': {
            '2': dict(list(todos_ngramas['2'].items())[:100]),
            '3': dict(list(todos_ngramas['3'].items())[:100]),
            '4': dict(list(todos_ngramas['4'].items())[:50])
        }
    }
    
    with open('markov_data_compact.json', 'w', encoding='utf-8') as f:
        json.dump(dados_compactos, f, ensure_ascii=False, indent=2)
    
    # Salva n-gramas por ordem separadamente (para carregamento sob demanda)
    print("Salvando n-gramas separadamente...")
    os.makedirs('ngrams', exist_ok=True)
    
    for n in range(2, 7):
        filename = f'ngrams/ngrams_{n}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(todos_ngramas[str(n)], f, ensure_ascii=False, separators=(',', ':'))
        print(f"  Salvo: {filename}")
    
    print("\n✅ Processamento concluído!")
    print("Arquivos gerados:")
    print("  - markov_data_complete.json (dados completos)")
    print("  - markov_data_compact.json (dados compactos)")
    print("  - ngrams/ngrams_2.json até ngrams_6.json (n-gramas por ordem)")
    
    # Mostra estatísticas finais
    print(f"\nEstatísticas:")
    print(f"  Total de tokens: {len(tokens):,}")
    print(f"  Tokens únicos: {len(set(tokens)):,}")
    print(f"  Palavras interessantes: {len(palavras_interessantes)}")
    print(f"  Exemplo de palavras: {', '.join(palavras_interessantes[:10])}")

if __name__ == "__main__":
    main()
