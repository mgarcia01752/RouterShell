class NumberChecker:
    @staticmethod
    def is_string_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_string_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_string_number(s):
        return NumberChecker.is_float(s)