SQL_CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL
    );
"""

SQL_INSERIR = """
    INSERT INTO categoria(descricao)
    VALUES (?);
"""

SQL_OBTER_UM = """
    SELECT id, descricao
    FROM categoria
    WHERE id=?;
"""

SQL_OBTER_TODOS = """
    SELECT id, descricao
    FROM categoria
    ORDER BY id;
"""

SQL_ALTERAR = """
    UPDATE categoria
    SET descricao=?
    WHERE id=?;
"""

SQL_EXCLUIR = """
    DELETE FROM categoria
    WHERE id=?;
"""

SQL_OBTER_QUANTIDADE = """
    SELECT COUNT(*) FROM categoria;
"""