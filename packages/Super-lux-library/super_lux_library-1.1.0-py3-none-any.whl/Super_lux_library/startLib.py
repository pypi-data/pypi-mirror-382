def start():
    print("🎉 Welcome to our awesome library!")
    print("Choose a library from the list: random / os / time / turtle / json")
    choice = input("Enter library name: ").strip().lower()

    libraries = {
        "random": {
            "randint(a, b)": "Returns a random integer between a and b.",
            "choice(seq)": "Returns a random element from the sequence seq.",
            "shuffle(seq)": "Shuffles the sequence seq randomly.",
            "random()": "Returns a random float between 0 and 1.",
            "uniform(a, b)": "Returns a random float between a and b.",
            "sample(population, k)": "Returns k random elements from population.",
            "seed(x)": "Sets the seed for the random number generator."
        },
        "os": {
            "os.getcwd()": "Returns the current working directory path.",
            "os.listdir(path)": "Returns a list of files and directories in path.",
            "os.mkdir(path)": "Creates a new directory at path.",
            "os.remove(path)": "Removes a file at path.",
            "os.rename(src, dst)": "Renames a file or directory.",
            "os.path.exists(path)": "Checks if a path exists.",
            "os.path.join(path1, path2)": "Joins two paths into one."
        },
        "time": {
            "time.sleep(sec)": "Pauses the program for sec seconds.",
            "time.time()": "Returns current time since 1970 in seconds.",
            "time.localtime()": "Returns local time as a struct_time object.",
            "time.strftime(format)": "Returns time formatted according to format.",
            "time.gmtime()": "Returns UTC time as a struct_time object."
        },
        "turtle": {
            "forward(dist)": "Moves turtle forward by dist units.",
            "backward(dist)": "Moves turtle backward by dist units.",
            "right(angle)": "Turns turtle right by angle degrees.",
            "left(angle)": "Turns turtle left by angle degrees.",
            "circle(radius)": "Draws a circle with given radius.",
            "penup()": "Lifts the pen so turtle moves without drawing.",
            "pendown()": "Puts the pen down to draw while moving.",
            "color(c)": "Changes pen color to c."
        },
        "json": {
            "json.dump(obj, file)": "Writes obj to a JSON file.",
            "json.dumps(obj)": "Converts obj to a JSON string.",
            "json.load(file)": "Reads a JSON file and returns its content.",
            "json.loads(str)": "Parses a JSON string into Python object.",
            "json.JSONEncoder": "Class for encoding Python objects into JSON.",
            "json.JSONDecoder": "Class for decoding JSON into Python objects."
        }
    }

    if choice in libraries:
        print(f"\n📚 Available commands in the {choice} library:")
        for cmd, desc in libraries[choice].items():
            print(f"- {cmd} : {desc}")
    else:
        print("⚠️ Library not found, please try again.")