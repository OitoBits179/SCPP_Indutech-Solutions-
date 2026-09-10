import json
import os


ARQUIVO = "banco_dados.json"


def carregar_dados():

    if not os.path.exists(ARQUIVO):

        try:

            with open(
                ARQUIVO,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    [],
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception:
            pass

        return []

    try:

        with open(
            ARQUIVO,
            "r",
            encoding="utf-8"
        ) as f:

            dados = json.load(f)

            if isinstance(dados, list):
                return dados

            return []

    except Exception:

        return []


def salvar_dados(dados):

    try:

        with open(
            ARQUIVO,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                dados,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception:

        return False
