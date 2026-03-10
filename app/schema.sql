CREATE TABLE IF NOT EXISTS recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    ingredients TEXT NOT NULL DEFAULT '[]',
    steps TEXT DEFAULT '[]',
    portions INTEGER DEFAULT 4,
    prep_time INTEGER,
    cook_time INTEGER,
    image_path TEXT,
    source_url TEXT,
    is_favorite INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS recipe_tag (
    recipe_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, tag_id),
    FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shopping_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shopping_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    recipe_id INTEGER,
    name TEXT NOT NULL,
    quantity TEXT,
    unit TEXT,
    checked INTEGER DEFAULT 0,
    FOREIGN KEY (list_id) REFERENCES shopping_list(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS shopping_item_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity TEXT,
    unit TEXT,
    count INTEGER DEFAULT 1,
    UNIQUE(name COLLATE NOCASE)
);
