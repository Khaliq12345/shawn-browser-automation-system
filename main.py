from src.platforms.perplexity import query_perplexity


def main():
    print("Hello from shawn-browser-automation-system !")
    prompt = "Explique-moi la théorie de la relativité en termes simples."
    query_perplexity(prompt)


if __name__ == "__main__":
    main()
