class DecoratorsService:

    @staticmethod
    def paginate(function):
        """Установка пагинации."""
        def wrapper(self, *args, **kwargs):
            if 'count' not in kwargs:
                kwargs['count'] = self.settings.count
            if 'offset' not in kwargs:
                kwargs['offset'] = self.settings.offset
            return function(self, *args, **kwargs)
        return wrapper


decorator_service = DecoratorsService()
