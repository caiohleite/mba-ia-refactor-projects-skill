from dataclasses import dataclass, field


VALID_CATEGORIES = (
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
)

VALID_ORDER_STATUSES = (
    "pendente",
    "aprovado",
    "enviado",
    "entregue",
    "cancelado",
)


@dataclass(frozen=True)
class Product:
    id: int
    nome: str
    descricao: str
    preco: float
    estoque: int
    categoria: str
    ativo: int
    criado_em: str

    @classmethod
    def from_row(cls, row):
        return cls(**{field_name: row[field_name] for field_name in cls.__dataclass_fields__})

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "estoque": self.estoque,
            "categoria": self.categoria,
            "ativo": self.ativo,
            "criado_em": self.criado_em,
        }


@dataclass(frozen=True)
class User:
    id: int
    nome: str
    email: str
    password_hash: str
    tipo: str
    criado_em: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            nome=row["nome"],
            email=row["email"],
            password_hash=row["senha"],
            tipo=row["tipo"],
            criado_em=row["criado_em"],
        )

    def to_public_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
            "criado_em": self.criado_em,
        }

    def to_login_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
        }


@dataclass(frozen=True)
class OrderItem:
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: float

    def to_dict(self):
        return {
            "produto_id": self.produto_id,
            "produto_nome": self.produto_nome,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
        }


@dataclass
class Order:
    id: int
    usuario_id: int
    status: str
    total: float
    criado_em: str
    itens: list[OrderItem] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "status": self.status,
            "total": self.total,
            "criado_em": self.criado_em,
            "itens": [item.to_dict() for item in self.itens],
        }
