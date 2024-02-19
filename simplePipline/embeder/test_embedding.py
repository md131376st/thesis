from simplePipline.embeder.embeder import OpenAIEmbeder

if __name__ == '__main__':
    embeding = OpenAIEmbeder(context=[])
    embeding.embedding(["hiisdg", "dvsfgsf"], "text-embedding-3-small", False)
    hi = embeding.get_embedding()
    # print(len(hi))
    pass
