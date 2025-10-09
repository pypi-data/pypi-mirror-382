from typing import List, Optional

import checkmarkandcross


def null_str(value: Optional[str]) -> str:
    if value is None:
        return 'NULL'
    else:
        return value


def row_count(count: int) -> str:
    return f'{count} row{"" if count == 1 else "s"}'


def rows_table(rows: List[List]) -> str:
    return ''.join(map(
        lambda row: '<tr>' + ''.join(map(lambda e: f'<td>{null_str(e)}</td>', row)) + '</tr>',
        rows
    ))


def wrap_image(val: bool, msg: str = '') -> str:
    image = checkmarkandcross.image_html(val, size=24, title=msg)
    return f'''
        <div style="display: flex; align-items: center; margin-top: 0.5rem">
            {image}
            <span style="margin-left: 0.5rem">
                {msg}
            </span>
        </div>
    '''
