from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Iterator


class TokenKind(enum.Enum):
    """Classe já implementada: nomes e números não devem ser alterados."""

    EOF = -1

    IDENTIFIER = 1
    INT_LITERAL = 2
    STRING_LITERAL = 3

    KW_INT = 10
    KW_BOOL = 11
    KW_VOID = 12
    KW_TRUE = 13
    KW_FALSE = 14
    KW_IF = 15
    KW_ELSE = 16
    KW_WHILE = 17
    KW_RETURN = 18
    KW_PRINT = 19

    PLUS = 20
    MINUS = 21
    STAR = 22
    SLASH = 23
    PERCENT = 24
    LESS = 25
    LESS_EQUAL = 26
    GREATER = 27
    GREATER_EQUAL = 28
    EQUAL_EQUAL = 29
    NOT_EQUAL = 30
    LOGICAL_AND = 31
    LOGICAL_OR = 32
    LOGICAL_NOT = 33
    ASSIGN = 34

    LEFT_PAREN = 40
    RIGHT_PAREN = 41
    LEFT_BRACE = 42
    RIGHT_BRACE = 43
    COMMA = 44
    SEMICOLON = 45


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    lexeme: str
    value: int | str | bool | None
    line: int
    column: int

    def __str__(self) -> str:
        return (
            f"<{self.kind.value}, {self.kind.name}, {self.lexeme!r}, "
            f"{self.value!r}, {self.line}, {self.column}>"
        )


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"erro léxico em {self.line}:{self.column}: {self.message}"


class Lexer:
    """Converte texto-fonte MicroC em uma sequência de tokens."""

    #as palavras reservadas vao consultadas nessa tabela.
    RESERVADAS = {
        "int": TokenKind.KW_INT,
        "bool": TokenKind.KW_BOOL,
        "void": TokenKind.KW_VOID,
        "true": TokenKind.KW_TRUE,
        "false": TokenKind.KW_FALSE,
        "if": TokenKind.KW_IF,
        "else": TokenKind.KW_ELSE,
        "while": TokenKind.KW_WHILE,
        "return": TokenKind.KW_RETURN,
        "print": TokenKind.KW_PRINT,
    }

    #os operadores e simbolos sao consultados nessa tabela.
    SIMBOLOS = {
        "<=": TokenKind.LESS_EQUAL,
        ">=": TokenKind.GREATER_EQUAL,
        "==": TokenKind.EQUAL_EQUAL,
        "!=": TokenKind.NOT_EQUAL,
        "&&": TokenKind.LOGICAL_AND,
        "||": TokenKind.LOGICAL_OR,
        "+": TokenKind.PLUS,
        "-": TokenKind.MINUS,
        "*": TokenKind.STAR,
        "/": TokenKind.SLASH,
        "%": TokenKind.PERCENT,
        "<": TokenKind.LESS,
        ">": TokenKind.GREATER,
        "!": TokenKind.LOGICAL_NOT,
        "=": TokenKind.ASSIGN,
        "(": TokenKind.LEFT_PAREN,
        ")": TokenKind.RIGHT_PAREN,
        "{": TokenKind.LEFT_BRACE,
        "}": TokenKind.RIGHT_BRACE,
        ",": TokenKind.COMMA,
        ";": TokenKind.SEMICOLON,
    }

    def __init__(self, source: str):
        self.source = source
        # TODO: inicialize aqui o estado exigido por sua estratégia.
        self.index = 0
        self.line = 1
        self.column = 1

    def avanco(self): #avança para pegar o estado 
        if self.index < len(self.source):
            if self.source[self.index]  == "\n":
                self.line += 1
                self.column = 1
            else :
                self.column += 1
            self.index += 1

    def caracter_atual(self): #pega o atual e retorna o caracter
        if self.index < len(self.source):
            return self.source[self.index]
        else:
            return None

    def ver_proximo_caracter(self): #ve o proximo, vai ajudar nos operadores log
        if self.index + 1 < len(self.source):
            return self.source[self.index+ 1] 
        else:
            return None

    def id_letra(self, character: str) -> bool:
        if character == None:
            return False
            return ( "a" <= character <= "z" or "A" <= character <= "Z" or character == "_" )

    def identificador_reservada(self):  #aqui n verifica se a palavra começa com letra
        inicio = self.index #salva o index(posicao) de quando entrou na funcao.
        # linha_inicio = self.line
        # coluna_inicio = self.column
        
        while True:
            character = self.caracter_atual() #enquanto for verdadeiro vai avancando o self.index

            if character is None:
                break

            if self.id_letra(character) or ("0" <= character <= "9"):  #se n for numero, letra ou _, da false e quebra
                self.avanco()
            else:
                break
        lexeme = self.source[inicio:self.index] #o index avança até o final da palavra, ent pegamos o index de quando entrou na funcao(inicio) até o index atual
        #e a palavra pe colocada no lexeme

        if lexeme in self.RESERVADAS: #ve c tem na tabela reservadas
            return self.RESERVADAS[lexeme] #se tiver, retorna o valor do lexeme
        else:
            return TokenKind.IDENTIFIER # se n tiver, é um identifcador e retorna tokem de identificador

    
    def id_numero(self, character: str) -> bool:
        return "0" <= character <= "9"
    
    def id_pular(self) -> None:
        while self.index < len(self.source):
            caractere = self.source[self.index]
            if (caractere == " " or caractere == "\n" or caractere == "\r" or caractere == "\t"):
                self.avanco()
                continue
            if (caractere == "/" and self.index + 1 < len(self.source) and self.source[self.index + 1] == "/"):
                self.avanco()
                self.avanco()

                while self.index < len(self.source):
                    caractere = self.source[self.index]
                    if caractere == "\n":
                        break
                    if ord(caractere) > 127: # Caractere eh valido
                        raise LexerError("caractere invalido", self.line, self.column)
                    self.avanco()
                continue
            if (caractere == "/" and self.index + 1 < len(self.source) and self.source[self.index + 1] == "*"):
                inicio_linha = self.line #GUARDAR POSICAO INICIAL PARA FECHAR DPS
                inicio_coluna = self.column
                fechou = False
                self.avanco()
                self.avanco()
                while self.index < len(self.source):
                    if ord(caractere) > 127:
                        raise LexerError("caractere invalido", self.line, self.column)
                    if (self.source[self.index] == "*" and self.index + 1 < len(self.source) and self.source[self.index + 1] == "/"): #FECHOU O COMENTARIO
                        self.avanco()
                        self.avanco()
                        fechou = True
                        break
                    self.avanco()
                if not fechou:
                    raise LexerError("comentario nao fechado", inicio_linha, inicio_coluna)
                continue
            return

    def tokens(self) -> Iterator[Token]:
        temporario = []
        while self.index < len(self.source):
            caractere = self.source[self.index]
            if self.index >= len(self.source):
                break
            caratere = self.source[self.index]
            letra = self.id_letra(caractere)

            if letra or caractere == "_":

    def scan(self) -> list[Token]:
        return list(self.tokens())
    
    # def espacos(self): #pula espaco até um caracter
    #     while self.caracter_atual() in (" ","\n","\r","\t"):
    #         self.avanco()
            
