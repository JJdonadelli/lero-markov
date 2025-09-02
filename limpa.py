import string
import re
import sys

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Uso: python limpa3.py <arquivo.txt>")
        sys.exit(1)

    # O primeiro argumento (depois do nome do script)
    arquivo_entrada = sys.argv[1]

    print(f"Processando arquivo: {arquivo_entrada}")
    
    arquivo_saida = f"{arquivo_entrada[:-4]}_limpo.txt"
    
    try:
        # Ler o arquivo de entrada
        with open("data/"+arquivo_entrada, 'r', encoding='utf-8') as arquivo:
            texto = arquivo.read()
        
        print(f"Arquivo '{arquivo_entrada}' lido com sucesso!")
        print(f"Texto original tem {len(texto)} caracteres")
        
        # Padrão para identificar locuções pronominais
        padrao_locucoes = r'\b([a-záàâãéêíóôõúç]+)(-(?:se|me|te|lhe|nos|vos|lhes|o|a|os|as|lo|la|los|las|no|na|nos|nas))\b'
        
        # Substituir temporariamente por um placeholder único que preserve a união das palavras
        texto_protegido = re.sub(padrao_locucoes, r'\1XHIFENX\2', texto, flags=re.IGNORECASE)
        
        # Remover pontuação incluindo todos os tipos de aspas e caracteres especiais
        # Lista completa de caracteres especiais encontrados em textos
        pontuacao_extra = '—""''´`""''‚„‹›«»“”…'
        pontuacao_completa = string.punctuation + pontuacao_extra
        
        # Criar uma tabela de tradução que remove todos os sinais de pontuação
        tradutor = str.maketrans('', '', pontuacao_completa)
        texto_sem_pontuacao = texto_protegido.translate(tradutor)
        
        # Restaurar as locuções pronominais unindo as palavras (remover o placeholder)
        texto_com_locucoes = texto_sem_pontuacao.replace('XHIFENX', '-')
        
        # Substituir múltiplos espaços por um único espaço e remover quebras de linha
        texto_limpo = re.sub(r'\s+', ' ', texto_com_locucoes).strip()
        
        # Salvar o texto limpo no arquivo de saída
        with open("data/"+arquivo_saida, 'w', encoding='utf-8') as arquivo:
            arquivo.write(texto_limpo)
        
        print(f"Texto limpo salvo em '{arquivo_saida}'")
        print(f"Texto limpo tem {len(texto_limpo)} caracteres")
        
        # Contar palavras
        palavras = texto_limpo.split()
        print(f"Total de palavras: {len(palavras)}")
        
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
