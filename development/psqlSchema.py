users = """
    name VARCHAR(64) PRIMARY KEY,
    hash VARCHAR(256),
    salt VARCHAR(64),
    org VARCHAR(64),
    role VARCHAR(64),
    token VARCHAR(64),
    deviceID VARCHAR(64)
    """

symptoms = """
    id SMALLINT PRIMARY KEY,
    description VARCHAR(256),
    errCode VARCHAR(16),
    phrase VARCHAR(256),
    keywords VARCHAR(512),
    precision SMALLINT
    """

sym_err = """
    id SMALLINT PRIMARY KEY,
    symId SMALLINT REFERENCES Symptoms (id),
    errorId SMALLINT
    """

resolutions = """
    id SMALLINT PRIMARY KEY,
    errorId SMALLINT,
    description VARCHAR(256)
    """

#List of table dicts (dicts have name of table and schema contents)
tables = [
    {
        "name":    "Users",
        "content": users,
    },
    {
        "name":    "Symptoms",
        "content": symptoms,
    },
    {
        "name":    "Sym_Err",
        "content": sym_err,
    },
    {
        "name":    "Resolutions",
        "content": resolutions,
    },
]
