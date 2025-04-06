from flask import Flask, render_template, redirect, url_for, request, json, Response
import psycopg2
from psycopg2 import OperationalError, Error
from flask_cors import CORS
from flasgger import Swagger, swag_from

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

DATABASE_URL = 'postgres://default:7Vxa6mIUDeop@ep-ancient-shape-a4mn5jxw-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require'

@app.route('/', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Lista todos os itens do estoque',
            'examples': {
                'application/json': [
                    {'id': 1, 'nome': 'Produto A', 'quantidade': 10, 'preco': 15.0}
                ]
            }
        }
    }
})
def estoque():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM estoque_padua')
        result = cursor.fetchall()
        data = [{'id': row[0], 'nome': row[1], 'quantidade': row[2], 'preco': row[3]} for row in result]
        return json.dumps(data)
    except (OperationalError, Error) as e:
        print(f"Erro ao buscar itens de estoque: {e}")
        return Response(status=400) 
    finally:
        conn.close()

@app.route('/adicionar_item', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nome': {'type': 'string'},
                    'quantidade': {'type': 'integer'},
                    'preco': {'type': 'number'}
                },
                'required': ['nome', 'quantidade', 'preco']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Item adicionado com sucesso'
        },
        400: {
            'description': 'Erro ao adicionar item'
        }
    }
})
def adicionar_item():
    if request.method == 'POST':
        nome = request.json['nome']
        quantidade = request.json['quantidade']
        preco = request.json['preco']
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO estoque_padua (nome, quantidade, preco) VALUES (%s, %s, %s)", (nome, quantidade, preco))
            conn.commit()
            return Response(json.dumps(request.json), status=201)
        except (OperationalError, Error) as e:
            print(f"Erro ao adicionar item ao estoque: {e}")
            return Response(status=400)
        finally:
            conn.close()

@app.route('/excluir/<int:item_id>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {
            'name': 'item_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do item a ser excluído'
        }
    ],
    'responses': {
        200: {
            'description': 'Item excluído com sucesso'
        },
        400: {
            'description': 'Erro ao excluir item'
        }
    }
})
def excluir_item(item_id):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM estoque_padua WHERE id_produto = %s', (item_id,))
        conn.commit()
        return Response(status=200)
    except (OperationalError, Error) as e:
        print(f"Erro ao excluir item do estoque: {e}")
        return Response(status=400)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
