import connection
import util


@connection.connection_handler
def get_sorted_questions(cursor, order_by, order_direction):
    query = """
        SELECT *,
        (SELECT COUNT(id) FROM answer a WHERE q.id = a.question_id) AS number_of_answers
        FROM question q
        ORDER BY {} {};
    """.format(order_by, order_direction)
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_question_data_by_id_dm(cursor, question_id):
    query = """
     SELECT *
     FROM question
     WHERE id= %(question_id)s;"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchone()


@connection.connection_handler
def get_answers_by_question_id_dm(cursor, question_id):
    query = """
     SELECT *
     FROM answer
     WHERE question_id= %(question_id)s
     ORDER BY submission_time DESC"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchall()


@connection.connection_handler
def add_question_dm(cursor, submission_time, title, message, image_path):
    cursor.execute("""
                    INSERT INTO question(submission_time, view_number, vote_number, title, message, image)
                    VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s)
                    RETURNING id;""",
                   {'submission_time': submission_time,
                    'view_number': 0,
                    'vote_number': 0,
                    'title': title,
                    'message': message,
                    'image': image_path})
    new_question_id = cursor.fetchone()['id']
    return new_question_id


@connection.connection_handler
def add_answer_dm(cursor, submission_time, message, question_id, image_path):
    cursor.execute("""
                 INSERT INTO answer(submission_time,vote_number,question_id,message,image)
                 VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s,%(message)s, %(image)s);
                 """,
                   {'submission_time': submission_time,
                    'vote_number': 0,
                    'question_id': question_id,
                    'message': message,
                    'image': image_path})


@connection.connection_handler
def get_question_id_by_answer(cursor, answer_id):
    query = """
        SELECT question_id 
        FROM answer
        WHERE id = %(answer_id)s;"""
    cursor.execute(query, {"answer_id": answer_id})
    return cursor.fetchone()["question_id"]


@connection.connection_handler
def delete_question_dm(cursor, question_id):
    image_paths = get_image_paths(question_id)
    cursor.execute("""
        DELETE FROM comment
        WHERE answer_id IN
        (SELECT answer_id
        FROM answer
        WHERE question_id = %(question_id)s);

        DELETE FROM answer
        WHERE question_id = %(question_id)s;

        DELETE FROM comment
        WHERE question_id = %(question_id)s;

        DELETE FROM question_tag
        WHERE question_id = %(question_id)s;

        DELETE FROM question
        WHERE id = %(question_id)s;
        """, {'question_id': question_id})
    util.delete_image_files(image_paths)


@connection.connection_handler
def delete_answer_by_id(cursor, answer_id):
    query = """
        DELETE FROM comment
        WHERE answer_id  = %(answer_id)s;
        
        DELETE FROM answer
        WHERE id  = %(answer_id)s
        RETURNING image, question_id;"""
    cursor.execute(query, {"answer_id": answer_id})
    data = cursor.fetchone()
    image_path = data['image']
    question_id = data["question_id"]
    util.delete_image_files(image_path)
    return question_id


@connection.connection_handler
def get_image_paths(cursor, question_id):
    cursor.execute("""
                    SELECT image
                    FROM question
                    WHERE id = %(question_id)s
                    UNION ALL
                    SELECT image
                    FROM answer
                    WHERE question_id = %(question_id)s
                    """, {'question_id': question_id})
    images = cursor.fetchall()
    image_paths = [image['image'] for image in images]
    return image_paths


@connection.connection_handler
def update_question_dm(cursor, title, message,old_image_path, new_image_file, question_id, remove_image):
    new_image_path = None
    if remove_image:
        util.delete_image_files([old_image_path])
    if new_image_file.filename !="":
        new_image_path = util.save_image_dm(new_image_file)
    if not remove_image and new_image_file.filename =="":
        new_image_path = old_image_path
    query = """
            UPDATE question
            SET 
            title = %(title)s,
            message = %(message)s,
            image = %(image)s
            WHERE id = %(question_id)s;"""
    cursor.execute(query, {'title': title, 'message': message, 'image': new_image_path,'question_id':question_id})


@connection.connection_handler
def vote_on_question_dm(cursor,question_id,vote_direction):
    query = """
            UPDATE question
            SET vote_number = CASE
                WHEN %(vote_direction)s = 'up' THEN vote_number + 1
                WHEN %(vote_direction)s = 'down' THEN vote_number - 1
                ELSE vote_number
            END
            WHERE id = %(question_id)s;"""
    cursor.execute(query, {'question_id':question_id, "vote_direction":vote_direction})



@connection.connection_handler
def vote_on_answer_dm(cursor, answer_id, vote_direction):
    cursor.execute("""
        UPDATE answer 
        SET vote_number = CASE
            WHEN %(vote_direction)s = 'up' THEN vote_number + 1
            WHEN %(vote_direction)s = 'down' THEN vote_number - 1
            ELSE vote_number
        END
        WHERE id = %(answer_id)s
        RETURNING question_id;
    """, {'answer_id': answer_id, 'vote_direction': vote_direction})
    question_id = cursor.fetchone()['question_id']
    return question_id



@connection.connection_handler
def view_question_dm(cursor, question_id):
    query = """
        UPDATE question
        SET view_number = view_number + 1
        WHERE id = %(question_id)s;"""
    cursor.execute(query, {"question_id": question_id})
