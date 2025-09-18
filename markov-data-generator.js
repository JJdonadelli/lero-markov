// markov-data-generator.js
// Execute este script no Node.js para gerar os arquivos JSON

const fs = require('fs');
const path = require('path');

function preprocessText(text) {
    if (!text) return "";
    
    // Remove quebras de linha excessivas e caracteres especiais
    text = text.replace(/\n+/g, ' ');
    text = text.replace(/[^\w\s\.\!\?\,\;\:]/g, '');
    
    // Converte para minúsculas
    text = text.toLowerCase();
    
    // Remove espaços múltiplos
    text = text.replace(/\s+/g, ' ');
    
    return text.trim();
}

function tokenize(text) {
    return text.split(' ').filter(token => token.length > 0);
}

function createNgrams(tokens, n) {
    const ngrams = {};
    
    for (let i = 0; i <= tokens.length - n; i++) {
        const key = tokens.slice(i, i + n - 1).join(' ');
        const nextWord = tokens[i + n - 1];
        
        if (!ngrams[key]) {
            ngrams[key] = [];
        }
        ngrams[key].push(nextWord);
    }
    
    return ngrams;
}

function findInterestingWords(tokens) {
    const aliceWords = [
        'alice', 'coelho', 'chapeleiro', 'gato', 'rainha', 'rei', 'carta', 'cartas',
        'chá', 'mesa', 'jardim', 'buraco', 'toca', 'relógio', 'tempo', 'mundo',
        'país', 'maravilhas', 'espelho', 'sonho', 'dormindo', 'acordar',
        'pequena', 'grande', 'crescer', 'diminuir', 'poção', 'beber', 'comer',
        'porta', 'chave', 'curiosa', 'estranha', 'estranho', 'medo', 'coragem'
    ];
    
    const counter = {};
    tokens.forEach(token => {
        counter[token] = (counter[token] || 0) + 1;
    });
    
    const availableWords = [];
    aliceWords.forEach(word => {
        if (counter[word] && counter[word] > 3) {
            availableWords.push(word);
        }
    });
    
    // Palavras mais frequentes
    const sortedWords = Object.entries(counter)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 30)
        .filter(([word, freq]) => word.length > 3 && /^[a-z]+$/.test(word))
        .map(([word]) => word)
        .slice(0, 15);
    
    const allWords = [...new Set([...availableWords, ...sortedWords])];
    return allWords.sort();
}

async function main() {
    console.log('🚀 Iniciando processamento...');
    
    // Caminhos dos arquivos
    const paths = [
        'public_html/estocastico/markov_lero/data/maravilha-limpo.txt',
        'public_html/estocastico/markov_lero/data/espelho-limpo.txt',
        'data/maravilha-limpo.txt',
        'data/espelho-limpo.txt'
    ];
    
    let maravilhaText = '';
    let espelhoText = '';
    
    // Tenta carregar os arquivos
    for (const basePath of ['public_html/estocastico/markov_lero/data/', 'data/']) {
        try {
            maravilhaText = fs.readFileSync(path.join(basePath, 'maravilha-limpo.txt'), 'utf8');
            espelhoText = fs.readFileSync(path.join(basePath, 'espelho-limpo.txt'), 'utf8');
            console.log(`✅ Arquivos carregados de: ${basePath}`);
            break;
        } catch (error) {
            console.log(`❌ Tentativa falhou: ${basePath}`);
        }
    }
    
    if (!maravilhaText || !espelhoText) {
        console.error('❌ Não foi possível carregar os arquivos de texto!');
        console.log('Certifique-se de que os arquivos estão em uma dessas localizações:');
        console.log('- public_html/estocastico/markov_lero/data/');
        console.log('- data/');
        return;
    }
    
    const fullText = maravilhaText + ' ' + espelhoText;
    console.log(`📖 Texto completo: ${fullText.length.toLocaleString()} caracteres`);
    
    // Preprocessa
    console.log('🔄 Preprocessando texto...');
    const cleanText = preprocessText(fullText);
    const tokens = tokenize(cleanText);
    console.log(`🔤 Tokens gerados: ${tokens.length.toLocaleString()}`);
    
    // Palavras interessantes
    console.log('🎯 Encontrando palavras interessantes...');
    const interestingWords = findInterestingWords(tokens);
    console.log(`✨ Palavras interessantes: ${interestingWords.length}`);
    
    // Gera n-gramas
    console.log('🔗 Gerando n-gramas...');
    const allNgrams = {};
    
    for (let n = 2; n <= 6; n++) {
        console.log(`  📊 Processando ${n}-gramas...`);
        const ngrams = createNgrams(tokens, n);
        allNgrams[n.toString()] = ngrams;
        console.log(`    ✅ ${Object.keys(ngrams).length.toLocaleString()} ${n}-gramas únicos`);
    }
    
    // Prepara dados
    const completeData = {
        palavras_interessantes: interestingWords,
        ngramas: allNgrams,
        estatisticas: {
            total_tokens: tokens.length,
            tokens_unicos: new Set(tokens).size,
            palavras_alice: interestingWords.filter(w => 
                ['alice', 'coelho', 'chapeleiro', 'gato', 'rainha'].includes(w)
            ).length
        }
    };
    
    // Dados compactos (apenas sample)
    const compactData = {
        palavras_interessantes: interestingWords,
        estatisticas: completeData.estatisticas,
        sample_ngramas: {
            '2': Object.fromEntries(Object.entries(allNgrams['2']).slice(0, 100)),
            '3': Object.fromEntries(Object.entries(allNgrams['3']).slice(0, 100)),
            '4': Object.fromEntries(Object.entries(allNgrams['4']).slice(0, 50))
        }
    };
    
    // Salva arquivos
    console.log('💾 Salvando arquivos...');
    
    // Arquivo compacto
    fs.writeFileSync('markov_data_compact.json', JSON.stringify(compactData, null, 2));
    console.log('✅ markov_data_compact.json salvo');
    
    // Arquivo completo
    fs.writeFileSync('markov_data_complete.json', JSON.stringify(completeData));
    console.log('✅ markov_data_complete.json salvo');
    
    // N-gramas separados
    if (!fs.existsSync('ngrams')) {
        fs.mkdirSync('ngrams');
    }
    
    for (let n = 2; n <= 6; n++) {
        const filename = `ngrams/ngrams_${n}.json`;
        fs.writeFileSync(filename, JSON.stringify(allNgrams[n.toString()]));
        console.log(`✅ ${filename} salvo`);
    }
    
    // Estatísticas finais
    console.log('\n📊 ESTATÍSTICAS FINAIS:');
    console.log(`Total de tokens: ${tokens.length.toLocaleString()}`);
    console.log(`Tokens únicos: ${new Set(tokens).size.toLocaleString()}`);
    console.log(`Palavras interessantes: ${interestingWords.length}`);
    console.log(`Exemplos: ${interestingWords.slice(0, 10).join(', ')}`);
    
    console.log('\n🎉 Processamento concluído com sucesso!');
    console.log('\n📁 Arquivos gerados:');
    console.log('  - markov_data_compact.json (carregamento rápido)');
    console.log('  - markov_data_complete.json (dados completos)');
    console.log('  - ngrams/ngrams_2.json até ngrams_6.json');
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { main, preprocessText, tokenize, createNgrams, findInterestingWords };