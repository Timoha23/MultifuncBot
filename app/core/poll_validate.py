import ast


async def poll_validator(text):
    """
    Функция валидатор для создания опроса
    """

    valid_keys = ['question', 'answers', 'chat_id', 'is_anon']

    # пытаемся преобразовать данные в словарь
    try:
        data = ast.literal_eval(text)
    except Exception as ex:
        return {
            'error': 'cant_convert_to_dict',
            'error_ex': ex,
            'description': ('Ошибка: Невозможно преобразовать в словарь. '
                            'Проверьте внимательно данные и приведите их в '
                            'соответствии с образцом')
        }

    # проверка на валидность ключей. Ключи невалидны если:
    # 1. расположены в неправильном порядке
    # 2. есть лишние ключи
    # 3. ошибка в написании ключей пользователем
    try:
        if valid_keys != list(data.keys()):
            return {
                'error': 'not_valid_keys',
                'error_ex': None,
                'description': ('Ошибка: Неверные ключи. Проверьте, что:\n'
                                '1. Ключи расположены в верном порядке\n'
                                '2. Нет лишних ключей\n'
                                '3. Нет ошибок в написании ключей.')
            }
    except AttributeError:
        return {
                'error': 'not_valid_keys',
                'error_ex': None,
                'description': ('Ошибка: Неверный формат. '
                                'Проверьте введенные данные')
            }

    # пытаем преобразовать id к int, если не получается возвращаем ошибку
    try:
        int(data['chat_id'])
    except ValueError:
        return {
            'error': 'chat_id_value_error',
            'error_ex': None,
            'description': ('Ошибка: Поле chat_id. ID может быть только'
                            ' числовым значением')
        }

    # проверка на то, что вопрос не превосходит 300 символов
    if len(data['question']) >= 300:
        return {
            'error': 'max_length_question',
            'error_ex': None,
            'description': ('Ошибка: Вопрос не должен превышать 300 символов')
        }

    # проверка на то, что в ключе answers лежит list
    if isinstance(data['answers'], list) is False:
        return {
            'error': 'answers_not_list',
            'error_ex': None,
            'description': ('Ошибка: Поле answers. Данное значение принимает'
                            ' list -> [].')
            }

    # проверка на то, что варинтов ответа не больше 10
    if len(data['answers']) > 10:
        return {
            'error': 'max_answers',
            'error_ex': None,
            'description': ('Ошибка: Вариантов ответа не может быть больше 10')
        }
    # и не меньше 2
    elif len(data['answers']) < 2:
        return {
            'error': 'max_answers',
            'error_ex': None,
            'description': ('Ошибка: Вариантов ответа не может быть меньше 2')
        }

    # проверяем что варианты длины вариантов ответов не превышают 100 символов

    for index, ans in enumerate(data['answers']):
        if len(ans) > 100:
            return {
                'error': 'max_length_answer',
                'error_ex': None,
                'description': (f'Ошибка: Вариант ответа под номером {index+1}'
                                f' имеет длину больше 100 символов')
            }

    # проверка на то, что в ключ is_anon введен один из четырех вариантов
    # (0,1,True,False)
    try:
        is_anon = int(data['is_anon'])
        if is_anon not in [0, 1]:
            int('a')  # вызываю исключение
    except ValueError:
        return {
            'error': 'anon_value_error',
            'error_ex': None,
            'description': ('Ошибка: Поле is_anon. Данное значение принимает'
                            ' только 0, 1, True, False')
            }

    return data
