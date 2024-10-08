from flask import Flask, render_template, redirect, url_for, request, json, Response
import psycopg2
from psycopg2 import OperationalError, Error
from flask_cors import CORS

# app = Flask(__name__,template_folder='templates')

app = Flask(__name__)
CORS(app)

# Configuração da conexão com o banco de dados PostgreSQL
DATABASE_URL = 'postgres://default:7Vxa6mIUDeop@ep-ancient-shape-a4mn5jxw-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require'
  
# Rota principal para exibir o estoque
@app.route('/',methods=['GET'])
def estoque():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM estoque_padua')
        result = cursor.fetchall()
        data = []

        for row in result:
          data.append({
              'id': row[0],
              'nome': row[1],
              'quantidade': row[2],
              'preco': row[3],
          })
        return json.dumps(data)
        # return render_template('estoque.html', items=items)
    except (OperationalError, Error) as e:
        print(f"Erro ao buscar itens de estoque: {e}")
        return Response(status=400) 
    finally:
        conn.close()

# Rota para adicionar um novo item ao estoque
@app.route('/adicionar_item', methods=['GET', 'POST'])
def adicionar_item():
    if request.method == 'POST':
        nome = request.json['nome']
        quantidade = request.json['quantidade']
        preco = request.json['preco']
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO estoque_padua (nome, quantidade, preco) VALUES ( %s, %s, %s)", (nome, quantidade, preco))
            conn.commit() 
            return Response(json.dumps(request.json), status=201)   
        except (OperationalError, Error) as e:
            print(f"Erro ao adicionar item ao estoque: {e}")
            return Response(status=400) 
        finally:
            conn.close() 

# Rota para excluir um item do estoque
@app.route('/excluir/<int:item_id>', methods=['DELETE'])
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