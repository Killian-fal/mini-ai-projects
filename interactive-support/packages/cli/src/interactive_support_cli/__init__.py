from dotenv import load_dotenv


def main():
    load_dotenv()
    from interactive_support_observability import init_observability
    from .main import start_conversation

    init_observability()
    start_conversation()
