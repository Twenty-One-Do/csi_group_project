def db_initialization(cur):
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username CHAR(25) NOT NULL UNIQUE,
        password CHAR(65) NOT NULL,
        consecutive_cnt INTEGER DEFAULT 0,
        admin INTEGER NOT NULL DEFAULT 0,
        reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_acc_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_deleted INTEGER NOT NULL DEFAULT 0
    );
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title CHAR(25),
        contents TEXT,
        user_id INTEGER,
        reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        mod_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        like_cnt INTEGER DEFAULT 0,
        cnt INTEGER DEFAULT 1,
        thumbnail TEXT,
        FOREIGN KEY(user_id) REFERENCES Members(id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user_id INTEGER,
        contents TEXT,
        reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        mod_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES Members(id),
        FOREIGN KEY(post_id) REFERENCES Posts(id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Post_Like (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        post_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES Members(id),
        FOREIGN KEY(post_id) REFERENCES Posts(id)
    )
    ''')

def search_query_execute(cur, queries):
    context = {key: [] for key in queries.keys()}

    for k in context.keys():

        attributes = ', '.join(queries[k]['attributes'])
        if queries[k]['condition'] is not None :
            query = '''
                    SELECT {}
                    FROM {}
                    WHERE {};
                    '''.format(attributes, queries[k]['table'], queries[k]['condition'])
        else :
            query = '''
                    SELECT {}
                    FROM {};
                    '''.format(attributes, queries[k]['table'])

        result = cur.execute(query)
        result = result.fetchall()
        for res in result:
            context[k].append(
                {key: val for key, val in zip(queries[k]['attributes'], res)})
        if len(context[k]) == 0:
            context[k].append(None)
    return context

def search_query_execute_join(cur, queries):
    context = {key: [] for key in queries.keys()}

    for k in context.keys():
        a_attributes = ','.join(['a.'+att for att in queries[k]['a_attributes']])
        b_attributes = ','.join(['b.'+att for att in queries[k]['b_attributes']])

        if queries[k]['condition'] is not None :
            query = f'''
                SELECT {a_attributes}, {b_attributes}
                FROM {queries[k]['a_table']} a INNER JOIN {queries[k]['b_table']} b ON a.{queries[k]['a_key']}=b.{queries[k]['b_key']}
                WHERE {queries[k]['condition']};
                '''
        else :
            query = f'''
                SELECT {a_attributes}, {b_attributes}
                FROM {queries[k]['a_table']} a INNER JOIN {queries[k]['b_table']} b ON a.{queries[k]['a_key']}=b.{queries[k]['b_key']};
                '''

        result = cur.execute(query)
        result = result.fetchall()
        for res in result:
            context[k].append(
                {key: val for key, val in zip((a_attributes+','+b_attributes).split(','), res)})
        if len(context[k]) == 0:
            context[k].append(None)
    return context

def check_like(cur, post_id, user_id):
    search_query = {
        'is_like':{
            'table': 'Post_Like',
            'attributes': ['id','post_id','user_id'],
            'condition': f'post_id = {post_id} AND user_id = {user_id}'
        }
    }
    res = search_query_execute(cur,search_query)['is_like'][0]

    if res is None:
        return False
    else:
        return True
