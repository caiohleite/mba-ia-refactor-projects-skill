from loja import create_app


app = create_app()

if __name__ == "__main__":
    app.logger.info("Servidor iniciado em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
