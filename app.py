from  flask import Flask, render_template
from banco import *

# connection = PostgreSQLConnection(
#     dbname="mecado_livre_produtos",
#     user="postgres",
#     password="senai2024",
#     host="10.130.18.41",
#     port="5432"
# )

connection = PostgreSQLConnection(
    dbname="mercado_livre_produtos",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

# print(produtos['data'])

app = Flask(__name__)

@app.route("/")
def produtos():
    produto = Produto(connection=connection)
    produtos = produto.produtos()
    return render_template("produtos.html", lista=produtos['data'])


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=2000)