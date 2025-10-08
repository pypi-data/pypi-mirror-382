class Terminal:
    @staticmethod
    def link(text: str, url: str) -> str:
        ESC = "\033"
        START_LINK = f"{ESC}]8;;{url}{ESC}\\"
        END_LINK = f"{ESC}]8;;{ESC}\\"
        STYLE = f"{ESC}[4;34m"  # underline + blue
        RESET = f"{ESC}[0m"
        return f"{START_LINK}{STYLE}{text}{RESET}{END_LINK}"

    @staticmethod
    def color(text: str, color: str = "red") -> str:
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "cyan": "\033[96m",
            "bold": "\033[1m",
        }
        return f"{colors.get(color, '')}{text}\033[0m"
