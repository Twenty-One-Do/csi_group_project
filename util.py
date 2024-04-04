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


def add_sample(connection, cur):
    cur.execute('''
    INSERT INTO Members (username, password, consecutive_cnt, admin, reg_date, last_acc_date, is_deleted)
    VALUES
    ('이혜민', 'hashed_password_1', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('양승조', 'hashed_password_2', 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('이원도', 'hashed_password_3', 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('임현경', 'hashed_password_4', 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('현유경', 'hashed_password_5', 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0);
    ''')
    cur.execute('''
    INSERT INTO Posts (title, thumbnail, like_cnt, user_id, reg_date, contents)
    VALUES
    ('안녕하세요!', 'https://velog.velcdn.com/images/dnjseh8962/post/f6c4feb7-eb76-4213-882e-aa80643d4f00/image.png', 5, 1, CURRENT_TIMESTAMP, '모두 반가워요 다들 힘내요!'),
    ('반가워요!', 'https://velog.velcdn.com/images/dnjseh8962/post/cf03a58f-6c61-4277-b694-b81001b8e9c8/image.png', 3, 2, CURRENT_TIMESTAMP, '프로젝트 힘내봅시다!'),
    ('오늘의 공부', 'https://velog.velcdn.com/images/dnjseh8962/post/c87af4b8-e454-4918-bd59-84a68a3ee1f2/image.png', 3, 2, CURRENT_TIMESTAMP, '안함');
    ''')
    connection.commit()


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
    
def db_clean(connection, cur):
    cur.execute(f"UPDATE Posts SET like_cnt=0")
    cur.execute(f"DROP TABLE Post_Like")
    connection.commit()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Post_Like (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        post_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES Members(id),
        FOREIGN KEY(post_id) REFERENCES Posts(id)
    )
    ''')
