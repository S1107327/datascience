import fasttext

def save_vec(model, dim):
    """ Convert FastText bin model in a character dictionary for the embedding
        Parameters
        ---------
        model: model
            The fasttext model
    """
    words = model.get_words()
    with open(f"fasttext.vec", 'w') as file_out:
        file_out.write(str(len(words)) + " " + str(model.get_dimension()) + "\n")
        for w in words:
            # Prendo la rappresentazione vettoriale della parola ciclata attualmente che è vector
            vector = model.get_word_vector(w)
            vector_string = ""
            for value in vector:
                vector_string += " " + str(value)
            try:
                file_out.write(w + vector_string + "\n")
            except:
                pass

train_data_path = "bigrams.txt"
dim = 3
model = fasttext.train_unsupervised(train_data_path, model="skipgram", dim=3, epoch=20)
save_vec(model, dim)