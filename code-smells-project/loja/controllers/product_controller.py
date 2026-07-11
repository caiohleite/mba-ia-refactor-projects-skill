from loja.services.product_service import ProductService


class ProductController:
    def __init__(self, service=None):
        self.service = service or ProductService()

    def list_products(self):
        return {"dados": self.service.list_products(), "sucesso": True}, 200

    def get_product(self, product_id):
        return {"dados": self.service.get_product(product_id), "sucesso": True}, 200

    def create_product(self, data):
        product_id = self.service.create_product(data)
        return {
            "dados": {"id": product_id},
            "sucesso": True,
            "mensagem": "Produto criado",
        }, 201

    def update_product(self, product_id, data):
        self.service.update_product(product_id, data)
        return {"sucesso": True, "mensagem": "Produto atualizado"}, 200

    def delete_product(self, product_id):
        self.service.delete_product(product_id)
        return {"sucesso": True, "mensagem": "Produto deletado"}, 200

    def search_products(self, query):
        products = self.service.search_products(
            term=query.get("q", ""),
            category=query.get("categoria"),
            min_price=query.get("preco_min"),
            max_price=query.get("preco_max"),
        )
        return {"dados": products, "total": len(products), "sucesso": True}, 200
