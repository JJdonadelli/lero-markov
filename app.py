import streamlit as st
import re
import random
from collections import defaultdict, Counter
import os

# Configuração da página
st.set_page_config(
    page_title="Gerador de Texto Alice",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def ler_arquivos():
    """Lê os dois arquivos de texto e retorna o conteúdo combinado."""
    maravilha = ""
    espelho = ""
    
    if os.path.exists('data/maravilha-limpo.txt'):
        try:
            with open('data/maravilha-limpo.txt', 'r', encoding='utf-8') as f:
                maravilha = f.read()
        except Exception as e:
            st.error(f"Erro ao ler maravilha-limpo.txt: {e}")
    else:
        st.error("Arquivo 'data/maravilha-limpo.txt' não encontrado!")
    
    if os.path.exists('data/espelho-limpo.txt'):
        try:
            with open('data/espelho-limpo.txt', 'r', encoding='utf-8') as f:
                espelho = f.read()
        except Exception as e:
            st.error(f"Erro ao ler espelho-limpo.txt: {e}")
    else:
        st.error("Arquivo 'data/espelho-limpo.txt' não encontrado!")
    
    return maravilha + " " + espelho

@st.cache_data
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

@st.cache_data
def tokenizar(texto):
    """Tokeniza o texto em palavras."""
    tokens = [token for token in texto.split() if token]
    return tokens

@st.cache_data
def criar_ngramas(tokens, n):
    """Cria um dicionário de n-gramas a partir dos tokens."""
    ngramas = defaultdict(list)
    
    for i in range(len(tokens) - n + 1):
        # Chave: n-1 palavras anteriores
        chave = tuple(tokens[i:i+n-1])
        # Valor: próxima palavra
        proxima_palavra = tokens[i+n-1]
        ngramas[chave].append(proxima_palavra)
    
    return dict(ngramas)

@st.cache_data
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

def gerar_texto(ngramas_dict, palavra_inicial, n, tamanho=51):
    """Gera texto usando cadeias de Markov com n-gramas progressivos."""
    resultado = [palavra_inicial]
    
    for tamanho_atual in range(2, n + 1):
        if len(resultado) >= tamanho:
            break
            
        ngramas_atuais = ngramas_dict[tamanho_atual]
        contexto_size = tamanho_atual - 1
        
        tentativas = 0
        max_tentativas = 100
        
        while len(resultado) < tamanho and tentativas < max_tentativas:
            tentativas += 1
            
            if len(resultado) < contexto_size:
                break
                
            contexto = tuple(resultado[-contexto_size:])
            
            if contexto in ngramas_atuais and ngramas_atuais[contexto]:
                proxima = random.choice(ngramas_atuais[contexto])
                resultado.append(proxima)
                tentativas = 0  # Reset tentativas quando encontra uma palavra
            else:
                if contexto_size > 1:
                    contexto_menor = contexto[1:]
                    if contexto_menor in ngramas_atuais and ngramas_atuais[contexto_menor]:
                        proxima = random.choice(ngramas_atuais[contexto_menor])
                        resultado.append(proxima)
                        tentativas = 0
                    else:
                        break
                else:
                    break
    
    return resultado[:tamanho]

def adicionar_pontuacao_basica(texto):
    """Adiciona pontuação básica ao texto gerado."""
    palavras = texto.split()
    resultado = []
    
    for i, palavra in enumerate(palavras):
        resultado.append(palavra)
        
        # Ponto a cada 10-15 palavras aproximadamente
        if (i + 1) % random.randint(10, 15) == 0 and i < len(palavras) - 1:
            resultado[-1] += '.'
    
    return ' '.join(resultado)

def main():
    # Título principal
    st.title("Gerador de Lero-lero com Cadeias de Markov")
    # st.markdown("### *Baseado nos livros de Alice no País das Maravilhas*")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Parâmetro N
        n = st.slider(
            "Ordem dos N-gramas (n)",
            min_value=2,
            max_value=6,
            value=3,
            help="Ordem dos n-gramas. Valores maiores geram texto mais coerente mas menos criativo."
        )
        
        # Tamanho do texto
        tamanho = st.number_input(
            "Tamanho do texto (palavras)",
            min_value=10,
            max_value=200,
            value=51,
            help="Número de palavras a serem geradas."
        )
        
        st.divider()
        
        # Informações
        st.markdown("""
        ### Como funciona?
        O algoritmo aprende padrões de palavras consecutivas através das estórias de Alice, de Lewis Carrol. 
        
        ### Dica:
        - N baixo = mais criativo, menos coerente
        - N alto = mais coerente, menos criativo
        """)
    
    # Carrega e processa os dados
    if 'texto_processado' not in st.session_state:
        with st.spinner("Carregando e processando os livros da Alice..."):
            texto_completo = ler_arquivos()
            
            if not texto_completo.strip():
                st.error("Não foi possível carregar os arquivos de texto!")
                st.stop()
            
            texto_limpo = preprocessar_texto(texto_completo)
            tokens = tokenizar(texto_limpo)
            
            st.session_state.texto_processado = True
            st.session_state.tokens = tokens
            st.session_state.palavras_interessantes = encontrar_palavras_interessantes(tokens)
    
    
    
    st.divider()
    
    # Seleção da palavra inicial
    st.header(" Escolha da Palavra Inicial")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Selectbox com palavras interessantes
        palavra_selecionada = st.selectbox(
            "Palavras sugeridas (relacionadas às fábulas):",
            options=st.session_state.palavras_interessantes,
            help="Palavras extraídas automaticamente dos textos da Alice"
        )
    
    with col2:
        # Input manual
        palavra_manual = st.text_input(
            "Ou digite uma palavra:",
            placeholder="ex: gato",
            help="Digite qualquer palavra para começar o texto"
        )
    
    # Determina a palavra inicial
    palavra_inicial = palavra_manual.lower().strip() if palavra_manual else palavra_selecionada
    
    # Botão para gerar texto
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        gerar_button = st.button(
            "🎲 Gerar Texto",
            type="primary",
            use_container_width=True
        )
    
    # Geração do texto
    if gerar_button:
        if not palavra_inicial:
            st.error("Por favor, selecione ou digite uma palavra inicial!")
        else:
            with st.spinner(f"Gerando texto com {n}-gramas..."):
                # Cria n-gramas
                ngramas_dict = {}
                progress_bar = st.progress(0)
                
                for i, tamanho_atual in enumerate(range(2, n + 1)):
                    ngramas_dict[tamanho_atual] = criar_ngramas(st.session_state.tokens, tamanho_atual)
                    progress_bar.progress((i + 1) / (n - 1))
                
                progress_bar.empty()
                
                # Gera o texto
                texto_gerado = gerar_texto(ngramas_dict, palavra_inicial, n, tamanho)
                
                # Exibe o resultado
                st.success("✨ Texto gerado com sucesso!")
                
                # Container para o texto gerado
                st.header("📖 Texto Gerado")
                
                texto_final = ' '.join(texto_gerado)
                # texto_final = adicionar_pontuacao_basica(texto_final_pre)

                # Caixa de texto com o resultado
                st.text_area(
                    "Resultado:",
                    value=texto_final,
                    height=200,
                    help="Texto gerado usando cadeias de Markov"
                )
                
                # Estatísticas da geração
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📝 Palavras Geradas", len(texto_gerado))
                with col2:
                    st.metric("🔧 N-gramas Usados", n)
                with col3:
                    st.metric("🎯 Palavra Inicial", f'"{palavra_inicial}"')
                with col4:
                    st.metric("📊 Caracteres", len(texto_final))
                
                # Opção de download
                st.download_button(
                    label="💾 Baixar Texto",
                    data=texto_final,
                    file_name=f"alice_texto_gerado_{n}gramas.txt",
                    mime="text/plain"
                )
                
                # Exibe algumas estatísticas dos n-gramas
                with st.expander("🔍 Estatísticas Detalhadas"):
                    for i in range(2, n + 1):
                        st.write(f"**{i}-gramas**: {len(ngramas_dict[i]):,} combinações únicas")
                    
                    # Mostra algumas palavras mais frequentes
                    contador = Counter(st.session_state.tokens)
                    palavras_freq = contador.most_common(10)
                    
                    st.write("**Palavras mais frequentes no corpus:**")
                    freq_text = ", ".join([f"{palavra} ({freq})" for palavra, freq in palavras_freq])
                    st.write(freq_text)
    
    # História de Markov no final da página
    st.divider()
# Estatísticas do corpus
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total de Palavras", f"{len(st.session_state.tokens):,}")
    with col2:
        st.metric("🔤 Palavras Únicas", f"{len(set(st.session_state.tokens)):,}")
    with col3:
        palavras_alice = len([p for p in st.session_state.palavras_interessantes 
                             if p in ['alice', 'coelho', 'chapeleiro', 'gato', 'rainha']])
        st.metric("🎭 Palavras da Alice", palavras_alice)

    st.divider()

    st.header("A história")
    
    st.markdown("""
    
    As **Cadeias de Markov** recebem o nome do matemático russo **Andrei Andreevich Markov** (1856-1922), que desenvolveu 
    essa teoria no início do século XX. Markov era professor na Universidade de São Petersburgo e um dos 
    principais matemáticos de sua época. 
      
    Curiosamente, o primeiro experimento famoso de Markov com sua própria teoria foi realizado em **1913** 
    usando o romance épico russo **"Eugene Onegin"** de Alexander Pushkin! Markov analisou a sequência de 
    vogais e consoantes no texto para demonstrar como eventos futuros podiam depender apenas do estado presente, 
    não de toda a história anterior.
    
    A **propriedade markoviana** estabelece que:
    > *"O futuro depende apenas do presente, não do passado"*
    
    Em termos matemáticos, isso significa que a probabilidade do próximo estado depende apenas do estado atual, 
    não de como chegamos até ele. No contexto de geração de texto:
    - A próxima palavra depende apenas das últimas N-1 palavras
    - Não importa todo o histórico anterior do texto
       
    Hoje, as Cadeias de Markov são fundamentais em:
    - **Processamento de Linguagem Natural** (como este aplicativo!)
    - **Análise Financeira** (modelagem de preços de ações)
    - **Bioinformática** (análise de sequências de DNA)
    - **Inteligência Artificial** (chatbots e sistemas de recomendação)
    """)
    
    # Créditos
    st.markdown("""
    ---
    **Desenvolvido em Streamlit**  
    """)

if __name__ == "__main__":
    main()
