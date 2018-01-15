class Warnings:

    def __init__(self):
        self._warnings = []

    def add(self, item_id: str, message: str):
        self._warnings.append({
            "item_id": item_id,
            "message": message,
        })

    def print(self):
        print('\n')
        print("\033[1;33m" + "=" * 50)
        print(" "*16 + "<<<< Warnings >>>>")
        print("=" * 50 + "\033[0m")
        print()

        if self._warnings:
            for num, warning in enumerate(self._warnings):
                print("\033[1;33m#### Warning #{} \033[0m".format(num))
                print('item with id={}: '.format(warning['item_id']), end='')
                print(warning["message"])
                print()

        else:
            print(">>> No warnings found!")


warnings = Warnings()
