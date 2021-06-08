from flask import Flask, jsonify, request

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

from pydantic import ValidationError
from pydantic.error_wrappers import ErrorList
from werkzeug.wrappers import response

from blog.commands import CreateArticleCommand
from blog.queries import GetArticleByIDQuery, ListArticlesQuery

app = Flask(__name__)
# app = FastAPI()

@app.route('/create-article/', methods=['POST'])
def create_article():
    cmd = CreateArticleCommand(
        **request.json
    )
    return jsonify(cmd.execute().dict())


@app.route('/article/<article_id>/', methods=['GET'])
def get_article(article_id):
    query = GetArticleByIDQuery(
        id=article_id
    )
    return jsonify(query.execute().dict())


@app.route('/article-list/', methods=['GET'])
def list_articles():
    query = ListArticlesQuery()
    records = [record.dict() for record in query.execute()]
    return jsonify(records)


#? Flask app errorhandler
@app.errorhandler(ValidationError)
def handle_validation_exception(error):
    response = jsonify(error.errors())
    response.status_code = 400
    return response

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return PlainTextResponse(str(exc), status_code=400)

if __name__ == '__main__':
    app.run()