"""Valida arquivos anexados a exercícios e respostas."""

from pathlib import Path

from django.core.exceptions import ValidationError


EXTENSOES_EXERCICIO = {
    ".pdf", ".doc", ".docx", ".odt", ".rtf",
    ".xls", ".xlsx", ".xlsm", ".ods", ".csv",
    ".ppt", ".pptx", ".odp",
    ".ipynb", ".py", ".txt", ".md", ".json", ".xml", ".yaml", ".yml",
    ".tex", ".sql", ".r", ".java", ".c", ".cpp", ".h", ".cs", ".js",
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".zip",
}
TAMANHO_MAXIMO_ARQUIVO = 20 * 1024 * 1024


def validar_arquivo_exercicio(arquivo):
    extensao = Path(arquivo.name).suffix.lower()
    if extensao not in EXTENSOES_EXERCICIO:
        raise ValidationError(
            "Formato não permitido. Envie PDF, Word, Excel/CSV, PowerPoint, "
            "notebook do Colab (.ipynb), arquivos de texto/código, imagens ou ZIP."
        )
    if arquivo.size > TAMANHO_MAXIMO_ARQUIVO:
        raise ValidationError("Cada arquivo deve ter no máximo 20 MB.")
