import json
import logging
import os
from doc_generator.article_builder import Article, DocArticle
from doc_generator.doc_reader import extract_doc_from
from doc_generator.diagram_builder import DiagramContent, DiagramAsCodeRenderer, D2Renderer, Link, LinkPreset

from doc_generator.json_dumps_fix import *  # Fix json.dumps


def generate_articles(file_path, out_path, group) -> list[Article]:
    docs = extract_doc_from(file_path)

    articles = []  # List of all Articles inside

    article = None

    for doc in docs:

        # We check if this doc is the beginning of a new class/struct
        if doc.isClass() or doc.isStruct():
            # Multiple class in one file
            if article:
                articles.append(article)

            article = DocArticle()
            article.SetClass(doc)
            article.SetGroup(group)
            article.SetDirectory(out_path)

            DiagramContent.addObject(group, doc.getName(), doc.getAlias())
            for link in article.class_content.links:
                if link.active:
                    DiagramContent.addLink(link=link)
                else:
                    DiagramContent.setNoAutoLink(link.objectA, link.objectB)
            continue

        if doc.isFunction():
            # If not inside a class / struct
            if not article:
                raise Exception(f'Commented function not in commented class nor commented struct for {file_path} : {doc}')

            article.AddFunction(doc)

    # Save content at the end
    if article:
        articles.append(article)

    return articles



def explore_file(file, out_directory, pretty_path) -> list[DocArticle]:
    # Get Article inside this file
    return generate_articles(file, out_directory, pretty_path)


def explore_directory(script_directory, doc_directory, pretty_path) -> list[DocArticle]:
    articles = []
    for file in os.listdir(script_directory):
        path = f'{script_directory}/{file}'
        if os.path.isfile(path):
            if file.endswith('.cs'):
                articles = articles + explore_file(path, doc_directory, pretty_path)
        elif os.path.isdir(path):
            articles = articles + explore_directory(path, f'{doc_directory}/{file}', f'{pretty_path}/{file}')

    return articles


import sys

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    script_folder = str(sys.argv[1])
    doc_folder = str(sys.argv[2])

    # Get all Articles for Documentation
    articles = explore_directory(script_folder, doc_folder, "")

    # Setup AutoLink
    for article in articles:
        for relation in article.getRelatedArticles():
            DiagramContent.addAutoLink(article.name, relation)

    debug = False
    if debug:
        DiagramContent.exportJson()  # Preview the values

    # Render diagram
    renderer = D2Renderer(DiagramContent, f"{doc_folder}/graphs/d2", f"{doc_folder}/graphs/svg")
    renderer.export()  # Global export

    for article in articles:
        article.SetGraph(renderer.export(limit_to=article.name))
        article.Publish()


    # Assign colors to graph group in obsidian config
    with open(f'{doc_folder}/.obsidian/graph.json', 'r') as graph_file:
        config = json.loads(graph_file.read())

    config['colorGroups'] = [{
        "query": name,
        "color": {
            "a": 1,
            "rgb": color
        }
    } for name, color in DiagramContent.colors.items()]

    with open(f'{doc_folder}/.obsidian/graph.json', 'w') as graph_file:
        graph_file.write(json.dumps(config, indent=2))
