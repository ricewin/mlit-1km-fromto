"""定数"""


class Const:
    # 平休日
    dayflag: dict[int, str] = {
        0: "休日",
        1: "平日",
        2: "全日",
    }

    # 時間帯
    timezone: dict[int, str] = {
        0: "昼",
        1: "深夜",
        2: "全日",
    }

    # 集計内容
    dataset: dict[str, str] = {
        "mdp": "1kmメッシュ",
        "fromto": "市区町村単位発地別",
    }

    # 居住地区分
    from_area: dict[int, str] = {
        0: "同一市区町村",
        1: "同一都道府県かつ自市区町村と異なる市町村",
        2: "同一の地方ブロックかつ異なる都道府県",
        3: "異なる地方ブロック",
    }
