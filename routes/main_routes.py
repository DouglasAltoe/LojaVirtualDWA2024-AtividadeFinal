import math
from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse

from dtos.entrar_dto import EntrarDto
from util.html import ler_html
from dtos.inserir_usuario_dto import InserirUsuarioDTO
from models.usuario_model import Usuario
from models.categoria_model import Categoria
from repositories.usuario_repo import UsuarioRepo
from repositories.produto_repo import ProdutoRepo
from repositories.categoria_repo import CategoriaRepo

from util.auth_jwt import (
    conferir_senha,
    criar_token,
    obter_hash_senha,
)

from util.cookies import TEMPO_COOKIE_AUTH, adicionar_cookie_auth, adicionar_mensagem_sucesso
from util.pydantic import create_validation_errors
from util.templates import obter_jinja_templates


router = APIRouter(include_in_schema=False)
templates = obter_jinja_templates("templates/main")


@router.get("/categoria")
async def obter_categorias(request: Request):
    categorias = CategoriaRepo.obter_todos()
    return templates.TemplateResponse(
        "pages/categorias_produtos", 
        {"request": request, "categorias": categorias}
    )


@router.get("/categoria/{id_categoria:int}")
async def obter_categoria(request: Request, id_categoria: int):
    categoria = CategoriaRepo.obter_um(id_categoria)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    return templates.TemplateResponse(
        "pages/categorias_produtos.html",
        {"request": request, "categoria": categoria},
    )


@router.post("/post_inserir_categoria", response_class=JSONResponse)
async def post_inserir_categoria(
    descricao: str = Query(...),
):
    nova_categoria = CategoriaRepo.inserir(Categoria(descricao=descricao))
    if not nova_categoria:
        raise HTTPException(status_code=400, detail="Erro ao criar categoria.")
    return {"redirect": {"url": "/categorias"}}


@router.post("/post_alterar_categoria", response_class=JSONResponse)
async def post_alterar_categoria(
    id_categoria: int = Query(...),
    descricao: str = Query(...),
):
    categoria = CategoriaRepo.obter_um(id_categoria)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    categoria.descricao = descricao
    if not CategoriaRepo.alterar(categoria):
        raise HTTPException(status_code=400, detail="Erro ao alterar categoria.")
    return {"redirect": {"url": f"/categoria/{id_categoria}"}}


@router.post("/post_excluir_categoria", response_class=JSONResponse)
async def post_excluir_categoria(id_categoria: int = Query(...)):
    categoria = CategoriaRepo.obter_um(id_categoria)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    if not CategoriaRepo.excluir(id_categoria):
        raise HTTPException(status_code=400, detail="Erro ao excluir categoria.")
    return {"redirect": {"url": "/categorias"}}

@router.get("/html/{arquivo}")
async def get_html(arquivo: str):
    response = HTMLResponse(ler_html(arquivo))
    return response


@router.get("/")
async def get_root(request: Request):
    produtos = ProdutoRepo.obter_todos()
    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "produtos": produtos,
        },
    )


@router.get("/contato")
async def get_contato(request: Request):
    return templates.TemplateResponse(
        "pages/contato.html",
        {"request": request},
    )


@router.get("/cadastro")
async def get_cadastro(request: Request):
    return templates.TemplateResponse(
        "pages/cadastro.html",
        {"request": request},
    )


@router.post("/post_cadastro", response_class=JSONResponse)
async def post_cadastro(cliente_dto: InserirUsuarioDTO):
    cliente_data = cliente_dto.model_dump(exclude={"confirmacao_senha"})
    cliente_data["senha"] = obter_hash_senha(cliente_data["senha"])
    novo_cliente = UsuarioRepo.inserir(Usuario(**cliente_data))
    if not novo_cliente or not novo_cliente.id:
        raise HTTPException(status_code=400, detail="Erro ao cadastrar cliente.")
    return {"redirect": {"url": "/cadastro_realizado"}}


@router.get("/cadastro_realizado")
async def get_cadastro_realizado(request: Request):
    return templates.TemplateResponse(
        "pages/cadastro_confirmado.html",
        {"request": request},
    )


@router.get("/entrar")
async def get_entrar(
    request: Request,
    return_url: str = Query("/"),
):
    return templates.TemplateResponse(
        "pages/entrar.html",
        {
            "request": request,
            "return_url": return_url,
        },
    )


@router.post("/post_entrar", response_class=JSONResponse)
async def post_entrar(entrar_dto: EntrarDto):
    cliente_entrou = UsuarioRepo.obter_por_email(entrar_dto.email)
    if (
        (not cliente_entrou)
        or (not cliente_entrou.senha)
        or (not conferir_senha(entrar_dto.senha, cliente_entrou.senha))
    ):
        return JSONResponse(
            content=create_validation_errors(
                entrar_dto,
                ["email", "senha"],
                ["Credenciais inválidas.", "Credenciais inválidas."],
            ),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    token = criar_token(cliente_entrou.id, cliente_entrou.nome, cliente_entrou.email, cliente_entrou.perfil)
    response = JSONResponse(content={"redirect": {"url": entrar_dto.return_url}})
    adicionar_mensagem_sucesso(
        response,
        f"Olá, <b>{cliente_entrou.nome}</b>. Seja bem-vindo(a) à Loja Virtual!",
    )
    adicionar_cookie_auth(response, token, TEMPO_COOKIE_AUTH)
    return response


@router.get("/produto/{id:int}")
async def get_produto(request: Request, id: int):
    produto = ProdutoRepo.obter_um(id)
    return templates.TemplateResponse(
        "pages/produto.html",
        {
            "request": request,
            "produto": produto,
        },
    )


@router.get("/buscar")
async def get_buscar(
    request: Request,
    q: str,
    p: int = 1,
    tp: int = 6,
    o: int = 1,
):
    produtos = ProdutoRepo.obter_busca(q, p, tp, o)
    qtde_produtos = ProdutoRepo.obter_quantidade_busca(q)
    qtde_paginas = math.ceil(qtde_produtos / float(tp))
    return templates.TemplateResponse(
        "pages/buscar.html",
        {
            "request": request,
            "produtos": produtos,
            "quantidade_paginas": qtde_paginas,
            "tamanho_pagina": tp,
            "pagina_atual": p,
            "termo_busca": q,
            "ordem": o,
        },
    )
