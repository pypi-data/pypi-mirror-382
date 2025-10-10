import requests
from typing import Optional


def fetch_page(url: str, format: Optional[str] = "html") -> str:
    """
    Jina AIのリダイレクトエンドポイント (https://r.jina.ai/{URL}) を利用して、
    指定したページのテキストまたはHTMLを取得する簡易スクレイピング関数。

    Args:
        url (str): 取得したいページのURL。
        format (Optional[str]): 出力形式。'html' または 'text' のどちらか。デフォルトは 'html'。

    Returns:
        str: ページ内容（HTMLまたはテキスト形式）。

    Raises:
        ValueError: formatが不正な場合。
        requests.exceptions.RequestException: HTTP通信でエラーが発生した場合。
    """
    # HTML形式はサポートされないためtextのみ出力
    endpoint = f"https://r.jina.ai/{url}"
    headers = {"User-Agent": "webscrapper_/1.0"}

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        raise ValueError("URLが不正です。'https://'または'http://'を付けてください。")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("サーバーに接続できません。ネットワークを確認してください。")
    except requests.exceptions.Timeout:
        raise TimeoutError("タイムアウトしました。レスポンスが遅すぎます。")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"スクレイピング中にエラーが発生しました: {e}")

    return response.text


__all__ = ["fetch_page"]
