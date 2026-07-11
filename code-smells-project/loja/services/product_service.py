from loja.database import get_db
from loja.errors import NotFoundError, ValidationError
from loja.models import VALID_CATEGORIES
from loja.repositories.product_repository import ProductRepository
from loja.services.validators import optional_float, require_number, require_object


class ProductService:
    def __init__(self, repository=None):
        self.repository = repository or ProductRepository()

    def list_products(self):
        return [product.to_dict() for product in self.repository.list_all()]

    def get_product(self, product_id):
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Produto não encontrado")
        return product.to_dict()

    def create_product(self, data):
        values = self._validate_product(data, require_all=True)
        product_id = self.repository.create(**values)
        get_db().commit()
        return product_id

    def update_product(self, product_id, data):
        if self.repository.get_by_id(product_id) is None:
            raise NotFoundError("Produto não encontrado")
        values = self._validate_product(data, require_all=True)
        self.repository.update(product_id, **values)
        get_db().commit()

    def delete_product(self, product_id):
        if self.repository.get_by_id(product_id) is None:
            raise NotFoundError("Produto não encontrado")
        self.repository.delete(product_id)
        get_db().commit()

    def search_products(self, term="", category=None, min_price=None, max_price=None):
        parsed_min = optional_float(min_price, "preco_min")
        parsed_max = optional_float(max_price, "preco_max")
        if parsed_min is not None and parsed_max is not None and parsed_min > parsed_max:
            raise ValidationError("preco_min não pode ser maior que preco_max")
        products = self.repository.search(term, category, parsed_min, parsed_max)
        return [product.to_dict() for product in products]

    @staticmethod
    def _validate_product(data, require_all):
        data = require_object(data)
        required = ("nome", "preco", "estoque")
        if require_all:
            for field_name in required:
                if field_name not in data:
                    labels = {"nome": "Nome", "preco": "Preço", "estoque": "Estoque"}
                    raise ValidationError(f"{labels[field_name]} é obrigatório")

        name = data["nome"]
        if not isinstance(name, str):
            raise ValidationError("Nome deve ser texto")
        name = name.strip()
        if len(name) < 2:
            raise ValidationError("Nome muito curto")
        if len(name) > 200:
            raise ValidationError("Nome muito longo")

        price = require_number(data["preco"], "Preço")
        stock = require_number(data["estoque"], "Estoque")
        if price < 0:
            raise ValidationError("Preço não pode ser negativo")
        if not isinstance(stock, int) or stock < 0:
            raise ValidationError("Estoque deve ser um inteiro não negativo")

        description = data.get("descricao", "")
        if not isinstance(description, str):
            raise ValidationError("Descrição deve ser texto")
        category = data.get("categoria", "geral")
        if category not in VALID_CATEGORIES:
            raise ValidationError(f"Categoria inválida. Válidas: {list(VALID_CATEGORIES)}")

        return {
            "nome": name,
            "descricao": description,
            "preco": price,
            "estoque": stock,
            "categoria": category,
        }
