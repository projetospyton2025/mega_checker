from flask import Flask, render_template, request, jsonify
import requests
import re
from typing import List, Dict
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max-limit
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calcular_valor_aposta(qtd_dezenas: int) -> float:
    valores = {
        6: 5.00,
        7: 35.00,
        8: 140.00,
        9: 420.00,
        10: 1050.00,
        11: 2310.00,
        12: 4620.00,
        13: 8580.00,
        14: 15015.00,
        15: 25025.00
    }
    return valores.get(qtd_dezenas, 0)

def extrair_numeros(texto: str) -> List[int]:
    numeros = re.findall(r'\d+', texto)
    return sorted([int(num) for num in numeros if 1 <= int(num) <= 60])

def obter_ultimo_resultado() -> Dict:
    response = requests.get("https://api.guidi.dev.br/loteria/megasena/ultimo")
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/')
def index():
    ultimo_resultado = obter_ultimo_resultado()
    return render_template('index.html', ultimo_resultado=ultimo_resultado)

@app.route('/conferir', methods=['POST'])
def conferir():
    try:
        numeros_texto = request.form.get('numeros', '')
        numeros_jogo = extrair_numeros(numeros_texto)
        
        if not 6 <= len(numeros_jogo) <= 15:
            return jsonify({
                'error': 'O jogo deve ter entre 6 e 15 números'
            }), 400

        ultimo_resultado = obter_ultimo_resultado()
        if not ultimo_resultado:
            return jsonify({
                'error': 'Não foi possível obter o resultado atual'
            }), 400

        numeros_sorteados = [int(n) for n in ultimo_resultado['dezenas']]
        acertos = len(set(numeros_jogo) & set(numeros_sorteados))
        numeros_acertados = sorted(list(set(numeros_jogo) & set(numeros_sorteados)))
        
        valor_gasto = calcular_valor_aposta(len(numeros_jogo))
        
        return jsonify({
            'sucesso': True,
            'resultado': {
                'numeros_jogados': numeros_jogo,
                'qtd_dezenas': len(numeros_jogo),
                'acertos': acertos,
                'numeros_acertados': numeros_acertados,
                'valor_gasto': valor_gasto,
                'concurso': ultimo_resultado['concurso'],
                'data_concurso': ultimo_resultado['data']
            }
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
            
        if file and allowed_file(file.filename):
            conteudo = file.read().decode('utf-8')
            numeros_jogo = extrair_numeros(conteudo)
            
            if not 6 <= len(numeros_jogo) <= 15:
                return jsonify({
                    'error': 'O jogo deve ter entre 6 e 15 números'
                }), 400

            ultimo_resultado = obter_ultimo_resultado()
            if not ultimo_resultado:
                return jsonify({
                    'error': 'Não foi possível obter o resultado atual'
                }), 400

            numeros_sorteados = [int(n) for n in ultimo_resultado['dezenas']]
            acertos = len(set(numeros_jogo) & set(numeros_sorteados))
            numeros_acertados = sorted(list(set(numeros_jogo) & set(numeros_sorteados)))
            
            valor_gasto = calcular_valor_aposta(len(numeros_jogo))
            
            return jsonify({
                'sucesso': True,
                'resultado': {
                    'numeros_jogados': numeros_jogo,
                    'qtd_dezenas': len(numeros_jogo),
                    'acertos': acertos,
                    'numeros_acertados': numeros_acertados,
                    'valor_gasto': valor_gasto,
                    'concurso': ultimo_resultado['concurso'],
                    'data_concurso': ultimo_resultado['data']
                }
            })
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)