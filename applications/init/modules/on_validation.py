#  SERVER MUST BE RELOADED WHEN CHANGED


def beautify_name(form):
    def beautify(name):
        chunks = name.split(" ")
        new_chunks = []
        for chunk in chunks:
            new_chunks.append(chunk.capitalize())
        return " ".join(new_chunks)

    form.vars.first_name = beautify(form.vars.first_name)
    form.vars.last_name = beautify(form.vars.last_name)